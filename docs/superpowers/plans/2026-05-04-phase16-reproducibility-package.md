# Phase 16 Reproducibility Package v2 Plan

## Goal

Make O2 reproducible from a fresh clone with deterministic local profiles and no
API key, paid service, or large external data requirement.

## Scope

- Add Phase 16 reproduction profiles: `local_demo`, `external_small`, and
  `llm_optional`.
- Add one CLI command:
  `PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo`.
- Export:
  - `artifacts/reproduction_manifest.json`
  - `artifacts/reproduction_summary.md`
  - existing report artifacts under `reports/`
  - existing rerun manifest and top programs under `artifacts/`
- Add Make targets for `reproduce`, `test`, `report`, and `demo`.
- Update docs and task memory without expanding claims.

## Acceptance Checklist

- [x] Red tests prove Phase 16 behavior is currently missing.
- [x] Reproduction profile builder records offline deterministic requirements.
- [x] CLI `reproduce` writes required artifacts.
- [x] Make targets and README/RUNBOOK/VALIDATION docs cover the commands.
- [x] Generated repository artifacts are refreshed deterministically.
- [x] Focused Phase16 tests pass.
- [x] Full pytest suite passes.
- [x] Ruff check, Ruff format check, and `git diff --check` pass.
- [x] Smoke checks cover `local_demo`, `external_small`, and `llm_optional`.
- [x] TASK_MEMORY and ROADMAP mark Phase 16 complete and recommend Phase 17.
- [x] Commit completed Phase 16.
