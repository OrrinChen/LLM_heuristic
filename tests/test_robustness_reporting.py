from __future__ import annotations

import math

from reports.robustness import (
    PHASE7_REPORTING_FIELDS,
    PHASE7_TESTING_DIMENSIONS,
    build_phase7_report,
)


def test_phase7_report_covers_all_benchmarks_and_required_fields() -> None:
    report = build_phase7_report()

    assert report["phase"] == 7
    assert report["benchmark_count"] == 3
    assert set(report["benchmarks"]) == {
        "bin_packing",
        "simple_routing",
        "amazon_routing",
    }
    assert tuple(report["required_reporting_fields"]) == PHASE7_REPORTING_FIELDS

    for benchmark in report["benchmarks"].values():
        assert set(PHASE7_REPORTING_FIELDS).issubset(benchmark)
        assert benchmark["program_id"]
        assert benchmark["program_complexity"] > 0
        assert benchmark["runtime"] >= 0
        assert 0 <= benchmark["failure_rate"] <= 1
        assert benchmark["train_score"] is not None
        assert benchmark["validation_score"] is not None
        assert benchmark["test_score"] is not None
        assert math.isclose(
            benchmark["generalization_gap"],
            abs(benchmark["validation_score"] - benchmark["test_score"]),
        )


def test_phase7_report_covers_roadmap_testing_dimensions() -> None:
    report = build_phase7_report()
    dimensions = {row["dimension"] for row in report["slice_summary"]}

    assert tuple(report["testing_dimensions"]) == PHASE7_TESTING_DIMENSIONS
    assert set(PHASE7_TESTING_DIMENSIONS).issubset(dimensions)

    assert any(
        row["benchmark"] == "bin_packing"
        and row["dimension"] == "held_out_item_size_distributions"
        and row["tags"]["distribution"] == "held_out"
        for row in report["slice_summary"]
    )
    assert any(
        row["benchmark"] == "simple_routing"
        and row["dimension"] == "held_out_routing_instance_sizes"
        and row["tags"]["stop_count"] == "14"
        for row in report["slice_summary"]
    )
    assert any(
        row["benchmark"] == "amazon_routing"
        and row["dimension"] == "held_out_amazon_city_slices"
        and row["tags"]["station_code"] == "DCH1"
        for row in report["slice_summary"]
    )
    assert any(
        row["benchmark"] == "amazon_routing"
        and row["dimension"] == "high_quality_vs_medium_quality_routes"
        and row["tags"]["quality_label"] == "Medium"
        for row in report["slice_summary"]
    )


def test_phase7_slice_rows_include_required_reporting_metrics() -> None:
    report = build_phase7_report()

    for row in report["slice_summary"]:
        assert set(PHASE7_REPORTING_FIELDS).issubset(row)
        assert row["slice_name"]
        assert row["test_score"] is not None
        assert row["runtime"] >= 0
        assert 0 <= row["failure_rate"] <= 1
        assert row["program_complexity"] > 0
        assert math.isclose(
            row["generalization_gap"],
            abs(row["validation_score"] - row["test_score"]),
        )


def test_phase7_report_has_stable_score_signature_and_worst_gaps() -> None:
    first = build_phase7_report()
    second = build_phase7_report()

    assert _score_signature(first) == _score_signature(second)
    assert first["worst_generalization_gaps"]
    assert (
        first["worst_generalization_gaps"][0]["generalization_gap"]
        >= (first["worst_generalization_gaps"][-1]["generalization_gap"])
    )
    assert "dangerous_call" in first["failure_taxonomy"]
    assert first["known_limitations"]


def _score_signature(report: dict[str, object]) -> tuple[object, ...]:
    benchmarks = report["benchmarks"]
    slices = report["slice_summary"]
    return (
        tuple(
            (
                name,
                row["program_id"],
                round(row["train_score"], 6),
                round(row["validation_score"], 6),
                round(row["test_score"], 6),
                round(row["generalization_gap"], 6),
            )
            for name, row in sorted(benchmarks.items())
        ),
        tuple(
            (
                row["benchmark"],
                row["dimension"],
                row["slice_name"],
                round(row["test_score"], 6),
                round(row["generalization_gap"], 6),
            )
            for row in slices
        ),
    )
