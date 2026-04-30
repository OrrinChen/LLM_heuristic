# LLM-Driven Program Search for OR Heuristics

O2 is a FunSearch-inspired program-search system for operations research
heuristics. The project constrains generated Python to compact scoring
functions, validates the code statically, runs it in a restricted sandbox, and
records evaluation results with archive and lineage metadata.

Current status:

- Phase 0 complete: project direction, roadmap, task memory, and workflow docs.
- Phase 1 complete: program-search skeleton, static checks, restricted
  execution, mutation interface, evaluator records, archive, and lineage.
- Phase 2 complete: online bin packing instances, baselines, evaluator, seed
  candidate sweep, held-out report, and seed archive.
- Phase 3 complete: deterministic mutation/crossover evolution loop,
  tournament selection, novelty filtering, generation metrics, complexity
  tracking, elite archive reporting, and rerunnable top candidates.
- Current phase: Phase 4, simple routing benchmark.

## Setup

Use Python 3.9 or newer.

```bash
python3 -m pip install -e ".[dev]"
```

## Tests

```bash
python3 -m pytest
python3 -m ruff check .
git diff --check
```

Sandbox-specific validation:

```bash
python3 -m pytest tests/test_program_sandbox.py -v
```

Bin packing validation:

```bash
python3 -m pytest tests/test_bin_packing_evaluator.py -v
```

Evolution-loop validation:

```bash
python3 -m pytest tests/test_evolution_loop.py -v
```

## Smoke Check

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

Expected output:

```text
True 6.0
```

## Bin Packing Smoke Check

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

Expected output for the deterministic default suite:

```text
120
0.25
seed-000-tight_fit
8.5
9.3333
12
```

## Evolution Smoke Check

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

Expected output:

```text
4
7.547333
7.555333
True
7.75
['dangerous_call']
```

## Safety Boundary

Generated programs must define only the configured scoring function. Static
checks reject extra top-level statements, helper functions, imports, file
access, network/process names, dangerous builtins, dunder attribute access, and
disallowed globals before code reaches restricted execution.

The current sandbox is a local Python AST and restricted-builtins boundary with
Unix signal timeouts. Subprocess isolation and memory limits are deferred until
later hardening work.

## Bin Packing Benchmark

The Phase 2 benchmark includes uniform-small, uniform-mixed, heavy-tail,
tiny-plus-large, adversarial, and held-out item-size distributions. Baselines
include First Fit, Best Fit, Worst Fit, First Fit Decreasing, Best Fit
Decreasing, a handwritten scoring heuristic, and a deterministic random
baseline.

The seed candidate sweep evaluates constrained `score_bin` programs through the
same sandbox boundary used for generated code. Invalid seed programs are
retained in the archive as structured failures instead of being silently
discarded.

## Evolution Loop

The Phase 3 loop evolves bin-packing `score_bin` programs through deterministic
local mutation and crossover operators. It uses seeded tournament selection,
exact-code novelty filtering, an elite archive, generation-level best/median
score and failure-rate metrics, program complexity tracking, and reruns of top
archived candidates against held-out instances.

Live LLM calls remain deferred; the current loop is designed to prove the
search/evaluation/archive contract before paid API usage is introduced.
