from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_release_summary_is_concise_and_interview_ready() -> None:
    summary = _read("RELEASE_SUMMARY.md")

    assert summary.startswith("# O2 Release Summary")
    for heading in (
        "## Project Thesis",
        "## System Architecture",
        "## Main Evidence Artifacts",
        "## One-Command Reproduction",
        "## Conservative Claim Boundary",
        "## Known Limitations",
        "## Resume Bullets",
        "## Interview Talking Points",
    ):
        assert heading in summary
    assert "heuristic design can be automated as constrained program search" in summary
    assert (
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo"
        in summary
    )
    assert "does not claim universal dominance" in summary
    assert "Sandboxed LLM-driven OR heuristic discovery system" in summary


def test_readme_first_screen_is_release_focused_not_phase_dump() -> None:
    readme = _read("README.md")
    first_screen = readme[:4200]

    for heading in (
        "## Recruiter Snapshot",
        "## What It Is",
        "## Why It Matters",
        "## One-Command Demo",
        "## Representative Heuristic",
        "## Pareto Evidence",
        "## Search Flow",
        "## Benchmark Evidence",
        "## Safety Boundary",
        "## Limitations",
    ):
        assert heading in first_screen
    assert "make portfolio-demo" in first_screen
    assert "AI agent infra" in first_screen
    assert "optimization tooling" in first_screen
    assert "seed-001-load_balancer" in first_screen
    assert "def score_bin" in first_screen
    assert "does not require an API key" in first_screen
    assert "Live Gemini mutation is optional" in first_screen
    assert "Before heuristic" in first_screen
    assert "Discovered heuristic" in first_screen
    assert "Score/runtime trade-off" in first_screen
    assert "7.75" in first_screen
    assert "0.023680" in first_screen
    assert "examples/top_program_before_after.md" in first_screen
    assert "docs/safety_boundary.md" in first_screen
    assert "reports/plots/pareto_frontier_main.svg" in first_screen
    assert "Current status:" not in first_screen
    assert "Phase 0 complete" not in first_screen
    assert "Phase 10A/10B/10C" not in first_screen
    assert "does not claim universal dominance" in first_screen


def test_before_after_example_shows_archived_heuristic_not_solver() -> None:
    example = _read("examples/top_program_before_after.md")

    assert example.startswith("# Top Program Before / After")
    assert "## Before" in example
    assert "## After" in example
    assert "seed-001-load_balancer" in example
    assert "def score_bin" in example
    assert "return abs(projected - 0.01)" in example
    assert "Line-by-line" in example
    assert "archived scoring function" in example
    assert "not a full solver" in example


def test_short_safety_boundary_doc_frontloads_llm_constraints() -> None:
    safety = _read("docs/safety_boundary.md")

    assert safety.startswith("# Safety Boundary")
    for phrase in (
        "narrow scoring-function interface",
        "static validation",
        "subprocess sandbox",
        "wall-clock timeout",
        "memory limit",
        "structured failure",
        "No file access",
        "No network access",
        "No unrestricted imports",
        "No credential access",
        "not letting an LLM write arbitrary code",
    ):
        assert phrase in safety


def test_release_summary_links_visual_evidence_and_api_key_boundary() -> None:
    summary = _read("RELEASE_SUMMARY.md")

    assert "## What The Heuristic Looks Like" in summary
    assert "examples/top_program_before_after.md" in summary
    assert "reports/plots/pareto_frontier_main.svg" in summary
    assert "default reproduction does not require an API key" in summary
    assert "superiority on Amazon data is not claimed" in summary


def test_release_validation_checklist_is_documented() -> None:
    validation = _read("VALIDATION.md")

    assert "## Release Validation Checklist" in validation
    for required in (
        "python3 -m pytest -q",
        "python3 -m ruff check .",
        "python3 -m ruff format --check .",
        "make portfolio-demo",
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo",
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile "
        "external_small",
        "PYTHONPATH=src python3 -m heuristic_discovery report",
        "Secret scan",
        "Large-file scan",
    ):
        assert required in validation


def test_portfolio_demo_make_target_is_short_and_api_key_free() -> None:
    makefile = _read("Makefile")
    readme = _read("README.md")
    runbook = _read("RUNBOOK.md")

    assert ".PHONY:" in makefile
    assert "portfolio-demo" in makefile
    assert "portfolio-demo:" in makefile
    assert (
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile "
        "local_demo --output-dir /tmp/o2-portfolio-demo --top-k 3"
    ) in makefile
    assert "GEMINI_API_KEY" not in makefile
    assert "make portfolio-demo" in readme
    assert "make portfolio-demo" in runbook


def test_release_freeze_status_and_future_work_are_explicit() -> None:
    for path in ("ROADMAP.md", "TASK_MEMORY.md", "RUNBOOK.md", "VALIDATION.md"):
        text = _read(path)
        assert "release-frozen" in text
        assert "portfolio-ready" in text
        assert "broader crossover" in text
        assert "paid cloud execution" in text
        assert "larger public benchmark corpora" in text


def test_release_claim_language_avoids_unsafe_shortcuts() -> None:
    checked_text = "\n".join(
        _read(path)
        for path in (
            "README.md",
            "RELEASE_SUMMARY.md",
            "ROADMAP.md",
            "RUNBOOK.md",
            "VALIDATION.md",
            "TASK_MEMORY.md",
            "docs/safety_boundary.md",
            "examples/top_program_before_after.md",
            "reports/final_report.md",
            "reports/portfolio_brief.md",
            "reports/technical_report.md",
        )
    ).lower()

    forbidden_phrases = (
        "beats lkh",
        "beats cvrp",
        "beats vrptw",
        "production routing solver",
        "real amazon superiority",
        "llm solves or",
        "llm solves operations research",
        "state-of-the-art performance",
        "sota performance",
        "universally dominates",
    )
    for phrase in forbidden_phrases:
        assert phrase not in checked_text
