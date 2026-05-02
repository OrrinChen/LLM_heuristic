# Phase 10 External Routing Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add TSPLIB-style external routing evidence without implementing CVRPLIB, time windows, cloud execution, or live LLM changes.

**Architecture:** Add `benchmarks.routing.external` for TSPLIB coordinate parsing, distance-matrix construction, external train/validation/test splits, baseline reuse, and `score_next_stop` candidate reruns. Thread the Phase 10 report into the existing final report, tables, artifact export, CLI, docs, and task memory.

**Tech Stack:** Python stdlib, existing routing evaluator/baselines, pytest, ruff.

---

### Task 1: Add Phase 10 Tests

**Files:**
- Create: `tests/test_external_routing_phase10.py`

- [x] **Step 1: Write failing tests**

Add tests for TSPLIB parsing, distance matrix construction, default external splits, Phase 10 report, final report/table export, and CLI `routing_external`.

- [x] **Step 2: Run red test**

Run: `python3 -m pytest tests/test_external_routing_phase10.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'benchmarks.routing.external'`.

### Task 2: Implement External Routing Module

**Files:**
- Create: `src/benchmarks/routing/external.py`
- Modify: `src/benchmarks/routing/instances.py`

- [x] **Step 1: Add external instance metadata**

Add `EXTERNAL` to `RoutingDistribution` and optional `instance_id` / `source` fields to `RoutingInstance`.

- [x] **Step 2: Add TSPLIB parser and default fixtures**

Parse `NAME`, `DIMENSION`, `EDGE_WEIGHT_TYPE`, `NODE_COORD_SECTION`, and `EOF`; use the first coordinate as depot and the remaining coordinates as stops.

- [x] **Step 3: Add Phase 10 report builder**

Build report fields for external split, baseline scores, synthetic-selected rerun, external-selected rerun, generalization gaps, and conservative claim boundary.

### Task 3: Integrate CLI And Reports

**Files:**
- Modify: `src/heuristic_discovery/__main__.py`
- Modify: `src/reports/final_report.py`
- Modify: `src/reports/tables.py`
- Modify: existing report tests.

- [x] **Step 1: Add `routing_external` CLI benchmark**

Support deterministic default fixtures and optional `--external-path` loading.

- [x] **Step 2: Add final report section data and Markdown**

Expose `routing_external` evidence without SOTA, LKH, CVRP, or Amazon superiority claims.

- [x] **Step 3: Add `routing_external_generalization.csv` table**

Export external routing rows through existing artifact export.

### Task 4: Update Docs And Generated Artifacts

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`
- Modify: generated `reports/`

- [x] **Step 1: Document Phase 10 validation and smoke commands**

- [x] **Step 2: Regenerate evidence package**

Run: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`.

### Task 5: Validate And Commit

**Files:**
- All Phase 10 files.

- [x] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [x] **Step 2: Run smoke checks**

Run Phase 10 direct smoke, CLI `routing_external` smoke, report artifact smoke, docs non-empty check, secret scan, and large-file scan.

- [x] **Step 3: Commit only this project**

Run: `git commit -m "feat: add external routing benchmark evidence" --only -- .`.
