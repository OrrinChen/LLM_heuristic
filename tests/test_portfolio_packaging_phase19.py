from __future__ import annotations

from pathlib import Path

from reports.artifacts import export_report_artifacts
from reports.portfolio import (
    PORTFOLIO_README_REQUIRED_HEADINGS,
    build_phase19_package,
    render_portfolio_brief_markdown,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase19_package_contains_resume_demo_and_claim_boundaries() -> None:
    package = build_phase19_package()

    assert package["phase"] == 19
    assert (
        "sandboxed LLM-driven OR heuristic discovery system"
        in (package["resume_bullets"][0])
    )
    assert package["demo_command"] == (
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile "
        "local_demo --output-dir /tmp/o2-demo --top-k 3"
    )
    assert package["claim_boundaries"]["does_not_claim"] == (
        "universal dominance, SOTA solver performance, or live LLM superiority"
    )
    assert package["recommended_next_phase"] == (
        "No required phase remains; optional broader crossover or release polish"
    )


def test_phase19_package_summarizes_architecture_results_and_safety() -> None:
    package = build_phase19_package()

    assert "seed heuristic library" in package["architecture_diagram"]
    assert len(package["benchmark_results"]) >= 10
    assert {
        "Online Bin Packing",
        "External Bin Packing",
        "External Routing",
        "Simple Routing",
        "Amazon-Style Routing",
    }.issubset({row["benchmark"] for row in package["benchmark_results"]})
    assert "subprocess" in package["safety_boundary"]
    assert "file access" in package["safety_boundary"]
    assert any("Live Gemini" in limitation for limitation in package["limitations"])
    assert any(
        "Semantic novelty" in limitation for limitation in package["limitations"]
    )
    assert any(
        "TSPLIB/CVRPLIB-style" in limitation for limitation in package["limitations"]
    )
    assert any("Failure repair" in limitation for limitation in package["limitations"])


def test_portfolio_brief_markdown_is_interview_ready() -> None:
    markdown = render_portfolio_brief_markdown(build_phase19_package())

    assert markdown.startswith("# O2 Portfolio Brief")
    assert "## Resume Bullets" in markdown
    assert "## Interview Demo" in markdown
    assert "## Benchmark Evidence" in markdown
    assert "## Safety Boundary" in markdown
    assert "## Conservative Claim" in markdown
    assert "universal dominance" in markdown


def test_readme_first_screen_contains_required_portfolio_sections() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    first_screen = readme[:4200]

    for heading in PORTFOLIO_README_REQUIRED_HEADINGS:
        assert heading in first_screen
    assert (
        "PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile "
        "local_demo --output-dir /tmp/o2-demo --top-k 3"
    ) in first_screen
    assert "seed heuristic library" in first_screen
    assert "Online Bin Packing" in first_screen
    assert "Safety Boundary" in first_screen
    assert "Limitations" in first_screen
    assert "does not claim universal dominance" in first_screen


def test_phase19_artifact_export_writes_portfolio_brief(tmp_path: Path) -> None:
    summary = export_report_artifacts(tmp_path, top_k=3)

    portfolio_path = tmp_path / "reports" / "portfolio_brief.md"
    assert summary["portfolio_brief"] == str(portfolio_path)
    assert portfolio_path.is_file()
    markdown = portfolio_path.read_text(encoding="utf-8")
    assert "## Resume Bullets" in markdown
    assert "## Interview Demo" in markdown
