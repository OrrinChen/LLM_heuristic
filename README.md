# LLM-Driven Program Search for OR Heuristics

O2 is a release-frozen, portfolio-ready research system for discovering compact
operations-research heuristic scoring programs under strict evaluator and
sandbox constraints.

## What It Is

O2 treats heuristic design as constrained program search. It mutates compact
`score_bin` and `score_next_stop` functions, validates them statically, executes
them in a subprocess sandbox, scores them on OR benchmark evaluators, archives
the results, and exports a reproducible evidence package.

Generated code fills a narrow scoring-function interface only. It is not allowed
to write a full solver, access hidden labels, read files, use network calls,
touch credentials, or import arbitrary packages.

## Why It Matters

Hand-designed OR heuristics are compact, auditable, and fast, but they are often
tuned by manual iteration. O2 shows how part of that design loop can be
automated while preserving a safety boundary, held-out evaluation, failure
analysis, rerun manifests, and conservative claims.

The supported claim is deliberately narrow: the system discovers compact
heuristic programs that improve selected quality-runtime-generalization
trade-offs under strict evaluator constraints. It does not claim universal
dominance, SOTA solver performance, superiority on Amazon data, or LKH/CVRP/
VRPTW solver comparison.

## One-Command Demo

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-demo --top-k 3
```

This regenerates a local evidence package: `reports/final_report.md`,
`reports/technical_report.md`, `reports/portfolio_brief.md`,
`reports/failure_cards.md`, CSV tables, plot-ready JSON, top programs,
frontier programs, a rerun manifest, `artifacts/reproduction_manifest.json`,
and `artifacts/reproduction_summary.md`.

For a report-only export, run:

```bash
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-report --top-k 3
```

## Core Architecture

```mermaid
flowchart LR
    A["seed heuristic library"] --> B["deterministic or LLM mutation operator"]
    B --> C["static validation"]
    C --> D["subprocess sandbox"]
    D --> E["OR benchmark evaluator"]
    E --> F["archive and rerun manifest"]
    F --> G["report artifacts and portfolio evidence"]
```

## Benchmark Evidence

| Evidence area | Key artifact | Claim boundary |
| --- | --- | --- |
| Online Bin Packing | `benchmark_comparison.csv` | compact `score_bin` evidence |
| External Bin Packing | `external_generalization.csv` | external transfer, not SOTA |
| External Routing | `routing_external_generalization.csv` | no LKH/CVRP/VRPTW comparison |
| Search Ablation | `ablation_summary.csv` | mechanism evidence, not live LLM superiority |
| Pareto Frontier | `pareto_frontier.csv` | selected trade-offs |
| Failure Analysis | `failure_cards.md` | transparent limits |
| Reproducibility | `reproduction_manifest.json` | deterministic local rerun |

## Safety Boundary

Static checks reject imports, file access, network/process names, dangerous
builtins, disallowed globals, dunder access, and non-approved function
interfaces before sandbox execution. Hardened scoring calls run in a subprocess
with wall-clock timeout handling and optional platform memory limits. Failures
are recorded as structured reasons instead of being hidden.

## Limitations

- Default runs are deterministic and local; live Gemini mutation is optional,
  environment-gated, and never bypasses validation or sandboxing.
- External benchmark fixtures are intentionally small and parser-backed; larger
  public benchmark corpora remain optional future work.
- Amazon-style routing uses deterministic local fixtures, not proprietary or
  public Amazon route data.
- Semantic novelty is based on fixed probe behavior fingerprints.
- Failure repair evidence is deterministic and local.
- Local parallel evidence uses process parallelism and a dry-run cloud adapter;
  paid cloud execution is optional future work.
- Broader crossover remains optional future work.
- O2 reports selected trade-offs and does not claim universal dominance.

See [RELEASE_SUMMARY.md](RELEASE_SUMMARY.md) for the 3-minute portfolio summary.

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

Routing validation:

```bash
python3 -m pytest tests/test_routing_validity.py -v
```

Amazon routing validation:

```bash
python3 -m pytest tests/test_amazon_routing_evaluator.py -v
```

Amazon heuristic discovery validation:

```bash
python3 -m pytest tests/test_amazon_heuristic_discovery.py -v
```

Robustness reporting validation:

```bash
python3 -m pytest tests/test_robustness_reporting.py -v
```

Failure-analysis validation:

```bash
python3 -m pytest tests/test_failure_analysis.py -v
```

Final-report validation:

```bash
python3 -m pytest tests/test_final_report.py -v
```

Report tables, plots, and optional live-LLM validation:

```bash
python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -v
```

Hardening validation:

```bash
python3 -m pytest tests/test_hardening_milestone.py -v
```

External bin packing validation:

```bash
python3 -m pytest tests/test_external_bin_packing_phase9.py -v
```

External routing validation:

```bash
python3 -m pytest tests/test_external_routing_phase10.py -v
```

Search ablation validation:

```bash
python3 -m pytest tests/test_search_ablation_phase11.py -v
```

Live LLM mutation validation:

```bash
python3 -m pytest tests/test_live_llm_phase12.py -v
```

Semantic novelty validation:

```bash
python3 -m pytest tests/test_semantic_novelty_phase13.py -v
```

Failure taxonomy v2 validation:

```bash
python3 -m pytest tests/test_failure_taxonomy_v2_phase14.py -v
```

Pareto frontier validation:

```bash
python3 -m pytest tests/test_pareto_frontier_phase15.py -v
```

Research-style technical report validation:

```bash
python3 -m pytest tests/test_technical_report_phase18.py -v
```

Portfolio packaging validation:

```bash
python3 -m pytest tests/test_portfolio_packaging_phase19.py -v
```

Reproducibility package validation:

```bash
python3 -m pytest tests/test_reproducibility_package_phase16.py -v
```

Local parallel runner validation:

```bash
python3 -m pytest tests/test_local_parallel_runner_phase17.py -v
```

## CLI

The deterministic local CLI is available through the package module:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing --generations 1
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing_external --output-dir /tmp/o2-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark routing_external --output-dir /tmp/o2-routing-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark search_ablation --candidate-budget 32 --output-dir /tmp/o2-ablation
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark live_llm --candidate-count 4 --output-dir /tmp/o2-live-llm
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark semantic_novelty --candidate-count 24 --output-dir /tmp/o2-semantic
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark parallel_runner --candidate-count 12 --max-workers 2 --output-dir /tmp/o2-parallel
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir .
PYTHONPATH=src python3 -m heuristic_discovery inspect --top-k 5
PYTHONPATH=src python3 -m heuristic_discovery rerun-manifest --output-dir . --top-k 5
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-reproduce-local
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-reproduce-external
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile llm_optional --output-dir /tmp/o2-reproduce-llm
```

After installation, the console script is also available:

```bash
heuristic-discovery report --output-dir .
```

The external bin packing command uses tiny parser-backed benchmark-style
fixtures by default, so the demo does not require large public benchmark files.
User-provided OR-Library-style or BPPLIB-style files can be passed with
`--external-path` and `--external-format`.

The external routing command uses tiny TSPLIB-style EUC_2D and CVRPLIB-style
capacitated/time-window fixtures by default. User-provided `.tsp`, `.vrp`, or
`.txt` files can be passed with `--external-path` and `--external-format tsplib`
or `--external-format cvrplib`. Do not commit large public benchmark corpora.

The reproduction command regenerates the deterministic evidence package and
writes `artifacts/reproduction_manifest.json` plus
`artifacts/reproduction_summary.md`. The `local_demo` and `external_small`
profiles require no API key or large external data. The `llm_optional` profile
uses deterministic fallback providers unless live Gemini is explicitly enabled
through the separate `live_llm` command.

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

## External Bin Packing Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from benchmarks.bin_packing.external import build_phase9_report

report = build_phase9_report(candidate_count=24, synthetic_item_count=16)
print(report["benchmark"])
print(report["external_split"]["test_count"])
print(report["best_external_program_id"])
print(report["best_external_test_score"])
print("first_fit" in report["external_test_baseline_scores"])
print(report["claim_boundary"])
PY
```

Expected output:

```text
bin_packing_external
2
seed-000-tight_fit
5.0
True
external benchmark-style evidence only; no SOTA or universal dominance claim
```

## External Routing Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from benchmarks.routing.external import build_phase10_report

report = build_phase10_report(candidate_count=8, synthetic_stop_count=8)
print(report["phase"])
print(report["benchmark"])
print(report["external_split"]["test_count"])
print(report["best_external_program_id"])
print(report["best_external_test_score"] is not None)
print("nearest_neighbor" in report["external_test_baseline_scores"])
print(report["external_formats"])
print(report["capacitated_instance_count"])
print(report["time_window_instance_count"])
print(report["best_external_test_capacity_violation"])
print(round(report["best_external_test_time_window_violation"], 6))
print(report["claim_boundary"])
PY
```

Expected output:

```text
10
routing_external
3
route-seed-000-nearest
True
True
['cvrplib', 'tsplib']
3
3
0.0
15.205163
external routing-style evidence only; no LKH, CVRP/VRPTW solver, Amazon, SOTA, or universal dominance claim
```

## Search Ablation Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from program_search.ablation import build_phase11_report

report = build_phase11_report(candidate_budget=16, generations=3, item_count=16)
print(report["benchmark"])
print(len(report["methods"]))
print(report["controls"]["candidate_budget"])
print(report["best_method"])
print(report["claim_boundary"])
PY
```

Expected output:

```text
bin_packing
8
16
llm_mutation
ablation compares deterministic operators under a fixed local budget; live LLM behavior is not claimed
```

## Live LLM Mutation Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from llm.live_experiment import LLMExperimentConfig, build_phase12_report

report = build_phase12_report(
    config=LLMExperimentConfig(candidate_budget=3, item_count=12)
)
print(report["phase"])
print(report["benchmark"])
print(report["live_provider_configured"])
print(len(report["operator_comparison"]))
print(len(report["candidate_audit"]))
print(report["operator_comparison"][0]["method"])
print(report["candidate_audit"][0]["prompt_version"])
print(report["claim_boundary"])
PY
```

Expected output for the deterministic default:

```text
12
live_llm_mutation
False
3
6
deterministic_fallback
score-bin-mutation-v1
LLM is one mutation operator inside a constrained program-search system; live LLM superiority is not claimed
```

## Pareto Frontier Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.pareto import build_phase15_report

report = build_phase15_report()
print(report["phase"])
print(len(report["candidate_rows"]))
print(len(report["frontier_rows"]))
print(tuple(report["benchmarks"]))
print(report["frontier_rows"][0]["benchmark"])
print(report["frontier_rows"][0]["program_id"])
print(report["claim_boundary"])
PY
```

Expected output:

```text
15
17
8
('amazon_routing', 'bin_packing', 'simple_routing')
amazon_routing
phase6-seed-000-travel_fast
The system discovers compact heuristic programs that improve selected quality-runtime-generalization trade-offs, rather than universally dominating classical baselines.
```

## Routing Smoke Check

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

Expected output for the deterministic default suite:

```text
8
8.626646
7.227464
18.407699
True
8
route-seed-003-slack_aware
```

## Amazon Routing Smoke Check

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

Expected output for the deterministic scaffold routes:

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

## Amazon Heuristic Discovery Smoke Check

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

Expected output for the deterministic scaffold routes:

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

## Robustness Reporting Smoke Check

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

Expected output for the deterministic robustness suite:

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

## Failure Analysis Smoke Check

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

Expected output for the deterministic failure-analysis suite:

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

## Final Report Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.final_report import build_final_report, render_final_report_markdown

report = build_final_report()
markdown = render_final_report_markdown(report)
benchmarks = report["killer_experiment"]["benchmarks"]
print(len(benchmarks))
print(report["evidence"]["robustness"]["slice_count"])
print(report["evidence"]["failure_analysis"]["failure_category_count"])
print(benchmarks["bin_packing"]["top_program_id"])
print(benchmarks["simple_routing"]["top_program_id"])
print(benchmarks["amazon_routing"]["top_program_id"])
print(report["pareto_frontier"]["frontier_count"])
print(report["recommended_next_steps"][0]["step"])
print("External Benchmark Evidence" in markdown)
print("LLM Live Mutation v1" in markdown)
print("Search Mechanism Ablation" in markdown)
print("Program Semantics And Novelty" in markdown)
print("Failure Taxonomy v2" in markdown)
print("Pareto Frontier Report" in markdown)
print("do not universally dominate" in markdown)
print("selected trade-offs" in markdown)
PY
```

Expected output for the deterministic final report:

```text
3
15
9
seed-000-tight_fit
route-seed-003-slack_aware
phase6-seed-000-travel_fast
8
reproducibility_package_v2
True
True
True
True
True
True
True
True
```

## Report Artifact Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.tables import build_report_tables, render_report_tables_markdown
from reports.plots import build_report_plots, render_report_plots_markdown
from llm.model_client import GeminiClientError, GeminiMutationProvider

tables = build_report_tables()
plots = build_report_plots()
print(tuple(tables["tables"]))
print(len(tables["benchmark_comparison"]["rows"]))
print(len(tables["external_generalization"]["rows"]))
print(len(tables["routing_external_generalization"]["rows"]))
print(len(tables["ablation_summary"]["rows"]))
print(len(tables["invalid_code_rate_by_method"]["rows"]))
print(len(tables["best_score_by_budget"]["rows"]))
print(len(tables["llm_operator_comparison"]["rows"]))
print(len(tables["llm_candidate_audit"]["rows"]))
print(len(tables["novelty_table"]["rows"]))
print(len(tables["duplicate_behavior_clusters"]["rows"]))
print(len(tables["pareto_frontier"]["rows"]))
print(len(tables["failure_taxonomy"]["rows"]))
print(len(tables["failure_taxonomy_v2"]["rows"]))
print(len(tables["repair_success_rate"]["rows"]))
print(tuple(plots["plots"]))
print(len(plots["robustness_generalization_gaps"]["points"]))
print(len(plots["generation_curve_by_method"]["points"]))
print(len(plots["behavior_fingerprint"]["points"]))
print(len(plots["frontier_plot_series"]["points"]))
print("routing-large-routes" in render_report_plots_markdown(plots))
print("Failure Taxonomy v2" in render_report_tables_markdown(tables))
try:
    GeminiMutationProvider.from_env()
except GeminiClientError as exc:
    print(str(exc).split()[0])
PY
```

Expected output without a live key exported:

```text
('benchmark_comparison', 'robustness_summary', 'worst_generalization_gaps', 'external_generalization', 'routing_external_generalization', 'ablation_summary', 'invalid_code_rate_by_method', 'best_score_by_budget', 'llm_operator_comparison', 'llm_candidate_audit', 'novelty_table', 'duplicate_behavior_clusters', 'pareto_frontier', 'failure_taxonomy', 'failure_taxonomy_v2', 'repair_success_rate', 'recommended_next_steps')
16
5
5
8
8
8
3
8
24
4
17
9
11
11
('bin_packing_evolution_best_score', 'amazon_discovery_best_score', 'robustness_generalization_gaps', 'generation_curve_by_method', 'behavior_fingerprint', 'frontier_plot_series', 'failure_rate_by_generation')
15
32
24
17
True
True
GEMINI_API_KEY
```

## Optional Gemini Mutation

Phase 12 keeps live mutation as a controlled experiment. The default command
uses deterministic fallback and repair providers. To opt into a real Gemini
provider for local smoke testing, set environment variables and pass
`--use-live-llm`; do not commit API keys, raw responses, or generated
proprietary data.

```bash
export GEMINI_API_KEY="..."
export GEMINI_MODEL="gemini-2.5-flash"  # optional; client default is gemini-2.5-flash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark live_llm \
  --use-live-llm \
  --candidate-count 1 \
  --output-dir /tmp/o2-live-gemini-smoke
```

`GeminiMutationProvider.from_env()` implements the existing mutation-provider
protocol. The `MutationEngine` still statically validates the returned code
before any evaluator can execute it. Phase 12 report rows store model,
prompt version, temperature, parent ids, raw-response hash, cleaned-code hash,
static-check result, sandbox result, score, failure reason, token counts,
latency, and a cost proxy without storing raw response text.

## Safety Boundary

Generated programs must define only the configured scoring function. Static
checks reject extra top-level statements, helper functions, imports, file
access, network/process names, dangerous builtins, dunder attribute access, and
disallowed globals before code reaches restricted execution.

The hardened single-call sandbox runs generated scoring functions in a separate
subprocess with wall-clock timeout handling and optional platform memory limits.
If the host does not expose compatible memory-limit primitives, requested memory
limits fail closed with a structured `memory_limit_unsupported` reason. The
benchmark evaluators preserve their deterministic static-validation contract and
can be rerun from exported manifests.

## Evidence Package Artifacts

The checked-in evidence package contains:

```text
reports/final_report.md
reports/technical_report.md
reports/portfolio_brief.md
reports/tables/*.csv
reports/tables/external_generalization.csv
reports/tables/routing_external_generalization.csv
reports/tables/llm_operator_comparison.csv
reports/tables/llm_candidate_audit.csv
reports/tables/novelty_table.csv
reports/tables/duplicate_behavior_clusters.csv
reports/tables/parallel_runner_summary.csv
reports/tables/checkpoint_resume.csv
reports/plots/plot_series.json
reports/plots/generation_curve_by_method.json
reports/plots/behavior_fingerprint.json
reports/plots/frontier_plot_series.json
artifacts/top_programs/*.py
artifacts/frontier_programs/*.py
artifacts/rerun_manifest.json
artifacts/phase17_checkpoint.json
artifacts/reproduction_manifest.json
artifacts/reproduction_summary.md
```

Regenerate it with:

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir . --top-k 5
```

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

The default loop remains deterministic; optional live LLM mutation can now be
provided through the `MutationEngine` provider protocol.

## Simple Routing Benchmark

The Phase 4 benchmark uses deterministic synthetic single-vehicle routing
instances with depot, stops, distance matrix, optional time windows, and
held-out stop counts. Baselines include random route, nearest neighbor,
cheapest insertion, 2-opt, and nearest neighbor plus 2-opt.

Candidate programs define only `score_next_stop(state, candidate_stop)`. The
evaluator greedily builds a route from candidate stop scores, rejects unsafe or
non-numeric programs with structured failure reasons, optionally applies 2-opt,
and reports route length, time-window violation penalty, route validity,
runtime, failure rate, and held-out test score.

## Amazon Routing Evaluator

The Phase 5 scaffold loads local dictionary or JSON route records shaped like
Amazon last-mile route data. It models depot, stops, packages, travel-time
matrix, historical driver sequence, quality label, service times, and time
windows without requiring proprietary datasets.

Baselines include nearest neighbor, cheapest insertion, 2-opt, and a
driver-aware hand heuristic. The evaluator reports travel time, time-window
violation, pairwise precedence driver-likeness, Kendall tau distance, zone
transition similarity, route compactness, runtime, failure rate, and held-out
test score. Generated programs still define only `score_next_stop`; route
quality labels and historical positions are kept out of candidate features.

## Amazon Heuristic Discovery

The Phase 6 discovery layer runs deterministic seed, mutation, and crossover
search over Amazon `score_next_stop` programs. It reuses the program archive,
novelty filter, tournament selection, complexity accounting, and sandboxed
Amazon evaluator while preserving Amazon-specific metrics in the report.

Reports include generation curves, baseline comparisons, the allowed candidate
feature contract, local-search and feasibility variants, top program code,
held-out reruns, failure taxonomy, and explicit trade-off callouts for programs
that reduce travel time while lowering driver-likeness. The default Phase 6 run
stays deterministic, while optional live mutation can be configured separately.

## Robustness Reporting

The Phase 7 report composes the existing benchmark evaluators without changing
generated-program interfaces. It evaluates one deterministic top program per
benchmark on train, validation, test, and additional held-out slices, then
reports runtime, failure rate, complexity, and validation-to-slice
generalization gaps.

The robustness slices cover held-out random seeds, held-out bin-packing item
distributions, held-out simple-routing sizes, synthetic Amazon station-code
proxies for city slices, small versus large routes, dense urban versus sparse
suburban routes, and high versus medium quality historical routes. Amazon city,
density, and quality slices remain deterministic local fixtures until external
public or user-provided data is configured.

## Failure Analysis

The Phase 8 report aggregates Phase 3 evolution, Phase 6 Amazon discovery, and
Phase 7 robustness results into a failure-analysis artifact. It includes the
full failure taxonomy, generation-level failure and invalid-code rates, top
rejected programs, top surviving programs, patterns that worked, and patterns
that failed.

Timeout, excessive-complexity, and driver-likeness-too-slow rows use
deterministic diagnostic probes to keep those failure modes visible without
loosening sandbox constraints. Routing feasibility violations are currently
zero-observation because generated programs only rank remaining stops; full
route-generation programs remain outside the project boundary.

## Final Report Packaging

The final report module composes the Phase 2 bin-packing report, Phase 4
simple-routing report, Phase 6 Amazon discovery report, Phase 7 robustness
report, and Phase 8 failure-analysis report. It returns a structured dictionary
and a Markdown rendering suitable for final write-up work.

The report centers the killer experiment across online bin packing, simple
routing, and Amazon-style routing. It states the conservative claim that compact
sandboxed scoring programs improve selected trade-offs, and explicitly avoids
claiming universal dominance over classical OR baselines.

## Report Tables, Plots, and Live LLM

The report artifact modules turn the structured final, robustness, and
failure-analysis dictionaries into deterministic Markdown tables and plot-ready
series with ASCII previews. The Gemini provider implements the existing
mutation protocol through the REST `generateContent` API, reads credentials only
from environment variables, and leaves code validation to the existing sandbox
pipeline.
