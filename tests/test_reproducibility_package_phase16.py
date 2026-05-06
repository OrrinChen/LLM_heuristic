from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from reports.reproducibility import (
    PHASE16_CLAIM_BOUNDARY,
    REPRODUCTION_PROFILE_NAMES,
    build_phase16_package,
    export_reproduction_package,
    render_reproduction_summary_markdown,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase16_profiles_are_deterministic_and_offline() -> None:
    assert REPRODUCTION_PROFILE_NAMES == (
        "local_demo",
        "external_small",
        "llm_optional",
    )

    for profile in REPRODUCTION_PROFILE_NAMES:
        package = build_phase16_package(profile=profile, output_dir="/tmp/o2-repro")

        assert package["phase"] == 16
        assert package["profile"] == profile
        assert package["deterministic"] is True
        assert package["requires_api_key"] is False
        assert package["requires_large_external_data"] is False
        assert package["live_llm_required"] is False
        assert package["claim_boundary"] == PHASE16_CLAIM_BOUNDARY
        assert (
            package["commands"]["reproduce"]
            == "PYTHONPATH=src python3 -m heuristic_discovery reproduce "
            f"--profile {profile} --output-dir /tmp/o2-repro"
        )

    with pytest.raises(ValueError, match="unknown reproduction profile"):
        build_phase16_package(profile="cloud")


def test_phase16_profiles_name_their_evidence_focus() -> None:
    local_demo = build_phase16_package(profile="local_demo")
    external_small = build_phase16_package(profile="external_small")
    llm_optional = build_phase16_package(profile="llm_optional")

    assert "reports/final_report.md" in local_demo["required_outputs"]
    assert (
        "reports/tables/external_generalization.csv" in external_small["evidence_focus"]
    )
    assert (
        "reports/tables/routing_external_generalization.csv"
        in external_small["evidence_focus"]
    )
    assert "reports/tables/llm_candidate_audit.csv" in llm_optional["evidence_focus"]
    assert "deterministic fallback" in llm_optional["description"]
    assert llm_optional["live_llm_required"] is False


def test_export_reproduction_package_writes_required_outputs(tmp_path: Path) -> None:
    summary = export_reproduction_package(tmp_path, profile="local_demo", top_k=2)

    manifest_path = tmp_path / "artifacts" / "reproduction_manifest.json"
    summary_path = tmp_path / "artifacts" / "reproduction_summary.md"

    assert summary["profile"] == "local_demo"
    assert summary["reproduction_manifest"] == str(manifest_path)
    assert summary["reproduction_summary"] == str(summary_path)
    assert (tmp_path / "reports" / "final_report.md").is_file()
    assert (tmp_path / "reports" / "tables" / "benchmark_comparison.csv").is_file()
    assert (tmp_path / "reports" / "plots" / "plot_series.json").is_file()
    assert (tmp_path / "artifacts" / "rerun_manifest.json").is_file()
    assert manifest_path.is_file()
    assert summary_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["profile"] == "local_demo"
    assert manifest["deterministic"] is True
    assert manifest["requires_api_key"] is False
    assert manifest["requires_large_external_data"] is False
    assert manifest["rerun_checks"]["all_code_hashes_match"] is True
    assert manifest["rerun_checks"]["all_scores_match"] is True
    assert "reports/final_report.md" in manifest["generated_artifacts"]
    assert "reports/tables/benchmark_comparison.csv" in manifest["generated_artifacts"]

    markdown = summary_path.read_text(encoding="utf-8")
    assert markdown.startswith("# O2 Reproduction Summary")
    assert "Profile: `local_demo`" in markdown
    assert "No API key required" in markdown
    assert "artifacts/reproduction_manifest.json" in markdown


def test_reproduction_summary_markdown_is_stable_and_auditable() -> None:
    package = build_phase16_package(profile="external_small", output_dir="/tmp/o2")
    markdown = render_reproduction_summary_markdown(package)

    assert "Profile: `external_small`" in markdown
    assert "## Commands" in markdown
    assert "## Required Outputs" in markdown
    assert "## Claim Boundary" in markdown
    assert "reports/tables/external_generalization.csv" in markdown
    assert PHASE16_CLAIM_BOUNDARY in markdown


def test_cli_reproduce_exports_local_demo_profile(tmp_path: Path) -> None:
    result = _run_cli(
        "reproduce",
        "--profile",
        "local_demo",
        "--output-dir",
        str(tmp_path),
        "--top-k",
        "2",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["profile"] == "local_demo"
    assert payload["deterministic"] is True
    assert payload["requires_api_key"] is False
    assert (tmp_path / "artifacts" / "reproduction_manifest.json").is_file()
    assert (tmp_path / "artifacts" / "reproduction_summary.md").is_file()


def test_reproducibility_docs_and_make_targets_are_present() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    validation = (PROJECT_ROOT / "VALIDATION.md").read_text(encoding="utf-8")
    runbook = (PROJECT_ROOT / "RUNBOOK.md").read_text(encoding="utf-8")
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    command = (
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo"
    )
    assert command in readme
    assert command in validation
    assert command in runbook
    for target in ("reproduce:", "test:", "report:", "demo:", "portfolio-demo:"):
        assert target in makefile


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
