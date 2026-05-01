# Phase 7 Robustness Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add cross-benchmark robustness reporting for held-out bin packing, simple routing, and Amazon-style routing slices.

**Architecture:** Create a focused `reports.robustness` module that composes existing evaluators and seed programs without changing generated-program interfaces. The report exposes benchmark summaries and slice rows with train, validation, test, runtime, failure rate, complexity, and generalization gap.

**Tech Stack:** Python dataclasses, existing benchmark evaluators, existing sandbox validation, pytest, Ruff.

---

### Task 1: Report Contract Tests

**Files:**
- Create: `tests/test_robustness_reporting.py`

- [x] **Step 1: Write failing tests**

Add tests that import `reports.robustness`, build `build_phase7_report()`, and verify benchmark coverage, required Phase 7 dimensions, required reporting fields, slice coverage, and stable score signatures.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m pytest tests/test_robustness_reporting.py -q
```

Expected: fail because `reports.robustness` does not exist yet.

### Task 2: Robustness Report Module

**Files:**
- Create: `src/reports/__init__.py`
- Create: `src/reports/robustness.py`

- [ ] **Step 1: Implement minimal report API**

Create constants `PHASE7_TESTING_DIMENSIONS` and `PHASE7_REPORTING_FIELDS`, plus `build_phase7_report()`.

- [ ] **Step 2: Compose existing evaluators**

Select deterministic top programs from bin packing, simple routing, and Amazon discovery; evaluate each across train, validation, test, and robustness slices.

- [ ] **Step 3: Surface gaps and limitations**

Return benchmark summaries, slice rows, worst generalization gaps, failure taxonomy, and notes for synthetic Amazon city/density/quality slices.

### Task 3: Documentation And Validation

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`

- [ ] **Step 1: Document Phase 7 smoke check**

Add the deterministic smoke command and expected output.

- [ ] **Step 2: Mark Phase 7 complete**

Update roadmap current state and task memory with validation results and remaining limitations.

### Task 4: Final Verification And Commit

**Files:**
- All changed Phase 7 files

- [ ] **Step 1: Run validation**

Run:

```bash
python3 -m pytest tests/test_robustness_reporting.py -v
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [ ] **Step 2: Run smoke check**

Run the Phase 7 smoke command from `VALIDATION.md`.

- [ ] **Step 3: Commit**

Commit with:

```bash
git commit -m "feat: add robustness reporting"
```
