from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from benchmarks.bin_packing.evaluator import BinPackingEvaluator
from benchmarks.bin_packing.instances import (
    BinPackingInstance,
    default_train_validation_test_suites,
)
from program_search.scoring import compute_program_complexity

PHASE11_METHODS = (
    "seed_only",
    "random_mutation",
    "deterministic_template_mutation",
    "crossover_only",
    "mutation_plus_crossover",
    "llm_mutation",
    "llm_repair",
    "llm_mutation_plus_repair",
)

PHASE11_CLAIM_BOUNDARY = (
    "ablation compares deterministic operators under a fixed local budget; "
    "live LLM behavior is not claimed"
)


@dataclass(frozen=True)
class AblationCandidate:
    candidate_id: str
    method: str
    code: str
    operator_source: str
    live_llm_required: bool = False


@dataclass(frozen=True)
class AblationEvaluation:
    candidate: AblationCandidate
    train_score: Optional[float]
    validation_score: Optional[float]
    test_score: Optional[float]
    failure_reason: Optional[str]
    runtime: float
    complexity: int

    @property
    def ok(self) -> bool:
        return self.failure_reason is None and self.validation_score is not None

    @property
    def invalid_code(self) -> bool:
        reason = self.failure_reason or ""
        return any(
            marker in reason
            for marker in (
                "dangerous_call",
                "dangerous_name",
                "import_not_allowed",
                "syntax_error",
                "missing_function",
            )
        )


def build_phase11_report(
    *,
    candidate_budget: int = 32,
    generations: int = 3,
    item_count: int = 20,
    random_seed: int = 23,
    timeout_seconds: float = 0.25,
) -> Dict[str, object]:
    if candidate_budget < 1:
        raise ValueError("candidate_budget must be positive")
    if generations < 1:
        raise ValueError("generations must be positive")
    train, validation, test = default_train_validation_test_suites(
        item_count=item_count
    )
    evaluator = BinPackingEvaluator(timeout_seconds=timeout_seconds)
    method_results: Dict[str, List[AblationEvaluation]] = {}
    for method in PHASE11_METHODS:
        candidates = _build_method_candidates(
            method=method,
            budget=candidate_budget,
            random_seed=random_seed,
        )
        method_results[method] = [
            _evaluate_candidate(
                evaluator=evaluator,
                candidate=candidate,
                train_instances=train,
                validation_instances=validation,
                test_instances=test,
            )
            for candidate in candidates
        ]

    summary_rows = [
        _summary_row(method, evaluations)
        for method, evaluations in method_results.items()
    ]
    best_row = min(
        summary_rows,
        key=lambda row: (
            float(row["best_validation_score"])
            if row["best_validation_score"] is not None
            else float("inf"),
            str(row["method"]),
        ),
    )
    generation_curve = {
        method: _generation_points(method, evaluations, generations=generations)
        for method, evaluations in method_results.items()
    }
    return {
        "phase": 11,
        "benchmark": "bin_packing",
        "methods": PHASE11_METHODS,
        "controls": {
            "candidate_budget": candidate_budget,
            "generations": generations,
            "benchmark_split": "default_bin_packing_train_validation_test",
            "timeout_seconds": timeout_seconds,
            "random_seed": random_seed,
            "item_count": item_count,
        },
        "summary_rows": summary_rows,
        "generation_curve_by_method": generation_curve,
        "invalid_code_rate_by_method": [
            {
                "method": row["method"],
                "invalid_code_rate": row["invalid_code_rate"],
                "evaluated_candidates": row["evaluated_candidates"],
                "operator_source": row["operator_source"],
            }
            for row in summary_rows
        ],
        "best_score_by_budget": [
            {
                "method": row["method"],
                "candidate_budget": candidate_budget,
                "best_validation_score": row["best_validation_score"],
                "best_test_score": row["best_test_score"],
                "best_program_id": row["best_program_id"],
            }
            for row in summary_rows
        ],
        "best_method": best_row["method"],
        "best_program_id": best_row["best_program_id"],
        "best_validation_score": best_row["best_validation_score"],
        "claim_boundary": PHASE11_CLAIM_BOUNDARY,
    }


def _build_method_candidates(
    *,
    method: str,
    budget: int,
    random_seed: int,
) -> List[AblationCandidate]:
    if method not in PHASE11_METHODS:
        raise ValueError(f"unknown ablation method: {method}")
    rng = Random(f"{random_seed}:{method}")
    return [
        AblationCandidate(
            candidate_id=f"{method}-{index:03d}",
            method=method,
            code=_candidate_code(method, index, rng),
            operator_source=_operator_source(method),
            live_llm_required=False,
        )
        for index in range(budget)
    ]


def _candidate_code(method: str, index: int, rng: Random) -> str:
    if method == "seed_only":
        return _seed_code(index)
    if method == "random_mutation":
        return _random_mutation_code(index, rng)
    if method == "deterministic_template_mutation":
        return _template_mutation_code(index)
    if method == "crossover_only":
        return _crossover_code(index)
    if method == "mutation_plus_crossover":
        if index % 2 == 0:
            return _template_mutation_code(index)
        return _crossover_code(index)
    if method == "llm_mutation":
        return _llm_proxy_code(index, repaired=False)
    if method == "llm_repair":
        return _repair_code(index)
    if method == "llm_mutation_plus_repair":
        if index % 3 == 0:
            return _repair_code(index)
        return _llm_proxy_code(index, repaired=True)
    raise ValueError(f"unknown ablation method: {method}")


def _seed_code(index: int) -> str:
    if index % 8 == 7:
        return (
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return open("hidden_labels.txt").read()
""".strip()
            + "\n"
        )
    target = (index % 5) / 20
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - {target:.4f})
""".strip()
        + "\n"
    )


def _random_mutation_code(index: int, rng: Random) -> str:
    if index % 6 == 5:
        return (
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return __import__("os").getcwd()
""".strip()
            + "\n"
        )
    target = rng.uniform(0.0, 0.35)
    bonus = rng.uniform(0.0, 0.08)
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - {target:.4f}) - {bonus:.4f} * bin_features["items_in_bin"]
""".strip()
        + "\n"
    )


def _template_mutation_code(index: int) -> str:
    weight = (index % 9) / 100
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected - {weight:.4f} * bin_features["items_in_bin"]
""".strip()
        + "\n"
    )


def _crossover_code(index: int) -> str:
    mix = 0.25 + ((index % 7) / 20)
    target = (index % 6) / 20
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    tight_fit = projected
    balance = abs(projected - {target:.4f})
    used_bonus = {mix / 8:.4f} * bin_features["items_in_bin"]
    return ({mix:.4f} * tight_fit) + ((1 - {mix:.4f}) * balance) - used_bonus
""".strip()
        + "\n"
    )


def _llm_proxy_code(index: int, *, repaired: bool) -> str:
    if not repaired and index % 7 == 6:
        return (
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return globals()["hidden_solution"]
""".strip()
            + "\n"
        )
    slack_target = 0.05 + ((index % 5) / 25)
    load_weight = 0.015 + ((index % 4) / 200)
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    fullness = bin_features["current_load"] / bin_features["capacity"]
    slack_score = abs(projected - {slack_target:.4f})
    return slack_score - {load_weight:.4f} * fullness
""".strip()
        + "\n"
    )


def _repair_code(index: int) -> str:
    repaired_target = 0.08 + ((index % 6) / 30)
    return (
        f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - {repaired_target:.4f}) - 0.01 * bin_features["items_in_bin"]
""".strip()
        + "\n"
    )


def _operator_source(method: str) -> str:
    if method.startswith("llm_"):
        return "deterministic_llm_proxy"
    if method == "seed_only":
        return "seed_library"
    if method == "random_mutation":
        return "deterministic_random_mutation"
    if method == "deterministic_template_mutation":
        return "deterministic_template_mutation"
    if method == "crossover_only":
        return "deterministic_crossover"
    if method == "mutation_plus_crossover":
        return "deterministic_mutation_crossover"
    raise ValueError(f"unknown ablation method: {method}")


def _evaluate_candidate(
    *,
    evaluator: BinPackingEvaluator,
    candidate: AblationCandidate,
    train_instances: Sequence[BinPackingInstance],
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
) -> AblationEvaluation:
    train = evaluator.evaluate_program(
        candidate.code,
        train_instances,
        program_id=candidate.candidate_id,
    )
    validation = evaluator.evaluate_program(
        candidate.code,
        validation_instances,
        program_id=candidate.candidate_id,
    )
    test = evaluator.evaluate_program(
        candidate.code,
        test_instances,
        program_id=candidate.candidate_id,
    )
    return AblationEvaluation(
        candidate=candidate,
        train_score=train.score,
        validation_score=validation.score,
        test_score=test.score,
        failure_reason=validation.failure_reason or train.failure_reason,
        runtime=train.runtime + validation.runtime + test.runtime,
        complexity=compute_program_complexity(candidate.code),
    )


def _summary_row(
    method: str,
    evaluations: Sequence[AblationEvaluation],
) -> Mapping[str, object]:
    best = _best_success(evaluations)
    return {
        "method": method,
        "evaluated_candidates": len(evaluations),
        "best_program_id": best.candidate.candidate_id if best else "",
        "best_train_score": best.train_score if best else None,
        "best_validation_score": best.validation_score if best else None,
        "best_test_score": best.test_score if best else None,
        "failure_rate": _rate(not evaluation.ok for evaluation in evaluations),
        "invalid_code_rate": _rate(
            evaluation.invalid_code for evaluation in evaluations
        ),
        "operator_source": _operator_source(method),
        "live_llm_required": False,
        "mean_complexity": round(
            _mean(float(evaluation.complexity) for evaluation in evaluations),
            6,
        ),
    }


def _generation_points(
    method: str,
    evaluations: Sequence[AblationEvaluation],
    *,
    generations: int,
) -> List[Mapping[str, object]]:
    points = []
    for generation in range(generations + 1):
        prefix_count = max(
            1,
            round(len(evaluations) * (generation + 1) / (generations + 1)),
        )
        prefix = list(evaluations[:prefix_count])
        best = _best_success(prefix)
        scores = [
            evaluation.validation_score
            for evaluation in prefix
            if evaluation.validation_score is not None
        ]
        best_score = best.validation_score if best else None
        points.append(
            {
                "method": method,
                "generation": generation,
                "evaluated_candidates": prefix_count,
                "best_score": best_score,
                "median_score": _median(scores),
                "failure_rate": _rate(not evaluation.ok for evaluation in prefix),
                "invalid_code_rate": _rate(
                    evaluation.invalid_code for evaluation in prefix
                ),
                "best_program_id": best.candidate.candidate_id if best else "",
            }
        )
    return points


def _best_success(
    evaluations: Sequence[AblationEvaluation],
) -> Optional[AblationEvaluation]:
    successful = [
        evaluation
        for evaluation in evaluations
        if evaluation.validation_score is not None
    ]
    if not successful:
        return None
    return min(
        successful,
        key=lambda evaluation: (
            float(evaluation.validation_score or float("inf")),
            evaluation.candidate.candidate_id,
        ),
    )


def _rate(values: Iterable[bool]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(1 for value in values if value) / len(values)


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def _median(values: Sequence[float]) -> Optional[float]:
    values = sorted(values)
    if not values:
        return None
    midpoint = len(values) // 2
    if len(values) % 2:
        return values[midpoint]
    return (values[midpoint - 1] + values[midpoint]) / 2
