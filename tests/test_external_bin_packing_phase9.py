from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from benchmarks.bin_packing.baselines import first_fit
from benchmarks.bin_packing.external import (
    build_phase9_report,
    default_external_train_validation_test_suites,
    parse_bpplib_bin_packing,
    parse_or_library_bin_packing,
)
from benchmarks.bin_packing.instances import InstanceDistribution, generate_instance
from reports.artifacts import export_report_artifacts
from reports.final_report import build_final_report, render_final_report_markdown
from reports.tables import build_report_tables

OR_LIBRARY_TEXT = """
2
or_a 6 10 3
2 8 4
6 5 5
or_b 5 10 3
7 3 5 5 4
"""


BPPLIB_TEXT = """
NAME: bpplib_a
CAPACITY: 10
ITEMS: 4
OPTIMUM: 2
WEIGHTS:
6
4
5
5
EOF
"""


def test_or_library_style_parser_loads_named_external_instances() -> None:
    instances = parse_or_library_bin_packing(
        OR_LIBRARY_TEXT,
        source="orlib-fixture",
    )

    assert len(instances) == 2
    assert instances[0].distribution == InstanceDistribution.EXTERNAL
    assert instances[0].instance_id == "or_a"
    assert instances[0].source == "orlib-fixture"
    assert instances[0].capacity == 10
    assert instances[0].items == (2.0, 8.0, 4.0, 6.0, 5.0, 5.0)
    assert instances[0].known_optimum == 3
    assert instances[1].seed != instances[0].seed


def test_bpplib_style_parser_loads_key_value_instance() -> None:
    instances = parse_bpplib_bin_packing(
        BPPLIB_TEXT,
        source="bpplib-fixture",
    )

    assert len(instances) == 1
    instance = instances[0]
    assert instance.distribution == InstanceDistribution.EXTERNAL
    assert instance.instance_id == "bpplib_a"
    assert instance.source == "bpplib-fixture"
    assert instance.capacity == 10
    assert instance.items == (6.0, 4.0, 5.0, 5.0)
    assert instance.known_optimum == 2


def test_external_default_suites_have_disjoint_train_validation_test_ids() -> None:
    train, validation, test = default_external_train_validation_test_suites()

    train_ids = {instance.instance_id for instance in train}
    validation_ids = {instance.instance_id for instance in validation}
    test_ids = {instance.instance_id for instance in test}

    assert train
    assert validation
    assert test
    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)
    assert all(
        instance.distribution == InstanceDistribution.EXTERNAL for instance in test
    )
    assert all(
        instance.known_optimum is not None for instance in train + validation + test
    )


def test_capacity_scaled_baseline_waste_uses_external_capacity() -> None:
    instance = generate_instance(
        InstanceDistribution.EXTERNAL,
        seed=1,
        capacity=10,
        items=(6, 4, 5, 5),
        instance_id="capacity_scaled",
        source="test",
        known_optimum=2,
    )

    result = first_fit(instance)

    assert result.is_valid is True
    assert result.bins_used == 2
    assert result.total_waste == 0
    assert result.average_waste == 0


def test_phase9_report_compares_external_and_synthetic_selection() -> None:
    report = build_phase9_report(candidate_count=24, synthetic_item_count=16)

    assert report["phase"] == 9
    assert report["benchmark"] == "bin_packing_external"
    assert report["external_split"]["train_count"] > 0
    assert report["external_split"]["validation_count"] > 0
    assert report["external_split"]["test_count"] > 0
    assert report["best_external_program_id"]
    assert report["best_external_test_score"] is not None
    assert report["synthetic_top_external_test_score"] is not None
    assert "synthetic_to_external_gap" in report
    assert "first_fit" in report["external_test_baseline_scores"]
    assert "best_fit_decreasing" in report["external_test_baseline_scores"]
    assert report["claim_boundary"] == (
        "external benchmark-style evidence only; no SOTA or universal dominance claim"
    )


def test_final_report_and_tables_include_external_benchmark_evidence() -> None:
    final = build_final_report()
    markdown = render_final_report_markdown(final)
    tables = build_report_tables(final_report=final)

    assert "external_benchmark_evidence" in final["sections"]
    assert final["external_benchmark"]["benchmark"] == "bin_packing_external"
    assert "External Benchmark Evidence" in markdown
    assert "bin_packing_external" in markdown
    assert "does not claim SOTA" in markdown
    assert "external_generalization" in tables["tables"]
    assert tables["external_generalization"]["rows"]


def test_report_artifact_export_writes_external_generalization_csv(
    tmp_path: Path,
) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    external_csv = tmp_path / "reports" / "tables" / "external_generalization.csv"
    assert str(external_csv) in summary["tables"]
    assert external_csv.is_file()
    with external_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert rows[0]["benchmark"] == "bin_packing_external"
    assert rows[0]["selection_source"] in {
        "external_validation",
        "synthetic_validation",
    }


def test_cli_can_run_bin_packing_external(tmp_path: Path) -> None:
    result = _run_cli(
        "run",
        "--benchmark",
        "bin_packing_external",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0
    assert "bin_packing_external" in result.stdout
    summary_path = tmp_path / "run_summary.json"
    assert summary_path.is_file()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["benchmark"] == "bin_packing_external"
    assert summary["phase"] == 9


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
