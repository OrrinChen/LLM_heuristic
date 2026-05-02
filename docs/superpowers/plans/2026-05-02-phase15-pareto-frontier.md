# Phase 15 Pareto Frontier Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a conservative Pareto frontier report that summarizes quality, runtime, complexity, failure, generalization, and operational-realism trade-offs.

**Architecture:** Create `reports.pareto` as the single source for Phase 15 frontier rows. Reuse existing deterministic Phase 2/3/4/6/7/8 reports for candidate metrics, compute nondominated rows per benchmark, then wire the output into final report, CSV tables, JSON plot series, frontier program exports, docs, and validation smokes.

**Tech Stack:** Python stdlib only, pytest, ruff, existing O2 report/evaluator modules.

---

### Task 1: Pareto Frontier Engine

**Files:**
- Create: `src/reports/pareto.py`
- Test: `tests/test_pareto_frontier_phase15.py`

- [x] **Step 1: Write failing Phase 15 tests**

Add tests that import `build_phase15_report`, assert the report includes the
Phase 15 claim boundary, rows for bin packing, simple routing, and Amazon
routing, all required trade-off fields, and at least one Pareto frontier row per
benchmark.

- [x] **Step 2: Run tests to verify red**

Run:
`python3 -m pytest tests/test_pareto_frontier_phase15.py -q`

Expected: fail because `reports.pareto` does not exist.

- [x] **Step 3: Implement deterministic Pareto engine**

Build candidate rows from existing deterministic reports, compute dominance per
benchmark using lower objective score, runtime, complexity, failure rate, and
generalization gap, and include driver-likeness / operational realism for
Amazon rows.

- [x] **Step 4: Verify focused tests pass**

Run:
`python3 -m pytest tests/test_pareto_frontier_phase15.py -q`

Expected: all Phase 15 tests pass.

### Task 2: Report, Artifact, And CLI Integration

**Files:**
- Modify: `src/reports/final_report.py`
- Modify: `src/reports/tables.py`
- Modify: `src/reports/plots.py`
- Modify: `src/reports/artifacts.py`
- Test: `tests/test_pareto_frontier_phase15.py`
- Test: `tests/test_report_tables_plots_and_live_llm.py`
- Test: `tests/test_final_report.py`
- Test: `tests/test_hardening_milestone.py`

- [x] **Step 1: Add failing integration expectations**

Require `pareto_frontier` in report tables, `frontier_plot_series` in plots,
`reports/plots/frontier_plot_series.json` and `artifacts/frontier_programs/*.py`
from artifact export, a `Pareto Frontier` section in final report Markdown, and
`research_style_report` as the next recommended phase.

- [x] **Step 2: Run focused integration tests**

Run:
`python3 -m pytest tests/test_pareto_frontier_phase15.py tests/test_report_tables_plots_and_live_llm.py tests/test_final_report.py tests/test_hardening_milestone.py -q`

Expected: fail until the report paths are wired.

- [x] **Step 3: Implement integration**

Wire Phase 15 into final report sections, report tables, plot series, artifact
export, and frontier program file export without changing generated-program
interfaces or live LLM behavior.

- [x] **Step 4: Verify focused integration tests pass**

Run the same focused pytest command.

Expected: all focused tests pass.

### Task 3: Docs, Evidence Package, And Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`
- Update generated artifacts under `reports/` and `artifacts/`

- [x] **Step 1: Update docs**

Mark Phase 15 complete, set Phase 18 as the recommended next phase, document
the Phase 15 smoke command, and keep claims conservative.

- [x] **Step 2: Regenerate report artifacts**

Run:
`PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`

Expected: generated reports include `pareto_frontier.csv`,
`frontier_plot_series.json`, and `artifacts/frontier_programs/*.py`.

- [x] **Step 3: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
PYTHONPATH=src python3 - <<'PY'
from reports.pareto import build_phase15_report
report = build_phase15_report()
print(report["phase"])
print(len(report["frontier_rows"]))
print(report["claim_boundary"])
PY
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-phase15-report --top-k 3
git diff --check -- .
```

Expected: all commands exit 0.

- [x] **Step 4: Commit only O2 files**

Stage only this project directory and commit:

```bash
git commit -m "feat: add pareto frontier reporting"
```
