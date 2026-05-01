# Phase 6 Amazon Heuristic Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the Amazon routing evaluator to deterministic heuristic search so held-out reports show top scoring programs, local-search variants, and travel-time versus driver-likeness trade-offs.

**Architecture:** Add `src/benchmarks/amazon_routing/discovery.py` as an Amazon-specific search/report layer. It reuses the existing archive, novelty filter, tournament selection, scoring, and sandboxed `AmazonRoutingEvaluator`, but keeps Amazon metrics and trade-off analysis explicit. Existing evaluator features and baselines are extended only where Phase 6 requires new candidate features or comparison baselines.

**Tech Stack:** Python standard library, existing sandbox/evaluator modules, existing program-search components, pytest, ruff.

---

### Task 1: Phase 6 Tests

**Files:**
- Create: `tests/test_amazon_heuristic_discovery.py`
- Modify: `tests/test_amazon_routing_evaluator.py`

- [ ] **Step 1: Write failing tests**

Add tests that assert:

- Candidate stop features include the full Phase 6 allowed feature contract: travel time, same-zone indicator, zone transition cost, time-window slack, package count, service time, stop density, depot distance, angle proxy, cluster compactness, and remaining route structure.
- Amazon baseline builders include deterministic `ml_next_stop_ranker` and `hybrid_ml_plus_local_search` alongside nearest neighbor, cheapest insertion, 2-opt, and driver-aware.
- `AmazonDiscoveryLoop` produces reproducible generation curves, archived candidates, top candidates, failure taxonomy, and rerunnable held-out scores.
- `build_phase6_report` includes held-out routes, baseline comparison, top program code/explanation, feature contract, variants, frontier improvements, and at least one program called out for improving travel time while hurting driver-likeness.

- [ ] **Step 2: Verify red**

Run: `python3 -m pytest tests/test_amazon_heuristic_discovery.py -q`

Expected: import failure for `benchmarks.amazon_routing.discovery`.

### Task 2: Feature and Baseline Extensions

**Files:**
- Modify: `src/benchmarks/amazon_routing/features.py`
- Modify: `src/benchmarks/amazon_routing/baselines.py`
- Modify: `src/benchmarks/amazon_routing/evaluator.py`

- [ ] **Step 1: Add candidate feature constants and values**

Expose `AMAZON_CANDIDATE_FEATURES` and add `depot_angle`, `cluster_compactness`, `remaining_same_zone_count`, and `remaining_zone_count` to stop features.

- [ ] **Step 2: Add Phase 6 baselines**

Implement:

- `ml_next_stop_ranker`: deterministic linear next-stop scoring proxy.
- `hybrid_ml_plus_local_search`: ML ranker followed by local-search improvement when the weighted route score improves.

- [ ] **Step 3: Run tests**

Run: `python3 -m pytest tests/test_amazon_routing_evaluator.py tests/test_amazon_heuristic_discovery.py -q`

Expected: Phase 6 tests progress to missing discovery loop failures.

### Task 3: Discovery Loop and Report

**Files:**
- Create: `src/benchmarks/amazon_routing/discovery.py`

- [ ] **Step 1: Implement deterministic search**

Create:

- `AmazonDiscoveryConfig`
- `AmazonGenerationReport`
- `AmazonTopCandidate`
- `AmazonDiscoveryRunResult`
- `AmazonDiscoveryLoop`
- `build_phase6_seed_programs`
- `build_phase6_report`

Use deterministic mutation/crossover templates and retain invalid probes for failure taxonomy.

- [ ] **Step 2: Add trade-off analysis**

Report candidates where held-out travel time improves over the driver-aware baseline but driver-likeness decreases. Include deltas and a clear `improves_travel_time_hurts_driver_likeness` pattern label.

- [ ] **Step 3: Run tests**

Run: `python3 -m pytest tests/test_amazon_heuristic_discovery.py -q`

Expected: all Phase 6 tests pass.

### Task 4: Documentation, Validation, and Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`

- [ ] **Step 1: Run verification**

Run:

```bash
python3 -m pytest tests/test_amazon_heuristic_discovery.py -v
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [ ] **Step 2: Run Phase 6 smoke check**

Run `build_phase6_report` with a small deterministic config and record output.

- [ ] **Step 3: Update docs and task memory**

Mark Phase 6 complete, set Phase 7 as current, document smoke command/output, and note limitations.

- [ ] **Step 4: Commit**

Stage only Phase 6 files and commit:

```bash
git commit -m "feat: add amazon heuristic discovery"
```
