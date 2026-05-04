from __future__ import annotations

import csv
import json
from pathlib import Path

from reports.artifacts import export_report_artifacts
from reports.final_report import build_final_report, render_final_report_markdown
from reports.pareto import build_phase15_report
from reports.plots import build_report_plots
from reports.tables import build_report_tables


def test_phase15_report_contains_required_tradeoff_axes() -> None:
    report = build_phase15_report()

    assert report["phase"] == 15
    assert report["frontier_axes"] == (
        "objective_quality",
        "runtime",
        "program_complexity",
        "failure_rate",
        "generalization_gap",
        "operational_penalty",
    )
    assert set(report["benchmarks"]) == {
        "bin_packing",
        "simple_routing",
        "amazon_routing",
    }
    assert "rather than universally dominating" in report["claim_boundary"]
    assert report["candidate_rows"]
    assert report["frontier_rows"]

    required = {
        "benchmark",
        "program_id",
        "objective_quality",
        "runtime",
        "program_complexity",
        "failure_rate",
        "generalization_gap",
        "driver_likeness_or_realism",
        "operational_penalty",
        "is_pareto_frontier",
        "dominance_count",
        "selected_tradeoff",
        "code",
    }
    for row in report["candidate_rows"]:
        assert required <= set(row)
        assert row["objective_quality"] is not None
        assert row["runtime"] >= 0
        assert row["program_complexity"] > 0
        assert row["failure_rate"] >= 0
        assert row["generalization_gap"] >= 0


def test_phase15_frontier_rows_are_nondominated_within_benchmark() -> None:
    report = build_phase15_report()

    frontier_by_benchmark = {
        benchmark: [
            row
            for row in report["candidate_rows"]
            if row["benchmark"] == benchmark and row["is_pareto_frontier"]
        ]
        for benchmark in report["benchmarks"]
    }
    assert all(frontier_by_benchmark.values())

    for benchmark in report["benchmarks"]:
        rows = [
            row for row in report["candidate_rows"] if row["benchmark"] == benchmark
        ]
        for frontier_row in frontier_by_benchmark[benchmark]:
            assert not any(
                challenger["program_id"] != frontier_row["program_id"]
                and _dominates(challenger, frontier_row)
                for challenger in rows
            )


def test_phase15_report_tables_plots_and_final_report_are_integrated() -> None:
    tables = build_report_tables()
    plots = build_report_plots()
    final = build_final_report()
    markdown = render_final_report_markdown(final)

    assert "pareto_frontier" in tables["tables"]
    assert len(tables["pareto_frontier"]["rows"]) >= 3
    assert "frontier_plot_series" in plots["plots"]
    assert plots["frontier_plot_series"]["points"]
    assert "pareto_frontier_report" in final["sections"]
    assert final["pareto_frontier"]["frontier_count"] >= 3
    assert "Pareto Frontier" in markdown
    assert final["recommended_next_steps"][0]["step"] == "optional_cloud_scale_search"


def test_phase15_artifacts_export_frontier_table_plot_and_programs(
    tmp_path: Path,
) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    pareto_csv = tmp_path / "reports" / "tables" / "pareto_frontier.csv"
    frontier_plot = tmp_path / "reports" / "plots" / "frontier_plot_series.json"
    frontier_programs = sorted(
        (tmp_path / "artifacts" / "frontier_programs").glob("*.py")
    )

    assert pareto_csv.is_file()
    assert str(pareto_csv) in summary["tables"]
    assert frontier_plot.is_file()
    assert str(frontier_plot) in summary["extra_plot_series"]
    assert frontier_programs
    assert {Path(path) for path in summary["frontier_programs"]} == set(
        frontier_programs
    )

    with pareto_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert any(row["is_pareto_frontier"] == "True" for row in rows)

    plot = json.loads(frontier_plot.read_text(encoding="utf-8"))
    assert plot["title"] == "Pareto Frontier Quality Runtime"
    assert plot["points"]


def _dominates(challenger: dict[str, object], candidate: dict[str, object]) -> bool:
    axes = (
        "objective_quality",
        "runtime",
        "program_complexity",
        "failure_rate",
        "generalization_gap",
        "operational_penalty",
    )
    challenger_values = [float(challenger[axis]) for axis in axes]
    candidate_values = [float(candidate[axis]) for axis in axes]
    return all(
        left <= right for left, right in zip(challenger_values, candidate_values)
    ) and any(left < right for left, right in zip(challenger_values, candidate_values))
