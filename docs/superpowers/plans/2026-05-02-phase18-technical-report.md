# Phase 18 Technical Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package O2's system design, safety boundary, benchmark evidence, ablation, Pareto frontier, failures, limitations, and conclusions into a conservative research-style technical report.

**Architecture:** Add a focused `reports.technical_report` module that derives a structured Phase 18 report from the existing final report evidence and renders it to Markdown. Extend artifact export so the deterministic `report` CLI writes `reports/technical_report.md` beside `reports/final_report.md`; then update docs and phase memory so Phase 19 becomes the next roadmap step.

**Tech Stack:** Python stdlib, existing `reports.final_report`, pytest, ruff.

---

### Task 1: Add Phase 18 Report Tests

**Files:**
- Create: `tests/test_technical_report_phase18.py`

- [x] **Step 1: Write the failing test**

```python
from reports.technical_report import (
    TECHNICAL_REPORT_SECTIONS,
    build_phase18_report,
    render_technical_report_markdown,
)

def test_phase18_report_has_paper_sections_and_conservative_claims():
    report = build_phase18_report()
    assert report["phase"] == 18
    assert tuple(section["id"] for section in report["sections"]) == TECHNICAL_REPORT_SECTIONS
    assert "compact heuristic scoring programs" in report["abstract"]
    assert "universal dominance" in report["claim_boundaries"]["does_not_claim"]

def test_phase18_markdown_renders_required_structure():
    markdown = render_technical_report_markdown(build_phase18_report())
    assert markdown.startswith("# Sandboxed LLM Program Search for OR Heuristic Discovery")
    for heading in ("Problem", "Why Heuristic Discovery Matters", "System Design", "Sandbox and Safety Boundary", "Benchmarks", "Search Loop", "External Benchmark Evidence", "Ablation", "Generalization", "Failure Analysis", "Limitations", "Conclusion"):
        assert f"## {heading}" in markdown
    assert "Phase 19" in markdown
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_technical_report_phase18.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'reports.technical_report'`.

### Task 2: Implement Structured Technical Report

**Files:**
- Create: `src/reports/technical_report.py`

- [x] **Step 1: Add minimal builder and renderer**

Create a report dictionary with:

```python
{
    "phase": 18,
    "title": "Sandboxed LLM Program Search for OR Heuristic Discovery",
    "sections": ...,
    "abstract": ...,
    "claim_boundaries": ...,
    "recommended_next_phase": "Phase 19: Resume / Portfolio Packaging",
}
```

- [x] **Step 2: Run focused tests**

Run: `python3 -m pytest tests/test_technical_report_phase18.py -q`

Expected: PASS.

### Task 3: Export Report Artifact

**Files:**
- Modify: `src/reports/artifacts.py`
- Modify: `tests/test_hardening_milestone.py`

- [x] **Step 1: Add artifact expectation**

Extend artifact export tests to assert `reports/technical_report.md` exists and is included in the CLI JSON output.

- [x] **Step 2: Update artifact export**

Import `build_phase18_report` and `render_technical_report_markdown`, write `reports/technical_report.md`, and include `"technical_report"` in the returned summary.

- [x] **Step 3: Run focused tests**

Run: `python3 -m pytest tests/test_technical_report_phase18.py tests/test_hardening_milestone.py -q`

Expected: PASS.

### Task 4: Advance Next Step And Docs

**Files:**
- Modify: `src/reports/final_report.py`
- Modify: `tests/test_final_report.py`
- Modify: `tests/test_report_tables_plots_and_live_llm.py`
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`

- [x] **Step 1: Update next recommended phase**

Change final report next step from `research_style_report` to `resume_portfolio_packaging`.

- [x] **Step 2: Update docs**

Mark Phase 18 complete, document technical report validation and smoke commands, and record Phase 18 changes in task memory.

- [x] **Step 3: Regenerate deterministic artifacts**

Run: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`

Expected: `reports/technical_report.md` and updated `reports/tables/recommended_next_steps.csv`.

### Task 5: Validate And Commit

**Files:**
- All touched Phase 18 files.

- [x] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [x] **Step 2: Run smoke checks**

Run direct Phase 18 smoke and CLI report smoke.

- [x] **Step 3: Commit only this project**

Run: `git commit -m "docs: add research-style technical report" --only -- .`

Expected: one commit containing Phase 18 implementation, tests, artifacts, and docs.
