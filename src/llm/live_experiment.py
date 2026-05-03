from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

from benchmarks.bin_packing.evaluator import BinPackingEvaluator
from benchmarks.bin_packing.instances import (
    BinPackingInstance,
    default_train_validation_test_suites,
)
from llm.model_client import (
    GeminiClientError,
    GeminiMutationProvider,
    GeneratedCode,
    build_generated_code,
)
from sandbox.static_checks import ValidationConfig, validate_candidate_code

MUTATION_PROMPT_VERSION = "score-bin-mutation-v1"
REPAIR_PROMPT_VERSION = "score-bin-repair-v1"
PHASE12_CLAIM_BOUNDARY = (
    "LLM is one mutation operator inside a constrained program-search system; "
    "live LLM superiority is not claimed"
)

_PARENT_PROGRAM_ID = "phase12-parent-tight-fit"
_PARENT_CODE = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected
""".strip()

_INVALID_REPAIR_TARGET = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return globals()["hidden_solution"]
""".strip()


class MetadataLLMProvider(Protocol):
    def generate_with_metadata(
        self,
        prompt: str,
        *,
        prompt_version: str = MUTATION_PROMPT_VERSION,
    ) -> GeneratedCode:
        raise NotImplementedError


@dataclass(frozen=True)
class LLMExperimentConfig:
    candidate_budget: int = 4
    item_count: int = 16
    timeout_seconds: float = 0.25
    prompt_version: str = MUTATION_PROMPT_VERSION
    repair_prompt_version: str = REPAIR_PROMPT_VERSION
    use_env_live_provider: bool = False


@dataclass
class ScriptedLLMProvider:
    model_name: str = "scripted-llm"
    responses: Sequence[str] = ()
    temperature: float = 0.0

    def __post_init__(self) -> None:
        self._index = 0

    def generate_with_metadata(
        self,
        prompt: str,
        *,
        prompt_version: str = MUTATION_PROMPT_VERSION,
    ) -> GeneratedCode:
        if self.responses:
            raw_text = self.responses[min(self._index, len(self.responses) - 1)]
        else:
            raw_text = _deterministic_code(self._index)
        self._index += 1
        return build_generated_code(
            raw_text,
            prompt=prompt,
            model_name=self.model_name,
            prompt_version=prompt_version,
            temperature=self.temperature,
            latency_seconds=0.0,
        )


class DeterministicLLMProvider(ScriptedLLMProvider):
    def __init__(self) -> None:
        super().__init__(
            model_name="deterministic-fallback",
            responses=(),
            temperature=0.0,
        )


def build_phase12_report(
    *,
    config: Optional[LLMExperimentConfig] = None,
    live_provider: Optional[MetadataLLMProvider] = None,
    repair_provider: Optional[MetadataLLMProvider] = None,
) -> Dict[str, object]:
    resolved = config or LLMExperimentConfig()
    if resolved.candidate_budget < 1:
        raise ValueError("candidate_budget must be positive")

    _train, validation, test = default_train_validation_test_suites(
        item_count=resolved.item_count
    )
    evaluator = BinPackingEvaluator(timeout_seconds=resolved.timeout_seconds)
    validation_config = ValidationConfig(allowed_function="score_bin")

    candidate_records: List[Mapping[str, object]] = []
    candidate_records.extend(
        _evaluate_provider_candidates(
            method="deterministic_fallback",
            provider=DeterministicLLMProvider(),
            provider_status="configured",
            candidate_budget=resolved.candidate_budget,
            prompt_version=resolved.prompt_version,
            evaluator=evaluator,
            validation_config=validation_config,
            validation_instances=validation,
            test_instances=test,
        )
    )
    candidate_records.extend(
        _evaluate_repair_candidates(
            provider=repair_provider or DeterministicLLMProvider(),
            candidate_budget=resolved.candidate_budget,
            prompt_version=resolved.repair_prompt_version,
            evaluator=evaluator,
            validation_config=validation_config,
            validation_instances=validation,
            test_instances=test,
        )
    )

    live_status = "not_configured"
    live_model_name = ""
    selected_live_provider = live_provider
    if selected_live_provider is None and resolved.use_env_live_provider:
        try:
            selected_live_provider = GeminiMutationProvider.from_env()
        except GeminiClientError:
            selected_live_provider = None
    if selected_live_provider is not None:
        live_status = "configured"
        live_records = _evaluate_provider_candidates(
            method="live_gemini",
            provider=selected_live_provider,
            provider_status=live_status,
            candidate_budget=resolved.candidate_budget,
            prompt_version=resolved.prompt_version,
            evaluator=evaluator,
            validation_config=validation_config,
            validation_instances=validation,
            test_instances=test,
        )
        candidate_records.extend(live_records)
        if live_records:
            live_model_name = str(live_records[0]["model_name"])

    operator_rows = [
        _operator_row("deterministic_fallback", candidate_records, "configured"),
        _operator_row("llm_repair", candidate_records, "configured"),
        _operator_row(
            "live_gemini",
            candidate_records,
            live_status,
            model_name=live_model_name,
        ),
    ]
    best_row = min(
        operator_rows,
        key=lambda row: (
            float(row["best_validation_score"])
            if row["best_validation_score"] is not None
            else float("inf"),
            str(row["method"]),
        ),
    )
    return {
        "phase": 12,
        "benchmark": "live_llm_mutation",
        "methods": (
            "deterministic_fallback",
            "llm_repair",
            "live_gemini",
        ),
        "controls": {
            "candidate_budget": resolved.candidate_budget,
            "item_count": resolved.item_count,
            "timeout_seconds": resolved.timeout_seconds,
            "prompt_version": resolved.prompt_version,
            "repair_prompt_version": resolved.repair_prompt_version,
            "benchmark_split": "default_bin_packing_train_validation_test",
        },
        "live_provider_configured": live_status == "configured",
        "operator_comparison": operator_rows,
        "candidate_audit": candidate_records,
        "best_method": best_row["method"],
        "best_validation_score": best_row["best_validation_score"],
        "claim_boundary": PHASE12_CLAIM_BOUNDARY,
        "framing": (
            "LLM is one mutation operator inside a constrained program-search system."
        ),
        "limitations": (
            "Default runs use deterministic fallback providers. Live Gemini "
            "runs require GEMINI_API_KEY and still pass through static "
            "validation and sandboxed scoring."
        ),
    }


def _evaluate_provider_candidates(
    *,
    method: str,
    provider: MetadataLLMProvider,
    provider_status: str,
    candidate_budget: int,
    prompt_version: str,
    evaluator: BinPackingEvaluator,
    validation_config: ValidationConfig,
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
) -> List[Mapping[str, object]]:
    records: List[Mapping[str, object]] = []
    for index in range(candidate_budget):
        prompt = _mutation_prompt(index=index, prompt_version=prompt_version)
        generation = provider.generate_with_metadata(
            prompt,
            prompt_version=prompt_version,
        )
        records.append(
            _evaluate_generated_code(
                method=method,
                candidate_id=f"{method}-{index:03d}",
                provider_status=provider_status,
                generation=generation,
                evaluator=evaluator,
                validation_config=validation_config,
                validation_instances=validation_instances,
                test_instances=test_instances,
                parent_ids=(_PARENT_PROGRAM_ID,),
                repair_of_failure_reason="",
            )
        )
    return records


def _evaluate_repair_candidates(
    *,
    provider: MetadataLLMProvider,
    candidate_budget: int,
    prompt_version: str,
    evaluator: BinPackingEvaluator,
    validation_config: ValidationConfig,
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
) -> List[Mapping[str, object]]:
    records: List[Mapping[str, object]] = []
    for index in range(candidate_budget):
        prompt = _repair_prompt(
            index=index,
            failure_reason="dangerous_name",
            prompt_version=prompt_version,
        )
        generation = provider.generate_with_metadata(
            prompt,
            prompt_version=prompt_version,
        )
        records.append(
            _evaluate_generated_code(
                method="llm_repair",
                candidate_id=f"llm_repair-{index:03d}",
                provider_status="configured",
                generation=generation,
                evaluator=evaluator,
                validation_config=validation_config,
                validation_instances=validation_instances,
                test_instances=test_instances,
                parent_ids=(_PARENT_PROGRAM_ID, f"invalid-{index:03d}"),
                repair_of_failure_reason="dangerous_name",
            )
        )
    return records


def _evaluate_generated_code(
    *,
    method: str,
    candidate_id: str,
    provider_status: str,
    generation: GeneratedCode,
    evaluator: BinPackingEvaluator,
    validation_config: ValidationConfig,
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
    parent_ids: Tuple[str, ...],
    repair_of_failure_reason: str,
) -> Mapping[str, object]:
    static = validate_candidate_code(generation.code, validation_config)
    static_result = "ok" if static.ok else str(static.failure_reason.code)
    sandbox_result = "rejected_before_sandbox"
    score: Optional[float] = None
    test_score: Optional[float] = None
    failure_reason = static_result if not static.ok else None
    runtime_seconds = 0.0
    if static.ok:
        started = perf_counter()
        validation_result = evaluator.evaluate_program(
            generation.code,
            validation_instances,
            program_id=candidate_id,
        )
        test_result = evaluator.evaluate_program(
            generation.code,
            test_instances,
            program_id=candidate_id,
        )
        runtime_seconds = perf_counter() - started
        sandbox_result = "ok" if validation_result.ok else "failed"
        score = validation_result.score
        test_score = test_result.score
        failure_reason = validation_result.failure_reason or test_result.failure_reason
    metadata = generation.metadata
    return {
        "candidate_id": candidate_id,
        "method": method,
        "provider_status": provider_status,
        "model_name": metadata.model_name,
        "prompt_version": metadata.prompt_version,
        "temperature": metadata.temperature,
        "parent_ids": parent_ids,
        "raw_response_hash": metadata.raw_response_hash,
        "cleaned_code_hash": metadata.cleaned_code_hash,
        "static_check_result": static_result,
        "sandbox_result": sandbox_result,
        "score": score,
        "test_score": test_score,
        "failure_reason": failure_reason,
        "runtime_seconds": runtime_seconds,
        "latency_seconds": metadata.latency_seconds,
        "input_tokens": metadata.input_tokens,
        "output_tokens": metadata.output_tokens,
        "total_tokens": metadata.total_tokens,
        "estimated_cost_usd": metadata.estimated_cost_usd,
        "repair_of_failure_reason": repair_of_failure_reason,
    }


def _operator_row(
    method: str,
    records: Sequence[Mapping[str, object]],
    provider_status: str,
    *,
    model_name: str = "",
) -> Mapping[str, object]:
    rows = [row for row in records if row["method"] == method]
    valid_scores = [row["score"] for row in rows if row["score"] is not None]
    best_score = min(valid_scores) if valid_scores else None
    invalid_count = sum(1 for row in rows if row["static_check_result"] != "ok")
    total_tokens = sum(int(row["total_tokens"]) for row in rows)
    estimated_cost = sum(float(row["estimated_cost_usd"]) for row in rows)
    average_latency = (
        sum(float(row["latency_seconds"]) for row in rows) / len(rows) if rows else 0.0
    )
    if rows and not model_name:
        model_name = str(rows[0]["model_name"])
    return {
        "method": method,
        "provider_status": provider_status,
        "model_name": model_name,
        "evaluated_candidates": len(rows),
        "best_validation_score": best_score,
        "invalid_code_rate": invalid_count / len(rows) if rows else None,
        "average_latency_seconds": average_latency,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "live_llm_required": method == "live_gemini",
    }


def _mutation_prompt(*, index: int, prompt_version: str) -> str:
    return "\n".join(
        [
            f"Prompt version: {prompt_version}",
            f"Candidate index: {index}",
            "Mutate this score_bin function.",
            "Return only the complete Python function.",
            "Do not import modules, read files, use network access, "
            "or inspect globals.",
            "",
            "Parent program:",
            _PARENT_CODE,
            "",
            "Benchmark feedback: prefer compact bin use with low waste.",
        ]
    )


def _repair_prompt(
    *,
    index: int,
    failure_reason: str,
    prompt_version: str,
) -> str:
    return "\n".join(
        [
            f"Prompt version: {prompt_version}",
            f"Repair candidate index: {index}",
            f"Static failure reason: {failure_reason}",
            "Repair this score_bin function while preserving compact heuristic intent.",
            "Return only the complete Python function.",
            "",
            "Invalid program:",
            _INVALID_REPAIR_TARGET,
        ]
    )


def _deterministic_code(index: int) -> str:
    if index % 6 == 5:
        return _INVALID_REPAIR_TARGET + "\n"
    target = 0.04 + (index % 5) * 0.03
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    fill_ratio = bin_features["current_load"] / bin_features["capacity"]
    return abs(projected - {target:.4f}) - 0.01 * fill_ratio
""".strip()
        + "\n"
    )
