# Phase 12 Live LLM Mutation v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make live Gemini mutation a controlled, auditable experiment module while preserving deterministic local defaults.

**Architecture:** Add a small Phase 12 experiment runner around the existing provider protocol and bin-packing evaluator. Generated code is logged by hashes and metadata only, then validated and evaluated through the existing static check and sandbox path. Reports and CLI compare deterministic fallback and optional live-provider rows without storing secrets or raw responses.

**Tech Stack:** Python stdlib, existing `llm.model_client`, existing bin-packing evaluator, pytest, ruff.

---

### Task 1: Add Phase 12 Tests

**Files:**
- Create: `tests/test_live_llm_phase12.py`

- [x] **Step 1: Write failing tests**

Add tests for deterministic fallback without `GEMINI_API_KEY`, live-provider fake transport metadata, repair provider behavior, sandbox rejection of unsafe LLM output, report table/artifact export, and CLI `live_llm`.

- [x] **Step 2: Run red test**

Run: `python3 -m pytest tests/test_live_llm_phase12.py -q`

Expected: FAIL with `ModuleNotFoundError` or missing `llm.live_experiment`.

### Task 2: Implement Provider Metadata And Repair

**Files:**
- Modify: `src/llm/model_client.py`
- Modify: `src/llm/prompt_builder.py`
- Create: `src/llm/live_experiment.py`

- [x] **Step 1: Add prompt versioning and metadata records**

Add prompt-version fields, response hashes, cleaned-code hashes, estimated/actual token counts, latency, model, and temperature fields without storing raw response text.

- [x] **Step 2: Add deterministic fallback and repair provider**

Provide deterministic mutation and repair providers for testable local runs, plus Gemini-backed mutation/repair adapters when a live provider is explicitly configured.

- [x] **Step 3: Add Phase 12 experiment runner**

Evaluate generated `score_bin` candidates through existing static validation and sandboxed bin-packing evaluator. Record model, prompt version, temperature, parent ids, raw response hash, cleaned code hash, static result, sandbox result, score, runtime, token/cost proxy, and failure reason.

### Task 3: Integrate CLI And Reports

**Files:**
- Modify: `src/heuristic_discovery/__main__.py`
- Modify: `src/reports/final_report.py`
- Modify: `src/reports/tables.py`
- Modify: `src/reports/technical_report.py`
- Modify: `src/reports/portfolio.py`
- Modify: report tests.

- [x] **Step 1: Add `live_llm` CLI benchmark**

Support deterministic fallback by default, with live mode gated behind `GEMINI_API_KEY`.

- [x] **Step 2: Add report sections and tables**

Export `llm_operator_comparison.csv` and `llm_candidate_audit.csv` through the existing artifact pipeline.

- [x] **Step 3: Keep claims conservative**

Move the recommended next phase to Phase 13 semantic novelty and state that live LLM is one mutation operator inside a constrained search system.

### Task 4: Update Docs And Generated Artifacts

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `RUNBOOK.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`
- Modify: generated `reports/`

- [x] **Step 1: Document Phase 12 validation and smoke commands**

- [x] **Step 2: Regenerate evidence package**

Run: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`.

### Task 5: Validate And Commit

**Files:**
- All Phase 12 files.

- [x] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [x] **Step 2: Run smoke checks**

Run Phase 12 direct smoke, CLI `live_llm` smoke, report artifact smoke, docs non-empty check, secret scan, and large-file scan.

- [x] **Step 3: Commit only this project**

Run: `git commit -m "feat: add controlled live llm mutation evidence" --only -- .`.
