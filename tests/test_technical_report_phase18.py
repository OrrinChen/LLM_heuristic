from __future__ import annotations

from pathlib import Path

from reports.artifacts import export_report_artifacts
from reports.technical_report import (
    TECHNICAL_REPORT_SECTIONS,
    build_phase18_report,
    render_technical_report_markdown,
)


def test_phase18_report_has_paper_sections_and_conservative_claims() -> None:
    report = build_phase18_report()

    assert report["phase"] == 18
    assert tuple(section["id"] for section in report["sections"]) == (
        TECHNICAL_REPORT_SECTIONS
    )
    assert report["title"] == (
        "Sandboxed LLM Program Search for OR Heuristic Discovery"
    )
    assert "compact heuristic scoring programs" in report["abstract"]
    assert "subprocess sandboxing" in report["abstract"]
    assert "universal dominance" in report["claim_boundaries"]["does_not_claim"]
    assert report["recommended_next_phase"] == (
        "No required phase remains; project is release-frozen and "
        "portfolio-ready. Optional future work: broader crossover, paid cloud "
        "execution, or larger public benchmark corpora."
    )


def test_phase18_report_sections_map_to_existing_evidence() -> None:
    report = build_phase18_report()
    section_by_id = {section["id"]: section for section in report["sections"]}

    assert section_by_id["benchmarks"]["evidence_refs"] == (
        "bin_packing",
        "simple_routing",
        "amazon_routing",
        "external_bin_packing",
        "external_routing",
    )
    assert section_by_id["ablation"]["evidence_refs"] == (
        "ablation_summary.csv",
        "generation_curve_by_method.json",
    )
    assert section_by_id["generalization"]["evidence_refs"] == (
        "robustness_summary.csv",
        "worst_generalization_gaps.csv",
        "pareto_frontier.csv",
    )
    assert section_by_id["failure_analysis"]["evidence_refs"] == (
        "failure_taxonomy.csv",
        "failure_taxonomy_v2.csv",
    )
    assert section_by_id["failure_taxonomy_v2"]["evidence_refs"] == (
        "failure_cards.md",
        "failure_taxonomy_v2.csv",
        "repair_success_rate.csv",
    )


def test_phase18_markdown_renders_required_paper_structure() -> None:
    markdown = render_technical_report_markdown(build_phase18_report())

    assert markdown.startswith(
        "# Sandboxed LLM Program Search for OR Heuristic Discovery"
    )
    for heading in (
        "Abstract",
        "Problem",
        "Why Heuristic Discovery Matters",
        "System Design",
        "Sandbox and Safety Boundary",
        "Benchmarks",
        "Search Loop",
        "External Benchmark Evidence",
        "Ablation",
        "LLM As Operator",
        "Program Semantics And Novelty",
        "Generalization",
        "Failure Analysis",
        "Failure Taxonomy v2",
        "Limitations",
        "Conclusion",
    ):
        assert f"## {heading}" in markdown
    assert "The system does not claim universal dominance" in markdown
    assert "No required phase remains" in markdown


def test_phase18_technical_report_is_exported_with_artifact_package(
    tmp_path: Path,
) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    technical_report = tmp_path / "reports" / "technical_report.md"
    assert summary["technical_report"] == str(technical_report)
    assert technical_report.is_file()
    markdown = technical_report.read_text(encoding="utf-8")
    assert "## Sandbox and Safety Boundary" in markdown
    assert "## Conclusion" in markdown
