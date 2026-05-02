from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
)
from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    build_seed_candidate_programs,
)
from benchmarks.bin_packing.instances import (
    default_train_validation_test_suites as default_bin_packing_suites,
)
from benchmarks.routing.evaluator import (
    RoutingEvaluator,
    build_seed_routing_programs,
)
from benchmarks.routing.instances import (
    default_train_validation_test_suites as default_routing_suites,
)
from program_search.scoring import compute_program_complexity

PHASE15_FRONTIER_AXES = (
    "objective_quality",
    "runtime",
    "program_complexity",
    "failure_rate",
    "generalization_gap",
    "operational_penalty",
)

PHASE15_CLAIM_BOUNDARY = (
    "The system discovers compact heuristic programs that improve selected "
    "quality-runtime-generalization trade-offs, rather than universally "
    "dominating classical baselines."
)


@dataclass(frozen=True)
class ParetoCandidate:
    benchmark: str
    program_id: str
    source: str
    objective_quality: float
    runtime: float
    program_complexity: int
    failure_rate: float
    generalization_gap: float
    driver_likeness_or_realism: Optional[float]
    operational_penalty: float
    code: str
    explanation: str

    def as_row(self) -> Dict[str, object]:
        return {
            "benchmark": self.benchmark,
            "program_id": self.program_id,
            "source": self.source,
            "objective_quality": self.objective_quality,
            "runtime": self.runtime,
            "program_complexity": self.program_complexity,
            "failure_rate": self.failure_rate,
            "generalization_gap": self.generalization_gap,
            "driver_likeness_or_realism": self.driver_likeness_or_realism,
            "operational_penalty": self.operational_penalty,
            "code": self.code,
            "explanation": self.explanation,
        }


def build_phase15_report() -> Dict[str, object]:
    candidates = (
        _bin_packing_candidates()
        + _simple_routing_candidates()
        + _amazon_routing_candidates()
    )
    candidate_rows = _annotate_frontier(candidates)
    frontier_rows = [row for row in candidate_rows if row["is_pareto_frontier"]]
    return {
        "phase": 15,
        "benchmarks": tuple(sorted({row["benchmark"] for row in candidate_rows})),
        "frontier_axes": PHASE15_FRONTIER_AXES,
        "candidate_rows": candidate_rows,
        "frontier_rows": frontier_rows,
        "frontier_count": len(frontier_rows),
        "benchmark_summaries": _benchmark_summaries(candidate_rows),
        "claim_boundary": PHASE15_CLAIM_BOUNDARY,
    }


def _bin_packing_candidates() -> List[ParetoCandidate]:
    train, validation, test = default_bin_packing_suites(item_count=20)
    evaluator = BinPackingEvaluator()
    candidates = build_seed_candidate_programs(16)[:8]
    operation_count = sum(len(instance.items) for instance in train + validation + test)
    rows: List[ParetoCandidate] = []
    for candidate in candidates:
        train_result = evaluator.evaluate_program(
            candidate.code,
            train,
            program_id=candidate.program_id,
        )
        validation_result = evaluator.evaluate_program(
            candidate.code,
            validation,
            program_id=candidate.program_id,
        )
        test_result = evaluator.evaluate_program(
            candidate.code,
            test,
            program_id=candidate.program_id,
        )
        if not (
            train_result.score is not None
            and validation_result.score is not None
            and test_result.score is not None
        ):
            continue
        complexity = compute_program_complexity(candidate.code)
        rows.append(
            ParetoCandidate(
                benchmark="bin_packing",
                program_id=candidate.program_id,
                source="phase2_seed_library",
                objective_quality=_score(test_result.score),
                runtime=_runtime_proxy(complexity, operation_count),
                program_complexity=complexity,
                failure_rate=_failure_rate(
                    train_result.ok,
                    validation_result.ok,
                    test_result.ok,
                ),
                generalization_gap=_gap(validation_result.score, test_result.score),
                driver_likeness_or_realism=1.0,
                operational_penalty=0.0,
                code=candidate.code,
                explanation=candidate.explanation,
            )
        )
    return rows


def _simple_routing_candidates() -> List[ParetoCandidate]:
    train, validation, test = default_routing_suites(
        train_sizes=(8,),
        validation_sizes=(10,),
        test_sizes=(12,),
    )
    evaluator = RoutingEvaluator()
    candidates = build_seed_routing_programs(15)[:8]
    operation_count = sum(len(instance.stops) for instance in train + validation + test)
    rows: List[ParetoCandidate] = []
    for candidate in candidates:
        train_result = evaluator.evaluate_program(
            candidate.code,
            train,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        validation_result = evaluator.evaluate_program(
            candidate.code,
            validation,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        test_result = evaluator.evaluate_program(
            candidate.code,
            test,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        if not (
            train_result.score is not None
            and validation_result.score is not None
            and test_result.score is not None
        ):
            continue
        complexity = compute_program_complexity(candidate.code)
        rows.append(
            ParetoCandidate(
                benchmark="simple_routing",
                program_id=candidate.program_id,
                source="phase4_seed_library_plus_2opt",
                objective_quality=_score(test_result.score),
                runtime=_runtime_proxy(complexity, operation_count),
                program_complexity=complexity,
                failure_rate=_failure_rate(
                    train_result.ok,
                    validation_result.ok,
                    test_result.ok,
                ),
                generalization_gap=_gap(validation_result.score, test_result.score),
                driver_likeness_or_realism=1.0,
                operational_penalty=0.0,
                code=candidate.code,
                explanation=candidate.explanation,
            )
        )
    return rows


def _amazon_routing_candidates() -> List[ParetoCandidate]:
    report = build_phase6_report(
        config=AmazonDiscoveryConfig(
            generations=2,
            population_size=12,
            offspring_per_generation=8,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        )
    )
    rows: List[ParetoCandidate] = []
    for candidate in report["top_candidates"]:
        metrics = candidate["test_metrics"]
        driver_likeness = float(metrics.get("average_driver_likeness", 0.0))
        complexity = int(candidate["complexity"])
        route_count = int(float(metrics.get("route_count", 1.0)))
        rows.append(
            ParetoCandidate(
                benchmark="amazon_routing",
                program_id=str(candidate["program_id"]),
                source="phase6_amazon_discovery",
                objective_quality=_score(candidate["test_score"]),
                runtime=_runtime_proxy(complexity, route_count),
                program_complexity=complexity,
                failure_rate=float(metrics.get("failure_rate", 0.0)),
                generalization_gap=_gap(
                    candidate["validation_score"],
                    candidate["test_score"],
                ),
                driver_likeness_or_realism=driver_likeness,
                operational_penalty=1.0 - driver_likeness,
                code=str(candidate["code"]),
                explanation=str(candidate["explanation"]),
            )
        )
    return rows


def _annotate_frontier(
    candidates: Sequence[ParetoCandidate],
) -> List[Dict[str, object]]:
    base_rows = [candidate.as_row() for candidate in candidates]
    annotated: List[Dict[str, object]] = []
    for row in base_rows:
        peers = [
            candidate
            for candidate in base_rows
            if candidate["benchmark"] == row["benchmark"]
        ]
        dominated_by = [
            candidate
            for candidate in peers
            if candidate["program_id"] != row["program_id"]
            and _dominates(candidate, row)
        ]
        dominates_count = sum(
            1
            for candidate in peers
            if candidate["program_id"] != row["program_id"]
            and _dominates(row, candidate)
        )
        enriched = dict(row)
        enriched["is_pareto_frontier"] = not dominated_by
        enriched["dominance_count"] = dominates_count
        enriched["selected_tradeoff"] = _tradeoff_label(enriched)
        annotated.append(enriched)
    return sorted(
        annotated,
        key=lambda candidate: (
            str(candidate["benchmark"]),
            not bool(candidate["is_pareto_frontier"]),
            float(candidate["objective_quality"]),
            str(candidate["program_id"]),
        ),
    )


def _dominates(
    challenger: Mapping[str, object], candidate: Mapping[str, object]
) -> bool:
    challenger_values = _axis_values(challenger)
    candidate_values = _axis_values(candidate)
    return all(
        left <= right for left, right in zip(challenger_values, candidate_values)
    ) and any(left < right for left, right in zip(challenger_values, candidate_values))


def _axis_values(row: Mapping[str, object]) -> List[float]:
    return [float(row[axis]) for axis in PHASE15_FRONTIER_AXES]


def _tradeoff_label(row: Mapping[str, object]) -> str:
    if not row["is_pareto_frontier"]:
        return "dominated_candidate"
    if row["benchmark"] == "amazon_routing":
        return "quality_runtime_driver_likeness_frontier"
    return "quality_runtime_generalization_frontier"


def _benchmark_summaries(
    rows: Sequence[Mapping[str, object]],
) -> Dict[str, Mapping[str, object]]:
    summaries: Dict[str, Mapping[str, object]] = {}
    benchmarks = sorted({str(row["benchmark"]) for row in rows})
    for benchmark in benchmarks:
        benchmark_rows = [row for row in rows if row["benchmark"] == benchmark]
        frontier_rows = [
            row for row in benchmark_rows if bool(row["is_pareto_frontier"])
        ]
        summaries[benchmark] = {
            "candidate_count": len(benchmark_rows),
            "frontier_count": len(frontier_rows),
            "best_quality_program_id": min(
                benchmark_rows,
                key=lambda row: (
                    float(row["objective_quality"]),
                    str(row["program_id"]),
                ),
            )["program_id"],
            "lowest_runtime_program_id": min(
                benchmark_rows,
                key=lambda row: (float(row["runtime"]), str(row["program_id"])),
            )["program_id"],
            "lowest_complexity_program_id": min(
                benchmark_rows,
                key=lambda row: (
                    int(row["program_complexity"]),
                    str(row["program_id"]),
                ),
            )["program_id"],
        }
    return summaries


def _score(value: object) -> float:
    if value is None:
        return float("inf")
    return float(value)


def _gap(left: object, right: object) -> float:
    left_score = _score(left)
    right_score = _score(right)
    if left_score == float("inf") and right_score == float("inf"):
        return float("inf")
    return abs(left_score - right_score)


def _runtime_proxy(complexity: int, operation_count: int) -> float:
    return round((complexity * max(operation_count, 1)) / 1_000_000, 6)


def _failure_rate(*ok_values: bool) -> float:
    return sum(1 for ok in ok_values if not ok) / len(ok_values)
