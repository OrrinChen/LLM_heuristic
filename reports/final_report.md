# LLM-Driven Program Search for OR Heuristics

## Executive Summary

Thesis: heuristic design can be automated as constrained program search.

A sandboxed LLM program-search loop can discover compact heuristics that improve selected trade-offs on held-out OR benchmark distributions.

The discovered heuristics do not universally dominate classical OR baselines; the evidence supports selected trade-offs under strict sandbox and evaluator constraints.

## System Architecture

Seed heuristics and generated scoring functions pass static validation, run in a restricted sandbox with subprocess isolation available for generated scoring calls, enter OR evaluators, and feed archive, manifest, artifact, robustness, and failure-analysis reports.

## Killer Experiment

### Online Bin Packing

A compact `score_bin` heuristic is compared with online and offline bin-packing baselines on held-out item distributions.

Top program: `seed-000-tight_fit`.
Held-out test score: `9.333333333333334`.

### Simple Routing

A constrained `score_next_stop` route heuristic is evaluated against nearest-neighbor, insertion, 2-opt, and local-search variants on held-out route sizes.

Top program: `route-seed-003-slack_aware`.
Held-out test score: `18.407699375000004`.

### Amazon-Style Routing

Amazon-style route sequencing evaluates travel time, driver-likeness, zone behavior, local search, and explicit frontier trade-offs.

Top program: `phase6-seed-000-travel_fast`.
Held-out test score: `10.833333333333332`.

## External Benchmark Evidence

Phase 9 evaluates bin packing candidates on BPPLIB / OR-Library-style external fixtures with separate train, validation, and test splits, then compares synthetic-selected and external-selected programs against classical baselines.

Benchmark: `bin_packing_external`.
External top program: `seed-000-tight_fit`.
External held-out test score: `5.0`.
Synthetic-selected program external test score: `5.0`.
Claim boundary: this section does not claim SOTA or universal dominance.

## Generalization And Robustness

The robustness report covers 3 benchmarks and 15 held-out slices.
Worst observed gap slice: `routing-large-routes`.

## Failure Analysis

The failure report tracks 9 failure categories, rejected programs, surviving programs, and worked/failed patterns.
Amazon trade-off callouts: 4.

## Limitations

- Live LLM mutation is optional and remains gated behind environment-variable configuration.
- External bin packing evidence uses parser-backed, small benchmark-style local fixtures by default; large public benchmark files are intentionally not committed.
- Amazon routing data is represented by deterministic local Amazon-shaped fixtures until public or user-provided data is configured.
- Rendered report artifacts are deterministic local files; PNG plot rendering remains optional when matplotlib is available.
- The current routing generated-program interface ranks next stops rather than emitting full routes.
- Subprocess memory limits are applied only on platforms that expose compatible resource limits.

## Recommended Next Steps

- `search_mechanism_ablation`: Compare seed-only, deterministic mutation, crossover, and LLM-enabled operators under a fixed evaluation budget.
- `pareto_frontier_report`: Report objective-quality, runtime, complexity, failure, and generalization trade-offs instead of a single winner.
- `research_style_report`: Package the system design, sandbox boundary, external evidence, ablation, limitations, and conclusions.
