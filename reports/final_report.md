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

## Generalization And Robustness

The robustness report covers 3 benchmarks and 15 held-out slices.
Worst observed gap slice: `routing-large-routes`.

## Failure Analysis

The failure report tracks 9 failure categories, rejected programs, surviving programs, and worked/failed patterns.
Amazon trade-off callouts: 4.

## Limitations

- Live LLM mutation is optional and remains gated behind environment-variable configuration.
- Amazon routing data is represented by deterministic local Amazon-shaped fixtures until public or user-provided data is configured.
- Rendered report artifacts are deterministic local files; PNG plot rendering remains optional when matplotlib is available.
- The current routing generated-program interface ranks next stops rather than emitting full routes.
- Subprocess memory limits are applied only on platforms that expose compatible resource limits.

## Recommended Next Steps

- `external_benchmark_adapter`: Add BPPLIB, OR-Library, TSPLIB, or CVRPLIB-style adapters to test whether discovered heuristics transfer beyond synthetic suites.
- `broader_crossover`: Add AST-level, feature-weight, and fragment crossover only after the hardened evidence package remains stable.
- `cloud_scale_experiments`: Scale deterministic runs after sandbox isolation and external-data adapters are in place.
