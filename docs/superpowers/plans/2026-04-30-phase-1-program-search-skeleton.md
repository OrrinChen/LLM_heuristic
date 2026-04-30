# Phase 1 Program-Search Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 skeleton that safely validates, executes, records, archives, and traces constrained heuristic scoring programs.

**Architecture:** Keep generated code in narrow scoring-function modules validated by AST checks before execution. Use immutable candidate/evaluation records, an in-memory archive for reproducibility, and protocol-based LLM/evaluator interfaces so later phases can add real models and OR benchmarks without changing the safety boundary.

**Tech Stack:** Python 3.11+, stdlib dataclasses/protocols/AST/signal, pytest, ruff.

---

### Task 1: Write Phase 1 Behavior Tests

**Files:**
- Create: `tests/test_program_sandbox.py`

- [ ] **Step 1: Add tests covering Phase 1 acceptance criteria**

Create tests that assert:
- static checks accept a single allowed scoring function
- static checks reject imports, file access, network access, extra top-level code, wrong function names, and disallowed globals
- restricted execution returns deterministic scores
- timeouts produce structured failure reasons
- invalid candidates are recorded rather than discarded
- surviving candidates retain lineage in the archive
- prompt and mutation interfaces preserve the allowed function boundary

- [ ] **Step 2: Run the tests to verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_program_sandbox.py -q`
Expected: FAIL because `program_search`, `sandbox`, and `llm` modules do not exist yet.

### Task 2: Add Python Scaffold and Candidate Records

**Files:**
- Create: `pyproject.toml`
- Create: `src/program_search/__init__.py`
- Create: `src/program_search/candidate_program.py`

- [ ] **Step 1: Implement package metadata and pytest path**

Add `pyproject.toml` with project metadata, pytest `pythonpath = ["src"]`, and ruff settings.

- [ ] **Step 2: Implement immutable candidate records**

Create `CandidateProgram` with `program_id`, `parent_id`, `generation`, `code`, `prompt`, `benchmark_scores`, `runtime`, `failure_reason`, and `created_at`.

- [ ] **Step 3: Run targeted tests**

Run: `python -m pytest tests/test_program_sandbox.py -q`
Expected: still FAIL until sandbox, archive, and LLM modules exist.

### Task 3: Add Static Validation and Restricted Execution

**Files:**
- Create: `src/sandbox/__init__.py`
- Create: `src/sandbox/static_checks.py`
- Create: `src/sandbox/restricted_exec.py`

- [ ] **Step 1: Implement AST validation**

Validate that candidate code contains exactly one function named by `ValidationConfig.allowed_function`, no decorators, no async functions, no imports outside the whitelist, no extra top-level statements, no dangerous calls (`open`, `eval`, `exec`, `compile`, `__import__`, networking/process APIs), no dunder attribute access, and no disallowed globals.

- [ ] **Step 2: Implement restricted execution**

Run static checks first, execute with a small builtins allowlist, call the allowed scoring function with positional and keyword arguments, enforce a Unix signal timeout, and return `ExecutionResult` with `ok`, `value`, `runtime`, and `failure_reason`.

- [ ] **Step 3: Run targeted tests**

Run: `python -m pytest tests/test_program_sandbox.py -q`
Expected: failures only for archive, lineage, prompt, or mutation pieces that remain unimplemented.

### Task 4: Add Prompt, Mutation, Evaluator, Archive, and Lineage Skeletons

**Files:**
- Create: `src/llm/__init__.py`
- Create: `src/llm/prompt_builder.py`
- Create: `src/llm/mutation_engine.py`
- Create: `src/program_search/archive.py`
- Create: `src/program_search/evaluator.py`
- Create: `src/program_search/lineage.py`

- [ ] **Step 1: Implement prompt and mutation interfaces**

Create a prompt builder that tells the model to return only the allowed function. Create a provider protocol and mutation engine that validates returned code before creating child candidates.

- [ ] **Step 2: Implement evaluator result and archive**

Create `EvaluationResult`, `ProgramArchive`, and `LineageRecord`. The archive stores both failed and surviving candidates, records structured failure reasons, and exposes parent-chain lookup.

- [ ] **Step 3: Run targeted tests**

Run: `python -m pytest tests/test_program_sandbox.py -q`
Expected: PASS.

### Task 5: Add User Docs and Phase Memory

**Files:**
- Create: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`

- [ ] **Step 1: Document Phase 1 usage**

Add README setup, test, and smoke-check commands. Mark Phase 1 complete in roadmap current state and move the current phase to Phase 2. Update task memory with changed files, validation results, known limitations, and next action. Update validation commands now that the scaffold exists.

- [ ] **Step 2: Run required verification**

Run:
- `python -m pytest`
- `ruff check .`
- `git diff --check`
- `python -m pytest tests/test_program_sandbox.py -v`
- `python - <<'PY' ... PY` smoke check that validates and executes a scoring function

Expected: all commands exit 0.

### Task 6: Commit Phase 1

**Files:**
- All project files changed in Phase 1

- [ ] **Step 1: Review diff**

Run: `git diff -- llm-or-heuristic-discovery`
Expected: only O2 project files changed.

- [ ] **Step 2: Stage and commit**

Run:
- `git add llm-or-heuristic-discovery`
- `git commit -m "feat: complete O2 program search skeleton"`

Expected: one commit containing Phase 0 docs plus completed Phase 1 implementation, with unrelated workspace files unstaged.
