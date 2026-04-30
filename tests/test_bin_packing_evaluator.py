from __future__ import annotations

import math

from benchmarks.bin_packing.baselines import (
    BASELINE_PACKERS,
    PackingResult,
    best_fit,
    best_fit_decreasing,
    first_fit,
    first_fit_decreasing,
    handwritten_score_heuristic,
    random_fit,
    validate_packing,
    worst_fit,
)
from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    archive_seed_candidates,
    build_phase2_report,
    build_seed_candidate_programs,
    evaluate_candidate_suite,
)
from benchmarks.bin_packing.instances import (
    InstanceDistribution,
    default_train_validation_test_suites,
    generate_instance,
    generate_suite,
)


def test_instance_generation_is_deterministic_and_covers_phase2_distributions() -> None:
    distributions = {
        InstanceDistribution.UNIFORM_SMALL,
        InstanceDistribution.UNIFORM_MIXED,
        InstanceDistribution.HEAVY_TAIL,
        InstanceDistribution.TINY_PLUS_LARGE,
        InstanceDistribution.ADVERSARIAL,
        InstanceDistribution.HELD_OUT,
    }

    for distribution in distributions:
        first = generate_instance(distribution, seed=17, item_count=40)
        second = generate_instance(distribution, seed=17, item_count=40)

        assert first == second
        assert first.distribution == distribution
        assert first.capacity == 1.0
        assert len(first.items) == 40
        assert all(0 < item <= first.capacity for item in first.items)


def test_default_suites_keep_training_validation_and_test_seeds_separate() -> None:
    train, validation, test = default_train_validation_test_suites(
        item_count=20,
        train_seeds=(1, 2),
        validation_seeds=(101,),
        test_seeds=(201,),
    )

    train_seeds = {instance.seed for instance in train}
    validation_seeds = {instance.seed for instance in validation}
    test_seeds = {instance.seed for instance in test}

    assert train_seeds == {1, 2}
    assert validation_seeds == {101}
    assert test_seeds == {201}
    assert train_seeds.isdisjoint(validation_seeds)
    assert train_seeds.isdisjoint(test_seeds)
    assert validation_seeds.isdisjoint(test_seeds)


def test_generate_suite_includes_each_requested_distribution_and_seed() -> None:
    suite = generate_suite(
        distributions=[
            InstanceDistribution.UNIFORM_SMALL,
            InstanceDistribution.HEAVY_TAIL,
        ],
        seeds=[3, 4],
        item_count=12,
    )

    assert len(suite) == 4
    assert {(instance.distribution, instance.seed) for instance in suite} == {
        (InstanceDistribution.UNIFORM_SMALL, 3),
        (InstanceDistribution.UNIFORM_SMALL, 4),
        (InstanceDistribution.HEAVY_TAIL, 3),
        (InstanceDistribution.HEAVY_TAIL, 4),
    }


def test_baselines_are_available_and_deterministic() -> None:
    expected = {
        "first_fit",
        "best_fit",
        "worst_fit",
        "first_fit_decreasing",
        "best_fit_decreasing",
        "handwritten_score_heuristic",
        "random",
    }
    instance = generate_instance(
        InstanceDistribution.UNIFORM_MIXED, seed=7, item_count=50
    )

    assert set(BASELINE_PACKERS) == expected
    for name, packer in BASELINE_PACKERS.items():
        first = packer(instance)
        second = packer(instance)

        assert isinstance(first, PackingResult)
        assert first.algorithm == name
        assert first.bins == second.bins
        assert first.is_valid
        assert first.bins_used == len(first.bins)
        assert first.average_waste >= 0


def test_core_baselines_compute_expected_bin_counts_on_small_instance() -> None:
    instance = generate_instance(
        InstanceDistribution.HELD_OUT,
        seed=99,
        item_count=0,
        items=[0.6, 0.4, 0.5, 0.5, 0.2],
    )

    assert first_fit(instance).bins_used == 3
    assert best_fit(instance).bins_used == 3
    assert worst_fit(instance).bins_used == 3
    assert first_fit_decreasing(instance).bins_used == 3
    assert best_fit_decreasing(instance).bins_used == 3
    assert handwritten_score_heuristic(instance).bins_used == 3
    assert random_fit(instance).bins_used == 3


def test_validate_packing_rejects_invalid_placements() -> None:
    instance = generate_instance(
        InstanceDistribution.HELD_OUT,
        seed=100,
        item_count=0,
        items=[0.7, 0.6],
    )

    assert validate_packing(instance, [[0.7], [0.6]]).ok is True
    invalid = validate_packing(instance, [[0.7, 0.6]])

    assert invalid.ok is False
    assert invalid.failure_reason == "bin_capacity_exceeded"


def test_score_bin_evaluator_runs_valid_candidate_program() -> None:
    code = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected
"""
    evaluator = BinPackingEvaluator()
    instance = generate_instance(
        InstanceDistribution.HELD_OUT,
        seed=5,
        item_count=0,
        items=[0.6, 0.4, 0.5, 0.5],
    )

    result = evaluator.evaluate_program(code, [instance], program_id="tight-fit")

    assert result.program_id == "tight-fit"
    assert result.ok is True
    assert result.failure_reason is None
    assert result.metrics["bins_used"] == 2
    assert result.metrics["average_waste"] == 0
    assert result.metrics["failure_rate"] == 0


def test_score_bin_evaluator_records_invalid_program_failure() -> None:
    evaluator = BinPackingEvaluator()
    instance = generate_instance(InstanceDistribution.UNIFORM_SMALL, seed=2)

    result = evaluator.evaluate_program(
        "def score_bin(item_size, bin_remaining_capacity, bin_features):\n"
        "    return open('x')\n",
        [instance],
        program_id="unsafe",
    )

    assert result.ok is False
    assert result.score is None
    assert result.failure_reason is not None
    assert "dangerous_call" in result.failure_reason
    assert result.metrics["failure_rate"] == 1


def test_score_bin_evaluator_rejects_candidate_that_cannot_place_an_item() -> None:
    code = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return 1000000
"""
    evaluator = BinPackingEvaluator()
    instance = generate_instance(
        InstanceDistribution.HELD_OUT,
        seed=6,
        item_count=0,
        items=[0.6, 0.4],
    )

    result = evaluator.evaluate_program(code, [instance], program_id="bad-placement")

    assert result.ok is False
    assert result.failure_reason == "no_feasible_bin_selected"
    assert result.metrics["failure_rate"] == 1


def test_evaluator_can_score_100_seed_candidate_programs() -> None:
    train, validation, test = default_train_validation_test_suites(item_count=25)
    candidates = build_seed_candidate_programs(100)

    assert len(candidates) == 100

    summary = evaluate_candidate_suite(
        candidates=candidates,
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )

    assert summary.candidate_count == 100
    assert 0 <= summary.failure_rate < 1
    assert summary.best_program_id
    assert summary.best_validation_score < summary.baseline_scores["random"]
    assert summary.best_validation_score <= summary.baseline_scores["first_fit"]
    assert summary.test_score is not None
    assert len(summary.top_programs) >= 3


def test_phase2_report_contains_reproducible_top_program_and_held_out_results() -> None:
    report = build_phase2_report(candidate_count=120, item_count=25)
    top = report["top_programs"][0]

    assert report["candidate_count"] == 120
    assert report["held_out"]["instance_count"] > 0
    assert report["held_out"]["score"] == report["test_score"]
    assert "first_fit" in report["baseline_scores"]
    assert "random" in report["baseline_scores"]
    assert top["program_id"]
    assert "def score_bin" in top["code"]
    assert top["explanation"]

    train, validation, test = default_train_validation_test_suites(item_count=25)
    rerun = BinPackingEvaluator().evaluate_program(
        top["code"], test, program_id=top["program_id"]
    )

    assert rerun.ok is True
    assert math.isclose(rerun.score or 0, report["test_score"])


def test_seed_candidate_archive_records_survivors_and_failures() -> None:
    instances = generate_suite(
        distributions=[InstanceDistribution.UNIFORM_SMALL],
        seeds=[11],
        item_count=15,
    )
    archive = archive_seed_candidates(build_seed_candidate_programs(8), instances)

    assert len(archive.survivors()) > 0
    assert len(archive.failures()) > 0
    survivor = archive.survivors()[0]
    lineage = archive.lineage_for(survivor.program_id)

    assert lineage[-1].program_id == survivor.program_id
