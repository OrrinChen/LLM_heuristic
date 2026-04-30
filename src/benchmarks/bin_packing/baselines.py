from __future__ import annotations

from dataclasses import dataclass
from random import Random
from time import perf_counter
from typing import Callable, Dict, List, Optional, Sequence

from benchmarks.bin_packing.instances import BinPackingInstance

EPSILON = 1e-9


@dataclass(frozen=True)
class PackingValidation:
    ok: bool
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class PackingResult:
    algorithm: str
    bins: List[List[float]]
    runtime: float
    is_valid: bool
    failure_reason: Optional[str] = None

    @property
    def bins_used(self) -> int:
        return len(self.bins)

    @property
    def total_waste(self) -> float:
        return sum(1.0 - sum(bin_items) for bin_items in self.bins)

    @property
    def average_waste(self) -> float:
        if not self.bins:
            return 0.0
        return self.total_waste / len(self.bins)


Packer = Callable[[BinPackingInstance], PackingResult]


def first_fit(instance: BinPackingInstance) -> PackingResult:
    return _pack_online(instance, "first_fit", _first_fit_choice)


def best_fit(instance: BinPackingInstance) -> PackingResult:
    return _pack_online(instance, "best_fit", _best_fit_choice)


def worst_fit(instance: BinPackingInstance) -> PackingResult:
    return _pack_online(instance, "worst_fit", _worst_fit_choice)


def first_fit_decreasing(instance: BinPackingInstance) -> PackingResult:
    sorted_instance = _with_items(instance, sorted(instance.items, reverse=True))
    return _pack_online(
        sorted_instance,
        "first_fit_decreasing",
        _first_fit_choice,
        original_instance=instance,
    )


def best_fit_decreasing(instance: BinPackingInstance) -> PackingResult:
    sorted_instance = _with_items(instance, sorted(instance.items, reverse=True))
    return _pack_online(
        sorted_instance,
        "best_fit_decreasing",
        _best_fit_choice,
        original_instance=instance,
    )


def handwritten_score_heuristic(instance: BinPackingInstance) -> PackingResult:
    def choose(item: float, bins: List[List[float]], capacity: float) -> Optional[int]:
        best_index = None
        best_score = float("inf")
        for index, bin_items in enumerate(bins):
            remaining = capacity - sum(bin_items)
            projected = remaining - item
            if projected < -EPSILON:
                continue
            fullness_bonus = len(bin_items) * 0.01
            score = projected - fullness_bonus
            if score < best_score:
                best_score = score
                best_index = index
        return best_index

    return _pack_online(instance, "handwritten_score_heuristic", choose)


def random_fit(instance: BinPackingInstance) -> PackingResult:
    rng = Random(instance.seed)

    def choose(item: float, bins: List[List[float]], capacity: float) -> Optional[int]:
        feasible = [
            index
            for index, bin_items in enumerate(bins)
            if capacity - sum(bin_items) + EPSILON >= item
        ]
        if not feasible:
            return None
        return rng.choice(feasible)

    return _pack_online(instance, "random", choose)


def validate_packing(
    instance: BinPackingInstance, bins: Sequence[Sequence[float]]
) -> PackingValidation:
    expected = sorted(round(item, 9) for item in instance.items)
    packed = sorted(round(item, 9) for bin_items in bins for item in bin_items)
    if packed != expected:
        return PackingValidation(False, "items_do_not_match_instance")
    for bin_items in bins:
        if sum(bin_items) > instance.capacity + EPSILON:
            return PackingValidation(False, "bin_capacity_exceeded")
    return PackingValidation(True)


def _pack_online(
    instance: BinPackingInstance,
    algorithm: str,
    chooser: Callable[[float, List[List[float]], float], Optional[int]],
    *,
    original_instance: Optional[BinPackingInstance] = None,
) -> PackingResult:
    started = perf_counter()
    bins: List[List[float]] = []
    for item in instance.items:
        chosen = chooser(item, bins, instance.capacity)
        if chosen is None:
            bins.append([item])
            continue
        if chosen < 0 or chosen >= len(bins):
            return PackingResult(
                algorithm=algorithm,
                bins=bins,
                runtime=perf_counter() - started,
                is_valid=False,
                failure_reason="invalid_bin_index",
            )
        if sum(bins[chosen]) + item > instance.capacity + EPSILON:
            return PackingResult(
                algorithm=algorithm,
                bins=bins,
                runtime=perf_counter() - started,
                is_valid=False,
                failure_reason="bin_capacity_exceeded",
            )
        bins[chosen].append(item)

    validation = validate_packing(original_instance or instance, bins)
    return PackingResult(
        algorithm=algorithm,
        bins=bins,
        runtime=perf_counter() - started,
        is_valid=validation.ok,
        failure_reason=validation.failure_reason,
    )


def _first_fit_choice(
    item: float, bins: List[List[float]], capacity: float
) -> Optional[int]:
    for index, bin_items in enumerate(bins):
        if capacity - sum(bin_items) + EPSILON >= item:
            return index
    return None


def _best_fit_choice(
    item: float, bins: List[List[float]], capacity: float
) -> Optional[int]:
    best_index = None
    best_remaining = float("inf")
    for index, bin_items in enumerate(bins):
        remaining = capacity - sum(bin_items) - item
        if remaining >= -EPSILON and remaining < best_remaining:
            best_remaining = remaining
            best_index = index
    return best_index


def _worst_fit_choice(
    item: float, bins: List[List[float]], capacity: float
) -> Optional[int]:
    worst_index = None
    worst_remaining = -1.0
    for index, bin_items in enumerate(bins):
        remaining = capacity - sum(bin_items) - item
        if remaining >= -EPSILON and remaining > worst_remaining:
            worst_remaining = remaining
            worst_index = index
    return worst_index


def _with_items(
    instance: BinPackingInstance, items: Sequence[float]
) -> BinPackingInstance:
    return BinPackingInstance(
        distribution=instance.distribution,
        seed=instance.seed,
        items=tuple(items),
        capacity=instance.capacity,
    )


BASELINE_PACKERS: Dict[str, Packer] = {
    "first_fit": first_fit,
    "best_fit": best_fit,
    "worst_fit": worst_fit,
    "first_fit_decreasing": first_fit_decreasing,
    "best_fit_decreasing": best_fit_decreasing,
    "handwritten_score_heuristic": handwritten_score_heuristic,
    "random": random_fit,
}
