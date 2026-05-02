# LLM-Driven Program Search for OR Heuristics

O2 is a FunSearch-inspired program-search system for operations research
heuristics. The project constrains generated Python to compact scoring
functions, validates the code statically, runs it in a restricted sandbox, and
records evaluation results with archive and lineage metadata.

## What It Does

O2 treats heuristic design as constrained program search. Seed heuristics and
generated scoring functions are mutated, statically validated, executed in a
sandbox, scored by OR benchmark evaluators, selected through an archive, and
exported as reproducible evidence.

The system discovers compact `score_bin` and `score_next_stop` programs for
bin packing and routing-style tasks. It does not let generated code write a full
solver or access hidden labels, files, network, credentials, or unrestricted
imports.

## Why It Matters

Hand-designed OR heuristics are useful because they are compact, auditable, and
fast, but they are usually tuned by human iteration. O2 shows how that design
loop can be automated while preserving a strict safety boundary and reporting
where candidates fail. The claim is conservative: discovered heuristics improve
selected quality-runtime-generalization trade-offs under evaluator constraints;
the project does not claim universal dominance or SOTA solver performance.

## One-Command Demo

```bash
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-demo --top-k 3
```

This writes a local evidence package with `reports/final_report.md`,
`reports/technical_report.md`, `reports/portfolio_brief.md`, CSV tables,
plot-ready JSON, top programs, frontier programs, and a rerun manifest.

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

## Benchmark Results

| Benchmark | Evidence | Representative result | Claim boundary |
| --- | --- | --- | --- |
| Online Bin Packing | Held-out synthetic distributions | `seed-000-tight_fit` top program | compact `score_bin` heuristic under evaluator constraints |
| External Bin Packing | BPPLIB / OR-Library-style fixtures | `external_generalization.csv` | external transfer evidence, not SOTA |
| Simple Routing | Held-out route sizes plus 2-opt | `route-seed-003-slack_aware` | `score_next_stop` heuristic comparison |
| Amazon-Style Routing | Local Amazon-shaped fixtures | `phase6-seed-000-travel_fast` | travel-time / driver-likeness frontier trade-off |
| Search Ablation | Fixed local candidate budget | seed, mutation, crossover, LLM-proxy, repair operators | mechanism evidence without live LLM superiority claims |
| Pareto Frontier | Quality, runtime, complexity, failures, gaps | 8 frontier rows | selected trade-offs, not universal dominance |

## Safety Boundary

Generated code is limited to narrow scoring functions. Static checks reject
imports, file access, network/process names, dangerous builtins, disallowed
globals, and dunder access before sandbox execution. Hardened single-call
execution runs in a subprocess with wall-clock timeout handling and optional
platform memory limits.

## Limitations

- Live LLM mutation is optional and requires environment variables.
- External routing evidence is deferred.
- External bin packing fixtures are intentionally small and parser-backed.
- Amazon-style routing uses deterministic local fixtures, not proprietary or
  public Amazon route data.
- Runtime frontier values use a deterministic proxy.
- O2 reports selected trade-offs and does not claim universal dominance.

Current status:

- Phase 0 complete: project direction, roadmap, task memory, and workflow docs.
- Phase 1 complete: program-search skeleton, static checks, restricted
  execution, mutation interface, evaluator records, archive, and lineage.
- Phase 2 complete: online bin packing instances, baselines, evaluator, seed
  candidate sweep, held-out report, and seed archive.
- Phase 3 complete: deterministic mutation/crossover evolution loop,
  tournament selection, novelty filtering, generation metrics, complexity
  tracking, elite archive reporting, and rerunnable top candidates.
- Phase 4 complete: simple routing instances, deterministic baselines,
  `score_next_stop` evaluation, time-window penalties, 2-opt local search,
  held-out instance sizes, and rerunnable top route programs.
- Phase 5 complete: Amazon last-mile routing evaluator scaffold with local
  route loading, route/stop/package features, similarity metrics, deterministic
  baselines, and sandboxed `score_next_stop` evaluation.
- Phase 6 complete: deterministic Amazon heuristic discovery with seed/mutated
  `score_next_stop` programs, held-out route scoring, local-search variants,
  feature contract reporting, and travel-time versus driver-likeness trade-off
  callouts.
- Phase 7 complete: cross-benchmark robustness reporting across held-out random
  seeds, item distributions, routing sizes, and Amazon-style city, route-size,
  density, and quality slices.
- Phase 8 complete: failure-analysis reporting across invalid code, timeout,
  hardcoded heuristic, overfitting, poor generalization, complexity, feasibility
  boundaries, and metric trade-off patterns.
- Final report packaging complete: structured and Markdown report around the
  killer experiment, conservative claims, robustness evidence, failure
  analysis, limitations, and next steps.
- Report tables and plots / optional live LLM integration complete:
  deterministic Markdown tables, plot-ready series, ASCII plot previews, and a
  stdlib-only Gemini mutation provider behind `GEMINI_API_KEY`.
- Hardening milestone complete: subprocess scoring-function isolation, wall
  clock timeout handling, optional platform memory limits, rerun manifests,
  exported report artifacts, top-program evidence files, and a deterministic
  CLI.
- Phase 9 complete: BPPLIB / OR-Library-style bin packing parser, external
  train / validation / test split, external baseline comparison,
  synthetic-to-external transfer gap, final report section,
  `external_generalization.csv`, and `bin_packing_external` CLI support.
- Phase 11 complete: controlled search-mechanism ablation across seed-only,
  mutation, crossover, deterministic LLM-proxy mutation, deterministic
  LLM-proxy repair, and mutation+repair under the same local budget, split,
  timeout, and seeds.
- Phase 15 complete: Pareto frontier reporting across objective quality,
  runtime, program complexity, failure rate, generalization gap, and
  Amazon-style driver-likeness / operational realism.
- Phase 18 complete: research-style technical report packaging the problem,
  system design, sandbox boundary, benchmarks, search loop, external evidence,
  ablation, generalization, failure analysis, limitations, and conclusion.
- Phase 19 complete: README-first portfolio narrative, one-command demo,
  architecture diagram, benchmark evidence table, safety boundary,
  limitations, resume bullets, and portfolio brief artifact.
- Current phase: the job-search portfolio track is complete; optional Phase 10
  external routing evidence is the next research extension.

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

Search ablation validation:

```bash
python3 -m pytest tests/test_search_ablation_phase11.py -v
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

## CLI

The deterministic local CLI is available through the package module:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing --generations 1
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing_external --output-dir /tmp/o2-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark search_ablation --candidate-budget 32 --output-dir /tmp/o2-ablation
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir .
PYTHONPATH=src python3 -m heuristic_discovery inspect --top-k 5
PYTHONPATH=src python3 -m heuristic_discovery rerun-manifest --output-dir . --top-k 5
```

After installation, the console script is also available:

```bash
heuristic-discovery report --output-dir .
```

The external bin packing command uses tiny parser-backed benchmark-style
fixtures by default, so the demo does not require large public benchmark files.
User-provided OR-Library-style or BPPLIB-style files can be passed with
`--external-path` and `--external-format`.

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
print("Search Mechanism Ablation" in markdown)
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
external_routing_evidence
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
print(len(tables["ablation_summary"]["rows"]))
print(len(tables["invalid_code_rate_by_method"]["rows"]))
print(len(tables["best_score_by_budget"]["rows"]))
print(len(tables["pareto_frontier"]["rows"]))
print(len(tables["failure_taxonomy"]["rows"]))
print(tuple(plots["plots"]))
print(len(plots["robustness_generalization_gaps"]["points"]))
print(len(plots["generation_curve_by_method"]["points"]))
print(len(plots["frontier_plot_series"]["points"]))
print("routing-large-routes" in render_report_plots_markdown(plots))
print("external_routing_evidence" in render_report_tables_markdown(tables))
try:
    GeminiMutationProvider.from_env()
except GeminiClientError as exc:
    print(str(exc).split()[0])
PY
```

Expected output without a live key exported:

```text
('benchmark_comparison', 'robustness_summary', 'worst_generalization_gaps', 'external_generalization', 'ablation_summary', 'invalid_code_rate_by_method', 'best_score_by_budget', 'pareto_frontier', 'failure_taxonomy', 'recommended_next_steps')
16
5
8
8
8
17
9
('bin_packing_evolution_best_score', 'amazon_discovery_best_score', 'robustness_generalization_gaps', 'generation_curve_by_method', 'frontier_plot_series', 'failure_rate_by_generation')
15
32
17
True
True
GEMINI_API_KEY
```

## Optional Gemini Mutation

Live mutation is configured only through environment variables. Do not commit
API keys or generated proprietary data.

```bash
export GEMINI_API_KEY="..."
export GEMINI_MODEL="gemini-2.5-flash"  # optional; client default is gemini-2.5-flash
```

`GeminiMutationProvider.from_env()` implements the existing mutation-provider
protocol. The `MutationEngine` still statically validates the returned code
before any evaluator can execute it.

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
reports/plots/plot_series.json
reports/plots/generation_curve_by_method.json
reports/plots/frontier_plot_series.json
artifacts/top_programs/*.py
artifacts/frontier_programs/*.py
artifacts/rerun_manifest.json
```

Regenerate it with:

```bash
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5
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
