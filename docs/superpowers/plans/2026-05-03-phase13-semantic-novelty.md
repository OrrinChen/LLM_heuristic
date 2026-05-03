# Phase 13 Program Semantics And Novelty Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add behavioral fingerprints and semantic novelty evidence so O2 can distinguish exact code novelty from behavior, feature, performance, and complexity novelty.

**Architecture:** Build a new deterministic `program_search.semantic_novelty` analyzer for bin-packing `score_bin` programs. It will run candidates against fixed probe states, hash ranking behavior, group equivalent behavior clusters, summarize feature usage and complexity, then expose Phase 13 tables and JSON through the existing report artifact pipeline and CLI.

**Tech Stack:** Python stdlib, existing bin-packing candidate programs, existing static validation and sandbox-safe builtins, report table / plot / CLI export modules, pytest, ruff.

---

### Task 1: Add Phase 13 Tests

**Files:**
- Create: `tests/test_semantic_novelty_phase13.py`

- [x] **Step 1: Write failing tests**

Add tests that require:

- `build_phase13_report()` returns Phase 13 metadata, novelty dimensions, probe count, novelty rows, behavior fingerprints, duplicate behavior clusters, and conservative claim boundaries.
- Two programs with different code but equivalent ranking behavior cluster together.
- `build_report_tables()`, `build_report_plots()`, final report rendering, and artifact export include `novelty_table.csv`, `duplicate_behavior_clusters.csv`, and `behavior_fingerprint.json`.
- CLI can run `--benchmark semantic_novelty` with deterministic local output.

- [x] **Step 2: Run red test**

Run: `python3 -m pytest tests/test_semantic_novelty_phase13.py -q`

Expected: FAIL because `program_search.semantic_novelty` does not exist.

### Task 2: Implement Semantic Novelty Analyzer

**Files:**
- Create: `src/program_search/semantic_novelty.py`

- [x] **Step 1: Add deterministic probe schema**

Create fixed bin-packing probe states with item size and candidate bin features. Each probe should produce a stable ranking vector from a valid `score_bin` program.

- [x] **Step 2: Add fingerprinting and equivalence detection**

Validate candidate code with `ValidationConfig(allowed_function="score_bin")`, execute through safe builtins and timeout-limited calls, hash score vectors/rankings, and group rows by behavior hash.

- [x] **Step 3: Add novelty dimensions**

Compute code novelty, behavior novelty, feature novelty, performance novelty, semantic novelty score, feature usage summary, and complexity decomposition.

- [x] **Step 4: Add Phase 13 report builder**

Return novelty rows, behavior fingerprints, duplicate behavior clusters, probe metadata, claim boundary, and recommended next phase.

### Task 3: Integrate Reports, Tables, Plots, And CLI

**Files:**
- Modify: `src/reports/final_report.py`
- Modify: `src/reports/tables.py`
- Modify: `src/reports/plots.py`
- Modify: `src/reports/artifacts.py`
- Modify: `src/reports/technical_report.py`
- Modify: `src/reports/portfolio.py`
- Modify: `src/heuristic_discovery/__main__.py`

- [x] **Step 1: Add final report section**

Include Phase 13 summary after LLM live mutation / before Pareto frontier, and move recommended next phase to Phase 14 failure taxonomy v2.

- [x] **Step 2: Add tables and JSON plot series**

Export `novelty_table.csv`, `duplicate_behavior_clusters.csv`, and `behavior_fingerprint.json`.

- [x] **Step 3: Add CLI benchmark**

Support `PYTHONPATH=src python3 -m heuristic_discovery run --benchmark semantic_novelty`.

- [x] **Step 4: Keep claims conservative**

State that semantic novelty reports equivalence/behavior evidence and does not prove human-level semantic understanding or universal improvement.

### Task 4: Update Docs And Generated Artifacts

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`
- Modify: generated `reports/`

- [x] **Step 1: Document Phase 13 validation and smoke commands**

- [x] **Step 2: Regenerate evidence package**

Run: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`.

### Task 5: Validate And Commit

**Files:**
- All Phase 13 files.

- [x] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [x] **Step 2: Run smoke checks**

Run Phase 13 direct smoke, CLI `semantic_novelty` smoke, report artifact smoke, docs non-empty check, secret scan, and large-file scan.

- [x] **Step 3: Commit only this project**

Run: `git commit -m "feat: add semantic novelty evidence" --only -- .`.
