# VALIDATION.md

This file defines the validation commands for O2.

## Current Docs-Only Validation

The repository currently contains planning and workflow files only. Until the Python scaffold exists, every documentation or planning change must pass:

```bash
git status --short
git diff --check
for f in AGENTS.md ROADMAP.md TASK_MEMORY.md VALIDATION.md RUNBOOK.md; do test -s "$f" || exit 1; done
```

Expected result:

```text
git diff --check exits 0
all required workflow files exist and are non-empty
```

## After Python Scaffold Exists

Run these after `pyproject.toml`, `src/`, and `tests/` exist:

```bash
python3 -m pytest
python3 -m ruff check .
git diff --check
```

If a formatter is configured:

```bash
python3 -m ruff format --check .
```

## Sandbox Validation

Run these once sandbox modules exist:

```bash
python3 -m pytest tests/test_program_sandbox.py -v
```

Expected result:

```text
imports outside the whitelist are rejected
file access is rejected
network access is rejected
timeouts are enforced
valid scoring functions execute deterministically
```

## Phase 1 Smoke Validation

Run this after sandbox modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from sandbox.restricted_exec import execute_scoring_function

code = """
def score_candidate(state, candidate):
    remaining = state["capacity"] - candidate["size"]
    if remaining < 0:
        return 1000000
    return remaining
"""

result = execute_scoring_function(code, {"capacity": 10}, {"size": 4})
print(result.ok, result.value)
PY
```

Expected result:

```text
True 6.0
```

## Bin Packing Validation

Run these once the bin packing benchmark exists:

```bash
python3 -m pytest tests/test_bin_packing_evaluator.py -v
```

Expected result:

```text
First Fit and Best Fit are deterministic
invalid placements are rejected
number of bins used is computed correctly
held-out seeds are separated from training seeds
```

## Phase 2 Smoke Validation

Run this after bin packing modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from benchmarks.bin_packing.evaluator import build_phase2_report

report = build_phase2_report(candidate_count=120, item_count=25)
print(report["candidate_count"])
print(round(report["failure_rate"], 4))
print(report["best_program_id"])
print(round(report["best_validation_score"], 4))
print(round(report["test_score"], 4))
print(report["held_out"]["instance_count"])
PY
```

Expected result:

```text
120
0.25
seed-000-tight_fit
8.5
9.3333
12
```

## Routing Validation

Run these once simple routing exists:

```bash
python3 -m pytest tests/test_routing_validity.py -v
```

Expected result:

```text
routes visit each stop exactly once
depot handling is consistent
distance and penalty calculations are deterministic
invalid generated routes are rejected or repaired explicitly
```

## Evolution Loop Validation

Run these once the evolution loop exists:

```bash
python3 -m pytest tests/test_evolution_loop.py -v
```

Expected result:

```text
candidate lineage is recorded
failed candidates keep failure reasons
tournament selection is deterministic under a fixed seed
top archived candidates can be re-evaluated
```

## Phase 3 Smoke Validation

Run this after evolution modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from program_search.evolution_loop import EvolutionConfig, build_phase3_report

report = build_phase3_report(
    config=EvolutionConfig(
        generations=3,
        population_size=16,
        offspring_per_generation=12,
        elite_size=4,
        tournament_size=3,
        random_seed=23,
    ),
    item_count=20,
)
print(report["generation_count"])
print(report["generation_curve"][-1]["best_score"])
print(report["generation_curve"][-1]["median_score"])
print(report["rerun_top"]["ok"])
print(round(report["rerun_top"]["score"], 4))
print(sorted(report["failure_taxonomy"]))
PY
```

Expected result:

```text
4
7.547333
7.555333
True
7.75
['dangerous_call']
```

## Report Validation

Before claiming a phase report is complete:

```bash
git diff --check
```

Also verify that the report includes:

- Baseline comparison.
- Train / validation / test split.
- Runtime and failure rate.
- Program complexity.
- Generalization gap.
- Failure taxonomy.
