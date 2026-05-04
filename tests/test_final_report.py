from __future__ import annotations

import pytest

from reports.final_report import (
    FINAL_REPORT_SECTIONS,
    KILLER_EXPERIMENT_BENCHMARKS,
    build_final_report,
    render_final_report_markdown,
)


@pytest.fixture(scope="module")
def final_report() -> dict[str, object]:
    return build_final_report()


def test_final_report_has_required_sections_and_claim_boundaries(
    final_report: dict[str, object],
) -> None:
    assert final_report["phase"] == "final_report"
    assert tuple(final_report["sections"]) == FINAL_REPORT_SECTIONS
    assert final_report["project"]["thesis"] == (
        "heuristic design can be automated as constrained program search"
    )
    assert "selected trade-offs" in final_report["claims"]["conservative"]
    assert "universal dominance" in final_report["claims"]["does_not_claim"]
    assert final_report["claims"]["live_llm_status"] == "optional_env_configured"
    assert "subprocess_sandbox" in final_report["claims"]["hardening_status"]


def test_final_report_covers_killer_experiment_benchmarks(
    final_report: dict[str, object],
) -> None:
    benchmarks = final_report["killer_experiment"]["benchmarks"]

    assert tuple(benchmarks) == KILLER_EXPERIMENT_BENCHMARKS
    assert set(benchmarks["bin_packing"]["comparisons"]) >= {
        "first_fit",
        "best_fit",
        "first_fit_decreasing",
        "handwritten_score_heuristic",
        "llm_discovered",
    }
    assert set(benchmarks["simple_routing"]["comparisons"]) >= {
        "nearest_neighbor",
        "cheapest_insertion",
        "two_opt",
        "llm_discovered",
        "llm_discovered_plus_2opt",
    }
    assert set(benchmarks["amazon_routing"]["comparisons"]) >= {
        "nearest_neighbor",
        "two_opt",
        "driver_aware",
        "ml_next_stop_ranker",
        "llm_discovered",
        "llm_discovered_plus_local_search",
    }

    for benchmark in benchmarks.values():
        assert benchmark["top_program_id"]
        assert benchmark["test_score"] is not None
        assert benchmark["summary"]


def test_final_report_links_robustness_and_failure_evidence(
    final_report: dict[str, object],
) -> None:
    evidence = final_report["evidence"]

    assert evidence["robustness"]["benchmark_count"] == 3
    assert evidence["robustness"]["slice_count"] == 15
    assert evidence["failure_analysis"]["failure_category_count"] == 9
    assert evidence["failure_analysis"]["top_rejected_count"] == 8
    assert evidence["failure_analysis"]["top_surviving_count"] == 8
    assert evidence["amazon_tradeoffs"]["tradeoff_count"] >= 1
    assert final_report["pareto_frontier"]["frontier_count"] >= 3
    assert final_report["limitations"]
    assert (
        final_report["recommended_next_steps"][0]["step"]
        == "optional_cloud_scale_search"
    )


def test_final_report_markdown_is_conservative_and_complete(
    final_report: dict[str, object],
) -> None:
    markdown = render_final_report_markdown(final_report)

    assert markdown.startswith("# LLM-Driven Program Search for OR Heuristics")
    assert "heuristic design can be automated as constrained program search" in markdown
    assert "do not universally dominate" in markdown
    assert "selected trade-offs" in markdown
    assert "## Killer Experiment" in markdown
    assert "## Program Semantics And Novelty" in markdown
    assert "## Pareto Frontier Report" in markdown
    assert "## Generalization And Robustness" in markdown
    assert "## Failure Analysis" in markdown
    assert "## Failure Taxonomy v2" in markdown
    assert "repair success" in markdown
    assert "phase6-seed-000-travel_fast" in markdown


def test_final_report_smoke_signature_is_stable(
    final_report: dict[str, object],
) -> None:
    assert _signature(final_report) == (
        3,
        15,
        9,
        "seed-000-tight_fit",
        "route-seed-003-slack_aware",
        "phase6-seed-000-travel_fast",
        "optional_cloud_scale_search",
    )


def _signature(report: dict[str, object]) -> tuple[object, ...]:
    benchmarks = report["killer_experiment"]["benchmarks"]
    return (
        len(benchmarks),
        report["evidence"]["robustness"]["slice_count"],
        report["evidence"]["failure_analysis"]["failure_category_count"],
        benchmarks["bin_packing"]["top_program_id"],
        benchmarks["simple_routing"]["top_program_id"],
        benchmarks["amazon_routing"]["top_program_id"],
        report["recommended_next_steps"][0]["step"],
    )
