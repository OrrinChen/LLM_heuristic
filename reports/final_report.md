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

## External Routing Evidence

Phase 10 evaluates `score_next_stop` routing candidates on TSPLIB-style EUC_2D external fixtures with separate train, validation, and test splits. It reuses nearest-neighbor, cheapest-insertion, 2-opt, and candidate rerun machinery while keeping the claim boundary below LKH, CVRP, SOTA, or Amazon routing superiority.

Benchmark: `routing_external`.
External routing top program: `route-seed-000-nearest`.
External routing held-out test score: `27.040973499999996`.
Synthetic-selected routing program external test score: `27.040973499999996`.
Claim boundary: this section does not claim LKH, CVRP, state-of-the-art solver, Amazon, or universal superiority.

## Search Mechanism Ablation

Phase 11 compares seed-only, mutation, crossover, deterministic LLM-proxy, and repair operators under the same candidate budget, split, timeout, and random seed. This is a fixed local budget ablation, not evidence about live LLM behavior.

Best method under fixed local budget: `crossover_only`.
Best validation score: `7.1`.
Methods compared: `seed_only`, `random_mutation`, `deterministic_template_mutation`, `crossover_only`, `mutation_plus_crossover`, `llm_mutation`, `llm_repair`, `llm_mutation_plus_repair`.
Claim boundary: ablation compares deterministic operators under a fixed local budget; live LLM behavior is not claimed.

## LLM Live Mutation v1

Phase 12 turns Gemini/live LLM mutation into a controlled experiment path. Deterministic fallback and repair providers run by default; optional live Gemini runs are gated behind environment variables and every generated program is logged by hashes, then checked by static validation and sandboxed scoring. The framing is that LLM is one mutation operator inside a constrained program-search system.

Benchmark: `live_llm_mutation`.
Best method: `deterministic_fallback`.
Best validation score: `5.8`.
Live provider configured by default run: `False`.
Claim boundary: LLM is one mutation operator inside a constrained program-search system; live LLM superiority is not claimed.

## Program Semantics And Novelty

Phase 13 adds probe-based behavior fingerprints for `score_bin` programs, then separates exact code novelty from behavior, feature, performance, and complexity evidence. It flags programs that look different in code but rank candidate bins identically on fixed probes.

Benchmark: `bin_packing_semantic_novelty`.
Candidates fingerprinted: `24`.
Behavior probes: `5`.
Behavior clusters: `7`.
Equivalent-program members detected: `21`.
Claim boundary: semantic novelty reports probe-based behavior evidence and equivalence clusters; it does not prove human-level semantic understanding or universal performance improvement.

## Pareto Frontier Report

Phase 15 reports nondominated quality-runtime-complexity-failure-generalization trade-offs per benchmark, with driver-likeness included for Amazon-style routing where that operational metric is available.

Candidate rows: `17`.
Frontier rows: `8`.
Benchmarks covered: `amazon_routing`, `bin_packing`, `simple_routing`.
Claim boundary: The system discovers compact heuristic programs that improve selected quality-runtime-generalization trade-offs, rather than universally dominating classical baselines.

## Generalization And Robustness

The robustness report covers 3 benchmarks and 15 held-out slices.
Worst observed gap slice: `routing-large-routes`.

## Failure Analysis

The failure report tracks 9 failure categories, rejected programs, surviving programs, and worked/failed patterns.
Amazon trade-off callouts: 4.

## Failure Taxonomy v2

Phase 14 upgrades failure analysis into cards with concrete example programs, trigger conditions, validator or evaluator sources, score impact, and possible repair strategies. Repair success rows remain deterministic evidence records.

Failure cards: `11`.
Repair success rows: `11`.
Claim boundary: failure taxonomy v2 explains deterministic failure modes and repair routes; it does not prove automated repair success on arbitrary LLM code.
The report includes repair success evidence for deterministic syntax, unsafe-code, timeout, and LLM hallucinated-feature failure routes.

## Limitations

- Live LLM mutation is optional and remains gated behind environment-variable configuration.
- External bin packing evidence uses parser-backed, small benchmark-style local fixtures by default; large public benchmark files are intentionally not committed.
- External routing evidence uses parser-backed, small TSPLIB-style local fixtures by default; large public benchmark files are intentionally not committed.
- Amazon routing data is represented by deterministic local Amazon-shaped fixtures until public or user-provided data is configured.
- Rendered report artifacts are deterministic local files; PNG plot rendering remains optional when matplotlib is available.
- Pareto frontier runtime is a deterministic local proxy for frontier comparison, not a hardware-independent benchmark.
- The current routing generated-program interface ranks next stops rather than emitting full routes.
- Subprocess memory limits are applied only on platforms that expose compatible resource limits.
- Semantic novelty is probe-based and detects behavior equivalence on fixed probe states; it does not prove human-level semantic understanding.
- Failure taxonomy v2 repair rows are deterministic evidence records, not proof that arbitrary LLM failures can be repaired automatically.

## Recommended Next Steps

- `optional_routing_depth_or_release_polish`: No required job-search roadmap phase remains. Optional extensions are CVRPLIB/time-window routing depth or release polish around the existing evidence package.
