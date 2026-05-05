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

## External Bin Packing Validation

Run these once Phase 9 external benchmark evidence exists:

```bash
python3 -m pytest tests/test_external_bin_packing_phase9.py -v
```

Expected result:

```text
OR-Library-style and BPPLIB-style parsers load small benchmark fixtures
external train / validation / test splits are disjoint
capacity-scaled waste is computed correctly
external baseline comparison and synthetic-to-external gap are reported
final report, artifact export, and CLI expose bin_packing_external evidence
```

## External Routing Validation

Run these once Phase 10 external routing evidence exists:

```bash
python3 -m pytest tests/test_external_routing_phase10.py -v
```

Expected result:

```text
TSPLIB-style EUC_2D and CVRPLIB-style fixtures parse into routing instances
CVRPLIB demand, depot, and capacity fields are preserved
CVRPLIB time-window and service-time sections are preserved
external routing train / validation / test splits are disjoint
nearest-neighbor, insertion, and 2-opt baselines are reused
score_next_stop candidates rerun on external validation and test splits
final report, artifact export, and CLI expose routing_external evidence
```

## Phase 9 Smoke Validation

Run this after external bin packing modules exist:

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

Expected result:

```text
bin_packing_external
2
seed-000-tight_fit
5.0
True
external benchmark-style evidence only; no SOTA or universal dominance claim
```

## Phase 10 Smoke Validation

Run this after external routing modules exist:

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

Expected result:

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

## Final Report Validation

Run these after final report packaging modules exist:

```bash
python3 -m pytest tests/test_final_report.py -v
```

Expected result:

```text
final report includes required sections and claim boundaries
killer experiment covers bin packing, simple routing, and Amazon routing
robustness and failure-analysis evidence are linked
Markdown rendering states selected trade-offs without universal dominance claims
external benchmark evidence is included without SOTA claims
search mechanism ablation evidence is included under a fixed local budget
Pareto frontier evidence is included without universal dominance claims
program semantics and novelty evidence is included without human-level semantic claims
failure taxonomy v2 evidence explains deterministic failure modes and repairs
recommended next steps prioritize reproducibility package v2 after Phase 14
```

## Final Report Smoke Validation

Run this after final report packaging modules exist:

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

Expected result:

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

## Pareto Frontier Validation

Run these once Phase 15 Pareto frontier reporting exists:

```bash
python3 -m pytest tests/test_pareto_frontier_phase15.py -v
```

Expected result:

```text
objective quality, runtime, program complexity, failure rate,
generalization gap, and operational realism axes are reported
Pareto frontier rows are nondominated within each benchmark
pareto_frontier.csv, frontier_plot_series.json, and frontier program files
are exported
final report includes Pareto frontier evidence without universal dominance claims
```

## Research-Style Technical Report Validation

Run these once Phase 18 technical reporting exists:

```bash
python3 -m pytest tests/test_technical_report_phase18.py -v
```

Expected result:

```text
paper-style sections cover problem, system design, sandbox boundary,
benchmarks, search loop, external evidence, ablation, generalization, failure
analysis, limitations, and conclusion
claim boundaries remain conservative and reject universal dominance
the technical report maps every major section to existing evidence artifacts
report artifact export writes reports/technical_report.md
```

## Portfolio Packaging Validation

Run these once Phase 19 portfolio packaging exists:

```bash
python3 -m pytest tests/test_portfolio_packaging_phase19.py -v
```

Expected result:

```text
portfolio package includes resume bullets, one-command demo, architecture,
benchmark results, safety boundary, limitations, and conservative claim
boundaries
README first screen includes what it does, why it matters, one-command demo,
core architecture, benchmark results, safety boundary, and limitations
report artifact export writes reports/portfolio_brief.md
```

## Portfolio Packaging Smoke Validation

Run this after Phase 19 modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path

from reports.portfolio import (
    build_phase19_package,
    render_portfolio_brief_markdown,
)

package = build_phase19_package()
markdown = render_portfolio_brief_markdown(package)
readme = Path("README.md").read_text(encoding="utf-8")[:4200]
print(package["phase"])
print(len(package["benchmark_results"]))
print(package["recommended_next_phase"])
print("sandboxed LLM-driven OR heuristic discovery system" in markdown)
print("PYTHONPATH=src python3 -m heuristic_discovery report" in readme)
print("## Core Architecture" in readme)
print("does not claim universal dominance" in readme)
PY
```

Expected result:

```text
19
10
Optional Phase 16: Reproducibility Package v2
True
True
True
True
```

## Research-Style Technical Report Smoke Validation

Run this after Phase 18 modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.technical_report import (
    build_phase18_report,
    render_technical_report_markdown,
)

report = build_phase18_report()
markdown = render_technical_report_markdown(report)
print(report["phase"])
print(len(report["sections"]))
print(report["evidence_snapshot"]["benchmark_count"])
print(report["evidence_snapshot"]["pareto_frontier_count"])
print(report["recommended_next_phase"])
print("Sandbox and Safety Boundary" in markdown)
print("External Benchmark Evidence" in markdown)
print("The system does not claim universal dominance" in markdown)
PY
```

Expected result:

```text
18
15
3
8
Phase 16: Reproducibility Package v2
True
True
True
```

## Pareto Frontier Smoke Validation

Run this after Phase 15 modules exist:

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

Expected result:

```text
15
17
8
('amazon_routing', 'bin_packing', 'simple_routing')
amazon_routing
phase6-seed-000-travel_fast
The system discovers compact heuristic programs that improve selected quality-runtime-generalization trade-offs, rather than universally dominating classical baselines.
```

## Search Ablation Validation

Run these once Phase 11 search-mechanism ablation exists:

```bash
python3 -m pytest tests/test_search_ablation_phase11.py -v
```

Expected result:

```text
seed-only, random mutation, deterministic template mutation, crossover,
mutation+crossover, deterministic LLM-proxy mutation, deterministic LLM-proxy
repair, and mutation+repair are compared under one local budget
all methods use the same benchmark split, timeout, evaluation budget, and seeds
LLM-labelled methods are deterministic local proxies and require no live API key
ablation_summary, invalid_code_rate_by_method, best_score_by_budget, and
generation_curve_by_method artifacts are exported
```

## Search Ablation Smoke Validation

Run this after Phase 11 ablation modules exist:

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

Expected result:

```text
bin_packing
8
16
llm_mutation
ablation compares deterministic operators under a fixed local budget; live LLM behavior is not claimed
```

## Live LLM Mutation Validation

Run these once Phase 12 live LLM mutation v1 exists:

```bash
python3 -m pytest tests/test_live_llm_phase12.py -v
```

Expected result:

```text
deterministic fallback runs without GEMINI_API_KEY
fake live provider rows record model, prompt, hashes, tokens, latency, and score
repair provider rows record prompt version and original failure reason
unsafe generated programs fail before sandbox execution
final report, artifact export, and CLI expose live_llm evidence
```

## Phase 12 Smoke Validation

Run this after Phase 12 modules exist:

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

Expected result:

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

## Program Semantics And Novelty Validation

Run these once Phase 13 semantic novelty exists:

```bash
python3 -m pytest tests/test_semantic_novelty_phase13.py -v
```

Expected result:

```text
behavior fingerprints are generated from fixed bin-packing probes
semantic novelty separates code, behavior, feature, and performance novelty
equivalent ranking behavior clusters different programs together
novelty_table, duplicate_behavior_clusters, behavior_fingerprint, final report,
artifact export, and CLI expose Phase 13 evidence
```

## Phase 13 Smoke Validation

Run this after Phase 13 modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from program_search.semantic_novelty import build_phase13_report

report = build_phase13_report(candidate_count=12)
print(report["phase"])
print(report["benchmark"])
print(report["candidate_count"])
print(report["probe_count"])
print(report["behavior_cluster_count"])
print(len(report["duplicate_behavior_clusters"]))
print(report["novelty_rows"][0]["program_id"])
print(report["claim_boundary"])
PY
```

Expected result:

```text
13
bin_packing_semantic_novelty
12
5
4
3
seed-010-prefer_used_bins
semantic novelty reports probe-based behavior evidence and equivalence clusters; it does not prove human-level semantic understanding or universal performance improvement
```

## Failure Taxonomy v2 Validation

Run these once Phase 14 failure cards exist:

```bash
python3 -m pytest tests/test_failure_taxonomy_v2_phase14.py -v
```

Expected result:

```text
all 11 failure cards include examples, triggers, detectors, score impact,
and repair strategies
failure_cards.md, failure_taxonomy_v2.csv, and repair_success_rate.csv export
final report, technical report, portfolio brief, and tables expose Phase 14
recommended next phase moves to reproducibility package v2
```

## Phase 14 Smoke Validation

Run this after Phase 14 modules exist:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.failure_taxonomy_v2 import build_phase14_report

report = build_phase14_report()
print(report["phase"])
print(report["benchmark"])
print(len(report["failure_cards"]))
print(len(report["repair_success_rows"]))
print(report["failure_cards"][0]["category"])
print(report["repair_success_rows"][0]["category"])
print(report["recommended_next_phase"])
print(report["claim_boundary"])
PY
```

Expected result:

```text
14
failure_taxonomy_v2
11
11
invalid_syntax
llm_hallucinated_feature
Phase 16: Reproducibility Package v2
failure taxonomy v2 explains deterministic failure modes and repair routes; it does not prove automated repair success on arbitrary LLM code
```

## Report Tables, Plots, and Live-LLM Client Validation

Run these after report artifact and optional live-LLM modules exist:

```bash
python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -v
```

Expected result:

```text
benchmark, robustness, failure-taxonomy, and next-step tables are rendered
plot-ready generation, robustness-gap, and failure-rate series are rendered
Gemini mutation uses the existing provider protocol behind GEMINI_API_KEY
Gemini model selection can be overridden through GEMINI_MODEL
Gemini test coverage uses fake transport and does not require live API calls
```

## Report Artifact Smoke Validation

Run this after report artifact modules exist:

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

Expected result without a live key exported:

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

## Hardening Milestone Validation

Run these after subprocess sandbox, manifest, artifact export, and CLI modules
exist:

```bash
python3 -m pytest tests/test_hardening_milestone.py -v
```

Expected result:

```text
subprocess scoring execution runs in a child process
infinite loops fail by wall-clock timeout
file access, imports, eval, and network/process names fail static validation
memory-heavy programs fail safely when a memory limit is requested
rerun manifests record code hashes, runtime, seeds, parent ids, and stable scores
report artifacts export final markdown, CSV tables, JSON plot series, top programs, and manifest files
CLI run, report, inspect, and rerun-manifest commands work with deterministic defaults
```

## Reproducibility Package Validation

Run this once Phase 16 exists:

```bash
python3 -m pytest tests/test_reproducibility_package_phase16.py -v
```

Expected result:

```text
local_demo, external_small, and llm_optional profiles are deterministic
no profile requires GEMINI_API_KEY, paid services, or large external data
reproduce CLI writes reports/final_report.md, reports/tables/*.csv, reports/plots/*.json, artifacts/rerun_manifest.json, artifacts/reproduction_manifest.json, and artifacts/reproduction_summary.md
rerun checks confirm stable scores and matching code hashes
Make targets exist for reproduce, test, report, and demo
```

## Local Parallel Runner Validation

Run this once Phase 17 exists:

```bash
python3 -m pytest tests/test_local_parallel_runner_phase17.py -v
```

Expected result:

```text
parallel process evaluation matches sequential top programs and scores
checkpoint/resume reconstructs the full sequential result
worker exceptions are recorded without losing successful candidates
cost budget stops evaluation and preserves checkpoint state
report export writes parallel_runner_summary.csv, checkpoint_resume.csv, and phase17_checkpoint.json
CLI parallel_runner smoke prints parallel_matches_sequential true
cloud adapter status remains dry_run_only and does not execute paid cloud jobs
```

## Reproducibility Smoke Validation

Run these from the repository root:

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-reproduce-local --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-reproduce-external --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile llm_optional --output-dir /tmp/o2-reproduce-llm --top-k 3
```

Expected result:

```text
each command prints deterministic true
each command prints requires_api_key false
each output directory contains artifacts/reproduction_manifest.json
each output directory contains artifacts/reproduction_summary.md
local_demo generates the full deterministic local evidence package
external_small highlights external_generalization.csv and routing_external_generalization.csv
llm_optional highlights llm_operator_comparison.csv and llm_candidate_audit.csv while using deterministic fallback
```

## Hardening Smoke Validation

Run this from the repository root:

```bash
PYTHONPATH=src python3 - <<'PY'
from sandbox.subprocess_exec import execute_scoring_function_subprocess

code = """
def score_candidate(state, candidate):
    return state["capacity"] - candidate["size"]
"""

result = execute_scoring_function_subprocess(
    code,
    {"capacity": 10},
    {"size": 4},
    timeout_seconds=1.0,
)
print(result.ok)
print(result.value)
print(result.metadata["is_subprocess"])
print(result.failure_reason)
PY
```

Expected result:

```text
True
6.0
True
None
```

## CLI Smoke Validation

Run these from the repository root:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing --generations 1 --output-dir /tmp/o2-cli-run
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing_external --output-dir /tmp/o2-cli-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark routing_external --output-dir /tmp/o2-cli-routing-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark search_ablation --candidate-budget 16 --generations 3 --output-dir /tmp/o2-cli-ablation
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark live_llm --candidate-count 4 --output-dir /tmp/o2-cli-live-llm
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark semantic_novelty --candidate-count 24 --output-dir /tmp/o2-cli-semantic
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark parallel_runner --candidate-count 12 --max-workers 2 --output-dir /tmp/o2-cli-parallel
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-cli-report --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery inspect --top-k 2
PYTHONPATH=src python3 -m heuristic_discovery rerun-manifest --output-dir /tmp/o2-cli-rerun --top-k 2
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-cli-reproduce --top-k 2
```

Expected result:

```text
run prints generation_count and writes run_summary.json
bin_packing_external run prints best_external_program_id and writes run_summary.json
routing_external run prints best_external_program_id and writes run_summary.json
search_ablation run prints best_method and writes run_summary.json
live_llm run prints best_method and writes run_summary.json
semantic_novelty run prints behavior_cluster_count and writes run_summary.json
parallel_runner run prints parallel_matches_sequential and writes run_summary.json
report writes reports/final_report.md, reports/tables/*.csv, reports/tables/routing_external_generalization.csv, reports/tables/llm_operator_comparison.csv, reports/tables/llm_candidate_audit.csv, reports/tables/novelty_table.csv, reports/tables/duplicate_behavior_clusters.csv, reports/plots/plot_series.json, reports/plots/behavior_fingerprint.json, reports/plots/frontier_plot_series.json, artifacts/top_programs/*.py, artifacts/frontier_programs/*.py, and artifacts/rerun_manifest.json
inspect prints candidate_id rows
rerun-manifest prints code_hash_matches true rows
reproduce prints deterministic true and writes reproduction_manifest.json plus reproduction_summary.md
```

## Optional Gemini Live Smoke Validation

Only run this when the user explicitly supplies a key or has exported
`GEMINI_API_KEY`. Do not write the key to repository files.

```bash
PYTHONPATH=src python3 - <<'PY'
from llm.model_client import GeminiMutationProvider
from sandbox.static_checks import validate_candidate_code

provider = GeminiMutationProvider.from_env()
code = provider.generate(
    "Return only this Python function:\n"
    "def score_candidate(state, candidate):\n"
    "    return 0\n"
)
validation = validate_candidate_code(code)
print(code.splitlines()[0])
print(validation.ok)
print(validation.failure_reason)
PY
```

Expected result:

```text
def score_candidate(state, candidate):
True
None
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
