from __future__ import annotations

from typing import Mapping, Sequence, Tuple

from benchmarks.routing.instances import RoutingInstance

EPSILON = 1e-9


def two_opt(
    instance: RoutingInstance,
    route: Sequence[str],
    *,
    max_passes: int = 50,
) -> Tuple[str, ...]:
    current = tuple(route)
    if not _is_valid_permutation(instance, current):
        return current
    if len(current) < 4:
        return current

    best_distance = _route_distance(instance, current)
    for _ in range(max_passes):
        improved = False
        for start in range(len(current) - 1):
            for end in range(start + 2, len(current) + 1):
                candidate = (
                    current[:start]
                    + tuple(reversed(current[start:end]))
                    + current[end:]
                )
                candidate_distance = _route_distance(instance, candidate)
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


def _is_valid_permutation(instance: RoutingInstance, route: Sequence[str]) -> bool:
    return {stop.stop_id for stop in instance.stops} == set(route) and len(
        route
    ) == len(set(route))


def _route_distance(instance: RoutingInstance, route: Sequence[str]) -> float:
    lookup = _stop_index_lookup(instance)
    total = 0.0
    current_index = 0
    for stop_id in route:
        next_index = lookup[stop_id]
        total += instance.distance_matrix[current_index][next_index]
        current_index = next_index
    total += instance.distance_matrix[current_index][0]
    return total


def _stop_index_lookup(instance: RoutingInstance) -> Mapping[str, int]:
    return {stop.stop_id: index + 1 for index, stop in enumerate(instance.stops)}
