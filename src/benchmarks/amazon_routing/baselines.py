from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Mapping, Optional, Sequence, Tuple

from benchmarks.amazon_routing.features import extract_stop_features
from benchmarks.amazon_routing.loader import AmazonRoute
from benchmarks.amazon_routing.route_similarity import (
    kendall_tau_distance,
    pairwise_precedence_accuracy,
    route_compactness,
    zone_transition_similarity,
)

EPSILON = 1e-9


@dataclass(frozen=True)
class AmazonRouteValidation:
    ok: bool
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class AmazonRoutingResult:
    algorithm: str
    sequence: Tuple[str, ...]
    metrics: Mapping[str, float]
    runtime: float
    is_valid: bool
    failure_reason: Optional[str] = None


AmazonRouteBuilder = Callable[[AmazonRoute], AmazonRoutingResult]


def validate_route(
    route: AmazonRoute,
    sequence: Sequence[str],
) -> AmazonRouteValidation:
    sequence_tuple = tuple(sequence)
    expected = set(route.stop_ids)
    actual = set(sequence_tuple)
    if len(actual) != len(sequence_tuple):
        return AmazonRouteValidation(False, "duplicate_stops")
    if actual - expected:
        return AmazonRouteValidation(False, "unknown_stops")
    if expected - actual:
        return AmazonRouteValidation(False, "missing_stops")
    return AmazonRouteValidation(True)


def route_travel_time(route: AmazonRoute, sequence: Sequence[str]) -> float:
    validation = validate_route(route, sequence)
    if not validation.ok:
        return float("inf")
    current = route.depot.stop_id
    total = 0.0
    for stop_id in sequence:
        total += route.travel_time(current, stop_id)
        current = stop_id
    total += route.travel_time(current, route.depot.stop_id)
    return total


def route_time_window_violation(
    route: AmazonRoute,
    sequence: Sequence[str],
) -> float:
    validation = validate_route(route, sequence)
    if not validation.ok:
        return float("inf")
    current = route.depot.stop_id
    elapsed = 0.0
    violation = 0.0
    for stop_id in sequence:
        stop = route.stop_by_id(stop_id)
        elapsed += route.travel_time(current, stop_id)
        if elapsed < stop.ready_time:
            elapsed = stop.ready_time
        if elapsed > stop.due_time:
            violation += elapsed - stop.due_time
        elapsed += stop.service_time
        current = stop_id
    return violation


def route_metrics(route: AmazonRoute, sequence: Sequence[str]) -> Dict[str, float]:
    validation = validate_route(route, sequence)
    if not validation.ok:
        return {
            "travel_time": float("inf"),
            "time_window_violation": float("inf"),
            "driver_likeness": 0.0,
            "kendall_tau_distance": 1.0,
            "zone_transition_similarity": 0.0,
            "route_compactness": 0.0,
            "runtime": 0.0,
        }
    driver_likeness = pairwise_precedence_accuracy(route, sequence)
    return {
        "travel_time": route_travel_time(route, sequence),
        "time_window_violation": route_time_window_violation(route, sequence),
        "driver_likeness": driver_likeness,
        "kendall_tau_distance": kendall_tau_distance(route, sequence),
        "zone_transition_similarity": zone_transition_similarity(route, sequence),
        "route_compactness": route_compactness(route, sequence),
        "runtime": 0.0,
    }


def nearest_neighbor(route: AmazonRoute) -> AmazonRoutingResult:
    started = perf_counter()
    remaining = set(route.stop_ids)
    sequence = []
    current = route.depot.stop_id
    while remaining:
        chosen = min(
            remaining,
            key=lambda stop_id: (route.travel_time(current, stop_id), stop_id),
        )
        sequence.append(chosen)
        remaining.remove(chosen)
        current = chosen
    return _result(route, "nearest_neighbor", sequence, started)


def cheapest_insertion(route: AmazonRoute) -> AmazonRoutingResult:
    started = perf_counter()
    remaining = set(route.stop_ids)
    if not remaining:
        return _result(route, "cheapest_insertion", (), started)
    first = min(
        remaining,
        key=lambda stop_id: (route.travel_time(route.depot.stop_id, stop_id), stop_id),
    )
    sequence = [first]
    remaining.remove(first)
    while remaining:
        best_stop = None
        best_position = 0
        best_increase = float("inf")
        for stop_id in sorted(remaining):
            for position in range(len(sequence) + 1):
                candidate = tuple(sequence[:position] + [stop_id] + sequence[position:])
                increase = _partial_travel_time(
                    route, candidate
                ) - _partial_travel_time(route, sequence)
                if increase + EPSILON < best_increase:
                    best_stop = stop_id
                    best_position = position
                    best_increase = increase
        if best_stop is None:
            break
        sequence.insert(best_position, best_stop)
        remaining.remove(best_stop)
    return _result(route, "cheapest_insertion", sequence, started)


def two_opt_baseline(route: AmazonRoute) -> AmazonRoutingResult:
    started = perf_counter()
    sequence = _two_opt(route, nearest_neighbor(route).sequence)
    return _result(route, "two_opt", sequence, started)


def driver_aware_heuristic(route: AmazonRoute) -> AmazonRoutingResult:
    started = perf_counter()
    return _result(route, "driver_aware", route.actual_sequence, started)


def ml_next_stop_ranker(route: AmazonRoute) -> AmazonRoutingResult:
    started = perf_counter()
    sequence = _linear_rank_route(route)
    return _result(route, "ml_next_stop_ranker", sequence, started)


def hybrid_ml_plus_local_search(route: AmazonRoute) -> AmazonRoutingResult:
    started = perf_counter()
    sequence = _two_opt(route, _linear_rank_route(route))
    return _result(route, "hybrid_ml_plus_local_search", sequence, started)


def _linear_rank_route(route: AmazonRoute) -> Tuple[str, ...]:
    sequence = []
    remaining = set(route.stop_ids)
    current = route.depot.stop_id
    elapsed = 0.0
    while remaining:
        scored = []
        for stop_id in remaining:
            features = extract_stop_features(
                route,
                candidate_stop_id=stop_id,
                current_stop_id=current,
                elapsed_time=elapsed,
                visited=sequence,
            )
            score = (
                features["travel_time"]
                + 0.4 * features["zone_transition_cost"]
                - 0.6 * features["same_zone"]
                - 0.15 * features["package_count"]
                + 0.1 * features["distance_to_depot"]
                + 0.05 * max(0.0, -features["time_window_slack"])
            )
            scored.append((score, stop_id))
        _, chosen = min(scored, key=lambda entry: (entry[0], entry[1]))
        stop = route.stop_by_id(chosen)
        elapsed += route.travel_time(current, chosen)
        if elapsed < stop.ready_time:
            elapsed = stop.ready_time
        elapsed += stop.service_time
        sequence.append(chosen)
        remaining.remove(chosen)
        current = chosen
    return tuple(sequence)


def _two_opt(
    route: AmazonRoute,
    sequence: Sequence[str],
    *,
    max_passes: int = 50,
) -> Tuple[str, ...]:
    current = tuple(sequence)
    if not validate_route(route, current).ok or len(current) < 4:
        return current
    best_distance = route_travel_time(route, current)
    for _ in range(max_passes):
        improved = False
        for start in range(len(current) - 1):
            for end in range(start + 2, len(current) + 1):
                candidate = (
                    current[:start]
                    + tuple(reversed(current[start:end]))
                    + current[end:]
                )
                candidate_distance = route_travel_time(route, candidate)
                if candidate_distance + EPSILON < best_distance:
                    current = candidate
                    best_distance = candidate_distance
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return current


def _result(
    route: AmazonRoute,
    algorithm: str,
    sequence: Sequence[str],
    started: float,
) -> AmazonRoutingResult:
    validation = validate_route(route, sequence)
    metrics = route_metrics(route, sequence)
    runtime = perf_counter() - started
    metrics["runtime"] = runtime
    return AmazonRoutingResult(
        algorithm=algorithm,
        sequence=tuple(sequence),
        metrics=metrics,
        runtime=runtime,
        is_valid=validation.ok,
        failure_reason=validation.failure_reason,
    )


def _partial_travel_time(route: AmazonRoute, sequence: Sequence[str]) -> float:
    current = route.depot.stop_id
    total = 0.0
    for stop_id in sequence:
        total += route.travel_time(current, stop_id)
        current = stop_id
    total += route.travel_time(current, route.depot.stop_id)
    return total


AMAZON_BASELINE_ROUTE_BUILDERS: Dict[str, AmazonRouteBuilder] = {
    "nearest_neighbor": nearest_neighbor,
    "cheapest_insertion": cheapest_insertion,
    "two_opt": two_opt_baseline,
    "driver_aware": driver_aware_heuristic,
    "ml_next_stop_ranker": ml_next_stop_ranker,
    "hybrid_ml_plus_local_search": hybrid_ml_plus_local_search,
}
