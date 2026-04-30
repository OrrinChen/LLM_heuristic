from __future__ import annotations

from typing import Sequence

from benchmarks.amazon_routing.loader import AmazonRoute


def pairwise_precedence_accuracy(
    route: AmazonRoute,
    sequence: Sequence[str],
) -> float:
    if not _is_valid_sequence(route, sequence):
        return 0.0
    actual_positions = _positions(route.actual_sequence)
    predicted_positions = _positions(sequence)
    correct = 0
    total = 0
    for first_index, first in enumerate(route.actual_sequence):
        for second in route.actual_sequence[first_index + 1 :]:
            total += 1
            actual_order = actual_positions[first] < actual_positions[second]
            predicted_order = predicted_positions[first] < predicted_positions[second]
            if actual_order == predicted_order:
                correct += 1
    if total == 0:
        return 1.0
    return correct / total


def kendall_tau_distance(route: AmazonRoute, sequence: Sequence[str]) -> float:
    return 1.0 - pairwise_precedence_accuracy(route, sequence)


def zone_transition_similarity(route: AmazonRoute, sequence: Sequence[str]) -> float:
    if not _is_valid_sequence(route, sequence):
        return 0.0
    actual = _zone_transitions(route, route.actual_sequence)
    predicted = _zone_transitions(route, sequence)
    if not actual:
        return 1.0
    matches = sum(
        actual_transition == predicted_transition
        for actual_transition, predicted_transition in zip(actual, predicted)
    )
    return matches / len(actual)


def route_compactness(route: AmazonRoute, sequence: Sequence[str]) -> float:
    if not _is_valid_sequence(route, sequence):
        return 0.0
    if len(sequence) <= 1:
        return 1.0
    zones = [route.stop_by_id(stop_id).zone_id for stop_id in sequence]
    changes = sum(first != second for first, second in zip(zones, zones[1:]))
    return 1.0 - changes / (len(sequence) - 1)


def _zone_transitions(
    route: AmazonRoute,
    sequence: Sequence[str],
) -> tuple[tuple[str, str], ...]:
    zones = [route.stop_by_id(stop_id).zone_id for stop_id in sequence]
    return tuple(zip(zones, zones[1:]))


def _positions(sequence: Sequence[str]) -> dict[str, int]:
    return {stop_id: index for index, stop_id in enumerate(sequence)}


def _is_valid_sequence(route: AmazonRoute, sequence: Sequence[str]) -> bool:
    return set(sequence) == set(route.stop_ids) and len(sequence) == len(set(sequence))
