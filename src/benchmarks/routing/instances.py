from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Iterable, List, Optional, Sequence, Tuple

InstanceSuites = Tuple[
    List["RoutingInstance"],
    List["RoutingInstance"],
    List["RoutingInstance"],
]


class RoutingDistribution(str, Enum):
    UNIFORM = "uniform"
    CLUSTERED = "clustered"
    LINE = "line"
    HELD_OUT = "held_out"
    EXTERNAL = "external"


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Stop:
    stop_id: str
    x: float
    y: float
    ready_time: float = 0.0
    due_time: float = 1_000_000.0
    service_time: float = 0.0
    demand: float = 0.0


@dataclass(frozen=True)
class RoutingInstance:
    distribution: RoutingDistribution
    seed: int
    depot: Point
    stops: Tuple[Stop, ...]
    distance_matrix: Tuple[Tuple[float, ...], ...]
    instance_id: Optional[str] = None
    source: Optional[str] = None
    vehicle_capacity: Optional[float] = None


def generate_routing_instance(
    distribution: RoutingDistribution,
    *,
    seed: int,
    stop_count: int = 20,
    time_windows: bool = False,
) -> RoutingInstance:
    if stop_count < 1:
        raise ValueError("stop_count must be positive")

    rng = Random(seed)
    depot = Point(0.5, 0.5)
    stops = tuple(
        _build_stop(distribution, rng, index, stop_count, time_windows)
        for index in range(stop_count)
    )
    return RoutingInstance(
        distribution=distribution,
        seed=seed,
        depot=depot,
        stops=stops,
        distance_matrix=_build_distance_matrix(depot, stops),
    )


def generate_routing_suite(
    *,
    distributions: Iterable[RoutingDistribution],
    sizes: Iterable[int],
    seeds: Iterable[int],
    time_windows: bool = False,
) -> List[RoutingInstance]:
    return [
        generate_routing_instance(
            distribution,
            seed=seed,
            stop_count=size,
            time_windows=time_windows,
        )
        for distribution in distributions
        for size in sizes
        for seed in seeds
    ]


def default_train_validation_test_suites(
    *,
    train_sizes: Sequence[int] = (8,),
    validation_sizes: Sequence[int] = (10,),
    test_sizes: Sequence[int] = (12,),
    seeds: Sequence[int] = (1, 2),
    time_windows: bool = True,
) -> InstanceSuites:
    train_distributions = (
        RoutingDistribution.UNIFORM,
        RoutingDistribution.CLUSTERED,
        RoutingDistribution.LINE,
    )
    test_distributions = train_distributions + (RoutingDistribution.HELD_OUT,)
    return (
        generate_routing_suite(
            distributions=train_distributions,
            sizes=train_sizes,
            seeds=seeds,
            time_windows=time_windows,
        ),
        generate_routing_suite(
            distributions=train_distributions,
            sizes=validation_sizes,
            seeds=[seed + 100 for seed in seeds],
            time_windows=time_windows,
        ),
        generate_routing_suite(
            distributions=test_distributions,
            sizes=test_sizes,
            seeds=[seed + 200 for seed in seeds],
            time_windows=time_windows,
        ),
    )


def _build_stop(
    distribution: RoutingDistribution,
    rng: Random,
    index: int,
    stop_count: int,
    time_windows: bool,
) -> Stop:
    point = _generate_point(distribution, rng, index, stop_count)
    if time_windows:
        ready_time = round(index * 0.08 + rng.uniform(0.0, 0.18), 6)
        due_time = round(ready_time + rng.uniform(1.2, 2.4), 6)
        service_time = round(rng.uniform(0.01, 0.04), 6)
    else:
        ready_time = 0.0
        due_time = 1_000_000.0
        service_time = 0.0
    return Stop(
        stop_id=f"s{index:03d}",
        x=point.x,
        y=point.y,
        ready_time=ready_time,
        due_time=due_time,
        service_time=service_time,
    )


def _generate_point(
    distribution: RoutingDistribution,
    rng: Random,
    index: int,
    stop_count: int,
) -> Point:
    if distribution == RoutingDistribution.UNIFORM:
        return _point(rng.uniform(0.05, 0.95), rng.uniform(0.05, 0.95))
    if distribution == RoutingDistribution.CLUSTERED:
        centers = ((0.25, 0.25), (0.72, 0.35), (0.42, 0.78))
        center_x, center_y = centers[index % len(centers)]
        return _point(
            _clamp(rng.gauss(center_x, 0.08)),
            _clamp(rng.gauss(center_y, 0.08)),
        )
    if distribution == RoutingDistribution.LINE:
        position = (index + 1) / (stop_count + 1)
        return _point(
            0.08 + 0.84 * position + rng.uniform(-0.025, 0.025),
            0.18 + 0.64 * position + rng.uniform(-0.04, 0.04),
        )
    if distribution == RoutingDistribution.HELD_OUT:
        angle = 2.0 * math.pi * index / stop_count + rng.uniform(-0.06, 0.06)
        radius = rng.uniform(0.28, 0.45)
        return _point(
            0.5 + radius * math.cos(angle),
            0.5 + radius * math.sin(angle),
        )
    raise ValueError(f"unknown routing distribution: {distribution}")


def _build_distance_matrix(
    depot: Point, stops: Sequence[Stop]
) -> Tuple[Tuple[float, ...], ...]:
    points = (depot,) + tuple(Point(stop.x, stop.y) for stop in stops)
    rows = []
    for first in points:
        row = []
        for second in points:
            row.append(round(math.dist((first.x, first.y), (second.x, second.y)), 6))
        rows.append(tuple(row))
    return tuple(rows)


def _point(x: float, y: float) -> Point:
    return Point(round(_clamp(x), 6), round(_clamp(y), 6))


def _clamp(value: float) -> float:
    return min(0.98, max(0.02, value))
