from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from benchmarks.routing.baselines import (
    nearest_neighbor_plus_2opt,
    route_capacity_violation,
    route_vehicle_count,
)
from benchmarks.routing.external import (
    PHASE10_CLAIM_BOUNDARY,
    build_phase10_report,
    default_external_routing_suites,
    load_external_routing_instances,
    parse_cvrplib_vrp,
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

CVRPLIB_TEXT = """
NAME : toy_cvrp
TYPE : CVRP
COMMENT : tiny capacitated parser fixture
DIMENSION : 5
EDGE_WEIGHT_TYPE : EUC_2D
CAPACITY : 10
NODE_COORD_SECTION
1 0 0
2 3 0
3 3 4
4 0 4
5 1 2
DEMAND_SECTION
1 0
2 4
3 5
4 3
5 2
DEPOT_SECTION
1
-1
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


def test_cvrplib_parser_loads_capacity_demands_and_depot() -> None:
    instances = parse_cvrplib_vrp(CVRPLIB_TEXT, source="unit-cvrp")

    assert len(instances) == 1
    instance = instances[0]
    assert instance.distribution == RoutingDistribution.EXTERNAL
    assert instance.instance_id == "toy_cvrp"
    assert instance.source == "unit-cvrp"
    assert instance.vehicle_capacity == 10.0
    assert instance.depot.x == 0.0
    assert instance.depot.y == 0.0
    assert tuple(stop.stop_id for stop in instance.stops) == (
        "n002",
        "n003",
        "n004",
        "n005",
    )
    assert tuple(stop.demand for stop in instance.stops) == (4.0, 5.0, 3.0, 2.0)
    assert instance.distance_matrix[0][1] == 3.0


def test_cvrplib_loader_supports_files_and_directories(tmp_path: Path) -> None:
    first = tmp_path / "a.vrp"
    second = tmp_path / "b.vrp"
    first.write_text(CVRPLIB_TEXT, encoding="utf-8")
    second.write_text(CVRPLIB_TEXT.replace("toy_cvrp", "toy_cvrp_b"), encoding="utf-8")

    instances = load_external_routing_instances(tmp_path, parser="cvrplib")

    assert [instance.instance_id for instance in instances] == [
        "toy_cvrp",
        "toy_cvrp_b",
    ]
    assert {instance.vehicle_capacity for instance in instances} == {10.0}


def test_capacity_aware_route_distance_splits_vehicle_tours() -> None:
    instance = parse_cvrplib_vrp(CVRPLIB_TEXT)[0]
    route = tuple(stop.stop_id for stop in instance.stops)

    assert route_capacity_violation(instance, route) == 0.0
    assert route_vehicle_count(instance, route) == 2
    assert nearest_neighbor_plus_2opt(instance).is_valid is True


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
    assert "cvrplib" in report["external_formats"]
    assert report["capacitated_instance_count"] > 0
    assert report["best_external_test_capacity_violation"] == 0.0
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
    assert "CVRPLIB-style" in markdown
    assert "routing_external" in markdown
    assert "does not claim LKH" in markdown
    assert "routing_external_generalization" in tables["tables"]
    assert tables["routing_external_generalization"]["rows"]
    assert "capacity_violation" in tables["routing_external_generalization"]["rows"][0]


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


def test_cli_can_run_routing_external_with_cvrplib_file(tmp_path: Path) -> None:
    fixture = tmp_path / "toy.vrp"
    fixture.write_text(CVRPLIB_TEXT, encoding="utf-8")

    result = _run_cli(
        "run",
        "--benchmark",
        "routing_external",
        "--external-path",
        str(fixture),
        "--external-format",
        "cvrplib",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads((tmp_path / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["benchmark"] == "routing_external"
    assert summary["external_formats"] == ["cvrplib"]
    assert summary["capacitated_instance_count"] == 1


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
