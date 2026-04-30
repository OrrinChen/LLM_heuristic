# Phase 4 Simple Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the simple single-vehicle routing benchmark that bridges clean bin packing to later Amazon routing evaluators.

**Architecture:** Add a focused `benchmarks.routing` package with deterministic Euclidean instances, route validation, baseline constructors, 2-opt local search, and a sandboxed `score_next_stop` evaluator. Keep live LLMs deferred by using deterministic seed scoring functions that follow the same narrow generated-program interface.

**Tech Stack:** Python 3.9 stdlib, existing sandbox/program-search modules, pytest, ruff.

---

### Task 1: Phase 4 Tests

**Files:**
- Create: `tests/test_routing_validity.py`

- [ ] **Step 1: Write failing tests**

Cover deterministic routing instance generation, distance matrix symmetry, route validity checks, baseline determinism and validity, 2-opt non-worsening behavior, sandboxed `score_next_stop` evaluation, invalid generated-route handling, held-out instance-size separation, local-search improvement, and Phase 4 report shape.

- [ ] **Step 2: Run RED**

Run: `python3 -m pytest tests/test_routing_validity.py -q`
Expected: fail because `benchmarks.routing` does not exist yet.

### Task 2: Instances and Route Utilities

**Files:**
- Create: `src/benchmarks/routing/__init__.py`
- Create: `src/benchmarks/routing/instances.py`

- [ ] **Step 1: Implement routing dataclasses and deterministic generators**

Create `Point`, `Stop`, `RoutingInstance`, `RoutingDistribution`, `generate_routing_instance`, `generate_routing_suite`, and `default_train_validation_test_suites`. Include Euclidean random, clustered, line, and held-out larger-size instances with optional time windows.

- [ ] **Step 2: Run targeted tests**

Run: `python3 -m pytest tests/test_routing_validity.py -q`
Expected: remaining failures for baselines/evaluator/local search.

### Task 3: Baselines and Local Search

**Files:**
- Create: `src/benchmarks/routing/baselines.py`
- Create: `src/benchmarks/routing/local_search.py`

- [ ] **Step 1: Implement route validation and metrics**

Validate each stop is visited exactly once, calculate depot-inclusive distance and time-window violation.

- [ ] **Step 2: Implement baselines**

Create deterministic random route, nearest neighbor, cheapest insertion, 2-opt, and nearest-neighbor plus 2-opt.

- [ ] **Step 3: Run targeted tests**

Run: `python3 -m pytest tests/test_routing_validity.py -q`
Expected: remaining failures for program evaluator/reporting.

### Task 4: Score-Function Evaluator and Report

**Files:**
- Create: `src/benchmarks/routing/evaluator.py`

- [ ] **Step 1: Implement sandboxed `score_next_stop` evaluator**

Compile and validate generated programs with `ValidationConfig(allowed_function="score_next_stop")`, construct routes greedily by lowest score, optionally apply 2-opt repair, and report route length, time-window penalty, validity, runtime, and failure rate.

- [ ] **Step 2: Implement deterministic seed scoring functions and report**

Create seed scoring programs, evaluate them against train/validation/test splits and baselines, report top candidates with explanations, and show local-search improvement.

- [ ] **Step 3: Run Phase 4 tests**

Run: `python3 -m pytest tests/test_routing_validity.py -q`
Expected: pass.

### Task 5: Docs, Validation, and Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`

- [ ] **Step 1: Update docs**

Mark Phase 4 complete, set Phase 5 as current, document routing smoke checks, and update task memory with validation evidence and limitations.

- [ ] **Step 2: Run final verification**

Run:
- `python3 -m pytest`
- `python3 -m pytest tests/test_routing_validity.py -v`
- `python3 -m ruff check .`
- `python3 -m ruff format --check .`
- `git diff --check -- .`
- `PYTHONPATH=src python3 - <<'PY' ... PY` routing smoke check

Expected: all commands exit 0.

- [ ] **Step 3: Commit**

Run:
- `git add .`
- `git commit -m "feat: add simple routing benchmark"`

Expected: one Phase 4 commit with only O2 files changed.
