# Hardening Milestone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make O2 safer, more reproducible, and more defensible as a resume/interview evidence package.

**Architecture:** Add subprocess isolation to the scoring-function sandbox while preserving the existing AST validation contract. Add manifest/export/CLI layers over existing deterministic reports and evaluators, without adding a new benchmark or expanding project claims.

**Tech Stack:** Python standard library, pytest, ruff, existing O2 benchmark/report modules.

---

### Task 1: Subprocess Sandbox Isolation

**Files:**
- Create: `src/sandbox/subprocess_exec.py`
- Modify: `src/sandbox/restricted_exec.py`
- Test: `tests/test_hardening_milestone.py`

- [x] **Step 1: Write failing tests**

```python
def test_subprocess_sandbox_executes_in_child_process() -> None:
    result = execute_scoring_function_subprocess(
        "def score_candidate(state, candidate):\n    return state['capacity'] - candidate['size']\n",
        {"capacity": 10},
        {"size": 4},
    )
    assert result.ok is True
```

- [x] **Step 2: Implement subprocess runner**

Use `multiprocessing` with a top-level child target, wall-clock join timeout,
optional `resource.setrlimit`, safe builtins, and structured `FailureReason`.

- [x] **Step 3: Preserve existing API**

Keep `execute_scoring_function()` callable as before while routing it through
subprocess isolation by default.

### Task 2: Rerun Manifest

**Files:**
- Create: `src/program_search/rerun_manifest.py`
- Test: `tests/test_hardening_milestone.py`

- [x] **Step 1: Write failing manifest tests**

```python
def test_manifest_records_candidate_hash_and_reruns_top_program() -> None:
    manifest = build_bin_packing_rerun_manifest(top_k=2)
    assert manifest["entries"][0]["code_hash"].startswith("sha256:")
```

- [x] **Step 2: Implement manifest records**

Record benchmark name, candidate id, code hash, generation, parent id, score,
failure reason, runtime, Python version, package version, and random seeds.

- [x] **Step 3: Implement rerun helper**

Rerun deterministic bin-packing top candidates from manifest entries and return
stable scores.

### Task 3: Report Artifact Export

**Files:**
- Create: `src/reports/artifacts.py`
- Test: `tests/test_hardening_milestone.py`

- [x] **Step 1: Write failing artifact export tests**

```python
def test_export_report_artifacts_writes_evidence_package(tmp_path) -> None:
    summary = export_report_artifacts(tmp_path)
    assert (tmp_path / "reports" / "final_report.md").exists()
```

- [x] **Step 2: Implement deterministic exports**

Write final report Markdown, CSV tables, JSON plot series, top program `.py`
files, and `artifacts/rerun_manifest.json`.

- [x] **Step 3: Optional PNG handling**

Do not require matplotlib. If unavailable, report `png_rendered: False`.

### Task 4: Minimal CLI

**Files:**
- Create: `src/heuristic_discovery/__init__.py`
- Create: `src/heuristic_discovery/__main__.py`
- Test: `tests/test_hardening_milestone.py`

- [x] **Step 1: Write failing CLI tests**

```python
def test_cli_report_exports_artifacts(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "heuristic_discovery", "report", "--output-dir", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

- [x] **Step 2: Implement commands**

Support `run`, `report`, `inspect`, and `rerun-manifest` with deterministic
local defaults and optional live LLM remaining environment-gated.

### Task 5: Docs and Validation

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`
- Modify: `RUNBOOK.md`

- [x] **Step 1: Document hardening commands**

Add exact pytest, ruff, smoke, and CLI validation commands.

- [x] **Step 2: Update memory and roadmap**

Record hardening as completed without broadening claims.

- [x] **Step 3: Run validation and commit**

Run targeted tests, full suite, ruff, format check, smoke checks, and
`git diff --check`, then commit the hardening milestone.
