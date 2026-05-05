from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from time import perf_counter
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from benchmarks.routing.baselines import (
    BASELINE_ROUTE_BUILDERS,
    RoutingResult,
    route_capacity_violation,
    route_distance,
    route_time_window_violation,
    route_vehicle_count,
    validate_route,
)
from benchmarks.routing.instances import (
    RoutingInstance,
    Stop,
    default_train_validation_test_suites,
)
from benchmarks.routing.local_search import two_opt
from sandbox.restricted_exec import SAFE_BUILTINS, SandboxTimeoutError, _timeout
from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    validate_candidate_code,
)

TIME_WINDOW_PENALTY = 10.0


@dataclass(frozen=True)
class RoutingProgramEvaluation:
    program_id: str
    ok: bool
    score: Optional[float]
    metrics: Mapping[str, float]
    runtime: float
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class SeedRoutingProgram:
    program_id: str
    code: str
    explanation: str


@dataclass(frozen=True)
class RoutingCandidateSuiteSummary:
    candidate_count: int
    failure_rate: float
    best_program_id: str
    best_validation_score: float
    best_with_local_search_score: float
    median_validation_score: float
    test_score: Optional[float]
    baseline_scores: Mapping[str, float]
    top_programs: List[Mapping[str, object]]


class RoutingEvaluator:
    def __init__(self, *, timeout_seconds: float = 0.25) -> None:
        self.timeout_seconds = timeout_seconds
        self.validation_config = ValidationConfig(allowed_function="score_next_stop")

    def evaluate_program(
        self,
        code: str,
        instances: Sequence[RoutingInstance],
        *,
        program_id: str,
        apply_local_search: bool = False,
    ) -> RoutingProgramEvaluation:
        started = perf_counter()
        if not instances:
            return RoutingProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={"failure_rate": 1.0},
                runtime=perf_counter() - started,
                failure_reason="no_instances",
            )
        scoring_function, failure = self._compile_program(code)
        if failure is not None:
            return RoutingProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={
                    "average_route_length": 0.0,
                    "average_time_window_violation": 0.0,
                    "route_validity": 0.0,
                    "failure_rate": 1.0,
                    "instance_count": float(len(instances)),
                },
                runtime=perf_counter() - started,
                failure_reason=str(failure),
            )

        lengths = []
        violations = []
        capacity_violations = []
        vehicle_counts = []
        failures = 0
        first_failure = None
        for instance in instances:
            result = self._route_with_program(
                scoring_function,
                instance,
                apply_local_search=apply_local_search,
            )
            if result.is_valid:
                lengths.append(result.total_distance)
                violations.append(result.time_window_violation)
                capacity_violations.append(result.capacity_violation)
                vehicle_counts.append(float(result.vehicle_count))
            else:
                failures += 1
                if first_failure is None:
                    first_failure = result.failure_reason or "invalid_route"

        failure_rate = failures / len(instances)
        metrics = {
            "average_route_length": _mean(lengths),
            "average_time_window_violation": _mean(violations),
            "average_capacity_violation": _mean(capacity_violations),
            "average_vehicle_count": _mean(vehicle_counts),
            "route_validity": 1.0 - failure_rate,
            "failure_rate": failure_rate,
            "instance_count": float(len(instances)),
        }
        if failures == len(instances):
            return RoutingProgramEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics=metrics,
                runtime=perf_counter() - started,
                failure_reason=first_failure,
            )
        score = (
            metrics["average_route_length"]
            + metrics["average_time_window_violation"] * TIME_WINDOW_PENALTY
            + failure_rate * 10_000.0
        )
        return RoutingProgramEvaluation(
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
        instance: RoutingInstance,
        *,
        apply_local_search: bool,
    ) -> RoutingResult:
        started = perf_counter()
        route: List[str] = []
        stop_lookup = {stop.stop_id: stop for stop in instance.stops}
        index_lookup = {
            stop.stop_id: index + 1 for index, stop in enumerate(instance.stops)
        }
        remaining = set(stop_lookup)
        current_index = 0
        elapsed = 0.0
        route_length = 0.0
        route_load = 0.0
        vehicle_count = 1
        try:
            with _timeout(self.timeout_seconds):
                while remaining:
                    current_stop = _current_stop_id(instance, current_index)
                    scored = []
                    for stop_id in remaining:
                        stop = stop_lookup[stop_id]
                        direct_travel_time = instance.distance_matrix[current_index][
                            index_lookup[stop_id]
                        ]
                        travel_time, requires_depot_return = _capacity_adjusted_travel(
                            instance,
                            current_index,
                            index_lookup[stop_id],
                            route_load,
                            stop.demand,
                        )
                        state = {
                            "current_stop_id": current_stop,
                            "current_index": current_index,
                            "depot_x": instance.depot.x,
                            "depot_y": instance.depot.y,
                            "elapsed_time": elapsed,
                            "route_length_so_far": route_length,
                            "visited_count": len(route),
                            "remaining_count": len(remaining),
                            "route_load": route_load,
                            "vehicle_capacity": instance.vehicle_capacity or 0.0,
                            "remaining_capacity": _remaining_capacity(
                                instance,
                                route_load,
                            ),
                            "vehicle_count_so_far": vehicle_count,
                        }
                        candidate = _candidate_features(
                            instance,
                            stop,
                            travel_time,
                            direct_travel_time,
                            elapsed,
                            route_load,
                            requires_depot_return,
                        )
                        score, failure = self._call_score_function(
                            scoring_function,
                            state,
                            candidate,
                        )
                        if failure is not None:
                            return _invalid_result(
                                "score_next_stop",
                                route,
                                started,
                                str(failure),
                            )
                        scored.append((score, stop_id, travel_time))
                    _, chosen, travel_time = min(
                        scored, key=lambda item: (item[0], item[1])
                    )
                    stop = stop_lookup[chosen]
                    _, requires_depot_return = _capacity_adjusted_travel(
                        instance,
                        current_index,
                        index_lookup[chosen],
                        route_load,
                        stop.demand,
                    )
                    if requires_depot_return:
                        vehicle_count += 1
                        route_load = 0.0
                    route.append(chosen)
                    route_length += travel_time
                    elapsed += travel_time
                    if elapsed < stop.ready_time:
                        elapsed = stop.ready_time
                    elapsed += stop.service_time
                    current_index = index_lookup[chosen]
                    route_load += max(0.0, stop.demand)
                    remaining.remove(chosen)
        except SandboxTimeoutError:
            return _invalid_result(
                "score_next_stop",
                route,
                started,
                f"timeout: candidate exceeded {self.timeout_seconds} seconds",
            )

        route_tuple = tuple(route)
        if apply_local_search:
            improved = two_opt(instance, route_tuple)
            if _route_score_for_route(instance, improved) <= _route_score_for_route(
                instance, route_tuple
            ):
                route_tuple = improved
        validation = validate_route(instance, route_tuple)
        return RoutingResult(
            algorithm="score_next_stop",
            route=route_tuple,
            total_distance=route_distance(instance, route_tuple),
            time_window_violation=route_time_window_violation(instance, route_tuple),
            runtime=perf_counter() - started,
            is_valid=validation.ok,
            failure_reason=validation.failure_reason,
            capacity_violation=route_capacity_violation(instance, route_tuple),
            vehicle_count=route_vehicle_count(instance, route_tuple),
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


def evaluate_routing_candidate_suite(
    *,
    candidates: Sequence[SeedRoutingProgram],
    train_instances: Sequence[RoutingInstance],
    validation_instances: Sequence[RoutingInstance],
    test_instances: Sequence[RoutingInstance],
) -> RoutingCandidateSuiteSummary:
    evaluator = RoutingEvaluator()
    validation_results = [
        evaluator.evaluate_program(
            candidate.code,
            validation_instances,
            program_id=candidate.program_id,
        )
        for candidate in candidates
    ]
    successful = [result for result in validation_results if result.score is not None]
    if not successful:
        raise ValueError("candidate suite produced no successful routing programs")
    local_results = [
        evaluator.evaluate_program(
            _code_for(candidates, result.program_id),
            validation_instances,
            program_id=result.program_id,
            apply_local_search=True,
        )
        for result in successful
    ]
    local_successful = [result for result in local_results if result.score is not None]
    best = min(successful, key=lambda result: result.score or float("inf"))
    best_local = min(local_successful, key=lambda result: result.score or float("inf"))
    test = evaluator.evaluate_program(
        _code_for(candidates, best_local.program_id),
        test_instances,
        program_id=best_local.program_id,
        apply_local_search=True,
    )
    baseline_scores = _baseline_scores(validation_instances)
    top_programs = []
    for result in sorted(local_successful, key=lambda item: item.score or float("inf"))[
        :5
    ]:
        candidate = _candidate_for(candidates, result.program_id)
        train_result = evaluator.evaluate_program(
            candidate.code,
            train_instances,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        base_result = _result_for(validation_results, result.program_id)
        top_programs.append(
            {
                "program_id": candidate.program_id,
                "validation_score": base_result.score,
                "local_search_validation_score": result.score,
                "train_score": train_result.score,
                "code": candidate.code,
                "explanation": candidate.explanation,
            }
        )
    return RoutingCandidateSuiteSummary(
        candidate_count=len(candidates),
        failure_rate=sum(not result.ok for result in validation_results)
        / len(validation_results),
        best_program_id=best.program_id,
        best_validation_score=best.score or 0.0,
        best_with_local_search_score=best_local.score or 0.0,
        median_validation_score=median(result.score or 0.0 for result in successful),
        test_score=test.score,
        baseline_scores=baseline_scores,
        top_programs=top_programs,
    )


def build_phase4_report(
    *,
    candidate_count: int = 120,
    stop_count: int = 10,
) -> Dict[str, object]:
    train, validation, test = default_train_validation_test_suites(
        train_sizes=(max(4, stop_count - 2),),
        validation_sizes=(stop_count,),
        test_sizes=(stop_count + 2,),
    )
    candidates = build_seed_routing_programs(candidate_count)
    summary = evaluate_routing_candidate_suite(
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
        "best_with_local_search_score": summary.best_with_local_search_score,
        "median_validation_score": summary.median_validation_score,
        "test_score": summary.test_score,
        "baseline_scores": dict(summary.baseline_scores),
        "local_search": {
            "improved_or_equal": summary.best_with_local_search_score
            <= summary.best_validation_score,
            "best_without_local_search_score": summary.best_validation_score,
            "best_with_local_search_score": summary.best_with_local_search_score,
        },
        "held_out": {
            "instance_count": len(test),
            "score": summary.test_score,
        },
        "top_programs": summary.top_programs,
    }


def build_seed_routing_programs(count: int = 120) -> List[SeedRoutingProgram]:
    if count < 1:
        raise ValueError("count must be positive")
    templates = [
        (
            "nearest",
            """
def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"]
""",
            "Nearest-neighbor scoring rule that minimizes immediate travel time.",
        ),
        (
            "return_aware",
            """
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        + {weight} * candidate_stop["distance_to_depot"]
    )
""",
            "Balances immediate travel time with eventual return-to-depot cost.",
        ),
        (
            "window_guard",
            """
def score_next_stop(state, candidate_stop):
    projected = state["elapsed_time"] + candidate_stop["travel_time"]
    lateness = max(0, projected - candidate_stop["due_time"])
    return candidate_stop["travel_time"] + {penalty} * lateness
""",
            "Adds a lateness penalty for stops whose time windows are becoming risky.",
        ),
        (
            "slack_aware",
            """
def score_next_stop(state, candidate_stop):
    urgency = max(0, 1.0 - candidate_stop["time_window_slack"])
    return candidate_stop["travel_time"] + {weight} * urgency
""",
            "Prefers nearby stops while nudging urgent time windows earlier.",
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
        parameter = round(0.05 + (index % 17) * 0.03, 4)
        code = template.format(weight=parameter, penalty=round(5.0 + parameter, 4))
        candidates.append(
            SeedRoutingProgram(
                program_id=f"route-seed-{index:03d}-{name}",
                code=code.strip() + "\n",
                explanation=explanation,
            )
        )
    return candidates


def _baseline_scores(instances: Sequence[RoutingInstance]) -> Dict[str, float]:
    scores = {}
    for name, builder in BASELINE_ROUTE_BUILDERS.items():
        results = [builder(instance) for instance in instances]
        scores[name] = _mean(_route_score(result) for result in results)
    return scores


def _candidate_features(
    instance: RoutingInstance,
    stop: Stop,
    travel_time: float,
    direct_travel_time: float,
    elapsed: float,
    route_load: float,
    requires_depot_return: bool,
) -> Mapping[str, object]:
    projected = elapsed + travel_time
    capacity = instance.vehicle_capacity or 0.0
    return {
        "stop_id": stop.stop_id,
        "x": stop.x,
        "y": stop.y,
        "travel_time": travel_time,
        "direct_travel_time": direct_travel_time,
        "distance_to_depot": instance.distance_matrix[
            _stop_index(instance, stop.stop_id)
        ][0],
        "ready_time": stop.ready_time,
        "due_time": stop.due_time,
        "service_time": stop.service_time,
        "time_window_slack": stop.due_time - projected,
        "demand": stop.demand,
        "vehicle_capacity": capacity,
        "route_load": route_load,
        "remaining_capacity": max(0.0, capacity - route_load) if capacity else 0.0,
        "requires_depot_return": 1.0 if requires_depot_return else 0.0,
    }


def _current_stop_id(instance: RoutingInstance, current_index: int) -> str:
    if current_index == 0:
        return "depot"
    return instance.stops[current_index - 1].stop_id


def _invalid_result(
    algorithm: str,
    route: Sequence[str],
    started: float,
    failure_reason: str,
) -> RoutingResult:
    return RoutingResult(
        algorithm=algorithm,
        route=tuple(route),
        total_distance=float("inf"),
        time_window_violation=float("inf"),
        runtime=perf_counter() - started,
        is_valid=False,
        failure_reason=failure_reason,
        capacity_violation=float("inf"),
        vehicle_count=0,
    )


def _route_score(result: RoutingResult) -> float:
    if not result.is_valid:
        return 10_000.0
    return result.total_distance + result.time_window_violation * TIME_WINDOW_PENALTY


def _route_score_for_route(instance: RoutingInstance, route: Sequence[str]) -> float:
    validation = validate_route(instance, route)
    if not validation.ok:
        return 10_000.0
    return (
        route_distance(instance, route)
        + route_time_window_violation(instance, route) * TIME_WINDOW_PENALTY
    )


def _capacity_adjusted_travel(
    instance: RoutingInstance,
    current_index: int,
    next_index: int,
    route_load: float,
    demand: float,
) -> Tuple[float, bool]:
    direct = instance.distance_matrix[current_index][next_index]
    capacity = instance.vehicle_capacity
    if capacity is None or route_load <= 1e-9:
        return direct, False
    if route_load + max(0.0, demand) <= capacity + 1e-9:
        return direct, False
    via_depot = (
        instance.distance_matrix[current_index][0]
        + instance.distance_matrix[0][next_index]
    )
    return via_depot, True


def _remaining_capacity(instance: RoutingInstance, route_load: float) -> float:
    if instance.vehicle_capacity is None:
        return 0.0
    return max(0.0, float(instance.vehicle_capacity) - route_load)


def _candidate_for(
    candidates: Sequence[SeedRoutingProgram],
    program_id: str,
) -> SeedRoutingProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _code_for(candidates: Sequence[SeedRoutingProgram], program_id: str) -> str:
    return _candidate_for(candidates, program_id).code


def _result_for(
    results: Sequence[RoutingProgramEvaluation],
    program_id: str,
) -> RoutingProgramEvaluation:
    for result in results:
        if result.program_id == program_id:
            return result
    raise KeyError(program_id)


def _stop_index(instance: RoutingInstance, stop_id: str) -> int:
    for index, stop in enumerate(instance.stops):
        if stop.stop_id == stop_id:
            return index + 1
    raise KeyError(stop_id)


def _mean(values: Sequence[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
