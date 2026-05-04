from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from llm.live_experiment import (
    LLMExperimentConfig,
    ScriptedLLMProvider,
    build_phase12_report,
)
from reports.artifacts import export_report_artifacts
from reports.final_report import build_final_report, render_final_report_markdown
from reports.tables import build_report_tables

VALID_MUTATION = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.05) - 0.01 * bin_features["items_in_bin"]
"""

UNSAFE_MUTATION = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return globals()["hidden_solution"]
"""


def test_phase12_report_uses_deterministic_fallback_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    report = build_phase12_report(
        config=LLMExperimentConfig(candidate_budget=3, item_count=12)
    )

    assert report["phase"] == 12
    assert report["benchmark"] == "live_llm_mutation"
    assert report["live_provider_configured"] is False
    assert report["methods"] == (
        "deterministic_fallback",
        "llm_repair",
        "live_gemini",
    )
    live_row = _row_by_method(report["operator_comparison"], "live_gemini")
    assert live_row["provider_status"] == "not_configured"
    assert live_row["evaluated_candidates"] == 0

    candidate = report["candidate_audit"][0]
    assert candidate["model_name"] == "deterministic-fallback"
    assert candidate["prompt_version"] == "score-bin-mutation-v1"
    assert candidate["parent_ids"]
    assert candidate["raw_response_hash"]
    assert candidate["cleaned_code_hash"]
    assert candidate["input_tokens"] > 0
    assert candidate["output_tokens"] > 0
    assert candidate["latency_seconds"] >= 0.0
    assert candidate["static_check_result"] in {"ok", "dangerous_name"}
    assert "raw_response" not in candidate
    assert "test-secret" not in json.dumps(report)
    assert "AIza" not in json.dumps(report)


def test_fake_live_provider_records_metadata_and_never_bypasses_sandbox() -> None:
    provider = ScriptedLLMProvider(
        model_name="gemini-test",
        temperature=0.17,
        responses=(VALID_MUTATION, UNSAFE_MUTATION),
    )

    report = build_phase12_report(
        config=LLMExperimentConfig(candidate_budget=2, item_count=12),
        live_provider=provider,
    )

    live_row = _row_by_method(report["operator_comparison"], "live_gemini")
    assert live_row["provider_status"] == "configured"
    assert live_row["model_name"] == "gemini-test"
    assert live_row["evaluated_candidates"] == 2

    live_records = [
        row for row in report["candidate_audit"] if row["method"] == "live_gemini"
    ]
    assert live_records[0]["static_check_result"] == "ok"
    assert live_records[0]["sandbox_result"] == "ok"
    assert live_records[0]["score"] is not None
    assert live_records[0]["temperature"] == 0.17
    assert live_records[1]["static_check_result"] == "dangerous_call"
    assert live_records[1]["sandbox_result"] == "rejected_before_sandbox"
    assert live_records[1]["score"] is None
    assert live_records[1]["failure_reason"] == "dangerous_call"
    assert "hidden_solution" not in json.dumps(report)


def test_repair_provider_records_prompt_version_and_repaired_score() -> None:
    repair_provider = ScriptedLLMProvider(
        model_name="gemini-repair-test",
        responses=(VALID_MUTATION,),
    )

    report = build_phase12_report(
        config=LLMExperimentConfig(candidate_budget=1, item_count=12),
        repair_provider=repair_provider,
    )

    repair_records = [
        row for row in report["candidate_audit"] if row["method"] == "llm_repair"
    ]
    assert len(repair_records) == 1
    assert repair_records[0]["model_name"] == "gemini-repair-test"
    assert repair_records[0]["prompt_version"] == "score-bin-repair-v1"
    assert repair_records[0]["repair_of_failure_reason"] == "dangerous_name"
    assert repair_records[0]["sandbox_result"] == "ok"
    assert repair_records[0]["score"] is not None


def test_final_report_tables_and_artifacts_include_phase12(tmp_path: Path) -> None:
    final = build_final_report()
    markdown = render_final_report_markdown(final)
    tables = build_report_tables(final_report=final)
    summary = export_report_artifacts(tmp_path, top_k=2)

    assert "llm_live_mutation_v1" in final["sections"]
    assert final["live_llm"]["benchmark"] == "live_llm_mutation"
    assert "LLM Live Mutation v1" in markdown
    assert (
        "one mutation operator inside a constrained program-search system" in markdown
    )
    assert final["recommended_next_steps"][0]["step"] == "optional_cloud_scale_search"
    assert "llm_operator_comparison" in tables["tables"]
    assert "llm_candidate_audit" in tables["tables"]

    operator_csv = tmp_path / "reports" / "tables" / "llm_operator_comparison.csv"
    audit_csv = tmp_path / "reports" / "tables" / "llm_candidate_audit.csv"
    assert str(operator_csv) in summary["tables"]
    assert str(audit_csv) in summary["tables"]
    rows = list(csv.DictReader(audit_csv.open(encoding="utf-8")))
    assert rows
    assert "raw_response" not in rows[0]
    assert "cleaned_code_hash" in rows[0]


def test_cli_can_run_live_llm_with_deterministic_default(tmp_path: Path) -> None:
    output_dir = tmp_path / "cli-live-llm"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "heuristic_discovery",
            "run",
            "--benchmark",
            "live_llm",
            "--candidate-count",
            "2",
            "--item-count",
            "12",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert "live_llm" in result.stdout
    summary = json.loads((output_dir / "run_summary.json").read_text())
    assert summary["benchmark"] == "live_llm_mutation"
    assert summary["live_provider_configured"] is False
    assert summary["candidate_audit"]


def _row_by_method(rows: object, method: str) -> dict[str, object]:
    for row in rows:
        if row["method"] == method:
            return row
    raise AssertionError(f"missing method row: {method}")
