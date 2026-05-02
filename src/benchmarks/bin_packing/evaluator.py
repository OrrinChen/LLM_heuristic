from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from time import perf_counter
from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.bin_packing.baselines import (
    BASELINE_PACKERS,
    EPSILON,
    PackingResult,
    validate_packing,
)
from benchmarks.bin_packing.instances import (
    BinPackingInstance,
    default_train_validation_test_suites,
)
from program_search.archive import ProgramArchive
from program_search.candidate_program import CandidateProgram
from program_search.evaluator import EvaluationResult
from sandbox.restricted_exec import SAFE_BUILTINS, SandboxTimeoutError, _timeout
from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    validate_candidate_code,
)


@dataclass(frozen=True)
class ProgramEvaluation:
    program_id: str
    ok: bool
    score: Optional[float]
    metrics: Mapping[str, float]
    runtime: float
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class SeedCandidateProgram:
    program_id: str
    code: str
    explanation: str


@dataclass(frozen=True)
class CandidateSuiteSummary:
    candidate_count: int
    failure_rate: float
    best_program_id: str
    best_validation_score: float
    median_validation_score: float
    test_score: Optional[float]
    baseline_scores: Mapping[str, float]
    top_programs: List[Mapping[str, object]]


class BinPackingEvaluator:
    def __init__(self, *, timeout_seconds: float = 0.25) -> None:
        self.timeout_seconds = timeout_seconds
        self.validation_config = ValidationConfig(allowed_function="score_bin")

    def evaluate_program(
        self,
        code: str,
        instances: Sequence[BinPackingInstance],
        *,
        program_id: str,
    ) -> ProgramEvaluation:
        started = perf_counter()
        if not instances:
            return ProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={"failure_rate": 1.0},
                runtime=perf_counter() - started,
                failure_reason="no_instances",
            )
        scoring_function, failure = self._compile_program(code)
        if failure is not None:
            return ProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={
                    "bins_used": 0.0,
                    "average_waste": 0.0,
                    "failure_rate": 1.0,
                    "instance_count": float(len(instances)),
                },
                runtime=perf_counter() - started,
                failure_reason=str(failure),
            )

        bins_used = []
        average_waste = []
        failures = 0
        first_failure = None
        for instance in instances:
            result = self._pack_with_program(scoring_function, instance)
            if result.is_valid:
                bins_used.append(float(result.bins_used))
                average_waste.append(result.average_waste)
            else:
                failures += 1
                if first_failure is None:
                    first_failure = result.failure_reason or "invalid_packing"

        failure_rate = failures / len(instances)
        metrics = {
            "bins_used": _mean(bins_used),
            "average_waste": _mean(average_waste),
            "failure_rate": failure_rate,
            "instance_count": float(len(instances)),
        }
        if failures == len(instances):
            return ProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics=metrics,
                runtime=perf_counter() - started,
                failure_reason=first_failure,
            )
        score = metrics["bins_used"] + failure_rate * 1000.0
        return ProgramEvaluation(
            program_id=program_id,
            ok=failures == 0,
            score=score,
            metrics=metrics,
            runtime=perf_counter() - started,
            failure_reason=first_failure,
        )

    def _compile_program(self, code: str) -> tuple[object, Optional[FailureReason]]:
        validation = validate_candidate_code(code, self.validation_config)
        if not validation.ok:
            return None, validation.failure_reason
        namespace = {"__builtins__": SAFE_BUILTINS}
        try:
            compiled = compile(code, "<candidate>", "exec")
            exec(compiled, namespace, namespace)
        except Exception as exc:  # noqa: BLE001 - sandbox compile boundary.
            return None, FailureReason(
                code="runtime_error",
                message=f"{type(exc).__name__}: {exc}",
            )
        return namespace[self.validation_config.allowed_function], None

    def _pack_with_program(
        self, scoring_function: object, instance: BinPackingInstance
    ) -> PackingResult:
        started = perf_counter()
        bins: List[List[float]] = []
        try:
            with _timeout(self.timeout_seconds):
                for item_index, item in enumerate(instance.items):
                    if item > instance.capacity:
                        return PackingResult(
                            algorithm="score_bin",
                            bins=bins,
                            runtime=perf_counter() - started,
                            is_valid=False,
                            capacity=instance.capacity,
                            failure_reason="item_exceeds_capacity",
                        )
                    if not bins:
                        bins.append([item])
                        continue
                    scored_bins = []
                    for bin_index, bin_items in enumerate(bins):
                        remaining = instance.capacity - sum(bin_items)
                        bin_features = {
                            "bin_index": bin_index,
                            "item_index": item_index,
                            "items_in_bin": len(bin_items),
                            "current_load": sum(bin_items),
                            "remaining_capacity": remaining,
                            "capacity": instance.capacity,
                        }
                        score, failure = self._call_score_function(
                            scoring_function, item, remaining, bin_features
                        )
                        if failure is not None:
                            return PackingResult(
                                algorithm="score_bin",
                                bins=bins,
                                runtime=perf_counter() - started,
                                is_valid=False,
                                capacity=instance.capacity,
                                failure_reason=str(failure),
                            )
                        scored_bins.append((score, bin_index, remaining))
                    capacity_feasible = [
                        (score, bin_index, remaining)
                        for score, bin_index, remaining in scored_bins
                        if remaining + EPSILON >= item
                    ]
                    if not capacity_feasible:
                        bins.append([item])
                        continue
                    feasible = [
                        (score, bin_index)
                        for score, bin_index, _ in capacity_feasible
                        if score < 1_000_000
                    ]
                    if not feasible:
                        return PackingResult(
                            algorithm="score_bin",
                            bins=bins,
                            runtime=perf_counter() - started,
                            is_valid=False,
                            capacity=instance.capacity,
                            failure_reason="no_feasible_bin_selected",
                        )
                    _, chosen = min(feasible, key=lambda entry: (entry[0], entry[1]))
                    bins[chosen].append(item)
        except SandboxTimeoutError:
            return PackingResult(
                algorithm="score_bin",
                bins=bins,
                runtime=perf_counter() - started,
                is_valid=False,
                capacity=instance.capacity,
                failure_reason=(
                    f"timeout: candidate exceeded {self.timeout_seconds} seconds"
                ),
            )

        validation = validate_packing(instance, bins)
        return PackingResult(
            algorithm="score_bin",
            bins=bins,
            runtime=perf_counter() - started,
            is_valid=validation.ok,
            capacity=instance.capacity,
            failure_reason=validation.failure_reason,
        )

    def _call_score_function(
        self,
        scoring_function: object,
        item: float,
        remaining: float,
        bin_features: Mapping[str, float],
    ) -> tuple[float, Optional[FailureReason]]:
        try:
            value = scoring_function(item, remaining, bin_features)  # type: ignore[operator]
        except Exception as exc:  # noqa: BLE001 - structured candidate failure.
            return 0.0, FailureReason(
                code="runtime_error",
                message=f"{type(exc).__name__}: {exc}",
            )
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return 0.0, FailureReason(
                code="non_numeric_score",
                message="scoring function must return an int or float",
            )
        return float(value), None


def evaluate_candidate_suite(
    *,
    candidates: Sequence[SeedCandidateProgram],
    train_instances: Sequence[BinPackingInstance],
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
) -> CandidateSuiteSummary:
    evaluator = BinPackingEvaluator()
    validation_results = [
        evaluator.evaluate_program(
            candidate.code, validation_instances, program_id=candidate.program_id
        )
        for candidate in candidates
    ]
    successful = [result for result in validation_results if result.score is not None]
    if not successful:
        raise ValueError("candidate suite produced no successful programs")
    best = min(successful, key=lambda result: result.score or float("inf"))
    test = evaluator.evaluate_program(
        _code_for(candidates, best.program_id),
        test_instances,
        program_id=best.program_id,
    )
    baseline_scores = _baseline_scores(validation_instances)
    top_programs = []
    for result in sorted(successful, key=lambda item: item.score or float("inf"))[:5]:
        candidate = _candidate_for(candidates, result.program_id)
        train_result = evaluator.evaluate_program(
            candidate.code, train_instances, program_id=candidate.program_id
        )
        top_programs.append(
            {
                "program_id": candidate.program_id,
                "validation_score": result.score,
                "train_score": train_result.score,
                "code": candidate.code,
                "explanation": candidate.explanation,
            }
        )
    return CandidateSuiteSummary(
        candidate_count=len(candidates),
        failure_rate=sum(not result.ok for result in validation_results)
        / len(validation_results),
        best_program_id=best.program_id,
        best_validation_score=best.score or 0.0,
        median_validation_score=median(result.score or 0.0 for result in successful),
        test_score=test.score,
        baseline_scores=baseline_scores,
        top_programs=top_programs,
    )


def build_phase2_report(
    *, candidate_count: int = 120, item_count: int = 50
) -> Dict[str, object]:
    train, validation, test = default_train_validation_test_suites(
        item_count=item_count
    )
    candidates = build_seed_candidate_programs(candidate_count)
    summary = evaluate_candidate_suite(
        candidates=candidates,
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )
    return {
        "candidate_count": summary.candidate_count,
        "failure_rate": summary.failure_rate,
        "best_program_id": summary.best_program_id,
        "best_validation_score": summary.best_validation_score,
        "median_validation_score": summary.median_validation_score,
        "test_score": summary.test_score,
        "baseline_scores": dict(summary.baseline_scores),
        "held_out": {
            "instance_count": len(test),
            "score": summary.test_score,
        },
        "top_programs": summary.top_programs,
    }


def archive_seed_candidates(
    candidates: Sequence[SeedCandidateProgram],
    instances: Sequence[BinPackingInstance],
) -> ProgramArchive:
    evaluator = BinPackingEvaluator()
    archive = ProgramArchive()
    for seed in candidates:
        candidate = CandidateProgram.create(
            code=seed.code,
            prompt=seed.explanation,
            generation=0,
        )
        result = evaluator.evaluate_program(
            seed.code, instances, program_id=candidate.program_id
        )
        if result.ok and result.score is not None:
            evaluation = EvaluationResult.success(
                candidate_id=candidate.program_id,
                benchmark_name="bin_packing",
                score=result.score,
                runtime=result.runtime,
                metrics=result.metrics,
            )
        else:
            candidate = CandidateProgram.create(
                code=seed.code,
                prompt=seed.explanation,
                generation=0,
                failure_reason=result.failure_reason,
            )
            evaluation = EvaluationResult.failure(
                candidate_id=candidate.program_id,
                benchmark_name="bin_packing",
                failure_reason=result.failure_reason or "candidate_failed",
                runtime=result.runtime,
                metrics=result.metrics,
            )
        archive.record(candidate, evaluation)
    return archive


def build_seed_candidate_programs(count: int = 120) -> List[SeedCandidateProgram]:
    if count < 1:
        raise ValueError("count must be positive")
    candidates = []
    templates = [
        (
            "tight_fit",
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected + {weight} * bin_features["items_in_bin"]
""",
            "Best-fit style rule that minimizes leftover capacity.",
        ),
        (
            "load_balancer",
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - {target})
""",
            "Keeps residual capacity near a tunable target.",
        ),
        (
            "prefer_used_bins",
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected - {bonus} * bin_features["items_in_bin"]
""",
            "Favors bins that already contain more items.",
        ),
        (
            "unsafe_probe",
            """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return open("hidden_labels.txt").read()
""",
            "Invalid safety probe retained to measure failure taxonomy.",
        ),
    ]
    for index in range(count):
        name, template, explanation = templates[index % len(templates)]
        parameter = (index % 25) / 100.0
        code = template.format(
            weight=round(parameter / 10.0, 4),
            target=round(parameter, 4),
            bonus=round(parameter / 5.0, 4),
        )
        candidates.append(
            SeedCandidateProgram(
                program_id=f"seed-{index:03d}-{name}",
                code=code.strip() + "\n",
                explanation=explanation,
            )
        )
    return candidates


def _baseline_scores(instances: Sequence[BinPackingInstance]) -> Dict[str, float]:
    scores = {}
    for name, packer in BASELINE_PACKERS.items():
        results = [packer(instance) for instance in instances]
        scores[name] = _mean(float(result.bins_used) for result in results)
    return scores


def _candidate_for(
    candidates: Sequence[SeedCandidateProgram], program_id: str
) -> SeedCandidateProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _code_for(candidates: Sequence[SeedCandidateProgram], program_id: str) -> str:
    return _candidate_for(candidates, program_id).code


def _mean(values: Sequence[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
