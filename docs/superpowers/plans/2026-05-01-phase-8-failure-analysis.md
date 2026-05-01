# Phase 8 Failure Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a cross-benchmark failure-analysis report that explains invalid, unsafe, overfit, complex, infeasible, timeout, and metric-trade-off failure modes.

**Architecture:** Create `reports.failure_analysis` as a read-only reporting layer over existing evolution/discovery/robustness reports plus deterministic diagnostic probes. The module must not widen generated-program permissions or alter evaluator contracts.

**Tech Stack:** Python dataclasses, existing evolution and Amazon discovery loops, existing robustness report, pytest, Ruff.

---

### Task 1: Report Contract Tests

**Files:**
- Create: `tests/test_failure_analysis.py`

- [x] **Step 1: Write failing tests**

Add tests that import `reports.failure_analysis`, build `build_phase8_report()`, and verify taxonomy coverage, generation failure-rate rows, rejected/surviving program lists, and worked/failed pattern summaries.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m pytest tests/test_failure_analysis.py -q
```

Expected: fail because `reports.failure_analysis` does not exist yet.

### Task 2: Failure Analysis Report Module

**Files:**
- Create: `src/reports/failure_analysis.py`

- [ ] **Step 1: Build deterministic report inputs**

Run Phase 3 bin-packing evolution, Phase 6 Amazon discovery, and Phase 7 robustness reporting with fixed configs.

- [ ] **Step 2: Classify failure modes**

Report all Phase 8 taxonomy categories, including zero-observation categories with explicit rationale.

- [ ] **Step 3: Include rejected/surviving programs and pattern summaries**

Extract top rejected and surviving programs from archives and add worked/failed pattern summaries.

### Task 3: Documentation And Validation

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`

- [ ] **Step 1: Document Phase 8 smoke check**

Add the deterministic smoke command and expected output.

- [ ] **Step 2: Mark Phase 8 complete**

Update roadmap current state and task memory with validation results and remaining limitations.

### Task 4: Final Verification And Commit

**Files:**
- All changed Phase 8 files

- [ ] **Step 1: Run validation**

Run:

```bash
python3 -m pytest tests/test_failure_analysis.py -v
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [ ] **Step 2: Run smoke check**

Run the Phase 8 smoke command from `VALIDATION.md`.

- [ ] **Step 3: Commit**

Commit with:

```bash
git commit -m "feat: add failure analysis reporting"
```
