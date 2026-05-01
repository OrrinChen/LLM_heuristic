from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
    default_phase6_train_validation_test_routes,
)
from benchmarks.amazon_routing.evaluator import AmazonRoutingEvaluator
from benchmarks.amazon_routing.loader import AmazonRoute, load_route_record
from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    ProgramEvaluation,
    SeedCandidateProgram,
    build_seed_candidate_programs,
)
from benchmarks.bin_packing.instances import (
    InstanceDistribution,
    generate_suite,
)
from benchmarks.bin_packing.instances import (
    default_train_validation_test_suites as default_bin_packing_suites,
)
from benchmarks.routing.evaluator import (
    RoutingEvaluator,
    RoutingProgramEvaluation,
    SeedRoutingProgram,
    build_seed_routing_programs,
)
from benchmarks.routing.instances import (
    RoutingDistribution,
    generate_routing_suite,
)
from benchmarks.routing.instances import (
    default_train_validation_test_suites as default_routing_suites,
)
from program_search.scoring import compute_program_complexity

PHASE7_TESTING_DIMENSIONS = (
    "held_out_random_seeds",
    "held_out_item_size_distributions",
    "held_out_routing_instance_sizes",
    "held_out_amazon_city_slices",
    "small_routes_vs_large_routes",
    "dense_urban_vs_sparse_suburban_routes",
    "high_quality_vs_medium_quality_routes",
)

PHASE7_REPORTING_FIELDS = (
    "train_score",
    "validation_score",
    "test_score",
    "runtime",
    "failure_rate",
    "program_complexity",
    "generalization_gap",
)


@dataclass(frozen=True)
class RobustProgram:
    benchmark: str
    program_id: str
    code: str
    complexity: int
    train_score: float
    validation_score: float
    test_score: float
    runtime: float
    failure_rate: float
    failure_taxonomy: Mapping[str, int]
    evaluator: object

    @property
    def generalization_gap(self) -> float:
        return abs(self.validation_score - self.test_score)

    def as_summary(self) -> Mapping[str, object]:
        return {
            "program_id": self.program_id,
            "train_score": self.train_score,
            "validation_score": self.validation_score,
            "test_score": self.test_score,
            "runtime": self.runtime,
            "failure_rate": self.failure_rate,
            "program_complexity": self.complexity,
            "generalization_gap": self.generalization_gap,
        }


def build_phase7_report() -> Dict[str, object]:
    bin_program = _build_bin_packing_program()
    routing_program = _build_routing_program()
    amazon_program = _build_amazon_program()

    slice_rows = (
        _bin_packing_slice_rows(bin_program)
        + _routing_slice_rows(routing_program)
        + _amazon_slice_rows(amazon_program)
    )
    failure_taxonomy = Counter()
    for program in (bin_program, routing_program, amazon_program):
        failure_taxonomy.update(program.failure_taxonomy)

    return {
        "phase": 7,
        "benchmark_count": 3,
        "testing_dimensions": PHASE7_TESTING_DIMENSIONS,
        "required_reporting_fields": PHASE7_REPORTING_FIELDS,
        "benchmarks": {
            "bin_packing": dict(bin_program.as_summary()),
            "simple_routing": dict(routing_program.as_summary()),
            "amazon_routing": dict(amazon_program.as_summary()),
        },
        "slice_summary": slice_rows,
        "worst_generalization_gaps": _worst_gaps(slice_rows),
        "failure_taxonomy": dict(sorted(failure_taxonomy.items())),
        "known_limitations": (
            "Amazon city, density, and quality slices are deterministic "
            "Amazon-shaped fixtures until external public or user-provided data is "
            "configured.",
            "Runtime values are local smoke metrics and should not be compared "
            "across machines.",
        ),
    }


def _build_bin_packing_program() -> RobustProgram:
    train, validation, test = default_bin_packing_suites(item_count=25)
    evaluator = BinPackingEvaluator()
    candidates = build_seed_candidate_programs(16)
    validation_results = [
        evaluator.evaluate_program(
            candidate.code,
            validation,
            program_id=candidate.program_id,
        )
        for candidate in candidates
    ]
    successful = [result for result in validation_results if result.score is not None]
    if not successful:
        raise ValueError("no successful bin-packing robustness candidates")
    best = min(
        successful,
        key=lambda result: (result.score or float("inf"), result.program_id),
    )
    candidate = _bin_candidate(candidates, best.program_id)
    train_result = evaluator.evaluate_program(
        candidate.code,
        train,
        program_id=candidate.program_id,
    )
    validation_result = evaluator.evaluate_program(
        candidate.code,
        validation,
        program_id=candidate.program_id,
    )
    test_result = evaluator.evaluate_program(
        candidate.code,
        test,
        program_id=candidate.program_id,
    )
    return RobustProgram(
        benchmark="bin_packing",
        program_id=candidate.program_id,
        code=candidate.code,
        complexity=compute_program_complexity(candidate.code),
        train_score=_score(train_result),
        validation_score=_score(validation_result),
        test_score=_score(test_result),
        runtime=_runtime(train_result, validation_result, test_result),
        failure_rate=_split_failure_rate(
            train_result,
            validation_result,
            test_result,
        ),
        failure_taxonomy=_failure_taxonomy(validation_results),
        evaluator=evaluator,
    )


def _build_routing_program() -> RobustProgram:
    train, validation, test = default_routing_suites(
        train_sizes=(8,),
        validation_sizes=(10,),
        test_sizes=(12,),
    )
    evaluator = RoutingEvaluator()
    candidates = build_seed_routing_programs(15)
    validation_results = [
        evaluator.evaluate_program(
            candidate.code,
            validation,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        for candidate in candidates
    ]
    successful = [result for result in validation_results if result.score is not None]
    if not successful:
        raise ValueError("no successful routing robustness candidates")
    best = min(
        successful,
        key=lambda result: (result.score or float("inf"), result.program_id),
    )
    candidate = _routing_candidate(candidates, best.program_id)
    train_result = evaluator.evaluate_program(
        candidate.code,
        train,
        program_id=candidate.program_id,
        apply_local_search=True,
    )
    validation_result = evaluator.evaluate_program(
        candidate.code,
        validation,
        program_id=candidate.program_id,
        apply_local_search=True,
    )
    test_result = evaluator.evaluate_program(
        candidate.code,
        test,
        program_id=candidate.program_id,
        apply_local_search=True,
    )
    return RobustProgram(
        benchmark="simple_routing",
        program_id=candidate.program_id,
        code=candidate.code,
        complexity=compute_program_complexity(candidate.code),
        train_score=_score(train_result),
        validation_score=_score(validation_result),
        test_score=_score(test_result),
        runtime=_runtime(train_result, validation_result, test_result),
        failure_rate=_split_failure_rate(
            train_result,
            validation_result,
            test_result,
        ),
        failure_taxonomy=_failure_taxonomy(validation_results),
        evaluator=evaluator,
    )


def _build_amazon_program() -> RobustProgram:
    train, validation, test = default_phase6_train_validation_test_routes()
    phase6 = build_phase6_report(
        config=AmazonDiscoveryConfig(
            generations=2,
            population_size=12,
            offspring_per_generation=8,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        )
    )
    top = phase6["top_candidates"][0]
    evaluator = AmazonRoutingEvaluator()
    train_result = evaluator.evaluate_program(
        top["code"],
        train,
        program_id=top["program_id"],
        apply_local_search=True,
    )
    validation_result = evaluator.evaluate_program(
        top["code"],
        validation,
        program_id=top["program_id"],
        apply_local_search=True,
    )
    test_result = evaluator.evaluate_program(
        top["code"],
        test,
        program_id=top["program_id"],
        apply_local_search=True,
    )
    return RobustProgram(
        benchmark="amazon_routing",
        program_id=str(top["program_id"]),
        code=str(top["code"]),
        complexity=compute_program_complexity(str(top["code"])),
        train_score=_score(train_result),
        validation_score=_score(validation_result),
        test_score=_score(test_result),
        runtime=_runtime(train_result, validation_result, test_result),
        failure_rate=_split_failure_rate(
            train_result,
            validation_result,
            test_result,
        ),
        failure_taxonomy=phase6["failure_taxonomy"],
        evaluator=evaluator,
    )


def _bin_packing_slice_rows(program: RobustProgram) -> List[Mapping[str, object]]:
    evaluator = _typed(program.evaluator, BinPackingEvaluator)
    slices = [
        (
            "bin-held-out-random-seeds",
            "held_out_random_seeds",
            generate_suite(
                distributions=[InstanceDistribution.UNIFORM_MIXED],
                seeds=[301, 302, 303],
                item_count=25,
            ),
            {"distribution": "uniform_mixed", "seeds": "301,302,303"},
        ),
        (
            "bin-held-out-item-distribution",
            "held_out_item_size_distributions",
            generate_suite(
                distributions=[InstanceDistribution.HELD_OUT],
                seeds=[401, 402],
                item_count=25,
            ),
            {"distribution": "held_out", "seeds": "401,402"},
        ),
    ]
    return [
        _slice_row(
            program,
            slice_name=name,
            dimension=dimension,
            result=evaluator.evaluate_program(
                program.code,
                instances,
                program_id=program.program_id,
            ),
            tags=tags,
        )
        for name, dimension, instances, tags in slices
    ]


def _routing_slice_rows(program: RobustProgram) -> List[Mapping[str, object]]:
    evaluator = _typed(program.evaluator, RoutingEvaluator)
    slices = [
        (
            "routing-held-out-random-seeds",
            "held_out_random_seeds",
            generate_routing_suite(
                distributions=[RoutingDistribution.UNIFORM],
                sizes=[10],
                seeds=[501, 502],
                time_windows=True,
            ),
            {"distribution": "uniform", "stop_count": "10", "seeds": "501,502"},
        ),
        (
            "routing-held-out-size-14",
            "held_out_routing_instance_sizes",
            generate_routing_suite(
                distributions=[RoutingDistribution.UNIFORM],
                sizes=[14],
                seeds=[601, 602],
                time_windows=True,
            ),
            {"distribution": "uniform", "stop_count": "14", "seeds": "601,602"},
        ),
        (
            "routing-small-routes",
            "small_routes_vs_large_routes",
            generate_routing_suite(
                distributions=[RoutingDistribution.CLUSTERED],
                sizes=[6],
                seeds=[701, 702],
                time_windows=True,
            ),
            {"distribution": "clustered", "stop_count": "6", "route_size": "small"},
        ),
        (
            "routing-large-routes",
            "small_routes_vs_large_routes",
            generate_routing_suite(
                distributions=[RoutingDistribution.CLUSTERED],
                sizes=[18],
                seeds=[703, 704],
                time_windows=True,
            ),
            {"distribution": "clustered", "stop_count": "18", "route_size": "large"},
        ),
        (
            "routing-dense-urban",
            "dense_urban_vs_sparse_suburban_routes",
            generate_routing_suite(
                distributions=[RoutingDistribution.CLUSTERED],
                sizes=[12],
                seeds=[801, 802],
                time_windows=True,
            ),
            {"distribution": "clustered", "density": "dense_urban"},
        ),
        (
            "routing-sparse-suburban",
            "dense_urban_vs_sparse_suburban_routes",
            generate_routing_suite(
                distributions=[RoutingDistribution.HELD_OUT],
                sizes=[12],
                seeds=[803, 804],
                time_windows=True,
            ),
            {"distribution": "held_out", "density": "sparse_suburban"},
        ),
    ]
    return [
        _slice_row(
            program,
            slice_name=name,
            dimension=dimension,
            result=evaluator.evaluate_program(
                program.code,
                instances,
                program_id=program.program_id,
                apply_local_search=True,
            ),
            tags=tags,
        )
        for name, dimension, instances, tags in slices
    ]


def _amazon_slice_rows(program: RobustProgram) -> List[Mapping[str, object]]:
    evaluator = _typed(program.evaluator, AmazonRoutingEvaluator)
    slices = [
        (
            "amazon-held-out-city-dch1",
            "held_out_amazon_city_slices",
            (
                _amazon_route(
                    "city-dch1-high-dense",
                    station_code="DCH1",
                    quality_label="High",
                    density="dense_urban",
                    stop_count=5,
                ),
            ),
            {
                "station_code": "DCH1",
                "quality_label": "High",
                "density": "dense_urban",
            },
        ),
        (
            "amazon-small-routes",
            "small_routes_vs_large_routes",
            (
                _amazon_route(
                    "small-dla9-high-dense",
                    station_code="DLA9",
                    quality_label="High",
                    density="dense_urban",
                    stop_count=4,
                ),
            ),
            {
                "station_code": "DLA9",
                "quality_label": "High",
                "route_size": "small",
                "stop_count": "4",
            },
        ),
        (
            "amazon-large-routes",
            "small_routes_vs_large_routes",
            (
                _amazon_route(
                    "large-dse8-medium-sparse",
                    station_code="DSE8",
                    quality_label="Medium",
                    density="sparse_suburban",
                    stop_count=7,
                ),
            ),
            {
                "station_code": "DSE8",
                "quality_label": "Medium",
                "route_size": "large",
                "stop_count": "7",
            },
        ),
        (
            "amazon-dense-urban",
            "dense_urban_vs_sparse_suburban_routes",
            (
                _amazon_route(
                    "dense-dla9-high",
                    station_code="DLA9",
                    quality_label="High",
                    density="dense_urban",
                    stop_count=5,
                ),
            ),
            {
                "station_code": "DLA9",
                "quality_label": "High",
                "density": "dense_urban",
            },
        ),
        (
            "amazon-sparse-suburban",
            "dense_urban_vs_sparse_suburban_routes",
            (
                _amazon_route(
                    "sparse-dch1-medium",
                    station_code="DCH1",
                    quality_label="Medium",
                    density="sparse_suburban",
                    stop_count=5,
                ),
            ),
            {
                "station_code": "DCH1",
                "quality_label": "Medium",
                "density": "sparse_suburban",
            },
        ),
        (
            "amazon-high-quality",
            "high_quality_vs_medium_quality_routes",
            (
                _amazon_route(
                    "quality-high",
                    station_code="DLA9",
                    quality_label="High",
                    density="dense_urban",
                    stop_count=5,
                ),
            ),
            {"station_code": "DLA9", "quality_label": "High"},
        ),
        (
            "amazon-medium-quality",
            "high_quality_vs_medium_quality_routes",
            (
                _amazon_route(
                    "quality-medium",
                    station_code="DCH1",
                    quality_label="Medium",
                    density="sparse_suburban",
                    stop_count=5,
                ),
            ),
            {"station_code": "DCH1", "quality_label": "Medium"},
        ),
    ]
    return [
        _slice_row(
            program,
            slice_name=name,
            dimension=dimension,
            result=evaluator.evaluate_program(
                program.code,
                routes,
                program_id=program.program_id,
                apply_local_search=True,
            ),
            tags=tags,
        )
        for name, dimension, routes, tags in slices
    ]


def _slice_row(
    program: RobustProgram,
    *,
    slice_name: str,
    dimension: str,
    result: ProgramEvaluation | RoutingProgramEvaluation | object,
    tags: Mapping[str, str],
) -> Mapping[str, object]:
    score = _score(result)
    failure_rate = float(result.metrics.get("failure_rate", 0.0))  # type: ignore[attr-defined]
    return {
        "benchmark": program.benchmark,
        "program_id": program.program_id,
        "slice_name": slice_name,
        "dimension": dimension,
        "train_score": program.train_score,
        "validation_score": program.validation_score,
        "test_score": score,
        "runtime": round(float(result.runtime), 6),  # type: ignore[attr-defined]
        "failure_rate": failure_rate,
        "program_complexity": program.complexity,
        "generalization_gap": abs(program.validation_score - score),
        "tags": dict(tags),
    }


def _amazon_route(
    route_id: str,
    *,
    station_code: str,
    quality_label: str,
    density: str,
    stop_count: int,
) -> AmazonRoute:
    if stop_count < 2:
        raise ValueError("stop_count must be at least 2")
    stops = []
    coordinates = {"depot": (0.0, 0.0)}
    for index in range(stop_count):
        stop_id = f"S{index + 1}"
        zone_id = chr(ord("A") + (index // max(1, stop_count // 3)))
        if density == "dense_urban":
            x = 0.8 + 0.28 * (index % 3) + 0.08 * (index // 3)
            y = 0.7 + 0.22 * (index // 3)
        elif density == "sparse_suburban":
            x = 1.2 + 1.35 * index
            y = 0.6 + (index % 2) * 1.45
        else:
            raise ValueError(f"unknown density: {density}")
        coordinates[stop_id] = (x, y)
        stops.append(
            {
                "stop_id": stop_id,
                "zone_id": zone_id,
                "x": x,
                "y": y,
                "service_time": 0.8 + 0.1 * (index % 3),
                "time_window": [0.0, 80.0 + index],
                "packages": [
                    {
                        "package_id": f"{route_id}-{stop_id}-p{package_index}",
                        "weight": 1.0,
                    }
                    for package_index in range(1 + index % 2)
                ],
            }
        )
    location_ids = ("depot",) + tuple(stop["stop_id"] for stop in stops)
    return load_route_record(
        {
            "route_id": route_id,
            "station_code": station_code,
            "quality_label": quality_label,
            "depot": {
                "stop_id": "depot",
                "zone_id": "DEPOT",
                "x": 0.0,
                "y": 0.0,
            },
            "stops": stops,
            "actual_sequence": [stop["stop_id"] for stop in stops],
            "travel_times": _travel_time_matrix(location_ids, coordinates),
        }
    )


def _travel_time_matrix(
    location_ids: Sequence[str],
    coordinates: Mapping[str, Tuple[float, float]],
) -> Mapping[str, Mapping[str, float]]:
    matrix = {}
    for from_id in location_ids:
        row = {}
        for to_id in location_ids:
            if from_id == to_id:
                row[to_id] = 0.0
            else:
                row[to_id] = round(
                    math.dist(coordinates[from_id], coordinates[to_id]),
                    6,
                )
        matrix[from_id] = row
    return matrix


def _worst_gaps(rows: Sequence[Mapping[str, object]]) -> List[Mapping[str, object]]:
    return [
        {
            "benchmark": row["benchmark"],
            "program_id": row["program_id"],
            "slice_name": row["slice_name"],
            "dimension": row["dimension"],
            "test_score": row["test_score"],
            "generalization_gap": row["generalization_gap"],
        }
        for row in sorted(
            rows,
            key=lambda item: (
                -float(item["generalization_gap"]),
                str(item["benchmark"]),
                str(item["slice_name"]),
            ),
        )[:5]
    ]


def _bin_candidate(
    candidates: Sequence[SeedCandidateProgram],
    program_id: str,
) -> SeedCandidateProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _routing_candidate(
    candidates: Sequence[SeedRoutingProgram],
    program_id: str,
) -> SeedRoutingProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _score(result: object) -> float:
    score = result.score
    if score is None:
        return 10_000.0
    return float(score)


def _runtime(*results: object) -> float:
    return round(sum(float(result.runtime) for result in results), 6)


def _split_failure_rate(*results: object) -> float:
    rates = [float(result.metrics.get("failure_rate", 0.0)) for result in results]
    if not rates:
        return 0.0
    return sum(rates) / len(rates)


def _failure_taxonomy(results: Sequence[object]) -> Mapping[str, int]:
    taxonomy: Counter[str] = Counter()
    for result in results:
        reason: Optional[str] = result.failure_reason
        if reason:
            taxonomy[reason.split(":", 1)[0]] += 1
    return dict(sorted(taxonomy.items()))


def _typed(value: object, expected_type: type[object]) -> object:
    if not isinstance(value, expected_type):
        raise TypeError(f"expected {expected_type.__name__}")
    return value
