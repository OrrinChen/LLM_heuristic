# Final Report Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package Phase 2-8 outputs into a final report artifact around the killer experiment.

**Architecture:** Create `reports.final_report` as a read-only composition layer over existing phase report builders. The final report should expose a structured dictionary and a markdown rendering without changing benchmark evaluators or generated-program interfaces.

**Tech Stack:** Python dictionaries, existing report builders, pytest, Ruff.

---

### Task 1: Report Contract Tests

**Files:**
- Create: `tests/test_final_report.py`

- [x] **Step 1: Write failing tests**

Add tests that import `reports.final_report`, build the final report once, and verify sections, killer-experiment benchmark coverage, conservative claims, evidence links, markdown rendering, and deterministic smoke signature.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m pytest tests/test_final_report.py -q
```

Expected: fail because `reports.final_report` does not exist yet.

### Task 2: Final Report Module

**Files:**
- Create: `src/reports/final_report.py`

- [ ] **Step 1: Compose Phase 2-8 outputs**

Call deterministic builders for bin packing, simple routing, Amazon discovery, robustness, and failure analysis.

- [ ] **Step 2: Build killer-experiment tables**

Expose the required baseline and discovered-heuristic comparisons for bin packing, simple routing, and Amazon routing.

- [ ] **Step 3: Render markdown**

Render a concise final report with thesis, conservative claim, benchmark evidence, robustness, failure analysis, limitations, and next steps.

### Task 3: Documentation And Validation

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `VALIDATION.md`
- Modify: `TASK_MEMORY.md`

- [ ] **Step 1: Document final report smoke check**

Add deterministic final-report validation commands and expected smoke output.

- [ ] **Step 2: Update current state**

Record final report packaging as completed and keep live LLM integration deferred.

### Task 4: Final Verification And Commit

**Files:**
- All final-report files

- [ ] **Step 1: Run validation**

Run:

```bash
python3 -m pytest tests/test_final_report.py -v
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
```

- [ ] **Step 2: Run smoke check**

Run the final report smoke command from `VALIDATION.md`.

- [ ] **Step 3: Commit**

Commit with:

```bash
git commit -m "feat: add final report packaging"
```
