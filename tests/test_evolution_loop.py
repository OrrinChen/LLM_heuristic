from __future__ import annotations

import math

from benchmarks.bin_packing.instances import default_train_validation_test_suites
from program_search.evolution_loop import (
    EvolutionConfig,
    EvolutionLoop,
    build_phase3_report,
)
from program_search.novelty_filter import ExactCodeNoveltyFilter
from program_search.scoring import ScoredCandidate, compute_program_complexity
from program_search.tournament_selection import TournamentSelector


def test_tournament_selection_is_deterministic_under_fixed_seed() -> None:
    candidates = [
        ScoredCandidate(
            program_id=f"candidate-{index}",
            code=f"def score_bin(a, b, c):\n    return {index}\n",
            generation=0,
            final_score=float(index),
            benchmark_score=float(index),
            runtime=0.0,
            complexity=4,
        )
        for index in range(8)
    ]

    first = TournamentSelector(tournament_size=3, random_seed=7).select_many(
        candidates, count=5
    )
    second = TournamentSelector(tournament_size=3, random_seed=7).select_many(
        candidates, count=5
    )

    assert [candidate.program_id for candidate in first] == [
        candidate.program_id for candidate in second
    ]
    assert all(candidate in candidates for candidate in first)


def test_novelty_filter_rejects_exact_duplicate_code() -> None:
    novelty = ExactCodeNoveltyFilter()
    code = (
        "def score_bin(item_size, bin_remaining_capacity, bin_features):\n"
        "    return 0\n"
    )

    assert novelty.is_novel(code) is True
    novelty.add(code)
    assert novelty.is_novel(code) is False
    assert novelty.is_novel(code + "\n") is False


def test_program_complexity_counts_ast_nodes() -> None:
    simple = (
        "def score_bin(item_size, bin_remaining_capacity, bin_features):\n"
        "    return 0\n"
    )
    richer = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected + bin_features["items_in_bin"]
"""

    assert compute_program_complexity(simple) > 0
    assert compute_program_complexity(richer) > compute_program_complexity(simple)


def test_evolution_loop_reports_reproducible_generation_curve_and_metrics() -> None:
    train, validation, test = default_train_validation_test_suites(item_count=20)
    config = EvolutionConfig(
        generations=3,
        population_size=16,
        offspring_per_generation=12,
        elite_size=4,
        tournament_size=3,
        random_seed=11,
    )

    first = EvolutionLoop(config=config).run(
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )
    second = EvolutionLoop(config=config).run(
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )

    assert [report.as_curve_point() for report in first.generation_reports] == [
        report.as_curve_point() for report in second.generation_reports
    ]
    assert len(first.generation_reports) == 4
    for report in first.generation_reports:
        assert report.best_score > 0
        assert report.median_score >= report.best_score
        assert 0 <= report.failure_rate <= 1
        assert 0 <= report.invalid_code_rate <= 1
        assert report.population_size > 0
    assert (
        first.generation_reports[-1].best_score
        <= first.generation_reports[0].best_score
    )


def test_evolution_loop_records_mutation_crossover_failures_and_lineage() -> None:
    train, validation, test = default_train_validation_test_suites(item_count=18)
    config = EvolutionConfig(
        generations=2,
        population_size=12,
        offspring_per_generation=10,
        elite_size=3,
        tournament_size=3,
        random_seed=5,
    )

    result = EvolutionLoop(config=config).run(
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )

    assert result.archive.survivors()
    assert result.archive.failures()
    assert any(candidate.generation > 0 for candidate in result.archive.survivors())
    assert any(
        "mutation" in candidate.prompt for candidate in result.archive.survivors()
    )
    assert any(
        "crossover" in candidate.prompt for candidate in result.archive.survivors()
    )

    top = result.top_candidates[0]
    lineage = result.archive.lineage_for(top.program_id)
    assert lineage[-1].program_id == top.program_id
    assert len(lineage) >= 1


def test_top_candidates_track_complexity_generalization_and_can_be_rerun() -> None:
    train, validation, test = default_train_validation_test_suites(item_count=20)
    result = EvolutionLoop(
        config=EvolutionConfig(
            generations=2,
            population_size=14,
            offspring_per_generation=10,
            elite_size=4,
            tournament_size=3,
            random_seed=19,
        )
    ).run(train_instances=train, validation_instances=validation, test_instances=test)

    top = result.top_candidates[0]

    assert top.complexity > 0
    assert top.train_score is not None
    assert top.validation_score is not None
    assert top.test_score is not None
    assert top.generalization_gap >= 0

    rerun = result.rerun_candidate(top.program_id, test)

    assert rerun.ok is True
    assert math.isclose(rerun.score or 0, top.test_score or 0)


def test_phase3_report_contains_generation_curve_and_failure_taxonomy() -> None:
    report = build_phase3_report(
        config=EvolutionConfig(
            generations=3,
            population_size=16,
            offspring_per_generation=12,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        ),
        item_count=20,
    )

    assert report["generation_count"] == 4
    assert len(report["generation_curve"]) == 4
    assert report["top_candidates"]
    assert report["failure_taxonomy"]
    assert report["rerun_top"]["ok"] is True
    assert "complexity" in report["top_candidates"][0]
    assert "generalization_gap" in report["top_candidates"][0]
