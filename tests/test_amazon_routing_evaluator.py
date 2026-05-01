from __future__ import annotations

import json
import math

import pytest

from benchmarks.amazon_routing.baselines import (
    AMAZON_BASELINE_ROUTE_BUILDERS,
    cheapest_insertion,
    driver_aware_heuristic,
    nearest_neighbor,
    route_metrics,
    route_time_window_violation,
    route_travel_time,
    two_opt_baseline,
    validate_route,
)
from benchmarks.amazon_routing.evaluator import (
    AmazonRoutingEvaluator,
    build_phase5_report,
    build_seed_amazon_programs,
    evaluate_amazon_candidate_suite,
)
from benchmarks.amazon_routing.features import (
    extract_route_features,
    extract_stop_features,
)
from benchmarks.amazon_routing.loader import (
    load_route_record,
    load_route_records,
    load_route_records_from_json,
)
from benchmarks.amazon_routing.route_similarity import (
    kendall_tau_distance,
    pairwise_precedence_accuracy,
    route_compactness,
    zone_transition_similarity,
)


def _route_payload(route_id: str = "route-a") -> dict[str, object]:
    return {
        "route_id": route_id,
        "station_code": "DLA9",
        "quality_label": "High",
        "depot": {
            "stop_id": "depot",
            "zone_id": "DEPOT",
            "x": 0.0,
            "y": 0.0,
        },
        "stops": [
            {
                "stop_id": "S1",
                "zone_id": "A",
                "x": 1.0,
                "y": 0.0,
                "service_time": 1.0,
                "time_window": [0.0, 20.0],
                "packages": [{"package_id": "p1", "weight": 2.0}],
            },
            {
                "stop_id": "S2",
                "zone_id": "A",
                "x": 2.0,
                "y": 0.0,
                "service_time": 1.5,
                "time_window": [0.0, 12.0],
                "packages": [
                    {"package_id": "p2", "weight": 1.0},
                    {"package_id": "p3", "weight": 3.0},
                ],
            },
            {
                "stop_id": "S3",
                "zone_id": "B",
                "x": 0.0,
                "y": 1.0,
                "service_time": 1.0,
                "time_window": [4.0, 30.0],
                "packages": [{"package_id": "p4", "weight": 1.5}],
            },
            {
                "stop_id": "S4",
                "zone_id": "B",
                "x": 0.0,
                "y": 2.0,
                "service_time": 2.0,
                "time_window": [5.0, 35.0],
                "packages": [{"package_id": "p5", "weight": 2.5}],
            },
        ],
        "actual_sequence": ["S1", "S2", "S3", "S4"],
        "travel_times": {
            "depot": {"depot": 0.0, "S1": 2.0, "S2": 3.0, "S3": 4.0, "S4": 5.0},
            "S1": {"depot": 2.0, "S1": 0.0, "S2": 1.0, "S3": 4.0, "S4": 5.0},
            "S2": {"depot": 3.0, "S1": 1.0, "S2": 0.0, "S3": 3.0, "S4": 4.0},
            "S3": {"depot": 4.0, "S1": 4.0, "S2": 3.0, "S3": 0.0, "S4": 1.0},
            "S4": {"depot": 5.0, "S1": 5.0, "S2": 4.0, "S3": 1.0, "S4": 0.0},
        },
    }


def test_route_loader_preserves_amazon_route_concepts_and_json_round_trip(
    tmp_path,
) -> None:
    route = load_route_record(_route_payload())

    assert route.route_id == "route-a"
    assert route.station_code == "DLA9"
    assert route.quality_label == "High"
    assert route.depot.stop_id == "depot"
    assert tuple(stop.stop_id for stop in route.stops) == ("S1", "S2", "S3", "S4")
    assert tuple(stop.zone_id for stop in route.stops) == ("A", "A", "B", "B")
    assert route.actual_sequence == ("S1", "S2", "S3", "S4")
    assert route.travel_time("S1", "S2") == 1.0
    assert route.travel_time("S4", "depot") == 5.0
    assert sum(len(stop.packages) for stop in route.stops) == 5

    records = load_route_records([_route_payload("route-a"), _route_payload("route-b")])
    assert [record.route_id for record in records] == ["route-a", "route-b"]

    json_path = tmp_path / "routes.json"
    json_path.write_text(json.dumps({"routes": [_route_payload("route-json")]}))
    from_json = load_route_records_from_json(json_path)
    assert [record.route_id for record in from_json] == ["route-json"]


def test_route_loader_rejects_duplicate_stops_and_bad_travel_time_matrix() -> None:
    duplicate = _route_payload()
    duplicate["stops"] = duplicate["stops"] + [duplicate["stops"][0]]  # type: ignore[operator]

    with pytest.raises(ValueError, match="duplicate_stop_id"):
        load_route_record(duplicate)

    missing_row = _route_payload()
    travel_times = dict(missing_row["travel_times"])  # type: ignore[arg-type]
    travel_times.pop("S4")
    missing_row["travel_times"] = travel_times

    with pytest.raises(ValueError, match="missing_travel_time_row"):
        load_route_record(missing_row)


def test_feature_extraction_exposes_route_stop_and_package_concepts() -> None:
    route = load_route_record(_route_payload())

    route_features = extract_route_features(route)
    assert route_features["stop_count"] == 4
    assert route_features["package_count"] == 5
    assert route_features["zone_count"] == 2
    assert route_features["quality_label"] == "High"

    stop_features = extract_stop_features(
        route,
        candidate_stop_id="S2",
        current_stop_id="S1",
        elapsed_time=4.0,
        visited=("S1",),
    )
    assert stop_features["stop_id"] == "S2"
    assert stop_features["zone_id"] == "A"
    assert stop_features["travel_time"] == 1.0
    assert stop_features["same_zone"] == 1.0
    assert stop_features["package_count"] == 2
    assert stop_features["package_weight"] == 4.0
    assert stop_features["service_time"] == 1.5
    assert stop_features["distance_to_depot"] == 3.0
    assert stop_features["time_window_slack"] == 7.0
    assert stop_features["historical_position"] == 1
    assert stop_features["remaining_count"] == 3


def test_route_similarity_metrics_are_deterministic() -> None:
    route = load_route_record(_route_payload())
    actual = ("S1", "S2", "S3", "S4")
    swapped = ("S2", "S1", "S3", "S4")
    reversed_route = tuple(reversed(actual))

    assert pairwise_precedence_accuracy(route, actual) == 1.0
    assert pairwise_precedence_accuracy(route, reversed_route) == 0.0
    assert math.isclose(pairwise_precedence_accuracy(route, swapped), 5 / 6)
    assert kendall_tau_distance(route, actual) == 0.0
    assert kendall_tau_distance(route, reversed_route) == 1.0
    assert math.isclose(kendall_tau_distance(route, swapped), 1 / 6)
    assert zone_transition_similarity(route, actual) == 1.0
    assert zone_transition_similarity(route, swapped) == 1.0
    assert zone_transition_similarity(route, reversed_route) == 0.0
    assert route_compactness(route, actual) > route_compactness(
        route, ("S1", "S3", "S2", "S4")
    )


def test_amazon_baselines_are_reproducible_and_metric_complete() -> None:
    route = load_route_record(_route_payload())
    expected = {
        "nearest_neighbor",
        "cheapest_insertion",
        "two_opt",
        "driver_aware",
        "ml_next_stop_ranker",
        "hybrid_ml_plus_local_search",
    }

    assert set(AMAZON_BASELINE_ROUTE_BUILDERS) == expected
    for name, builder in AMAZON_BASELINE_ROUTE_BUILDERS.items():
        first = builder(route)
        second = builder(route)

        assert first.algorithm == name
        assert first.sequence == second.sequence
        assert first.is_valid
        assert first.metrics["travel_time"] > 0
        assert first.metrics["time_window_violation"] >= 0
        assert 0 <= first.metrics["driver_likeness"] <= 1
        assert 0 <= first.metrics["zone_transition_similarity"] <= 1
        assert 0 <= first.metrics["route_compactness"] <= 1
        assert first.metrics["runtime"] >= 0


def test_core_baselines_and_metric_helpers_are_consistent() -> None:
    route = load_route_record(_route_payload())
    nearest = nearest_neighbor(route)
    insertion = cheapest_insertion(route)
    two_opt = two_opt_baseline(route)
    driver = driver_aware_heuristic(route)

    assert validate_route(route, nearest.sequence).ok is True
    assert route_travel_time(route, nearest.sequence) == nearest.metrics["travel_time"]
    assert (
        route_time_window_violation(route, nearest.sequence)
        == nearest.metrics["time_window_violation"]
    )
    assert insertion.is_valid
    assert two_opt.metrics["travel_time"] <= nearest.metrics["travel_time"]
    assert driver.sequence == route.actual_sequence
    assert driver.metrics["driver_likeness"] == 1.0

    metrics = route_metrics(route, ("S2", "S1", "S3", "S4"))
    assert math.isclose(metrics["driver_likeness"], 5 / 6)
    assert math.isclose(metrics["kendall_tau_distance"], 1 / 6)


def test_amazon_score_next_stop_evaluator_runs_valid_program() -> None:
    code = """
def score_next_stop(state, candidate_stop):
    same_zone_bonus = -2.0 * candidate_stop["same_zone"]
    return candidate_stop["travel_time"] + same_zone_bonus
"""
    route = load_route_record(_route_payload())
    result = AmazonRoutingEvaluator().evaluate_program(
        code,
        [route],
        program_id="same-zone",
    )

    assert result.program_id == "same-zone"
    assert result.ok is True
    assert result.failure_reason is None
    assert result.metrics["route_validity"] == 1
    assert result.metrics["average_travel_time"] > 0
    assert result.metrics["failure_rate"] == 0
    assert result.metrics["average_driver_likeness"] >= 0


def test_amazon_score_next_stop_evaluator_rejects_unsafe_program() -> None:
    route = load_route_record(_route_payload())
    result = AmazonRoutingEvaluator().evaluate_program(
        "def score_next_stop(state, candidate_stop):\n"
        "    return open('hidden_labels.json').read()\n",
        [route],
        program_id="unsafe",
    )

    assert result.ok is False
    assert result.failure_reason is not None
    assert "dangerous_call" in result.failure_reason
    assert result.metrics["failure_rate"] == 1


def test_amazon_candidate_suite_and_phase5_report_are_rerunnable() -> None:
    train = [load_route_record(_route_payload("train"))]
    validation = [load_route_record(_route_payload("validation"))]
    test = [load_route_record(_route_payload("test"))]
    candidates = build_seed_amazon_programs(8)

    summary = evaluate_amazon_candidate_suite(
        candidates=candidates,
        train_routes=train,
        validation_routes=validation,
        test_routes=test,
    )

    assert summary.candidate_count == 8
    assert summary.best_program_id
    assert summary.test_score is not None
    assert "driver_aware" in summary.baseline_scores
    assert "dangerous_call" in summary.failure_taxonomy
    assert summary.top_programs[0]["explanation"]

    report = build_phase5_report(candidate_count=8)
    top = report["top_programs"][0]
    rerun = AmazonRoutingEvaluator().evaluate_program(
        top["code"],
        report["splits"]["test_routes"],
        program_id=top["program_id"],
        apply_local_search=True,
    )

    assert report["candidate_count"] == 8
    assert report["held_out"]["route_count"] > 0
    assert report["held_out"]["score"] == report["test_score"]
    assert "nearest_neighbor" in report["baseline_scores"]
    assert "driver_aware" in report["baseline_scores"]
    assert "def score_next_stop" in top["code"]
    assert rerun.ok is True
    assert math.isclose(rerun.score or 0, report["test_score"])
