from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from program_search.ablation import (
    PHASE11_METHODS,
    build_phase11_report,
)
from reports.artifacts import export_report_artifacts
from reports.final_report import build_final_report, render_final_report_markdown
from reports.plots import build_report_plots
from reports.tables import build_report_tables


def test_phase11_report_compares_all_methods_under_same_controls() -> None:
    report = build_phase11_report(
        candidate_budget=16,
        generations=3,
        item_count=16,
        random_seed=31,
    )

    assert report["phase"] == 11
    assert report["benchmark"] == "bin_packing"
    assert tuple(report["methods"]) == PHASE11_METHODS
    assert report["controls"] == {
        "candidate_budget": 16,
        "generations": 3,
        "benchmark_split": "default_bin_packing_train_validation_test",
        "timeout_seconds": 0.25,
        "random_seed": 31,
        "item_count": 16,
    }

    rows = report["summary_rows"]
    assert len(rows) == len(PHASE11_METHODS)
    assert {row["method"] for row in rows} == set(PHASE11_METHODS)
    assert {row["evaluated_candidates"] for row in rows} == {16}
    assert all(row["best_validation_score"] is not None for row in rows)
    assert all(0 <= row["invalid_code_rate"] <= 1 for row in rows)
    assert all(row["live_llm_required"] is False for row in rows)
    assert all(row["operator_source"] for row in rows)


def test_phase11_report_has_budget_curves_and_invalid_rate_rows() -> None:
    report = build_phase11_report(
        candidate_budget=16,
        generations=3,
        item_count=16,
        random_seed=31,
    )

    generation_curve = report["generation_curve_by_method"]
    invalid_rows = report["invalid_code_rate_by_method"]
    budget_rows = report["best_score_by_budget"]

    assert set(generation_curve) == set(PHASE11_METHODS)
    assert all(len(points) == 4 for points in generation_curve.values())
    assert all(
        points[0]["evaluated_candidates"] >= 1 for points in generation_curve.values()
    )
    assert {row["method"] for row in invalid_rows} == set(PHASE11_METHODS)
    assert {row["method"] for row in budget_rows} == set(PHASE11_METHODS)
    assert all(row["candidate_budget"] == 16 for row in budget_rows)


def test_phase11_report_keeps_llm_as_deterministic_proxy_not_live_dependency() -> None:
    report = build_phase11_report(candidate_budget=12, generations=2)

    llm_rows = [
        row
        for row in report["summary_rows"]
        if row["method"] in {"llm_mutation", "llm_repair", "llm_mutation_plus_repair"}
    ]

    assert llm_rows
    assert all(row["operator_source"] == "deterministic_llm_proxy" for row in llm_rows)
    assert all(row["live_llm_required"] is False for row in llm_rows)
    assert report["claim_boundary"] == (
        "ablation compares deterministic operators under a fixed local budget; "
        "live LLM behavior is not claimed"
    )


def test_report_tables_and_plots_include_phase11_outputs() -> None:
    tables = build_report_tables()
    plots = build_report_plots()

    assert "ablation_summary" in tables["tables"]
    assert "invalid_code_rate_by_method" in tables["tables"]
    assert "best_score_by_budget" in tables["tables"]
    assert len(tables["ablation_summary"]["rows"]) == len(PHASE11_METHODS)
    assert len(tables["invalid_code_rate_by_method"]["rows"]) == len(PHASE11_METHODS)
    assert len(tables["best_score_by_budget"]["rows"]) == len(PHASE11_METHODS)
    assert "generation_curve_by_method" in plots["plots"]
    assert (
        len(plots["generation_curve_by_method"]["points"]) == len(PHASE11_METHODS) * 4
    )


def test_final_report_includes_search_ablation_section_and_next_phase() -> None:
    report = build_final_report()
    markdown = render_final_report_markdown(report)

    assert "search_mechanism_ablation" in report["sections"]
    assert report["search_ablation"]["best_method"]
    assert "Search Mechanism Ablation" in markdown
    assert "fixed local budget" in markdown
    assert report["recommended_next_steps"][0]["step"] == "semantic_novelty"


def test_report_artifacts_export_ablation_tables_and_curve(tmp_path: Path) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    expected_tables = {
        tmp_path / "reports" / "tables" / "ablation_summary.csv",
        tmp_path / "reports" / "tables" / "invalid_code_rate_by_method.csv",
        tmp_path / "reports" / "tables" / "best_score_by_budget.csv",
    }
    assert expected_tables.issubset({Path(path) for path in summary["tables"]})
    for table_path in expected_tables:
        assert table_path.is_file()
        with table_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == len(PHASE11_METHODS)

    plot_series = json.loads(
        (tmp_path / "reports" / "plots" / "plot_series.json").read_text(
            encoding="utf-8"
        )
    )
    assert "generation_curve_by_method" in plot_series["plots"]


def test_cli_can_run_search_ablation(tmp_path: Path) -> None:
    result = _run_cli(
        "run",
        "--benchmark",
        "search_ablation",
        "--candidate-budget",
        "16",
        "--generations",
        "3",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0
    assert "search_ablation" in result.stdout
    summary_path = tmp_path / "run_summary.json"
    assert summary_path.is_file()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["phase"] == 11
    assert summary["controls"]["candidate_budget"] == 16


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(src_dir)
    return subprocess.run(
        [sys.executable, "-m", "heuristic_discovery", *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
