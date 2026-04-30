# Phase 2 Bin Packing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the online bin packing benchmark, deterministic baselines, scoring-function evaluator, and held-out reporting needed for Phase 2.

**Architecture:** Add a focused `benchmarks.bin_packing` package split into instance generation, baseline policies, and evaluator/reporting logic. Reuse the Phase 1 sandbox to evaluate constrained `score_bin` programs, and provide deterministic seed candidate programs so the benchmark can evaluate 100+ candidates before live LLM integration exists.

**Tech Stack:** Python 3.9 stdlib, existing sandbox/program-search modules, pytest, ruff.

---

### Task 1: Phase 2 Tests

**Files:**
- Create: `tests/test_bin_packing_evaluator.py`

- [ ] **Step 1: Write failing tests**

Cover deterministic instance generation for all roadmap distributions, held-out seed separation, baseline correctness and determinism, invalid placement rejection, score-program evaluation, failure-rate reporting, 100-candidate evaluation, held-out report creation, and top-program reproducibility/explanation.

- [ ] **Step 2: Run RED**

Run: `python3 -m pytest tests/test_bin_packing_evaluator.py -q`
Expected: fail because `benchmarks.bin_packing` does not exist yet.

### Task 2: Instances

**Files:**
- Create: `src/benchmarks/__init__.py`
- Create: `src/benchmarks/bin_packing/__init__.py`
- Create: `src/benchmarks/bin_packing/instances.py`

- [ ] **Step 1: Implement dataclasses and distributions**

Create `BinPackingInstance`, `InstanceDistribution`, `generate_instance`, `generate_suite`, and `default_train_validation_test_suites`. Generate uniform small, uniform mixed, heavy-tail, tiny-plus-large, adversarial, and held-out distributions with deterministic `random.Random(seed)`.

- [ ] **Step 2: Run instance tests**

Run: `python3 -m pytest tests/test_bin_packing_evaluator.py -q`
Expected: remaining failures for baselines/evaluator.

### Task 3: Baselines

**Files:**
- Create: `src/benchmarks/bin_packing/baselines.py`

- [ ] **Step 1: Implement baseline packers**

Create First Fit, Best Fit, Worst Fit, First Fit Decreasing, Best Fit Decreasing, Random, and handwritten score heuristic. All return a `PackingResult` with bins, bins used, waste, runtime, and validity.

- [ ] **Step 2: Run baseline tests**

Run: `python3 -m pytest tests/test_bin_packing_evaluator.py -q`
Expected: remaining failures for program evaluator/reporting.

### Task 4: Evaluator and Reports

**Files:**
- Create: `src/benchmarks/bin_packing/evaluator.py`

- [ ] **Step 1: Implement score-bin evaluator**

Use `execute_scoring_function` with `ValidationConfig(allowed_function="score_bin")` to choose a bin by lower score. Record bins used, average waste, runtime, failure reason, and invalid placement failures.

- [ ] **Step 2: Implement candidate sweep and held-out report**

Create deterministic seed candidate programs, evaluate 100-1000 programs, compute failure rate and best/median metrics, compare top programs with baselines, and return a serializable held-out report with top code and explanations.

- [ ] **Step 3: Run Phase 2 tests**

Run: `python3 -m pytest tests/test_bin_packing_evaluator.py -q`
Expected: pass.

### Task 5: Docs, Validation, and Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`

- [ ] **Step 1: Update docs**

Mark Phase 2 complete, set Phase 3 as current, document bin packing smoke checks, and update task memory with validation evidence and limitations.

- [ ] **Step 2: Run final verification**

Run:
- `python3 -m pytest`
- `python3 -m pytest tests/test_bin_packing_evaluator.py -v`
- `python3 -m ruff check .`
- `python3 -m ruff format --check .`
- `git diff --check -- .`
- `PYTHONPATH=src python3 - <<'PY' ... PY` bin packing smoke check

Expected: all commands exit 0.

- [ ] **Step 3: Commit**

Run:
- `git add .`
- `git commit -m "feat: add bin packing benchmark"`

Expected: one Phase 2 commit with only O2 files changed.
