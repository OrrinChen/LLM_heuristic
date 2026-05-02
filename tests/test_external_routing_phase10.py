from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from benchmarks.routing.baselines import nearest_neighbor_plus_2opt
from benchmarks.routing.external import (
    PHASE10_CLAIM_BOUNDARY,
    build_phase10_report,
    default_external_routing_suites,
    load_external_routing_instances,
    parse_tsplib_tsp,
)
from benchmarks.routing.instances import RoutingDistribution
from reports.artifacts import export_report_artifacts
from reports.final_report import build_final_report, render_final_report_markdown
from reports.tables import build_report_tables

TSPLIB_TEXT = """
NAME: toy_tsp
TYPE: TSP
COMMENT: tiny parser fixture
DIMENSION: 5
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0 0
2 3 0
3 3 4
4 0 4
5 1 2
EOF
"""


def test_tsplib_parser_loads_depot_stops_and_distance_matrix() -> None:
    instances = parse_tsplib_tsp(TSPLIB_TEXT, source="unit-fixture")

    assert len(instances) == 1
    instance = instances[0]
    assert instance.distribution == RoutingDistribution.EXTERNAL
    assert instance.instance_id == "toy_tsp"
    assert instance.source == "unit-fixture"
    assert instance.depot.x == 0.0
    assert instance.depot.y == 0.0
    assert tuple(stop.stop_id for stop in instance.stops) == (
        "n002",
        "n003",
        "n004",
        "n005",
    )
    assert instance.distance_matrix[0][1] == 3.0
    assert instance.distance_matrix[1][2] == 4.0
    assert instance.distance_matrix[0][0] == 0.0


def test_load_external_routing_instances_supports_directory(tmp_path: Path) -> None:
    (tmp_path / "a.tsp").write_text(TSPLIB_TEXT, encoding="utf-8")
    (tmp_path / "b.tsp").write_text(
        TSPLIB_TEXT.replace("toy_tsp", "toy_tsp_b"),
        encoding="utf-8",
    )

    instances = load_external_routing_instances(tmp_path)

    assert [instance.instance_id for instance in instances] == ["toy_tsp", "toy_tsp_b"]
    assert {instance.source for instance in instances} == {"a.tsp", "b.tsp"}


def test_external_routing_default_suites_have_disjoint_splits() -> None:
    train, validation, test = default_external_routing_suites()

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
        instance.distribution == RoutingDistribution.EXTERNAL for instance in test
    )


def test_phase10_report_compares_external_baselines_and_candidates() -> None:
    report = build_phase10_report(candidate_count=8, synthetic_stop_count=8)

    assert report["phase"] == 10
    assert report["benchmark"] == "routing_external"
    assert report["external_split"]["train_count"] > 0
    assert report["external_split"]["validation_count"] > 0
    assert report["external_split"]["test_count"] > 0
    assert report["best_external_program_id"]
    assert report["best_external_test_score"] is not None
    assert report["synthetic_top_external_test_score"] is not None
    assert "nearest_neighbor" in report["external_test_baseline_scores"]
    assert "cheapest_insertion" in report["external_test_baseline_scores"]
    assert "two_opt" in report["external_test_baseline_scores"]
    assert (
        report["external_test_baseline_scores"]["nearest_neighbor_plus_2opt"]
        <= (report["external_test_baseline_scores"]["nearest_neighbor"])
    )
    assert report["claim_boundary"] == PHASE10_CLAIM_BOUNDARY


def test_external_routing_baseline_reuses_two_opt_on_fixture() -> None:
    instance = parse_tsplib_tsp(TSPLIB_TEXT)[0]

    result = nearest_neighbor_plus_2opt(instance)

    assert result.is_valid is True
    assert set(result.route) == {stop.stop_id for stop in instance.stops}
    assert result.total_distance > 0


def test_final_report_and_tables_include_external_routing_evidence() -> None:
    final = build_final_report()
    markdown = render_final_report_markdown(final)
    tables = build_report_tables(final_report=final)

    assert "routing_external_benchmark_evidence" in final["sections"]
    assert final["routing_external"]["benchmark"] == "routing_external"
    assert "External Routing Evidence" in markdown
    assert "routing_external" in markdown
    assert "does not claim LKH" in markdown
    assert "routing_external_generalization" in tables["tables"]
    assert tables["routing_external_generalization"]["rows"]


def test_report_artifact_export_writes_routing_external_generalization_csv(
    tmp_path: Path,
) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    routing_csv = (
        tmp_path / "reports" / "tables" / "routing_external_generalization.csv"
    )
    assert str(routing_csv) in summary["tables"]
    assert routing_csv.is_file()
    with routing_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert rows[0]["benchmark"] == "routing_external"
    assert rows[0]["selection_source"] in {
        "external_validation",
        "synthetic_validation",
    }


def test_cli_can_run_routing_external(tmp_path: Path) -> None:
    result = _run_cli(
        "run",
        "--benchmark",
        "routing_external",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0
    assert "routing_external" in result.stdout
    summary_path = tmp_path / "run_summary.json"
    assert summary_path.is_file()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["benchmark"] == "routing_external"
    assert summary["phase"] == 10


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
