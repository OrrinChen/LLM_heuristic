from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from benchmarks.bin_packing.evaluator import (
    SeedCandidateProgram,
    build_seed_candidate_programs,
)
from benchmarks.bin_packing.instances import default_train_validation_test_suites
from program_search.parallel_runner import (
    PHASE17_CLAIM_BOUNDARY,
    ParallelEvaluationConfig,
    build_phase17_report,
    run_candidate_evaluation_batch,
)
from reports.artifacts import export_report_artifacts
from reports.tables import build_report_tables


def test_parallel_runner_matches_sequential_top_programs() -> None:
    train, validation, test = default_train_validation_test_suites(item_count=14)
    candidates = build_seed_candidate_programs(12)

    sequential = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="sequential"),
    )
    parallel = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="parallel", max_workers=2),
    )

    assert parallel.parallelism == "process"
    assert parallel.worker_count == 2
    assert parallel.top_program_ids == sequential.top_program_ids
    assert parallel.result_signature == sequential.result_signature
    assert parallel.stop_reason == "complete"


def test_checkpoint_resume_reconstructs_full_result(tmp_path: Path) -> None:
    train, validation, test = default_train_validation_test_suites(item_count=12)
    candidates = build_seed_candidate_programs(8)
    checkpoint = tmp_path / "phase17_checkpoint.json"

    full = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="sequential"),
    )
    partial = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(
            mode="sequential",
            candidate_budget=4,
            checkpoint_path=checkpoint,
        ),
    )
    resumed = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(
            mode="parallel",
            max_workers=2,
            checkpoint_path=checkpoint,
            resume=True,
        ),
    )

    assert partial.stop_reason == "candidate_budget_exhausted"
    assert len(partial.records) == 4
    assert resumed.stop_reason == "complete"
    assert resumed.result_signature == full.result_signature
    payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert payload["phase"] == 17
    assert len(payload["results"]) == len(candidates)


def test_failed_worker_is_recorded_without_losing_valid_candidates() -> None:
    train, validation, test = default_train_validation_test_suites(item_count=10)
    candidates = [
        SeedCandidateProgram(
            program_id="phase17-worker-crash",
            code=None,  # type: ignore[arg-type]
            explanation="forces unexpected worker exception",
        ),
        *build_seed_candidate_programs(6),
    ]

    result = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="parallel", max_workers=2),
    )

    failure = result.record_by_id["phase17-worker-crash"]
    assert failure.ok is False
    assert failure.failure_reason.startswith("worker_exception")
    assert result.successful_count > 0
    assert result.top_program_ids


def test_cost_budget_stops_and_preserves_checkpoint(tmp_path: Path) -> None:
    train, validation, test = default_train_validation_test_suites(item_count=10)
    checkpoint = tmp_path / "budget_checkpoint.json"

    result = run_candidate_evaluation_batch(
        build_seed_candidate_programs(8),
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(
            mode="parallel",
            max_workers=2,
            cost_budget=3.0,
            cost_per_candidate=1.0,
            checkpoint_path=checkpoint,
        ),
    )

    assert result.stop_reason == "cost_budget_exhausted"
    assert result.evaluated_count == 3
    assert result.estimated_cost == 3.0
    checkpoint_payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert len(checkpoint_payload["results"]) == 3
    assert checkpoint_payload["stop_reason"] == "cost_budget_exhausted"


def test_phase17_report_tables_and_artifacts_are_exported(tmp_path: Path) -> None:
    report = build_phase17_report(candidate_count=12, max_workers=2)
    tables = build_report_tables(phase17_report=report)
    summary = export_report_artifacts(tmp_path, top_k=2)

    assert report["phase"] == 17
    assert report["parallel_matches_sequential"] is True
    assert report["checkpoint_resume_matches_full"] is True
    assert report["failed_worker_recorded"] is True
    assert report["cost_budget_stop_reason"] == "cost_budget_exhausted"
    assert report["cloud_adapter_status"] == "dry_run_only"
    assert report["claim_boundary"] == PHASE17_CLAIM_BOUNDARY
    assert "parallel_runner_summary" in tables["tables"]
    assert "checkpoint_resume" in tables["tables"]
    assert (tmp_path / "reports" / "tables" / "parallel_runner_summary.csv").is_file()
    assert (tmp_path / "reports" / "tables" / "checkpoint_resume.csv").is_file()
    assert summary["phase17_checkpoint"].endswith("artifacts/phase17_checkpoint.json")
    assert (tmp_path / "artifacts" / "phase17_checkpoint.json").is_file()


def test_cli_parallel_runner_smoke(tmp_path: Path) -> None:
    result = _run_cli(
        "run",
        "--benchmark",
        "parallel_runner",
        "--candidate-count",
        "10",
        "--max-workers",
        "2",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["benchmark"] == "parallel_runner"
    assert payload["parallel_matches_sequential"] is True
    assert payload["cloud_adapter_status"] == "dry_run_only"
    assert (tmp_path / "run_summary.json").is_file()


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
