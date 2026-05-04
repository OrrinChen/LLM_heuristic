# Phase 17 Local Parallel Runner Plan

## Goal

Add scale-search evidence without binding the project to a paid cloud provider:
local process parallelism, checkpoint/resume, worker failure isolation, and a
cost budget guardrail.

## Scope

- Add a deterministic local candidate-evaluation batch runner.
- Support sequential and process-parallel modes.
- Persist and resume checkpoint JSON.
- Stop evaluation when candidate or cost budgets are exhausted.
- Record worker exceptions as structured candidate failures.
- Add a dry-run cloud adapter status only; do not execute paid cloud work.
- Export Phase 17 report tables and a checkpoint example artifact.
- Update CLI, README, RUNBOOK, ROADMAP, VALIDATION, and TASK_MEMORY.

## Acceptance Checklist

- [x] Red tests prove Phase 17 behavior is missing.
- [x] Parallel top programs and scores match sequential evaluation for the same seed.
- [x] Checkpoint/resume reconstructs the full sequential result.
- [x] Worker failure is recorded without losing valid candidates.
- [x] Cost budget stops evaluation before corrupting checkpoint state.
- [x] CLI exposes `parallel_runner`.
- [x] Report artifacts include Phase17 tables and checkpoint example.
- [x] Focused Phase17 tests pass.
- [x] Full pytest suite passes.
- [x] Ruff check, Ruff format check, and `git diff --check` pass.
- [x] TASK_MEMORY and ROADMAP mark Phase 17 complete.
- [x] Commit completed Phase 17.
