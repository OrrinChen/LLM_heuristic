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
        "## What It Is",
        "## Why It Matters",
        "## One-Command Demo",
        "## Core Architecture",
        "## Benchmark Evidence",
        "## Safety Boundary",
        "## Limitations",
    ):
        assert heading in first_screen
    assert "Current status:" not in first_screen
    assert "Phase 0 complete" not in first_screen
    assert "Phase 10A/10B/10C" not in first_screen
    assert "does not claim universal dominance" in first_screen


def test_release_validation_checklist_is_documented() -> None:
    validation = _read("VALIDATION.md")

    assert "## Release Validation Checklist" in validation
    for required in (
        "python3 -m pytest -q",
        "python3 -m ruff check .",
        "python3 -m ruff format --check .",
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo",
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile "
        "external_small",
        "PYTHONPATH=src python3 -m heuristic_discovery report",
        "Secret scan",
        "Large-file scan",
    ):
        assert required in validation


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
