from __future__ import annotations

import math

from benchmarks.routing.baselines import (
    BASELINE_ROUTE_BUILDERS,
    cheapest_insertion,
    nearest_neighbor,
    nearest_neighbor_plus_2opt,
    random_route,
    route_distance,
    route_time_window_violation,
    validate_route,
)
from benchmarks.routing.evaluator import (
    RoutingEvaluator,
    build_phase4_report,
    build_seed_routing_programs,
    evaluate_routing_candidate_suite,
)
from benchmarks.routing.instances import (
    RoutingDistribution,
    default_train_validation_test_suites,
    generate_routing_instance,
    generate_routing_suite,
)
from benchmarks.routing.local_search import two_opt


def test_routing_instance_generation_is_deterministic_and_symmetric() -> None:
    first = generate_routing_instance(
        RoutingDistribution.CLUSTERED, seed=17, stop_count=12, time_windows=True
    )
    second = generate_routing_instance(
        RoutingDistribution.CLUSTERED, seed=17, stop_count=12, time_windows=True
    )

    assert first == second
    assert len(first.stops) == 12
    assert len(first.distance_matrix) == 13
    assert all(len(row) == 13 for row in first.distance_matrix)
    for row_index, row in enumerate(first.distance_matrix):
        assert row[row_index] == 0
        for col_index, value in enumerate(row):
            assert math.isclose(value, first.distance_matrix[col_index][row_index])
    assert all(stop.ready_time <= stop.due_time for stop in first.stops)


def test_default_suites_hold_out_unseen_instance_sizes() -> None:
    train, validation, test = default_train_validation_test_suites(
        train_sizes=(8,),
        validation_sizes=(10,),
        test_sizes=(14,),
        seeds=(1, 2),
    )

    assert {len(instance.stops) for instance in train} == {8}
    assert {len(instance.stops) for instance in validation} == {10}
    assert {len(instance.stops) for instance in test} == {14}
    assert {instance.seed for instance in train} == {1, 2}
    assert {instance.seed for instance in validation} == {101, 102}
    assert {instance.seed for instance in test} == {201, 202}


def test_generate_routing_suite_covers_distributions_sizes_and_seeds() -> None:
    suite = generate_routing_suite(
        distributions=[RoutingDistribution.UNIFORM, RoutingDistribution.LINE],
        sizes=[6, 9],
        seeds=[3],
    )

    assert len(suite) == 4
    assert {
        (instance.distribution, len(instance.stops), instance.seed)
        for instance in suite
    } == {
        (RoutingDistribution.UNIFORM, 6, 3),
        (RoutingDistribution.UNIFORM, 9, 3),
        (RoutingDistribution.LINE, 6, 3),
        (RoutingDistribution.LINE, 9, 3),
    }


def test_route_validation_rejects_missing_duplicate_and_unknown_stops() -> None:
    instance = generate_routing_instance(
        RoutingDistribution.UNIFORM, seed=5, stop_count=5
    )
    valid_route = tuple(stop.stop_id for stop in instance.stops)

    assert validate_route(instance, valid_route).ok is True
    assert validate_route(instance, valid_route[:-1]).failure_reason == "missing_stops"
    assert (
        validate_route(instance, valid_route + (valid_route[0],)).failure_reason
        == "duplicate_stops"
    )
    assert (
        validate_route(instance, valid_route[:-1] + ("bad-stop",)).failure_reason
        == "unknown_stops"
    )


def test_baselines_are_available_deterministic_and_valid() -> None:
    expected = {
        "random",
        "nearest_neighbor",
        "cheapest_insertion",
        "two_opt",
        "nearest_neighbor_plus_2opt",
    }
    instance = generate_routing_instance(
        RoutingDistribution.CLUSTERED, seed=7, stop_count=11
    )

    assert set(BASELINE_ROUTE_BUILDERS) == expected
    for name, builder in BASELINE_ROUTE_BUILDERS.items():
        first = builder(instance)
        second = builder(instance)

        assert first.algorithm == name
        assert first.route == second.route
        assert first.is_valid
        assert first.total_distance > 0
        assert first.time_window_violation >= 0


def test_core_baselines_compute_valid_route_metrics() -> None:
    instance = generate_routing_instance(RoutingDistribution.LINE, seed=9, stop_count=8)

    random_result = random_route(instance)
    nearest_result = nearest_neighbor(instance)
    insertion_result = cheapest_insertion(instance)

    assert random_result.is_valid
    assert nearest_result.is_valid
    assert insertion_result.is_valid
    assert (
        route_distance(instance, nearest_result.route) == nearest_result.total_distance
    )
    assert (
        route_time_window_violation(instance, nearest_result.route)
        == nearest_result.time_window_violation
    )


def test_two_opt_and_nearest_neighbor_plus_2opt_do_not_worsen_routes() -> None:
    instance = generate_routing_instance(
        RoutingDistribution.UNIFORM, seed=13, stop_count=13
    )
    nearest_result = nearest_neighbor(instance)
    improved_route = two_opt(instance, nearest_result.route)
    improved_result = nearest_neighbor_plus_2opt(instance)

    assert validate_route(instance, improved_route).ok is True
    assert route_distance(instance, improved_route) <= nearest_result.total_distance
    assert improved_result.total_distance <= nearest_result.total_distance


def test_score_next_stop_evaluator_runs_valid_candidate_program() -> None:
    code = """
def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"]
"""
    evaluator = RoutingEvaluator()
    instance = generate_routing_instance(
        RoutingDistribution.UNIFORM, seed=4, stop_count=8
    )

    result = evaluator.evaluate_program(code, [instance], program_id="nearest-like")

    assert result.program_id == "nearest-like"
    assert result.ok is True
    assert result.failure_reason is None
    assert result.metrics["route_validity"] == 1
    assert result.metrics["average_route_length"] > 0
    assert result.metrics["failure_rate"] == 0


def test_score_next_stop_evaluator_records_invalid_program_failure() -> None:
    evaluator = RoutingEvaluator()
    instance = generate_routing_instance(
        RoutingDistribution.UNIFORM, seed=8, stop_count=8
    )

    result = evaluator.evaluate_program(
        "def score_next_stop(state, candidate_stop):\n"
        "    return open('hidden_labels.json').read()\n",
        [instance],
        program_id="unsafe",
    )

    assert result.ok is False
    assert result.failure_reason is not None
    assert "dangerous_call" in result.failure_reason
    assert result.metrics["failure_rate"] == 1


def test_score_next_stop_evaluator_rejects_invalid_generated_route() -> None:
    code = """
def score_next_stop(state, candidate_stop):
    return "near"
"""
    evaluator = RoutingEvaluator()
    instance = generate_routing_instance(
        RoutingDistribution.UNIFORM, seed=10, stop_count=8
    )

    result = evaluator.evaluate_program(code, [instance], program_id="non-numeric")

    assert result.ok is False
    assert result.failure_reason is not None
    assert "non_numeric_score" in result.failure_reason


def test_routing_suite_competes_with_baselines_and_2opt_improves() -> None:
    train, validation, test = default_train_validation_test_suites(
        train_sizes=(8,),
        validation_sizes=(10,),
        test_sizes=(12,),
    )
    candidates = build_seed_routing_programs()

    summary = evaluate_routing_candidate_suite(
        candidates=candidates,
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )

    assert summary.candidate_count == len(candidates)
    assert summary.best_program_id
    assert summary.best_validation_score <= summary.baseline_scores["random"]
    assert summary.best_validation_score <= summary.baseline_scores["nearest_neighbor"]
    assert summary.best_with_local_search_score <= summary.best_validation_score
    assert summary.test_score is not None
    assert summary.top_programs[0]["explanation"]


def test_phase4_report_contains_rerunnable_top_program_and_held_out_results() -> None:
    report = build_phase4_report(candidate_count=8, stop_count=10)
    top = report["top_programs"][0]

    assert report["candidate_count"] == 8
    assert report["held_out"]["instance_count"] > 0
    assert report["held_out"]["score"] == report["test_score"]
    assert "nearest_neighbor" in report["baseline_scores"]
    assert "nearest_neighbor_plus_2opt" in report["baseline_scores"]
    assert report["local_search"]["improved_or_equal"] is True
    assert "def score_next_stop" in top["code"]
    assert top["explanation"]

    _, _, test = default_train_validation_test_suites(test_sizes=(12,))
    rerun = RoutingEvaluator().evaluate_program(
        top["code"], test, program_id=top["program_id"], apply_local_search=True
    )

    assert rerun.ok is True
    assert math.isclose(rerun.score or 0, report["test_score"])
