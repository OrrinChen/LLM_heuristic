from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from program_search.semantic_novelty import (
    NoveltyCandidate,
    build_phase13_report,
)
from reports.artifacts import export_report_artifacts
from reports.final_report import build_final_report, render_final_report_markdown
from reports.plots import build_report_plots
from reports.tables import build_report_tables


def test_phase13_report_contains_required_semantic_novelty_evidence() -> None:
    report = build_phase13_report(candidate_count=12)

    assert report["phase"] == 13
    assert report["benchmark"] == "bin_packing_semantic_novelty"
    assert report["novelty_dimensions"] == (
        "code_novelty",
        "behavior_novelty",
        "feature_novelty",
        "performance_novelty",
    )
    assert report["probe_count"] >= 4
    assert report["candidate_count"] == 12
    assert report["novelty_rows"]
    assert report["behavior_fingerprints"]
    assert report["duplicate_behavior_clusters"]
    assert (
        "does not prove human-level semantic understanding"
        in (report["claim_boundary"])
    )

    first = report["novelty_rows"][0]
    required = {
        "program_id",
        "source",
        "code_hash",
        "behavior_hash",
        "code_novelty",
        "behavior_novelty",
        "feature_novelty",
        "performance_novelty",
        "semantic_novelty_score",
        "feature_usage",
        "complexity_nodes",
        "complexity_branches",
        "complexity_operations",
        "validation_score",
        "test_score",
    }
    assert required <= set(first)
    assert 0.0 <= first["semantic_novelty_score"] <= 1.0
    assert first["complexity_nodes"] > 0


def test_equivalent_ranking_behavior_clusters_programs_with_different_code() -> None:
    candidates = (
        NoveltyCandidate(
            program_id="equiv-a",
            source="unit",
            code="""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected
""".strip()
            + "\n",
            validation_score=5.0,
            test_score=5.0,
        ),
        NoveltyCandidate(
            program_id="equiv-b",
            source="unit",
            code="""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 999999 + abs(projected)
    return projected + 0.0001 * item_size
""".strip()
            + "\n",
            validation_score=5.2,
            test_score=5.1,
        ),
        NoveltyCandidate(
            program_id="different",
            source="unit",
            code="""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return -bin_features["items_in_bin"]
""".strip()
            + "\n",
            validation_score=6.0,
            test_score=6.0,
        ),
    )

    report = build_phase13_report(candidates=candidates)

    clusters = report["duplicate_behavior_clusters"]
    equiv_cluster = next(
        cluster for cluster in clusters if "equiv-a" in cluster["program_ids"]
    )
    assert set(equiv_cluster["program_ids"]) == {"equiv-a", "equiv-b"}
    assert equiv_cluster["cluster_size"] == 2
    assert "different" not in equiv_cluster["program_ids"]

    row_by_id = {row["program_id"]: row for row in report["novelty_rows"]}
    assert (
        row_by_id["equiv-a"]["behavior_hash"] == row_by_id["equiv-b"]["behavior_hash"]
    )
    assert (
        row_by_id["different"]["behavior_hash"] != row_by_id["equiv-a"]["behavior_hash"]
    )
    assert row_by_id["equiv-a"]["behavior_novelty"] < 1.0


def test_phase13_integrates_with_reports_tables_plots_and_artifacts(
    tmp_path: Path,
) -> None:
    final = build_final_report()
    markdown = render_final_report_markdown(final)
    tables = build_report_tables(final_report=final)
    plots = build_report_plots(phase13_report=final["semantic_novelty"])
    summary = export_report_artifacts(tmp_path, top_k=2)

    assert "program_semantics_and_novelty" in final["sections"]
    assert final["semantic_novelty"]["behavior_cluster_count"] >= 1
    assert "Program Semantics And Novelty" in markdown
    assert final["recommended_next_steps"][0]["step"] == "optional_cloud_scale_search"
    assert "novelty_table" in tables["tables"]
    assert "duplicate_behavior_clusters" in tables["tables"]
    assert "behavior_fingerprint" in plots["plots"]

    novelty_csv = tmp_path / "reports" / "tables" / "novelty_table.csv"
    clusters_csv = tmp_path / "reports" / "tables" / "duplicate_behavior_clusters.csv"
    fingerprint_json = tmp_path / "reports" / "plots" / "behavior_fingerprint.json"
    assert novelty_csv.is_file()
    assert clusters_csv.is_file()
    assert fingerprint_json.is_file()
    assert str(novelty_csv) in summary["tables"]
    assert str(clusters_csv) in summary["tables"]
    assert str(fingerprint_json) in summary["extra_plot_series"]

    with novelty_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert "semantic_novelty_score" in rows[0]

    fingerprint = json.loads(fingerprint_json.read_text(encoding="utf-8"))
    assert fingerprint["title"] == "Behavior Fingerprint"
    assert fingerprint["program_fingerprints"]


def test_cli_can_run_semantic_novelty(tmp_path: Path) -> None:
    output_dir = tmp_path / "semantic"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "heuristic_discovery",
            "run",
            "--benchmark",
            "semantic_novelty",
            "--candidate-count",
            "10",
            "--output-dir",
            str(output_dir),
        ],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    summary = json.loads((output_dir / "run_summary.json").read_text())
    assert payload["benchmark"] == "semantic_novelty"
    assert payload["behavior_cluster_count"] == summary["behavior_cluster_count"]
    assert payload["duplicate_behavior_cluster_count"] == len(
        summary["duplicate_behavior_clusters"]
    )
    assert summary["phase"] == 13
    assert summary["novelty_rows"]
