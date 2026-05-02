# Phase 9 External Bin Packing Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add BPPLIB / OR-Library-style external bin packing evidence without expanding into routing, live LLM, or cloud work.

**Architecture:** Keep external data handling inside `benchmarks.bin_packing` and reuse the existing `BinPackingEvaluator`, seed candidates, baselines, report tables, artifact export, and CLI. Use tiny built-in benchmark-style fixtures for deterministic local validation while supporting user-provided instance files through parser functions and CLI options.

**Tech Stack:** Python stdlib only, pytest, ruff, existing O2 package modules.

---

### Task 1: External Parser And Split

**Files:**
- Create: `src/benchmarks/bin_packing/external.py`
- Modify: `src/benchmarks/bin_packing/instances.py`
- Test: `tests/test_external_bin_packing_phase9.py`

- [ ] **Step 1: Write failing parser and split tests**

Add tests that import `parse_or_library_bin_packing`, `parse_bpplib_bin_packing`,
`default_external_train_validation_test_suites`, and assert parsed instance ids,
capacity, items, known optimum, source, and disjoint train / validation / test
ids.

- [ ] **Step 2: Run the new test file**

Run: `python3 -m pytest tests/test_external_bin_packing_phase9.py -q`

Expected: fail with `ModuleNotFoundError` or missing symbol errors because the
external module does not exist yet.

- [ ] **Step 3: Implement the parser and split**

Create a stdlib-only parser that supports:

- OR-Library-style multi-instance text:
  `instance_count`, then `name item_count capacity known_optimum`, then item
  weights across one or more lines.
- BPPLIB-style key-value text:
  `NAME`, `CAPACITY`, `ITEMS`, optional `OPTIMUM`, then `WEIGHTS`.

Extend `BinPackingInstance` with `EXTERNAL`, `instance_id`, `source`, and
`known_optimum` while preserving existing constructor defaults.

- [ ] **Step 4: Verify parser tests pass**

Run: `python3 -m pytest tests/test_external_bin_packing_phase9.py -q`

Expected: parser and split tests pass.

### Task 2: External Evaluator Report

**Files:**
- Modify: `src/benchmarks/bin_packing/baselines.py`
- Create or modify: `src/benchmarks/bin_packing/external.py`
- Test: `tests/test_external_bin_packing_phase9.py`

- [ ] **Step 1: Write failing report tests**

Add tests for `build_phase9_report` proving external baseline scores,
external-top test score, synthetic-top external test score, split ids, and
synthetic-to-external gap are recorded.

- [ ] **Step 2: Run the focused tests**

Run: `python3 -m pytest tests/test_external_bin_packing_phase9.py -q`

Expected: fail because `build_phase9_report` does not exist.

- [ ] **Step 3: Implement the report**

Reuse existing seed candidates and `BinPackingEvaluator`. Compare candidate
selection on synthetic validation with candidate selection on external
validation. Record external validation/test baseline scores and known-optimum
gaps when present.

- [ ] **Step 4: Verify report tests pass**

Run: `python3 -m pytest tests/test_external_bin_packing_phase9.py -q`

Expected: report tests pass.

### Task 3: Reports, Artifacts, And CLI

**Files:**
- Modify: `src/reports/final_report.py`
- Modify: `src/reports/tables.py`
- Modify: `src/reports/artifacts.py`
- Modify: `src/heuristic_discovery/__main__.py`
- Test: `tests/test_external_bin_packing_phase9.py`
- Test: `tests/test_final_report.py`
- Test: `tests/test_report_tables_plots_and_live_llm.py`
- Test: `tests/test_hardening_milestone.py`

- [ ] **Step 1: Write failing integration tests**

Add tests that require:

- final report Markdown contains `External Benchmark Evidence`;
- report tables include `external_generalization`;
- artifact export writes `reports/tables/external_generalization.csv`;
- CLI `run --benchmark bin_packing_external` writes `run_summary.json`.

- [ ] **Step 2: Run focused tests**

Run: `python3 -m pytest tests/test_external_bin_packing_phase9.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_hardening_milestone.py -q`

Expected: fail on missing external report/table/CLI behavior.

- [ ] **Step 3: Implement report, table, artifact, and CLI integration**

Add external benchmark report data to `build_final_report`, render a conservative
Markdown section, add `external_generalization` rows to report tables, and
support `bin_packing_external` in the deterministic CLI.

- [ ] **Step 4: Verify focused tests pass**

Run: `python3 -m pytest tests/test_external_bin_packing_phase9.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_hardening_milestone.py -q`

Expected: all focused tests pass.

### Task 4: Docs, Validation, And Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`

- [ ] **Step 1: Update docs**

Document the `bin_packing_external` CLI, `external_generalization.csv`, no-large
benchmark-file rule, conservative claims, and validation commands.

- [ ] **Step 2: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing_external --output-dir /tmp/o2-phase9-external
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-phase9-report --top-k 3
git diff --check -- .
```

Expected: all commands exit 0; report output includes
`reports/tables/external_generalization.csv`.

- [ ] **Step 3: Commit only O2 project files**

Run `git status --short -- .`, stage only files under
`llm-or-heuristic-discovery`, and commit with:

```bash
git commit -m "feat: add external bin packing evidence"
```
