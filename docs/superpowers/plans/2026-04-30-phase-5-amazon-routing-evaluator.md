# Phase 5 Amazon Routing Evaluator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic Amazon last-mile routing evaluator scaffold that can load route records, compute operational metrics, run reproducible baselines, and evaluate `score_next_stop` programs without special-casing generated code.

**Architecture:** Implement a local, no-network benchmark package under `src/benchmarks/amazon_routing/`. The loader accepts dictionary or JSON payloads shaped like public last-mile route records, validates route/stop/package/travel-time data, and exposes immutable dataclasses. Baselines and the evaluator share the same metric functions so route quality, driver-likeness, and time-window behavior stay consistent.

**Tech Stack:** Python standard library, existing sandbox static checks, existing timeout helper, pytest, ruff.

---

### Task 1: Loader, Features, and Metrics Tests

**Files:**
- Create: `tests/test_amazon_routing_evaluator.py`
- Create: `src/benchmarks/amazon_routing/__init__.py`
- Create: `src/benchmarks/amazon_routing/loader.py`
- Create: `src/benchmarks/amazon_routing/features.py`
- Create: `src/benchmarks/amazon_routing/route_similarity.py`

- [ ] **Step 1: Write failing tests**

Add tests that build a tiny in-memory route fixture, load it through `load_route_record`, and assert:

- Route ID, depot, stop IDs, zone IDs, package counts, service times, and quality label are preserved.
- Travel-time matrix is square, deterministic, and includes depot plus every stop.
- `extract_stop_features` exposes route-level, stop-level, package-level, same-zone, travel-time, slack, depot-distance, and density features.
- Pairwise precedence accuracy, Kendall tau distance, zone transition similarity, and route compactness are deterministic.
- Invalid routes with missing travel-time rows or duplicate stop IDs are rejected with `ValueError`.

- [ ] **Step 2: Run test to verify red**

Run: `python3 -m pytest tests/test_amazon_routing_evaluator.py -q`

Expected: import failure because `benchmarks.amazon_routing` does not exist.

- [ ] **Step 3: Implement minimal loader/feature/metric modules**

Create focused dataclasses and pure functions:

- `PackageRecord`
- `AmazonStop`
- `AmazonRoute`
- `load_route_record`
- `load_route_records`
- `load_route_records_from_json`
- `extract_route_features`
- `extract_stop_features`
- `pairwise_precedence_accuracy`
- `kendall_tau_distance`
- `zone_transition_similarity`
- `route_compactness`

- [ ] **Step 4: Run tests to verify green**

Run: `python3 -m pytest tests/test_amazon_routing_evaluator.py -q`

Expected: loader, feature, and metric tests pass.

### Task 2: Baselines and Evaluator

**Files:**
- Modify: `tests/test_amazon_routing_evaluator.py`
- Create: `src/benchmarks/amazon_routing/baselines.py`
- Create: `src/benchmarks/amazon_routing/evaluator.py`

- [ ] **Step 1: Extend failing tests**

Add tests that assert:

- `AMAZON_BASELINE_ROUTE_BUILDERS` exposes `nearest_neighbor`, `cheapest_insertion`, `two_opt`, and `driver_aware`.
- Each baseline returns a valid deterministic route and metrics for travel time, time-window violation, driver-likeness, zone transition similarity, route compactness, and runtime.
- `AmazonRoutingEvaluator.evaluate_program` can run a valid `score_next_stop` candidate on the same feature contract.
- Unsafe generated code is rejected with a `dangerous_call` failure.
- `build_phase5_report` returns baseline comparison, candidate count, failure taxonomy, train/validation/test split, top program code, and a rerunnable test score.

- [ ] **Step 2: Run test to verify red**

Run: `python3 -m pytest tests/test_amazon_routing_evaluator.py -q`

Expected: missing baselines/evaluator symbols.

- [ ] **Step 3: Implement baselines and evaluator**

Implement:

- Route validation.
- Travel-time and time-window scoring.
- Nearest-neighbor baseline.
- Cheapest-insertion baseline.
- Distance-only 2-opt baseline.
- Driver-aware baseline that favors same zone, historical-neighbor proximity, and time-window slack.
- `AmazonRoutingEvaluator` that greedily builds routes from `score_next_stop(state, candidate_stop)` using sandboxed generated code.
- Seed programs and `build_phase5_report` using deterministic synthetic fixtures.

- [ ] **Step 4: Run test to verify green**

Run: `python3 -m pytest tests/test_amazon_routing_evaluator.py -q`

Expected: all Amazon evaluator tests pass.

### Task 3: Documentation, Validation, and Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`

- [ ] **Step 1: Run verification**

Run:

```bash
python3 -m pytest tests/test_amazon_routing_evaluator.py -v
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [ ] **Step 2: Run Phase 5 smoke check**

Run `build_phase5_report(candidate_count=8)` and record deterministic output.

- [ ] **Step 3: Update docs and task memory**

Mark Phase 5 complete, set Phase 6 as current, document smoke command/output, note limitations, and update the next recommended action.

- [ ] **Step 4: Commit**

Stage only this project’s Phase 5 files and commit:

```bash
git commit -m "feat: add amazon routing evaluator"
```
