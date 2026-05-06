from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from program_search.rerun_manifest import (
    build_bin_packing_rerun_manifest,
    rerun_manifest_entries,
)
from reports.artifacts import export_report_artifacts
from sandbox.subprocess_exec import execute_scoring_function_subprocess


def test_subprocess_sandbox_executes_valid_code_in_child_process() -> None:
    code = """
def score_candidate(state, candidate):
    return state["capacity"] - candidate["size"]
"""

    result = execute_scoring_function_subprocess(
        code,
        {"capacity": 10},
        {"size": 4},
        timeout_seconds=1.0,
    )

    assert result.ok is True
    assert result.value == 6.0
    assert result.failure_reason is None
    assert result.metadata["is_subprocess"] is True
    assert result.metadata["child_pid"] != os.getpid()


def test_subprocess_sandbox_fails_infinite_loop_by_wall_clock_timeout() -> None:
    code = """
def score_candidate(state, candidate):
    while True:
        pass
"""

    result = execute_scoring_function_subprocess(code, {}, {}, timeout_seconds=0.05)

    assert result.ok is False
    assert result.value is None
    assert result.failure_reason is not None
    assert result.failure_reason.code == "timeout"
    assert result.runtime < 1.0


@pytest.mark.parametrize(
    ("code", "failure_code"),
    [
        (
            "def score_candidate(state, candidate):\n    return open('x').read()\n",
            "dangerous_call",
        ),
        (
            "import os\n\ndef score_candidate(state, candidate):\n    return 0\n",
            "import_not_allowed",
        ),
        (
            "def score_candidate(state, candidate):\n    return eval('1 + 1')\n",
            "dangerous_call",
        ),
        (
            "def score_candidate(state, candidate):\n    return socket.socket()\n",
            "dangerous_name",
        ),
    ],
)
def test_subprocess_sandbox_preserves_static_security_failures(
    code: str,
    failure_code: str,
) -> None:
    result = execute_scoring_function_subprocess(code, {}, {}, timeout_seconds=1.0)

    assert result.ok is False
    assert result.failure_reason is not None
    assert result.failure_reason.code == failure_code
    assert result.metadata["is_subprocess"] is False


def test_subprocess_sandbox_fails_memory_heavy_code_when_limit_supported() -> None:
    code = """
def score_candidate(state, candidate):
    blob = [0] * 50000000
    return len(blob)
"""

    result = execute_scoring_function_subprocess(
        code,
        {},
        {},
        timeout_seconds=2.0,
        memory_limit_mb=64,
    )

    assert result.ok is False
    assert result.failure_reason is not None
    assert result.failure_reason.code in {
        "memory_limit_exceeded",
        "process_error",
        "runtime_error",
        "timeout",
        "memory_limit_unsupported",
    }


def test_rerun_manifest_records_hashes_and_stable_scores() -> None:
    manifest = build_bin_packing_rerun_manifest(
        top_k=2,
        generations=1,
        population_size=8,
        offspring_per_generation=4,
        item_count=12,
        random_seed=17,
    )

    assert manifest["schema_version"] == 1
    assert manifest["benchmark"] == "bin_packing"
    assert len(manifest["entries"]) == 2
    first = manifest["entries"][0]
    assert first["code_hash"].startswith("sha256:")
    assert first["candidate_id"]
    assert first["python_version"]
    assert first["package_version"] == "0.1.0"
    assert first["random_seeds"]["evolution"] == 17

    reruns = rerun_manifest_entries(manifest)

    assert len(reruns["results"]) == 2
    assert reruns["results"][0]["ok"] is True
    assert reruns["results"][0]["score"] == first["score"]
    assert reruns["results"][0]["code_hash_matches"] is True


def test_export_report_artifacts_writes_evidence_package(tmp_path: Path) -> None:
    summary = export_report_artifacts(tmp_path, top_k=3)

    assert summary["output_dir"] == str(tmp_path)
    assert summary["png_rendered"] is False
    assert (tmp_path / "reports" / "final_report.md").is_file()
    assert (tmp_path / "reports" / "technical_report.md").is_file()
    assert "technical_report.md" in summary["technical_report"]
    assert (tmp_path / "reports" / "tables" / "benchmark_comparison.csv").is_file()
    assert (tmp_path / "reports" / "tables" / "failure_taxonomy.csv").is_file()
    assert (tmp_path / "reports" / "plots" / "plot_series.json").is_file()
    assert (tmp_path / "reports" / "plots" / "pareto_frontier_main.svg").is_file()
    assert summary["pareto_frontier_main_svg"].endswith(
        "reports/plots/pareto_frontier_main.svg"
    )
    assert (tmp_path / "artifacts" / "rerun_manifest.json").is_file()
    top_programs = sorted((tmp_path / "artifacts" / "top_programs").glob("*.py"))
    assert len(top_programs) == 3
    assert top_programs[0].read_text(encoding="utf-8").startswith("# candidate_id:")

    manifest = json.loads(
        (tmp_path / "artifacts" / "rerun_manifest.json").read_text(encoding="utf-8")
    )
    assert len(manifest["entries"]) == 3


def test_cli_report_exports_artifacts(tmp_path: Path) -> None:
    result = _run_cli("report", "--output-dir", str(tmp_path))

    assert result.returncode == 0
    assert "final_report.md" in result.stdout
    assert "technical_report.md" in result.stdout
    assert (tmp_path / "reports" / "final_report.md").is_file()
    assert (tmp_path / "reports" / "technical_report.md").is_file()


def test_cli_run_inspect_and_rerun_manifest(tmp_path: Path) -> None:
    run_result = _run_cli(
        "run",
        "--benchmark",
        "bin_packing",
        "--generations",
        "1",
        "--output-dir",
        str(tmp_path),
    )
    inspect_result = _run_cli("inspect", "--top-k", "2")
    manifest_result = _run_cli(
        "rerun-manifest",
        "--output-dir",
        str(tmp_path),
        "--top-k",
        "2",
    )

    assert run_result.returncode == 0
    assert "generation_count" in run_result.stdout
    assert (tmp_path / "run_summary.json").is_file()
    assert inspect_result.returncode == 0
    assert "candidate_id" in inspect_result.stdout
    assert manifest_result.returncode == 0
    assert "code_hash_matches" in manifest_result.stdout
    assert (tmp_path / "artifacts" / "rerun_manifest.json").is_file()


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
