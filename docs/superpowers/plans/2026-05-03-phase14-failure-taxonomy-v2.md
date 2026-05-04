# Phase 14 Failure Taxonomy v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade O2 failure reporting from category counts to auditable failure cards with triggers, detectors, score impact, and repair evidence.

**Architecture:** Add a deterministic `reports.failure_taxonomy_v2` builder that composes existing Phase 8, Phase 12, Phase 13, Phase 15, and external benchmark evidence into 11 explicit failure categories. Integrate the new rows into report tables, artifact export, final report, technical report, portfolio brief, docs, and generated reports without changing candidate execution or benchmark claims.

**Tech Stack:** Python stdlib, existing report builders, CSV/Markdown artifact export, pytest, ruff.

---

### Task 1: Add Phase 14 Tests

**Files:**
- Create: `tests/test_failure_taxonomy_v2_phase14.py`

- [x] **Step 1: Write failing tests**

Add tests that require:

- `build_phase14_report()` returns phase 14 metadata and all 11 categories:
  invalid syntax, unsafe code, timeout, over-complex code, overfit small instances,
  poor external transfer, baseline-dominated, runtime too slow, behavior duplicate,
  LLM hallucinated feature, and objective gaming.
- Every failure card has `example_program`, `trigger_condition`,
  `detected_by`, `score_impact`, and `repair_strategy`.
- Repair rows include attempted count, repaired count, repair success rate, and
  repaired example id.
- `render_failure_cards_markdown()` renders one section per card.
- `build_report_tables()` includes `failure_taxonomy_v2` and
  `repair_success_rate`.
- `export_report_artifacts()` writes `reports/failure_cards.md`,
  `reports/tables/failure_taxonomy_v2.csv`, and
  `reports/tables/repair_success_rate.csv`.
- Final report, technical report, and portfolio package recommend Phase 16 after
  Phase 14.

- [x] **Step 2: Run red test**

Run: `python3 -m pytest tests/test_failure_taxonomy_v2_phase14.py -q`

Expected: FAIL because `reports.failure_taxonomy_v2` does not exist.

### Task 2: Implement Failure Taxonomy v2 Builder

**Files:**
- Create: `src/reports/failure_taxonomy_v2.py`

- [x] **Step 1: Define category schema**

Create constants for the 11 Phase 14 categories and card fields.

- [x] **Step 2: Compose deterministic evidence**

Use existing report outputs to derive examples and impacts:

- Phase 8 for invalid, timeout, complexity, overfit, and trade-off failures.
- Phase 9 / Phase 10 external rows for poor external transfer and
  baseline-dominated cases.
- Phase 12 candidate audit for LLM hallucinated feature and repair rows.
- Phase 13 duplicate behavior clusters for behavior duplicate.
- Phase 15 Pareto rows for runtime-too-slow and objective-gaming trade-offs.

- [x] **Step 3: Add repair success summaries**

Return deterministic repair rows with attempted count, repaired count,
success rate, repair provider, and repaired example id.

- [x] **Step 4: Render failure cards markdown**

Render one concise card per failure type with trigger, detector, score impact,
repair strategy, and example code excerpt.

### Task 3: Integrate Reports And Artifacts

**Files:**
- Modify: `src/reports/tables.py`
- Modify: `src/reports/artifacts.py`
- Modify: `src/reports/final_report.py`
- Modify: `src/reports/technical_report.py`
- Modify: `src/reports/portfolio.py`

- [x] **Step 1: Add v2 tables**

Add `failure_taxonomy_v2` and `repair_success_rate` to `build_report_tables()`.

- [x] **Step 2: Export failure cards**

Write `reports/failure_cards.md` during report artifact export.

- [x] **Step 3: Update report summaries**

Include Phase 14 evidence in final report, technical report, and portfolio brief,
and move recommended next phase to Phase 16 reproducibility package v2.

### Task 4: Update Docs And Generated Artifacts

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`
- Modify: generated `reports/`

- [x] **Step 1: Document Phase 14 validation and smoke commands**

- [x] **Step 2: Regenerate evidence package**

Run: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`.

### Task 5: Validate And Commit

**Files:**
- All Phase 14 files.

- [x] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [x] **Step 2: Run smoke checks**

Run Phase 14 direct smoke, report artifact smoke, final report smoke, portfolio
and technical report smoke, CLI report smoke, docs non-empty check, secret scan,
and large-file scan.

- [x] **Step 3: Commit only this project**

Run: `git commit -m "feat: add failure taxonomy v2 evidence" --only -- .`.
