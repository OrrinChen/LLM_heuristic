from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

from benchmarks.routing.baselines import BASELINE_ROUTE_BUILDERS, RoutingResult
from benchmarks.routing.evaluator import (
    RoutingEvaluator,
    SeedRoutingProgram,
    build_seed_routing_programs,
    evaluate_routing_candidate_suite,
)
from benchmarks.routing.instances import (
    Point,
    RoutingDistribution,
    RoutingInstance,
    Stop,
    default_train_validation_test_suites,
)

ExternalRoutingSuites = Tuple[
    List[RoutingInstance],
    List[RoutingInstance],
    List[RoutingInstance],
]

PHASE10_CLAIM_BOUNDARY = (
    "external routing-style evidence only; no LKH, CVRP, Amazon, SOTA, or "
    "universal dominance claim"
)

_DEFAULT_TSPLIB_FIXTURES = (
    """
NAME: tsp_train_a
TYPE: TSP
DIMENSION: 6
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0 0
2 2 0
3 4 1
4 4 4
5 1 5
6 0 3
EOF
""",
    """
NAME: tsp_train_b
TYPE: TSP
DIMENSION: 7
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 1 1
2 2 4
3 5 5
4 7 2
5 6 -1
6 3 -2
7 0 -1
EOF
""",
    """
NAME: tsp_validation_a
TYPE: TSP
DIMENSION: 6
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0 0
2 1 3
3 3 5
4 6 4
5 7 1
6 3 -1
EOF
""",
    """
NAME: tsp_validation_b
TYPE: TSP
DIMENSION: 7
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0 0
2 2 1
3 5 1
4 7 3
5 5 6
6 2 7
7 -1 4
EOF
""",
    """
NAME: tsp_test_a
TYPE: TSP
DIMENSION: 8
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0 0
2 1 2
3 3 3
4 6 2
5 7 5
6 5 8
7 2 7
8 -1 4
EOF
""",
    """
NAME: tsp_test_b
TYPE: TSP
DIMENSION: 8
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0 0
2 3 -1
3 6 0
4 8 3
5 7 6
6 4 8
7 1 6
8 -2 3
EOF
""",
)


def parse_tsplib_tsp(
    text: str,
    *,
    source: str = "tsplib",
) -> List[RoutingInstance]:
    lines = _meaningful_lines(text)
    if not lines:
        raise ValueError("TSPLIB text is empty")

    name = source
    dimension: Optional[int] = None
    edge_weight_type = "EUC_2D"
    coordinates: List[Tuple[str, float, float]] = []
    reading_coordinates = False
    for line in lines:
        upper = line.upper()
        if upper == "EOF":
            break
        if reading_coordinates:
            parts = line.split()
            if len(parts) < 3:
                raise ValueError("NODE_COORD_SECTION rows need id, x, and y")
            coordinates.append((parts[0], float(parts[1]), float(parts[2])))
            continue
        if upper == "NODE_COORD_SECTION":
            reading_coordinates = True
            continue
        key, value = _split_tsplib_key_value(line)
        if key == "NAME":
            name = value
        elif key == "DIMENSION":
            dimension = int(float(value))
        elif key == "EDGE_WEIGHT_TYPE":
            edge_weight_type = value.upper()

    if edge_weight_type != "EUC_2D":
        raise ValueError("only EUC_2D TSPLIB coordinates are supported")
    if dimension is None:
        raise ValueError("TSPLIB DIMENSION is required")
    if len(coordinates) != dimension:
        raise ValueError(
            f"{name} expected {dimension} coordinates, got {len(coordinates)}"
        )
    if dimension < 3:
        raise ValueError("TSPLIB fixture must have at least three nodes")
    return [_routing_instance_from_coordinates(name, source, coordinates)]


def load_external_routing_instances(
    path: Union[str, Path],
    *,
    parser: str = "tsplib",
) -> List[RoutingInstance]:
    data_path = Path(path)
    if parser != "tsplib":
        raise ValueError(f"unknown external routing parser: {parser}")
    if data_path.is_dir():
        instances: List[RoutingInstance] = []
        for child in sorted(data_path.iterdir()):
            if child.is_file() and child.suffix.lower() in {".tsp", ".txt"}:
                instances.extend(
                    parse_tsplib_tsp(
                        child.read_text(encoding="utf-8"),
                        source=child.name,
                    )
                )
        if not instances:
            raise ValueError("directory contains no TSPLIB .tsp or .txt files")
        return instances
    return parse_tsplib_tsp(
        data_path.read_text(encoding="utf-8"),
        source=data_path.name,
    )


def split_external_routing_instances(
    instances: Sequence[RoutingInstance],
) -> ExternalRoutingSuites:
    if len(instances) < 3:
        raise ValueError("at least three external routing instances are required")
    ordered = list(instances)
    train_end = max(1, len(ordered) // 3)
    validation_end = max(train_end + 1, (len(ordered) * 2) // 3)
    validation_end = min(validation_end, len(ordered) - 1)
    return (
        ordered[:train_end],
        ordered[train_end:validation_end],
        ordered[validation_end:],
    )


def default_external_routing_suites() -> ExternalRoutingSuites:
    instances: List[RoutingInstance] = []
    for index, fixture in enumerate(_DEFAULT_TSPLIB_FIXTURES):
        instances.extend(parse_tsplib_tsp(fixture, source=f"tsplib_fixture_{index}"))
    return split_external_routing_instances(instances)


def build_phase10_report(
    *,
    candidate_count: int = 16,
    synthetic_stop_count: int = 10,
    external_instances: Optional[Sequence[RoutingInstance]] = None,
) -> Dict[str, object]:
    if candidate_count < 1:
        raise ValueError("candidate_count must be positive")
    synthetic_train, synthetic_validation, synthetic_test = (
        default_train_validation_test_suites(
            train_sizes=(max(4, synthetic_stop_count - 2),),
            validation_sizes=(synthetic_stop_count,),
            test_sizes=(synthetic_stop_count + 2,),
            time_windows=True,
        )
    )
    if external_instances is None:
        external_train, external_validation, external_test = (
            default_external_routing_suites()
        )
    else:
        external_train, external_validation, external_test = (
            split_external_routing_instances(external_instances)
        )

    candidates = build_seed_routing_programs(candidate_count)
    synthetic_summary = evaluate_routing_candidate_suite(
        candidates=candidates,
        train_instances=synthetic_train,
        validation_instances=synthetic_validation,
        test_instances=synthetic_test,
    )
    external_summary = evaluate_routing_candidate_suite(
        candidates=candidates,
        train_instances=external_train,
        validation_instances=external_validation,
        test_instances=external_test,
    )
    evaluator = RoutingEvaluator()
    synthetic_top = _candidate_for(candidates, synthetic_summary.best_program_id)
    external_top = _candidate_for(candidates, external_summary.best_program_id)
    synthetic_top_external = evaluator.evaluate_program(
        synthetic_top.code,
        external_test,
        program_id=synthetic_top.program_id,
        apply_local_search=True,
    )
    external_top_validation = evaluator.evaluate_program(
        external_top.code,
        external_validation,
        program_id=external_top.program_id,
        apply_local_search=True,
    )
    external_top_test = evaluator.evaluate_program(
        external_top.code,
        external_test,
        program_id=external_top.program_id,
        apply_local_search=True,
    )
    return {
        "phase": 10,
        "benchmark": "routing_external",
        "source": "TSPLIB-style EUC_2D parser with small local fixtures",
        "candidate_count": candidate_count,
        "external_split": {
            "train_count": len(external_train),
            "validation_count": len(external_validation),
            "test_count": len(external_test),
            "train_ids": _instance_ids(external_train),
            "validation_ids": _instance_ids(external_validation),
            "test_ids": _instance_ids(external_test),
        },
        "synthetic_top_program_id": synthetic_top.program_id,
        "synthetic_top_validation_score": synthetic_summary.best_validation_score,
        "synthetic_top_external_test_score": synthetic_top_external.score,
        "best_external_program_id": external_top.program_id,
        "best_external_validation_score": external_top_validation.score,
        "best_external_test_score": external_top_test.score,
        "synthetic_to_external_gap": _gap(
            synthetic_summary.best_validation_score,
            synthetic_top_external.score,
        ),
        "external_generalization_gap": _gap(
            external_top_validation.score,
            external_top_test.score,
        ),
        "external_validation_baseline_scores": _baseline_scores(external_validation),
        "external_test_baseline_scores": _baseline_scores(external_test),
        "top_programs": external_summary.top_programs,
        "claim_boundary": PHASE10_CLAIM_BOUNDARY,
    }


def _routing_instance_from_coordinates(
    instance_id: str,
    source: str,
    coordinates: Sequence[Tuple[str, float, float]],
) -> RoutingInstance:
    depot_id, depot_x, depot_y = coordinates[0]
    depot = Point(float(depot_x), float(depot_y))
    stops = tuple(
        Stop(stop_id=f"n{int(float(node_id)):03d}", x=float(x), y=float(y))
        for node_id, x, y in coordinates[1:]
    )
    return RoutingInstance(
        distribution=RoutingDistribution.EXTERNAL,
        seed=_stable_seed(f"{source}:{instance_id}:{depot_id}"),
        depot=depot,
        stops=stops,
        distance_matrix=_build_distance_matrix(depot, stops),
        instance_id=instance_id,
        source=source,
    )


def _build_distance_matrix(
    depot: Point,
    stops: Sequence[Stop],
) -> Tuple[Tuple[float, ...], ...]:
    points = (depot,) + tuple(Point(stop.x, stop.y) for stop in stops)
    rows = []
    for first in points:
        row = []
        for second in points:
            row.append(round(math.dist((first.x, first.y), (second.x, second.y)), 6))
        rows.append(tuple(row))
    return tuple(rows)


def _baseline_scores(instances: Sequence[RoutingInstance]) -> Dict[str, float]:
    return {
        name: _mean(_route_score(result) for result in _build_all(builder, instances))
        for name, builder in BASELINE_ROUTE_BUILDERS.items()
    }


def _build_all(
    builder: Callable[[RoutingInstance], RoutingResult],
    instances: Sequence[RoutingInstance],
) -> List[RoutingResult]:
    return [builder(instance) for instance in instances]


def _route_score(result: RoutingResult) -> float:
    if not result.is_valid:
        return 10_000.0
    return result.total_distance + result.time_window_violation * 10.0


def _instance_ids(instances: Sequence[RoutingInstance]) -> Tuple[str, ...]:
    return tuple(str(instance.instance_id) for instance in instances)


def _candidate_for(
    candidates: Sequence[SeedRoutingProgram],
    program_id: str,
) -> SeedRoutingProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _gap(
    validation_score: Optional[float],
    test_score: Optional[float],
) -> Optional[float]:
    if validation_score is None or test_score is None:
        return None
    return test_score - validation_score


def _meaningful_lines(text: str) -> List[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _split_tsplib_key_value(line: str) -> Tuple[str, str]:
    if ":" in line:
        key, value = line.split(":", 1)
        return key.strip().upper(), value.strip()
    parts = line.split(maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip().upper(), parts[1].strip()
    return line.strip().upper(), ""


def _stable_seed(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _mean(values: Sequence[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
