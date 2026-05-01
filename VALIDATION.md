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

Run these after simple routing modules exist:

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

## Phase 4 Smoke Validation

Run this after routing modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from benchmarks.routing.evaluator import build_phase4_report

report = build_phase4_report(candidate_count=8, stop_count=10)
print(report["candidate_count"])
print(round(report["best_validation_score"], 6))
print(round(report["best_with_local_search_score"], 6))
print(round(report["test_score"], 6))
print(report["local_search"]["improved_or_equal"])
print(report["held_out"]["instance_count"])
print(report["top_programs"][0]["program_id"])
PY
```

Expected result:

```text
8
8.626646
7.227464
18.407699
True
8
route-seed-003-slack_aware
```

## Amazon Routing Validation

Run these after Amazon routing evaluator modules exist:

```bash
python3 -m pytest tests/test_amazon_routing_evaluator.py -v
```

Expected result:

```text
local route records load from dictionaries and JSON
route, stop, package, travel-time, history, and quality fields are preserved
nearest neighbor, insertion, 2-opt, and driver-aware baselines are reproducible
route similarity metrics are deterministic
score_next_stop programs run through the sandbox without special casing
unsafe generated programs are rejected with structured failure reasons
```

## Phase 5 Smoke Validation

Run this after Amazon routing modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from benchmarks.amazon_routing.evaluator import build_phase5_report

report = build_phase5_report(candidate_count=8)
print(report["candidate_count"])
print(round(report["failure_rate"], 4))
print(report["best_program_id"])
print(round(report["best_validation_score"], 6))
print(round(report["test_score"], 6))
print(report["held_out"]["route_count"])
print(sorted(report["failure_taxonomy"]))
print(report["top_programs"][0]["program_id"])
PY
```

Expected result:

```text
8
0.125
amazon-seed-000-nearest
12.666667
12.666667
2
['dangerous_call']
amazon-seed-000-nearest
```

## Amazon Heuristic Discovery Validation

Run these after Amazon discovery modules exist:

```bash
python3 -m pytest tests/test_amazon_heuristic_discovery.py -v
```

Expected result:

```text
candidate feature contract covers Phase 6 roadmap features
Amazon baselines include ML-ranker and hybrid local-search variants
discovery generation curves are reproducible
top discovered programs can be rerun on held-out routes
trade-off reports call out travel-time improvement with driver-likeness harm
```

## Phase 6 Smoke Validation

Run this after Amazon discovery modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from benchmarks.amazon_routing.discovery import AmazonDiscoveryConfig, build_phase6_report

report = build_phase6_report(
    config=AmazonDiscoveryConfig(
        generations=2,
        population_size=12,
        offspring_per_generation=8,
        elite_size=4,
        tournament_size=3,
        random_seed=23,
    )
)
print(report["generation_count"])
print(report["generation_curve"][-1]["best_score"])
print(report["top_candidates"][0]["program_id"])
print(round(report["top_candidates"][0]["test_score"], 6))
print(len(report["tradeoff_programs"]))
print(len(report["frontier_improvements"]))
print(sorted(report["failure_taxonomy"]))
print(report["rerun_top"]["ok"])
PY
```

Expected result:

```text
3
10.855333
phase6-seed-000-travel_fast
10.833333
4
4
['dangerous_call']
True
```

## Robustness Reporting Validation

Run these after Phase 7 robustness modules exist:

```bash
python3 -m pytest tests/test_robustness_reporting.py -v
```

Expected result:

```text
cross-benchmark report covers bin packing, simple routing, and Amazon routing
held-out random seeds, item distributions, routing sizes, Amazon city slices,
route size, density, and quality dimensions are represented
train, validation, test, runtime, failure rate, complexity, and generalization
gap fields are present in benchmark and slice rows
worst generalization gaps and failure taxonomy are reported
```

## Phase 7 Smoke Validation

Run this after robustness reporting modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.robustness import build_phase7_report

report = build_phase7_report()
print(report["benchmark_count"])
print(len(report["slice_summary"]))
print(tuple(report["benchmarks"]))
print(report["benchmarks"]["bin_packing"]["program_id"])
print(report["benchmarks"]["simple_routing"]["program_id"])
print(report["benchmarks"]["amazon_routing"]["program_id"])
print(round(report["benchmarks"]["bin_packing"]["generalization_gap"], 6))
print(round(report["benchmarks"]["simple_routing"]["generalization_gap"], 6))
print(round(report["benchmarks"]["amazon_routing"]["generalization_gap"], 6))
print(report["worst_generalization_gaps"][0]["slice_name"])
print(round(report["worst_generalization_gaps"][0]["generalization_gap"], 6))
print(sorted(report["failure_taxonomy"]))
PY
```

Expected result:

```text
3
15
('bin_packing', 'simple_routing', 'amazon_routing')
seed-000-tight_fit
route-seed-011-return_aware
phase6-seed-000-travel_fast
0.833333
9.907981
0.0
routing-large-routes
68.753356
['dangerous_call']
```

## Failure Analysis Validation

Run these after Phase 8 failure-analysis modules exist:

```bash
python3 -m pytest tests/test_failure_analysis.py -v
```

Expected result:

```text
full Phase 8 failure taxonomy is represented
failure rate by generation and invalid-code rate rows are reported
top rejected and top surviving programs are listed
patterns that worked and patterns that failed are summarized
diagnostic timeout and excessive-complexity probes are recorded explicitly
```

## Phase 8 Smoke Validation

Run this after failure-analysis reporting modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.failure_analysis import build_phase8_report

report = build_phase8_report()
print(len(report["failure_categories"]))
print(len(report["failure_rate_by_generation"]))
print(len(report["top_rejected_programs"]))
print(len(report["top_surviving_programs"]))
print(report["top_rejected_programs"][0]["category"])
print(report["top_surviving_programs"][0]["program_id"])
print(report["failure_taxonomy"]["generated_invalid_code"]["count"])
print(report["failure_taxonomy"]["timeout"]["count"])
print(report["failure_taxonomy"]["poor_generalization"]["count"])
print(
    report["failure_taxonomy"][
        "improves_travel_time_but_hurts_driver_likeness"
    ]["count"]
)
print(tuple(row["pattern"] for row in report["patterns_that_failed"]))
PY
```

Expected result:

```text
9
7
8
8
generated_invalid_code
seed-001-load_balancer
7
1
2
4
('unsafe_data_access', 'routing_large_slice_generalization_gap', 'travel_time_driver_likeness_tradeoff', 'driver_like_timeout')
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
