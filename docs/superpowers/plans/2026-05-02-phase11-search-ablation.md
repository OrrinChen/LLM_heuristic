# Phase 11 Search Mechanism Ablation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add controlled search-mechanism ablations that show whether gains come from seeds, mutation, crossover, deterministic LLM-proxy operators, or repair under one fixed evaluation budget.

**Architecture:** Create a focused `program_search.ablation` module that reuses the existing bin packing evaluator, seed candidates, static validation, and deterministic train / validation / test suites. Export ablation CSV and JSON plot artifacts through existing report artifact paths, and expose a deterministic CLI run path without requiring a live LLM key.

**Tech Stack:** Python stdlib only, pytest, ruff, existing O2 package modules.

---

### Task 1: Ablation Engine

**Files:**
- Create: `src/program_search/ablation.py`
- Test: `tests/test_search_ablation_phase11.py`

- [x] **Step 1: Write failing ablation engine tests**

Add tests that import `build_phase11_report`, assert all required methods are
present, candidate budgets are identical, split/control metadata is identical,
and each method reports best score, invalid-code rate, failure rate, and a
budget curve.

- [x] **Step 2: Run focused tests**

Run: `python3 -m pytest tests/test_search_ablation_phase11.py -q`

Expected: fail because `program_search.ablation` does not exist.

- [x] **Step 3: Implement deterministic ablation engine**

Implement methods:

- `seed_only`
- `random_mutation`
- `deterministic_template_mutation`
- `crossover_only`
- `mutation_plus_crossover`
- `llm_mutation`
- `llm_repair`
- `llm_mutation_plus_repair`

Use deterministic local LLM-proxy templates, not live provider calls. Keep the
generated code inside the existing `score_bin` interface and evaluator.

- [x] **Step 4: Verify ablation tests pass**

Run: `python3 -m pytest tests/test_search_ablation_phase11.py -q`

Expected: all Phase 11 ablation tests pass.

### Task 2: Report Tables, Plot Series, And CLI

**Files:**
- Modify: `src/reports/tables.py`
- Modify: `src/reports/plots.py`
- Modify: `src/reports/artifacts.py`
- Modify: `src/reports/final_report.py`
- Modify: `src/heuristic_discovery/__main__.py`
- Test: `tests/test_search_ablation_phase11.py`
- Test: `tests/test_report_tables_plots_and_live_llm.py`
- Test: `tests/test_final_report.py`
- Test: `tests/test_hardening_milestone.py`

- [x] **Step 1: Write failing integration tests**

Require:

- `ablation_summary`, `invalid_code_rate_by_method`, and
  `best_score_by_budget` report tables;
- `generation_curve_by_method` plot JSON series;
- final report Markdown section `Search Mechanism Ablation`;
- CLI `run --benchmark search_ablation` writes `run_summary.json`.

- [x] **Step 2: Run focused tests**

Run:
`python3 -m pytest tests/test_search_ablation_phase11.py tests/test_report_tables_plots_and_live_llm.py tests/test_final_report.py tests/test_hardening_milestone.py -q`

Expected: fail on missing integration behavior.

- [x] **Step 3: Implement integration**

Wire `build_phase11_report` into final report, report tables, plot series,
artifact export, and CLI. Preserve existing outputs and add new CSV / JSON
files.

- [x] **Step 4: Verify focused tests pass**

Run the same focused pytest command.

Expected: all focused tests pass.

### Task 3: Docs, Evidence Package, And Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`
- Update generated artifacts under `reports/`

- [x] **Step 1: Update docs and roadmap**

Mark Phase 11 complete, set Phase 15 as the recommended next phase, document
validation and smoke commands, and keep live LLM claims conservative.

- [x] **Step 2: Regenerate report artifacts**

Run:
`PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`

Expected: generated reports include ablation CSV tables and
`generation_curve_by_method.json`.

- [x] **Step 3: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark search_ablation --output-dir /tmp/o2-phase11-ablation
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-phase11-report --top-k 3
git diff --check -- .
```

Expected: all commands exit 0.

- [ ] **Step 4: Commit only O2 files**

Stage only `llm-or-heuristic-discovery/` files and commit:

```bash
git commit -m "feat: add search mechanism ablation"
```
