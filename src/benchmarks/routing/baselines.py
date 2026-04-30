from __future__ import annotations

from dataclasses import dataclass
from random import Random
from time import perf_counter
from typing import Callable, Dict, Mapping, Optional, Sequence, Tuple

from benchmarks.routing.instances import RoutingInstance, Stop
from benchmarks.routing.local_search import two_opt

EPSILON = 1e-9


@dataclass(frozen=True)
class RouteValidation:
    ok: bool
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class RoutingResult:
    algorithm: str
    route: Tuple[str, ...]
    total_distance: float
    time_window_violation: float
    runtime: float
    is_valid: bool
    failure_reason: Optional[str] = None


RouteBuilder = Callable[[RoutingInstance], RoutingResult]


def validate_route(instance: RoutingInstance, route: Sequence[str]) -> RouteValidation:
    route_tuple = tuple(route)
    expected = {stop.stop_id for stop in instance.stops}
    actual = set(route_tuple)
    if len(actual) != len(route_tuple):
        return RouteValidation(False, "duplicate_stops")
    if actual - expected:
        return RouteValidation(False, "unknown_stops")
    if expected - actual:
        return RouteValidation(False, "missing_stops")
    return RouteValidation(True)


def route_distance(instance: RoutingInstance, route: Sequence[str]) -> float:
    validation = validate_route(instance, route)
    if not validation.ok:
        return float("inf")
    lookup = _stop_index_lookup(instance)
    total = 0.0
    current_index = 0
    for stop_id in route:
        next_index = lookup[stop_id]
        total += instance.distance_matrix[current_index][next_index]
        current_index = next_index
    total += instance.distance_matrix[current_index][0]
    return total


def route_time_window_violation(
    instance: RoutingInstance,
    route: Sequence[str],
) -> float:
    validation = validate_route(instance, route)
    if not validation.ok:
        return float("inf")
    lookup = _stop_lookup(instance)
    index_lookup = _stop_index_lookup(instance)
    elapsed = 0.0
    violation = 0.0
    current_index = 0
    for stop_id in route:
        next_index = index_lookup[stop_id]
        stop = lookup[stop_id]
        elapsed += instance.distance_matrix[current_index][next_index]
        if elapsed < stop.ready_time:
            elapsed = stop.ready_time
        if elapsed > stop.due_time:
            violation += elapsed - stop.due_time
        elapsed += stop.service_time
        current_index = next_index
    return violation


def random_route(instance: RoutingInstance) -> RoutingResult:
    started = perf_counter()
    route = [stop.stop_id for stop in instance.stops]
    Random(instance.seed).shuffle(route)
    return _result(instance, "random", tuple(route), started)


def nearest_neighbor(instance: RoutingInstance) -> RoutingResult:
    started = perf_counter()
    lookup = _stop_index_lookup(instance)
    remaining = set(lookup)
    route = []
    current_index = 0
    while remaining:
        chosen = min(
            remaining,
            key=lambda stop_id: (
                instance.distance_matrix[current_index][lookup[stop_id]],
                stop_id,
            ),
        )
        route.append(chosen)
        remaining.remove(chosen)
        current_index = lookup[chosen]
    return _result(instance, "nearest_neighbor", tuple(route), started)


def cheapest_insertion(instance: RoutingInstance) -> RoutingResult:
    started = perf_counter()
    if not instance.stops:
        return _result(instance, "cheapest_insertion", (), started)
    lookup = _stop_index_lookup(instance)
    remaining = {stop.stop_id for stop in instance.stops}
    first = min(
        remaining,
        key=lambda stop_id: (instance.distance_matrix[0][lookup[stop_id]], stop_id),
    )
    route = [first]
    remaining.remove(first)
    while remaining:
        best_stop = None
        best_position = 0
        best_increase = float("inf")
        for stop_id in sorted(remaining):
            for position in range(len(route) + 1):
                candidate = tuple(route[:position] + [stop_id] + route[position:])
                increase = _partial_route_distance(
                    instance, candidate
                ) - _partial_route_distance(instance, route)
                if increase + EPSILON < best_increase:
                    best_stop = stop_id
                    best_position = position
                    best_increase = increase
        if best_stop is None:
            break
        route.insert(best_position, best_stop)
        remaining.remove(best_stop)
    return _result(instance, "cheapest_insertion", tuple(route), started)


def two_opt_baseline(instance: RoutingInstance) -> RoutingResult:
    started = perf_counter()
    route = two_opt(instance, random_route(instance).route)
    return _result(instance, "two_opt", route, started)


def nearest_neighbor_plus_2opt(instance: RoutingInstance) -> RoutingResult:
    started = perf_counter()
    route = two_opt(instance, nearest_neighbor(instance).route)
    return _result(instance, "nearest_neighbor_plus_2opt", route, started)


def _result(
    instance: RoutingInstance,
    algorithm: str,
    route: Sequence[str],
    started: float,
) -> RoutingResult:
    validation = validate_route(instance, route)
    route_tuple = tuple(route)
    return RoutingResult(
        algorithm=algorithm,
        route=route_tuple,
        total_distance=route_distance(instance, route_tuple),
        time_window_violation=route_time_window_violation(instance, route_tuple),
        runtime=perf_counter() - started,
        is_valid=validation.ok,
        failure_reason=validation.failure_reason,
    )


def _stop_lookup(instance: RoutingInstance) -> Mapping[str, Stop]:
    return {stop.stop_id: stop for stop in instance.stops}


def _stop_index_lookup(instance: RoutingInstance) -> Mapping[str, int]:
    return {stop.stop_id: index + 1 for index, stop in enumerate(instance.stops)}


def _partial_route_distance(instance: RoutingInstance, route: Sequence[str]) -> float:
    lookup = _stop_index_lookup(instance)
    total = 0.0
    current_index = 0
    for stop_id in route:
        next_index = lookup[stop_id]
        total += instance.distance_matrix[current_index][next_index]
        current_index = next_index
    total += instance.distance_matrix[current_index][0]
    return total


BASELINE_ROUTE_BUILDERS: Dict[str, RouteBuilder] = {
    "random": random_route,
    "nearest_neighbor": nearest_neighbor,
    "cheapest_insertion": cheapest_insertion,
    "two_opt": two_opt_baseline,
    "nearest_neighbor_plus_2opt": nearest_neighbor_plus_2opt,
}
