from __future__ import annotations

import math

from benchmarks.amazon_routing.baselines import AMAZON_BASELINE_ROUTE_BUILDERS
from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    AmazonDiscoveryLoop,
    build_phase6_report,
    build_phase6_seed_programs,
    default_phase6_train_validation_test_routes,
)
from benchmarks.amazon_routing.evaluator import AmazonRoutingEvaluator
from benchmarks.amazon_routing.features import (
    AMAZON_CANDIDATE_FEATURES,
    extract_stop_features,
)


def test_phase6_candidate_feature_contract_matches_roadmap() -> None:
    train, _, _ = default_phase6_train_validation_test_routes()
    route = train[0]
    features = extract_stop_features(
        route,
        candidate_stop_id=route.stop_ids[0],
        current_stop_id=route.depot.stop_id,
        elapsed_time=0.0,
        visited=(),
    )
    required = {
        "travel_time",
        "same_zone",
        "zone_transition_cost",
        "time_window_slack",
        "package_count",
        "service_time",
        "zone_density",
        "distance_to_depot",
        "depot_angle",
        "cluster_compactness",
        "remaining_count",
        "remaining_same_zone_count",
        "remaining_zone_count",
    }

    assert required.issubset(set(AMAZON_CANDIDATE_FEATURES))
    assert required.issubset(set(features))
    assert isinstance(features["depot_angle"], float)
    assert 0 <= features["cluster_compactness"] <= 1
    assert features["remaining_zone_count"] >= 1


def test_phase6_baselines_include_ml_and_hybrid_variants() -> None:
    expected = {
        "nearest_neighbor",
        "cheapest_insertion",
        "two_opt",
        "driver_aware",
        "ml_next_stop_ranker",
        "hybrid_ml_plus_local_search",
    }
    train, _, _ = default_phase6_train_validation_test_routes()

    assert set(AMAZON_BASELINE_ROUTE_BUILDERS) == expected
    for name in ("ml_next_stop_ranker", "hybrid_ml_plus_local_search"):
        first = AMAZON_BASELINE_ROUTE_BUILDERS[name](train[0])
        second = AMAZON_BASELINE_ROUTE_BUILDERS[name](train[0])
        assert first.algorithm == name
        assert first.sequence == second.sequence
        assert first.is_valid
        assert first.metrics["travel_time"] > 0


def test_amazon_discovery_loop_is_reproducible_and_rerunnable() -> None:
    train, validation, test = default_phase6_train_validation_test_routes()
    config = AmazonDiscoveryConfig(
        generations=2,
        population_size=10,
        offspring_per_generation=8,
        elite_size=3,
        tournament_size=3,
        random_seed=17,
    )

    first = AmazonDiscoveryLoop(config=config).run(
        train_routes=train,
        validation_routes=validation,
        test_routes=test,
    )
    second = AmazonDiscoveryLoop(config=config).run(
        train_routes=train,
        validation_routes=validation,
        test_routes=test,
    )

    assert [report.as_curve_point() for report in first.generation_reports] == [
        report.as_curve_point() for report in second.generation_reports
    ]
    assert len(first.generation_reports) == 3
    assert first.archive.survivors()
    assert first.archive.failures()
    assert first.failure_taxonomy
    assert first.top_candidates
    assert all(candidate.complexity > 0 for candidate in first.top_candidates)

    top = first.top_candidates[0]
    rerun = first.rerun_candidate(top.program_id, test, apply_local_search=True)
    assert rerun.ok is True
    assert math.isclose(rerun.score or 0.0, top.test_score or 0.0)


def test_phase6_report_contains_tradeoffs_variants_and_rerunnable_top_program() -> None:
    report = build_phase6_report(
        config=AmazonDiscoveryConfig(
            generations=2,
            population_size=12,
            offspring_per_generation=8,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        )
    )
    top = report["top_candidates"][0]

    assert report["generation_count"] == 3
    assert report["held_out"]["route_count"] > 0
    assert "driver_aware" in report["baseline_scores"]
    assert "ml_next_stop_ranker" in report["baseline_scores"]
    assert "hybrid_ml_plus_local_search" in report["baseline_scores"]
    assert "score_next_stop" in top["code"]
    assert top["explanation"]
    assert top["test_score"] == report["held_out"]["best_score"]
    assert report["feature_contract"] == tuple(AMAZON_CANDIDATE_FEATURES)
    assert set(report["variants"]) == {
        "llm_heuristic",
        "llm_heuristic_plus_2opt",
        "feasibility_repair",
        "local_search",
    }
    assert report["frontier_improvements"]
    assert report["tradeoff_programs"]
    assert any(
        item["pattern"] == "improves_travel_time_hurts_driver_likeness"
        and item["travel_time_delta"] < 0
        and item["driver_likeness_delta"] < 0
        for item in report["tradeoff_programs"]
    )
    assert report["failure_taxonomy"]

    rerun = AmazonRoutingEvaluator().evaluate_program(
        top["code"],
        report["splits"]["test_routes"],
        program_id=top["program_id"],
        apply_local_search=True,
    )
    assert rerun.ok is True
    assert math.isclose(rerun.score or 0.0, top["test_score"] or 0.0)


def test_phase6_seed_programs_include_tradeoff_and_invalid_probe() -> None:
    seeds = build_phase6_seed_programs(10)

    assert len(seeds) == 10
    assert any("same_zone" in seed.program_id for seed in seeds)
    assert any("travel_fast" in seed.program_id for seed in seeds)
    assert any("open(" in seed.code for seed in seeds)
