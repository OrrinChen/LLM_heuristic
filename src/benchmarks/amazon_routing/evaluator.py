from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from time import perf_counter
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from benchmarks.amazon_routing.baselines import (
    AMAZON_BASELINE_ROUTE_BUILDERS,
    AmazonRoutingResult,
    route_metrics,
    validate_route,
)
from benchmarks.amazon_routing.features import extract_stop_features
from benchmarks.amazon_routing.loader import AmazonRoute, load_route_record
from sandbox.restricted_exec import SAFE_BUILTINS, SandboxTimeoutError, _timeout
from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    validate_candidate_code,
)

TIME_WINDOW_PENALTY = 10.0
DRIVER_LIKENESS_PENALTY = 5.0
ZONE_TRANSITION_PENALTY = 3.0
COMPACTNESS_PENALTY = 2.0


@dataclass(frozen=True)
class AmazonProgramEvaluation:
    program_id: str
    ok: bool
    score: Optional[float]
    metrics: Mapping[str, float]
    runtime: float
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class SeedAmazonProgram:
    program_id: str
    code: str
    explanation: str


@dataclass(frozen=True)
class AmazonCandidateSuiteSummary:
    candidate_count: int
    failure_rate: float
    failure_taxonomy: Mapping[str, int]
    best_program_id: str
    best_validation_score: float
    median_validation_score: float
    test_score: Optional[float]
    baseline_scores: Mapping[str, float]
    top_programs: List[Mapping[str, object]]


class AmazonRoutingEvaluator:
    def __init__(self, *, timeout_seconds: float = 0.25) -> None:
        self.timeout_seconds = timeout_seconds
        self.validation_config = ValidationConfig(allowed_function="score_next_stop")

    def evaluate_program(
        self,
        code: str,
        routes: Sequence[AmazonRoute],
        *,
        program_id: str,
        apply_local_search: bool = False,
    ) -> AmazonProgramEvaluation:
        started = perf_counter()
        if not routes:
            return AmazonProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={"failure_rate": 1.0},
                runtime=perf_counter() - started,
                failure_reason="no_routes",
            )
        scoring_function, failure = self._compile_program(code)
        if failure is not None:
            return AmazonProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics=_empty_metrics(len(routes), failure_rate=1.0),
                runtime=perf_counter() - started,
                failure_reason=str(failure),
            )

        metric_rows = []
        failures = 0
        first_failure = None
        for route in routes:
            result = self._route_with_program(
                scoring_function,
                route,
                apply_local_search=apply_local_search,
            )
            if result.is_valid:
                metric_rows.append(result.metrics)
            else:
                failures += 1
                if first_failure is None:
                    first_failure = result.failure_reason or "invalid_route"

        failure_rate = failures / len(routes)
        metrics = _aggregate_metrics(metric_rows, len(routes), failure_rate)
        if failures == len(routes):
            return AmazonProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics=metrics,
                runtime=perf_counter() - started,
                failure_reason=first_failure,
            )
        score = _score_metrics(metrics) + failure_rate * 10_000.0
        return AmazonProgramEvaluation(
            program_id=program_id,
            ok=failures == 0,
            score=score,
            metrics=metrics,
            runtime=perf_counter() - started,
            failure_reason=first_failure,
        )

    def _compile_program(self, code: str) -> Tuple[object, Optional[FailureReason]]:
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

    def _route_with_program(
        self,
        scoring_function: object,
        route: AmazonRoute,
        *,
        apply_local_search: bool,
    ) -> AmazonRoutingResult:
        started = perf_counter()
        sequence: List[str] = []
        remaining = set(route.stop_ids)
        current_stop_id = route.depot.stop_id
        elapsed = 0.0
        try:
            with _timeout(self.timeout_seconds):
                while remaining:
                    scored = []
                    for stop_id in remaining:
                        candidate = dict(
                            extract_stop_features(
                                route,
                                candidate_stop_id=stop_id,
                                current_stop_id=current_stop_id,
                                elapsed_time=elapsed,
                                visited=sequence,
                            )
                        )
                        candidate.pop("historical_position", None)
                        candidate.pop("stop_id", None)
                        state = {
                            "current_stop_id": current_stop_id,
                            "elapsed_time": elapsed,
                            "visited_count": len(sequence),
                            "remaining_count": len(remaining),
                        }
                        score, failure = self._call_score_function(
                            scoring_function,
                            state,
                            candidate,
                        )
                        if failure is not None:
                            return _invalid_result(
                                "score_next_stop",
                                sequence,
                                started,
                                str(failure),
                            )
                        scored.append((score, stop_id))
                    _, chosen = min(scored, key=lambda entry: (entry[0], entry[1]))
                    stop = route.stop_by_id(chosen)
                    elapsed += route.travel_time(current_stop_id, chosen)
                    if elapsed < stop.ready_time:
                        elapsed = stop.ready_time
                    elapsed += stop.service_time
                    sequence.append(chosen)
                    remaining.remove(chosen)
                    current_stop_id = chosen
        except SandboxTimeoutError:
            return _invalid_result(
                "score_next_stop",
                sequence,
                started,
                f"timeout: candidate exceeded {self.timeout_seconds} seconds",
            )

        sequence_tuple = tuple(sequence)
        if apply_local_search:
            improved = _two_opt_if_better(route, sequence_tuple)
            if _route_score(route, improved) <= _route_score(route, sequence_tuple):
                sequence_tuple = improved
        validation = validate_route(route, sequence_tuple)
        metrics = route_metrics(route, sequence_tuple)
        runtime = perf_counter() - started
        metrics["runtime"] = runtime
        return AmazonRoutingResult(
            algorithm="score_next_stop",
            sequence=sequence_tuple,
            metrics=metrics,
            runtime=runtime,
            is_valid=validation.ok,
            failure_reason=validation.failure_reason,
        )

    def _call_score_function(
        self,
        scoring_function: object,
        state: Mapping[str, object],
        candidate_stop: Mapping[str, object],
    ) -> Tuple[float, Optional[FailureReason]]:
        try:
            value = scoring_function(state, candidate_stop)  # type: ignore[operator]
        except SandboxTimeoutError:
            raise
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


def evaluate_amazon_candidate_suite(
    *,
    candidates: Sequence[SeedAmazonProgram],
    train_routes: Sequence[AmazonRoute],
    validation_routes: Sequence[AmazonRoute],
    test_routes: Sequence[AmazonRoute],
) -> AmazonCandidateSuiteSummary:
    evaluator = AmazonRoutingEvaluator()
    validation_results = [
        evaluator.evaluate_program(
            candidate.code,
            validation_routes,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        for candidate in candidates
    ]
    successful = [result for result in validation_results if result.score is not None]
    if not successful:
        raise ValueError("candidate suite produced no successful Amazon route programs")
    best = min(successful, key=lambda result: result.score or float("inf"))
    test = evaluator.evaluate_program(
        _code_for(candidates, best.program_id),
        test_routes,
        program_id=best.program_id,
        apply_local_search=True,
    )
    top_programs = []
    for result in sorted(successful, key=lambda item: item.score or float("inf"))[:5]:
        candidate = _candidate_for(candidates, result.program_id)
        train = evaluator.evaluate_program(
            candidate.code,
            train_routes,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        top_programs.append(
            {
                "program_id": candidate.program_id,
                "validation_score": result.score,
                "train_score": train.score,
                "code": candidate.code,
                "explanation": candidate.explanation,
            }
        )
    return AmazonCandidateSuiteSummary(
        candidate_count=len(candidates),
        failure_rate=sum(not result.ok for result in validation_results)
        / len(validation_results),
        failure_taxonomy=_failure_taxonomy(validation_results),
        best_program_id=best.program_id,
        best_validation_score=best.score or 0.0,
        median_validation_score=median(result.score or 0.0 for result in successful),
        test_score=test.score,
        baseline_scores=_baseline_scores(validation_routes),
        top_programs=top_programs,
    )


def build_phase5_report(*, candidate_count: int = 120) -> Dict[str, object]:
    train, validation, test = default_train_validation_test_routes()
    candidates = build_seed_amazon_programs(candidate_count)
    summary = evaluate_amazon_candidate_suite(
        candidates=candidates,
        train_routes=train,
        validation_routes=validation,
        test_routes=test,
    )
    return {
        "candidate_count": summary.candidate_count,
        "failure_rate": summary.failure_rate,
        "failure_taxonomy": dict(summary.failure_taxonomy),
        "best_program_id": summary.best_program_id,
        "best_validation_score": summary.best_validation_score,
        "median_validation_score": summary.median_validation_score,
        "test_score": summary.test_score,
        "baseline_scores": dict(summary.baseline_scores),
        "held_out": {
            "route_count": len(test),
            "score": summary.test_score,
        },
        "splits": {
            "train_route_ids": tuple(route.route_id for route in train),
            "validation_route_ids": tuple(route.route_id for route in validation),
            "test_route_ids": tuple(route.route_id for route in test),
            "test_routes": test,
        },
        "top_programs": summary.top_programs,
    }


def build_seed_amazon_programs(count: int = 120) -> List[SeedAmazonProgram]:
    if count < 1:
        raise ValueError("count must be positive")
    templates = [
        (
            "nearest",
            """
def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"]
""",
            "Nearest-stop rule using current travel time only.",
        ),
        (
            "same_zone",
            """
def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"] - {weight} * candidate_stop["same_zone"]
""",
            "Favors nearby stops in the current zone to preserve driver-like blocks.",
        ),
        (
            "window_guard",
            """
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        + {penalty} * candidate_stop["lateness"]
        + 0.1 * candidate_stop["wait_time"]
    )
""",
            "Balances travel time with time-window lateness and early-arrival waits.",
        ),
        (
            "package_dense",
            """
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        - {weight} * candidate_stop["package_count"]
        + 0.2 * candidate_stop["distance_to_depot"]
    )
""",
            "Prefers dense nearby delivery stops while tracking depot return cost.",
        ),
        (
            "unsafe_probe",
            """
def score_next_stop(state, candidate_stop):
    return open("hidden_labels.json").read()
""",
            "Invalid safety probe retained to measure sandbox failure taxonomy.",
        ),
    ]
    candidates = []
    for index in range(count):
        name, template, explanation = templates[index % len(templates)]
        parameter = round(1.0 + (index % 11) * 0.25, 4)
        code = template.format(weight=parameter, penalty=round(4.0 + parameter, 4))
        candidates.append(
            SeedAmazonProgram(
                program_id=f"amazon-seed-{index:03d}-{name}",
                code=code.strip() + "\n",
                explanation=explanation,
            )
        )
    return candidates


def default_train_validation_test_routes() -> Tuple[
    Tuple[AmazonRoute, ...],
    Tuple[AmazonRoute, ...],
    Tuple[AmazonRoute, ...],
]:
    return (
        tuple(
            load_route_record(_route_payload(f"train-{index}", offset=index))
            for index in range(2)
        ),
        tuple(
            load_route_record(_route_payload(f"validation-{index}", offset=10 + index))
            for index in range(2)
        ),
        tuple(
            load_route_record(_route_payload(f"test-{index}", offset=20 + index))
            for index in range(2)
        ),
    )


def _baseline_scores(routes: Sequence[AmazonRoute]) -> Dict[str, float]:
    scores = {}
    for name, builder in AMAZON_BASELINE_ROUTE_BUILDERS.items():
        results = [builder(route) for route in routes]
        scores[name] = _mean(_score_metrics(result.metrics) for result in results)
    return scores


def _score_metrics(metrics: Mapping[str, float]) -> float:
    travel_time = metrics.get("travel_time", metrics.get("average_travel_time", 0.0))
    time_window_violation = metrics.get(
        "time_window_violation",
        metrics.get("average_time_window_violation", 0.0),
    )
    driver_likeness = metrics.get(
        "driver_likeness",
        metrics.get("average_driver_likeness", 0.0),
    )
    zone_transition = metrics.get(
        "zone_transition_similarity",
        metrics.get("average_zone_transition_similarity", 0.0),
    )
    compactness = metrics.get(
        "route_compactness",
        metrics.get("average_route_compactness", 0.0),
    )
    return (
        travel_time
        + time_window_violation * TIME_WINDOW_PENALTY
        + (1.0 - driver_likeness) * DRIVER_LIKENESS_PENALTY
        + (1.0 - zone_transition) * ZONE_TRANSITION_PENALTY
        + (1.0 - compactness) * COMPACTNESS_PENALTY
    )


def _route_score(route: AmazonRoute, sequence: Sequence[str]) -> float:
    return _score_metrics(route_metrics(route, sequence))


def _two_opt_if_better(route: AmazonRoute, sequence: Sequence[str]) -> Tuple[str, ...]:
    current = tuple(sequence)
    if not validate_route(route, current).ok or len(current) < 4:
        return current
    best_score = _route_score(route, current)
    for _ in range(50):
        improved = False
        for start in range(len(current) - 1):
            for end in range(start + 2, len(current) + 1):
                candidate = (
                    current[:start]
                    + tuple(reversed(current[start:end]))
                    + current[end:]
                )
                candidate_score = _route_score(route, candidate)
                if candidate_score < best_score:
                    current = candidate
                    best_score = candidate_score
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _aggregate_metrics(
    rows: Sequence[Mapping[str, float]],
    route_count: int,
    failure_rate: float,
) -> Dict[str, float]:
    if not rows:
        return _empty_metrics(route_count, failure_rate=failure_rate)
    return {
        "average_travel_time": _mean(row["travel_time"] for row in rows),
        "average_time_window_violation": _mean(
            row["time_window_violation"] for row in rows
        ),
        "average_driver_likeness": _mean(row["driver_likeness"] for row in rows),
        "average_kendall_tau_distance": _mean(
            row["kendall_tau_distance"] for row in rows
        ),
        "average_zone_transition_similarity": _mean(
            row["zone_transition_similarity"] for row in rows
        ),
        "average_route_compactness": _mean(row["route_compactness"] for row in rows),
        "average_runtime": _mean(row["runtime"] for row in rows),
        "route_validity": 1.0 - failure_rate,
        "failure_rate": failure_rate,
        "route_count": float(route_count),
    }


def _empty_metrics(route_count: int, *, failure_rate: float) -> Dict[str, float]:
    return {
        "average_travel_time": 0.0,
        "average_time_window_violation": 0.0,
        "average_driver_likeness": 0.0,
        "average_kendall_tau_distance": 1.0,
        "average_zone_transition_similarity": 0.0,
        "average_route_compactness": 0.0,
        "average_runtime": 0.0,
        "route_validity": 1.0 - failure_rate,
        "failure_rate": failure_rate,
        "route_count": float(route_count),
    }


def _invalid_result(
    algorithm: str,
    sequence: Sequence[str],
    started: float,
    failure_reason: str,
) -> AmazonRoutingResult:
    return AmazonRoutingResult(
        algorithm=algorithm,
        sequence=tuple(sequence),
        metrics=route_metrics_for_invalid(),
        runtime=perf_counter() - started,
        is_valid=False,
        failure_reason=failure_reason,
    )


def route_metrics_for_invalid() -> Dict[str, float]:
    return {
        "travel_time": float("inf"),
        "time_window_violation": float("inf"),
        "driver_likeness": 0.0,
        "kendall_tau_distance": 1.0,
        "zone_transition_similarity": 0.0,
        "route_compactness": 0.0,
        "runtime": 0.0,
    }


def _failure_taxonomy(
    results: Sequence[AmazonProgramEvaluation],
) -> Dict[str, int]:
    taxonomy: Dict[str, int] = {}
    for result in results:
        if result.ok:
            continue
        reason = (result.failure_reason or "unknown_failure").split(":", 1)[0]
        taxonomy[reason] = taxonomy.get(reason, 0) + 1
    return taxonomy


def _candidate_for(
    candidates: Sequence[SeedAmazonProgram],
    program_id: str,
) -> SeedAmazonProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _code_for(candidates: Sequence[SeedAmazonProgram], program_id: str) -> str:
    return _candidate_for(candidates, program_id).code


def _route_payload(route_id: str, *, offset: int = 0) -> Mapping[str, object]:
    due_shift = offset * 0.05
    return {
        "route_id": route_id,
        "station_code": "DLA9",
        "quality_label": "High" if offset % 2 == 0 else "Medium",
        "depot": {
            "stop_id": "depot",
            "zone_id": "DEPOT",
            "x": 0.0,
            "y": 0.0,
        },
        "stops": [
            {
                "stop_id": "S1",
                "zone_id": "A",
                "x": 1.0,
                "y": 0.0,
                "service_time": 1.0,
                "time_window": [0.0, 20.0 + due_shift],
                "packages": [{"package_id": f"{route_id}-p1", "weight": 2.0}],
            },
            {
                "stop_id": "S2",
                "zone_id": "A",
                "x": 2.0,
                "y": 0.0,
                "service_time": 1.5,
                "time_window": [0.0, 12.0 + due_shift],
                "packages": [
                    {"package_id": f"{route_id}-p2", "weight": 1.0},
                    {"package_id": f"{route_id}-p3", "weight": 3.0},
                ],
            },
            {
                "stop_id": "S3",
                "zone_id": "B",
                "x": 0.0,
                "y": 1.0,
                "service_time": 1.0,
                "time_window": [4.0, 30.0 + due_shift],
                "packages": [{"package_id": f"{route_id}-p4", "weight": 1.5}],
            },
            {
                "stop_id": "S4",
                "zone_id": "B",
                "x": 0.0,
                "y": 2.0,
                "service_time": 2.0,
                "time_window": [5.0, 35.0 + due_shift],
                "packages": [{"package_id": f"{route_id}-p5", "weight": 2.5}],
            },
        ],
        "actual_sequence": ["S1", "S2", "S3", "S4"],
        "travel_times": {
            "depot": {"depot": 0.0, "S1": 2.0, "S2": 3.0, "S3": 4.0, "S4": 5.0},
            "S1": {"depot": 2.0, "S1": 0.0, "S2": 1.0, "S3": 4.0, "S4": 5.0},
            "S2": {"depot": 3.0, "S1": 1.0, "S2": 0.0, "S3": 3.0, "S4": 4.0},
            "S3": {"depot": 4.0, "S1": 4.0, "S2": 3.0, "S3": 0.0, "S4": 1.0},
            "S4": {"depot": 5.0, "S1": 5.0, "S2": 4.0, "S3": 1.0, "S4": 0.0},
        },
    }


def _mean(values: Sequence[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
