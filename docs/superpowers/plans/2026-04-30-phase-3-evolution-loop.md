# Phase 3 Evolution Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic evolution loop over constrained bin-packing `score_bin` programs with tournament selection, mutation/crossover, novelty filtering, elite archive reporting, generation metrics, and rerunnable top candidates.

**Architecture:** Reuse Phase 2 seed programs and `BinPackingEvaluator`, then add focused program-search modules for score accounting, tournament selection, novelty filtering, and evolution orchestration. Keep live LLMs deferred by using deterministic local mutation/crossover operators that still emit normal candidate code passing the Phase 1 sandbox boundary.

**Tech Stack:** Python 3.9 stdlib, existing `program_search`, `benchmarks.bin_packing`, pytest, ruff.

---

### Task 1: Phase 3 Tests

**Files:**
- Create: `tests/test_evolution_loop.py`

- [ ] **Step 1: Write failing tests**

Cover deterministic tournament selection, novelty filtering, complexity scoring, generation metrics, reproducible generation-vs-score curves, mutation/crossover lineage, failure recording, top-candidate archive reruns, and Phase 3 report shape.

- [ ] **Step 2: Run RED**

Run: `python3 -m pytest tests/test_evolution_loop.py -q`
Expected: fail because `program_search.evolution_loop`, `program_search.tournament_selection`, and `program_search.novelty_filter` do not exist yet.

### Task 2: Selection, Novelty, and Scoring

**Files:**
- Create: `src/program_search/tournament_selection.py`
- Create: `src/program_search/novelty_filter.py`
- Create: `src/program_search/scoring.py`
- Modify: `src/program_search/__init__.py`

- [ ] **Step 1: Implement deterministic tournament selection**

Select the lowest final-score candidate from seeded random tournament samples. Ties break by program ID.

- [ ] **Step 2: Implement exact-code novelty filter**

Normalize source text and reject exact duplicates while preserving the first candidate.

- [ ] **Step 3: Implement score accounting**

Track benchmark score, runtime penalty, complexity penalty, instability/generalization penalty, failure penalty, and program complexity. Lower final score is better.

- [ ] **Step 4: Run targeted tests**

Run: `python3 -m pytest tests/test_evolution_loop.py -q`
Expected: remaining failures for the evolution loop itself.

### Task 3: Evolution Loop

**Files:**
- Create: `src/program_search/evolution_loop.py`

- [ ] **Step 1: Implement deterministic mutation and crossover**

Generate valid `score_bin` candidates from selected parents using deterministic parameterized templates. Include a small invalid-code probe to keep failure-rate accounting exercised.

- [ ] **Step 2: Implement generation loop and archive recording**

Evaluate seeds and offspring on train/validation/test splits, record every candidate in `ProgramArchive`, compute best/median/failure metrics per generation, keep elites, and store top candidates with code, explanation, complexity, train/validation/test scores, and lineage.

- [ ] **Step 3: Implement rerun helper and report builder**

Add `build_phase3_report` with generation curve, failure taxonomy, and top-program rerun data.

- [ ] **Step 4: Run Phase 3 tests**

Run: `python3 -m pytest tests/test_evolution_loop.py -q`
Expected: pass.

### Task 4: Docs, Validation, and Commit

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`

- [ ] **Step 1: Update docs**

Mark Phase 3 complete, set Phase 4 as current, document evolution smoke checks, and update task memory with validation evidence and limitations.

- [ ] **Step 2: Run final verification**

Run:
- `python3 -m pytest`
- `python3 -m pytest tests/test_evolution_loop.py -v`
- `python3 -m ruff check .`
- `python3 -m ruff format --check .`
- `git diff --check -- .`
- `PYTHONPATH=src python3 - <<'PY' ... PY` evolution smoke check

Expected: all commands exit 0.

- [ ] **Step 3: Commit**

Run:
- `git add .`
- `git commit -m "feat: add evolution loop"`

Expected: one Phase 3 commit with only O2 files changed.
