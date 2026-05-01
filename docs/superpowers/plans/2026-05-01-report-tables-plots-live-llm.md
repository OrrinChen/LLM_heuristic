# Report Tables, Plots, and Live LLM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the current roadmap phase by turning structured reports into tables/plots and connecting optional Gemini mutation behind environment variables.

**Architecture:** Keep report artifacts deterministic and dependency-free by rendering Markdown tables plus plot-ready series with ASCII previews. Add Gemini as a `CodeMutationProvider` transport only; static validation and sandbox execution remain in existing modules.

**Tech Stack:** Python standard library, pytest, ruff, existing O2 report/evaluator modules.

---

### Task 1: Report Tables

**Files:**
- Create: `src/reports/tables.py`
- Test: `tests/test_report_tables_plots_and_live_llm.py`

- [x] **Step 1: Write failing table tests**

```python
def test_report_tables_cover_benchmarks_robustness_failures_and_steps() -> None:
    tables = build_report_tables()
    assert len(tables["benchmark_comparison"]["rows"]) == 16
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'llm.model_client'`.

- [x] **Step 3: Implement tables**

Create deterministic benchmark, robustness, worst-gap, failure-taxonomy, and next-step tables.

- [x] **Step 4: Run table tests**

Run: `python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -q`
Expected: PASS after plot and Gemini tasks are implemented.

### Task 2: Report Plots

**Files:**
- Create: `src/reports/plots.py`
- Test: `tests/test_report_tables_plots_and_live_llm.py`

- [x] **Step 1: Write failing plot tests**

```python
def test_report_plots_return_plot_ready_series_and_ascii_rendering() -> None:
    plots = build_report_plots()
    assert len(plots["robustness_generalization_gaps"]["points"]) == 15
```

- [x] **Step 2: Implement plot-ready series**

Create deterministic generation-score, Amazon-discovery, robustness-gap, and failure-rate series.

- [x] **Step 3: Render ASCII previews**

Add `render_report_plots_markdown()` and ASCII bars for smoke-checkable output.

### Task 3: Optional Gemini Provider

**Files:**
- Create: `src/llm/model_client.py`
- Test: `tests/test_report_tables_plots_and_live_llm.py`

- [x] **Step 1: Write failing Gemini tests**

```python
def test_gemini_provider_requires_environment_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(GeminiClientError):
        GeminiMutationProvider.from_env()
```

- [x] **Step 2: Implement stdlib REST provider**

Use `urllib.request` against Gemini `generateContent`; read `GEMINI_API_KEY` and optional `GEMINI_MODEL` from the environment.

- [x] **Step 3: Keep sandbox boundary unchanged**

Return generated text to `MutationEngine`; existing static checks validate the candidate before evaluator execution.

### Task 4: Docs and Validation

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `TASK_MEMORY.md`
- Modify: `VALIDATION.md`

- [x] **Step 1: Document new tests and smoke checks**

Add report artifact and optional live Gemini smoke commands.

- [x] **Step 2: Update roadmap status**

Mark report tables/plots and optional live LLM integration complete.

- [x] **Step 3: Run validation**

Run targeted tests, full test suite, ruff checks, report smoke checks, and `git diff --check`.
