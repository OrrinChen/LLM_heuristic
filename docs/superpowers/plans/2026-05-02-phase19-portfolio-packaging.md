# Phase 19 Portfolio Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make O2 directly usable as a resume, GitHub, demo, and interview project without changing its technical claims.

**Architecture:** Add a small `reports.portfolio` module that turns existing final-report evidence into resume bullets, one-command demo copy, architecture text, benchmark summary rows, safety boundary, and limitations. Export `reports/portfolio_brief.md`, then rewrite the README first screen so the required portfolio signals appear before the long status log.

**Tech Stack:** Python stdlib, existing report builders, Markdown, pytest, ruff.

---

### Task 1: Add Phase 19 Tests

**Files:**
- Create: `tests/test_portfolio_packaging_phase19.py`

- [x] **Step 1: Write failing tests**

Write tests that import `reports.portfolio`, validate the structured Phase 19 package, assert the README first screen contains the roadmap-required sections, and assert artifact export writes `reports/portfolio_brief.md`.

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_portfolio_packaging_phase19.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'reports.portfolio'`.

### Task 2: Implement Portfolio Brief

**Files:**
- Create: `src/reports/portfolio.py`
- Modify: `src/reports/artifacts.py`

- [x] **Step 1: Add structured portfolio builder and Markdown renderer**

Return phase `19`, the primary resume bullet, demo command, architecture diagram text, benchmark rows, safety boundary, limitations, and next recommended optional phase.

- [x] **Step 2: Export portfolio brief artifact**

Write `reports/portfolio_brief.md` during `export_report_artifacts()` and include `portfolio_brief` in the returned CLI summary.

- [x] **Step 3: Run focused tests**

Run: `python3 -m pytest tests/test_portfolio_packaging_phase19.py tests/test_hardening_milestone.py -q`

Expected: PASS.

### Task 3: Rewrite README First Screen

**Files:**
- Modify: `README.md`

- [x] **Step 1: Move portfolio content to the top**

Add `What It Does`, `Why It Matters`, `One-Command Demo`, `Core Architecture`, `Benchmark Results`, `Safety Boundary`, and `Limitations` before setup and long status details.

- [x] **Step 2: Keep claims conservative**

Use selected trade-off language and explicitly reject universal dominance / SOTA claims.

- [x] **Step 3: Run README-focused tests**

Run: `python3 -m pytest tests/test_portfolio_packaging_phase19.py -q`

Expected: PASS.

### Task 4: Advance Docs And Artifacts

**Files:**
- Modify: `src/reports/final_report.py`
- Modify: `tests/test_final_report.py`
- Modify: `tests/test_report_tables_plots_and_live_llm.py`
- Modify: `tests/test_pareto_frontier_phase15.py`
- Modify: `tests/test_search_ablation_phase11.py`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`
- Modify: `RUNBOOK.md`
- Modify: generated reports under `reports/`

- [x] **Step 1: Update next-step recommendation**

After Phase 19, recommend optional Phase 10 external routing evidence rather than another required job-search packaging task.

- [x] **Step 2: Document Phase 19 validation and smoke commands**

Update ROADMAP, TASK_MEMORY, VALIDATION, and RUNBOOK with portfolio packaging status and commands.

- [x] **Step 3: Regenerate evidence package**

Run: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`

Expected: `reports/portfolio_brief.md` exists and `reports/tables/recommended_next_steps.csv` points to optional external routing evidence.

### Task 5: Validate And Commit

**Files:**
- All Phase 19 files.

- [x] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [x] **Step 2: Run smoke checks**

Run Phase 19 direct smoke, README first-screen smoke, CLI report export smoke, docs non-empty check, secret scan, and large-file scan.

- [x] **Step 3: Commit only this project**

Run: `git commit -m "docs: package portfolio-ready project evidence" --only -- .`
