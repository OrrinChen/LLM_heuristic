from __future__ import annotations

from reports.failure_analysis import (
    PHASE8_FAILURE_CATEGORIES,
    build_phase8_report,
)


def test_phase8_report_covers_full_failure_taxonomy() -> None:
    report = build_phase8_report()

    assert report["phase"] == 8
    assert tuple(report["failure_categories"]) == PHASE8_FAILURE_CATEGORIES
    assert set(report["failure_taxonomy"]) == set(PHASE8_FAILURE_CATEGORIES)

    for category, row in report["failure_taxonomy"].items():
        assert row["category"] == category
        assert row["count"] >= 0
        assert row["severity"] in {"none", "low", "medium", "high"}
        assert row["rationale"]

    assert report["failure_taxonomy"]["generated_invalid_code"]["count"] > 0
    assert report["failure_taxonomy"]["timeout"]["count"] > 0
    assert report["failure_taxonomy"]["poor_generalization"]["count"] > 0
    assert (
        report["failure_taxonomy"]["improves_travel_time_but_hurts_driver_likeness"][
            "count"
        ]
        > 0
    )


def test_phase8_report_includes_generation_failure_rates_and_invalid_rates() -> None:
    report = build_phase8_report()
    rows = report["failure_rate_by_generation"]

    assert rows
    assert {row["benchmark"] for row in rows} == {
        "bin_packing_evolution",
        "amazon_routing_discovery",
    }
    for row in rows:
        assert row["generation"] >= 0
        assert row["population_size"] > 0
        assert 0 <= row["failure_rate"] <= 1
        assert 0 <= row["invalid_code_rate"] <= 1
        assert row["best_program_id"]
    assert any(row["invalid_code_rate"] > 0 for row in rows)


def test_phase8_report_lists_rejected_and_surviving_programs() -> None:
    report = build_phase8_report()

    rejected = report["top_rejected_programs"]
    surviving = report["top_surviving_programs"]

    assert rejected
    assert surviving
    assert any(item["category"] == "generated_invalid_code" for item in rejected)
    assert any(item["category"] == "timeout" for item in rejected)
    assert all(item["program_id"] for item in rejected)
    assert all(item["program_id"] for item in surviving)
    assert all(item["score"] is not None for item in surviving)
    assert any(item["benchmark"] == "amazon_routing_discovery" for item in surviving)


def test_phase8_report_summarizes_worked_and_failed_patterns() -> None:
    report = build_phase8_report()

    worked_patterns = {row["pattern"] for row in report["patterns_that_worked"]}
    failed_patterns = {row["pattern"] for row in report["patterns_that_failed"]}

    assert "tight_fit_bin_packing" in worked_patterns
    assert "amazon_travel_time_frontier" in worked_patterns
    assert "unsafe_data_access" in failed_patterns
    assert "routing_large_slice_generalization_gap" in failed_patterns
    assert "travel_time_driver_likeness_tradeoff" in failed_patterns


def test_phase8_report_has_stable_smoke_signature() -> None:
    first = build_phase8_report()
    second = build_phase8_report()

    assert _signature(first) == _signature(second)
    assert first["known_limitations"]


def _signature(report: dict[str, object]) -> tuple[object, ...]:
    taxonomy = report["failure_taxonomy"]
    return (
        len(report["failure_rate_by_generation"]),
        len(report["top_rejected_programs"]),
        len(report["top_surviving_programs"]),
        tuple(
            (category, taxonomy[category]["count"])
            for category in PHASE8_FAILURE_CATEGORIES
        ),
        tuple(row["pattern"] for row in report["patterns_that_failed"]),
    )
