from __future__ import annotations

import csv
import json
from pathlib import Path

from reports.artifacts import export_report_artifacts
from reports.failure_taxonomy_v2 import (
    PHASE14_FAILURE_CATEGORIES,
    build_phase14_report,
    render_failure_cards_markdown,
)
from reports.final_report import build_final_report, render_final_report_markdown
from reports.portfolio import build_phase19_package
from reports.tables import build_report_tables
from reports.technical_report import build_phase18_report


def test_phase14_report_contains_full_failure_card_schema() -> None:
    report = build_phase14_report()

    assert report["phase"] == 14
    assert tuple(report["failure_categories"]) == PHASE14_FAILURE_CATEGORIES
    assert len(report["failure_cards"]) == 11
    assert {card["category"] for card in report["failure_cards"]} == set(
        PHASE14_FAILURE_CATEGORIES
    )

    for card in report["failure_cards"]:
        assert card["display_name"]
        assert card["example_program"]["program_id"]
        assert card["example_program"]["code_excerpt"]
        assert card["trigger_condition"]
        assert card["detected_by"]
        assert card["score_impact"]["impact_type"]
        assert card["score_impact"]["claim"]
        assert card["repair_strategy"]["strategy"]
        assert card["repair_strategy"]["expected_effect"]

    assert report["claim_boundary"] == (
        "failure taxonomy v2 explains deterministic failure modes and repair "
        "routes; it does not prove automated repair success on arbitrary LLM code"
    )


def test_phase14_report_tracks_repair_success_rates() -> None:
    report = build_phase14_report()
    rows = report["repair_success_rows"]

    assert {row["category"] for row in rows} >= {
        "invalid_syntax",
        "unsafe_code",
        "timeout",
        "llm_hallucinated_feature",
    }
    for row in rows:
        assert row["attempted_repairs"] >= row["successful_repairs"] >= 0
        assert 0.0 <= row["repair_success_rate"] <= 1.0
        assert row["repair_provider"]
        assert row["repair_strategy"]
        if row["successful_repairs"]:
            assert row["repaired_example_id"]


def test_failure_cards_markdown_renders_all_categories() -> None:
    report = build_phase14_report()
    markdown = render_failure_cards_markdown(report)

    assert markdown.startswith("# Failure Cards")
    for card in report["failure_cards"]:
        assert f"## {card['display_name']}" in markdown
        assert card["trigger_condition"] in markdown
        assert card["detected_by"] in markdown
    assert "Repair Strategy" in markdown


def test_phase14_report_tables_and_artifacts_are_exported(tmp_path: Path) -> None:
    report = build_phase14_report()
    tables = build_report_tables(phase14_report=report)

    assert "failure_taxonomy_v2" in tables["tables"]
    assert "repair_success_rate" in tables["tables"]
    assert len(tables["failure_taxonomy_v2"]["rows"]) == 11
    assert len(tables["repair_success_rate"]["rows"]) == len(
        report["repair_success_rows"]
    )

    summary = export_report_artifacts(tmp_path, top_k=3)
    failure_cards_path = tmp_path / "reports" / "failure_cards.md"
    taxonomy_path = tmp_path / "reports" / "tables" / "failure_taxonomy_v2.csv"
    repair_path = tmp_path / "reports" / "tables" / "repair_success_rate.csv"

    assert str(failure_cards_path) == summary["failure_cards"]
    assert failure_cards_path.exists()
    assert taxonomy_path.exists()
    assert repair_path.exists()

    taxonomy_rows = list(csv.DictReader(taxonomy_path.open()))
    repair_rows = list(csv.DictReader(repair_path.open()))
    assert len(taxonomy_rows) == 11
    assert len(repair_rows) >= 4
    assert "objective_gaming" in {row["category"] for row in taxonomy_rows}


def test_phase14_updates_report_narrative_and_next_phase() -> None:
    final = build_final_report()
    markdown = render_final_report_markdown(final)
    technical = build_phase18_report(final_report=final)
    portfolio = build_phase19_package(final_report=final)

    assert final["failure_taxonomy_v2"]["failure_card_count"] == 11
    assert (
        final["recommended_next_steps"][0]["step"]
        == "optional_routing_depth_or_release_polish"
    )
    assert "Failure Taxonomy v2" in markdown
    assert "repair success" in markdown
    assert technical["recommended_next_phase"] == (
        "No required phase remains; optional broader crossover or release polish"
    )
    assert portfolio["recommended_next_phase"] == (
        "No required phase remains; optional broader crossover or release polish"
    )


def test_phase14_cli_report_writes_required_files(tmp_path: Path) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    payload = json.loads(json.dumps(summary))
    assert payload["failure_cards"].endswith("reports/failure_cards.md")
    assert (tmp_path / "reports" / "failure_cards.md").read_text()
    assert (tmp_path / "reports" / "tables" / "failure_taxonomy_v2.csv").exists()
    assert (tmp_path / "reports" / "tables" / "repair_success_rate.csv").exists()
