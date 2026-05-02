from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Iterable, List, Optional, Sequence, Tuple

InstanceSuites = Tuple[
    List["BinPackingInstance"],
    List["BinPackingInstance"],
    List["BinPackingInstance"],
]


class InstanceDistribution(str, Enum):
    UNIFORM_SMALL = "uniform_small"
    UNIFORM_MIXED = "uniform_mixed"
    HEAVY_TAIL = "heavy_tail"
    TINY_PLUS_LARGE = "tiny_plus_large"
    ADVERSARIAL = "adversarial"
    HELD_OUT = "held_out"
    EXTERNAL = "external"


@dataclass(frozen=True)
class BinPackingInstance:
    distribution: InstanceDistribution
    seed: int
    items: Tuple[float, ...]
    capacity: float = 1.0
    instance_id: str = ""
    source: str = "synthetic"
    known_optimum: Optional[int] = None


def generate_instance(
    distribution: InstanceDistribution,
    *,
    seed: int,
    item_count: int = 50,
    capacity: float = 1.0,
    items: Optional[Sequence[float]] = None,
    instance_id: str = "",
    source: str = "synthetic",
    known_optimum: Optional[int] = None,
) -> BinPackingInstance:
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    if items is not None:
        normalized = tuple(float(item) for item in items)
        _validate_items(normalized, capacity)
        return BinPackingInstance(
            distribution=distribution,
            seed=seed,
            items=normalized,
            capacity=float(capacity),
            instance_id=instance_id,
            source=source,
            known_optimum=known_optimum,
        )
    if item_count < 0:
        raise ValueError("item_count must be non-negative")

    rng = Random(seed)
    generated = tuple(
        round(_generate_item(distribution, rng, index, item_count), 6)
        for index in range(item_count)
    )
    _validate_items(generated, capacity)
    return BinPackingInstance(
        distribution=distribution,
        seed=seed,
        items=generated,
        capacity=float(capacity),
        instance_id=instance_id,
        source=source,
        known_optimum=known_optimum,
    )


def generate_suite(
    *,
    distributions: Iterable[InstanceDistribution],
    seeds: Iterable[int],
    item_count: int = 50,
    capacity: float = 1.0,
) -> List[BinPackingInstance]:
    return [
        generate_instance(
            distribution,
            seed=seed,
            item_count=item_count,
            capacity=capacity,
        )
        for distribution in distributions
        for seed in seeds
    ]


def default_train_validation_test_suites(
    *,
    item_count: int = 50,
    train_seeds: Sequence[int] = (1, 2, 3),
    validation_seeds: Sequence[int] = (101, 102),
    test_seeds: Sequence[int] = (201, 202),
) -> InstanceSuites:
    train_distributions = (
        InstanceDistribution.UNIFORM_SMALL,
        InstanceDistribution.UNIFORM_MIXED,
        InstanceDistribution.HEAVY_TAIL,
        InstanceDistribution.TINY_PLUS_LARGE,
        InstanceDistribution.ADVERSARIAL,
    )
    validation_distributions = train_distributions
    test_distributions = (
        InstanceDistribution.UNIFORM_SMALL,
        InstanceDistribution.UNIFORM_MIXED,
        InstanceDistribution.HEAVY_TAIL,
        InstanceDistribution.TINY_PLUS_LARGE,
        InstanceDistribution.ADVERSARIAL,
        InstanceDistribution.HELD_OUT,
    )
    return (
        generate_suite(
            distributions=train_distributions,
            seeds=train_seeds,
            item_count=item_count,
        ),
        generate_suite(
            distributions=validation_distributions,
            seeds=validation_seeds,
            item_count=item_count,
        ),
        generate_suite(
            distributions=test_distributions,
            seeds=test_seeds,
            item_count=item_count,
        ),
    )


def _generate_item(
    distribution: InstanceDistribution, rng: Random, index: int, item_count: int
) -> float:
    if distribution == InstanceDistribution.UNIFORM_SMALL:
        return rng.uniform(0.05, 0.35)
    if distribution == InstanceDistribution.UNIFORM_MIXED:
        return rng.uniform(0.1, 0.85)
    if distribution == InstanceDistribution.HEAVY_TAIL:
        if rng.random() < 0.72:
            return rng.uniform(0.04, 0.28)
        return rng.uniform(0.55, 0.92)
    if distribution == InstanceDistribution.TINY_PLUS_LARGE:
        large_cutoff = max(1, item_count // 5)
        if index < large_cutoff:
            return rng.uniform(0.62, 0.9)
        return rng.uniform(0.03, 0.18)
    if distribution == InstanceDistribution.ADVERSARIAL:
        pattern = (0.51, 0.49, 0.52, 0.48, 0.34, 0.33, 0.33)
        jitter = rng.uniform(-0.005, 0.005)
        return min(0.95, max(0.02, pattern[index % len(pattern)] + jitter))
    if distribution == InstanceDistribution.HELD_OUT:
        if index % 4 == 0:
            return rng.uniform(0.45, 0.58)
        if index % 4 == 1:
            return rng.uniform(0.22, 0.32)
        if index % 4 == 2:
            return rng.uniform(0.12, 0.22)
        return rng.uniform(0.58, 0.78)
    raise ValueError(f"unknown distribution: {distribution}")


def _validate_items(items: Sequence[float], capacity: float) -> None:
    for item in items:
        if item <= 0:
            raise ValueError("item sizes must be positive")
        if item > capacity:
            raise ValueError("item sizes must not exceed capacity")
