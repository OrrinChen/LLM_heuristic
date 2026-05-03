# Sandboxed LLM Program Search for OR Heuristic Discovery

## Abstract

This project studies whether compact heuristic scoring programs can be discovered through constrained program search. The system uses LLM or deterministic mutation operators, static validation, subprocess sandboxing, benchmark evaluators, evolutionary selection, rerun manifests, and held-out generalization tests. Results show that generated heuristics can improve selected trade-offs on bin packing and routing-style benchmarks, while failure analysis shows clear limits under external transfer and strong classical baselines.

## Claim Boundary

Supported claim: A sandboxed LLM program-search loop can discover compact heuristics that improve selected trade-offs on held-out OR benchmark distributions.

The system does not claim universal dominance: The report does not claim universal dominance over classical OR baselines or that LLMs solve OR problems directly.

## Problem

Operations research heuristics are often hand-designed for a specific objective, benchmark family, or operational setting. O2 frames heuristic design as constrained program search over small scoring functions rather than full solver generation.

Evidence references: `project_thesis`, `generated_scoring_function_contract`.

## Why Heuristic Discovery Matters

Compact scoring heuristics are inspectable, cheap to rerun, and easier to audit than opaque end-to-end solvers. This makes them useful for studying quality-runtime-generalization trade-offs under explicit evaluator constraints.

Evidence references: `pareto_frontier.csv`, `failure_taxonomy.csv`.

## System Design

The system connects seed programs, mutation operators, static validation, sandbox execution, benchmark evaluators, archive selection, rerun manifests, and report artifact export. Generated code only implements narrow scoring functions.

Evidence references: `architecture`, `rerun_manifest.json`, `top_programs`.

## Sandbox and Safety Boundary

Generated functions are statically checked before execution and can run inside subprocess isolation with wall-clock timeouts and optional platform memory limits. File access, network access, imports, dangerous calls, and hidden labels remain outside the candidate interface.

Evidence references: `tests/test_program_sandbox.py`, `tests/test_hardening_milestone.py`.

## Benchmarks

Evidence covers online bin packing, simple routing, Amazon-style routing fixtures, and parser-backed external bin-packing and TSPLIB-style routing benchmark-style instances. Each benchmark is compared against deterministic classical baselines.

Evidence references: `bin_packing`, `simple_routing`, `amazon_routing`, `external_bin_packing`, `external_routing`.

## Search Loop

Evolutionary selection evaluates generated candidates under fixed interfaces, records lineage, filters exact duplicate programs, and keeps elite candidates for held-out evaluation.

Evidence references: `generation_curve_by_method.json`, `artifacts/rerun_manifest.json`.

## External Benchmark Evidence

External evidence uses BPPLIB / OR-Library-style bin packing fixtures and TSPLIB-style routing fixtures with train, validation, and test splits. The report compares synthetic-selected and external-selected programs without claiming SOTA, LKH, CVRP, or universal transfer.

Evidence references: `external_generalization.csv`, `routing_external_generalization.csv`, `bin_packing_external`, `routing_external`.

## Ablation

The ablation fixes candidate budget, benchmark split, timeout, evaluation budget, and seeds while comparing seed-only, random mutation, deterministic templates, crossover, LLM-proxy mutation, and repair-style operators.

Evidence references: `ablation_summary.csv`, `generation_curve_by_method.json`.

## LLM As Operator

Phase 12 treats live Gemini as one mutation operator inside the constrained search loop. Candidate audit rows record model, prompt version, temperature, parent ids, response hashes, static-check outcome, sandbox outcome, score, tokens, latency, and cost proxy without storing raw responses or secrets.

Evidence references: `llm_operator_comparison.csv`, `llm_candidate_audit.csv`.

## Generalization

Generalization evidence combines held-out benchmark slices, external bin-packing transfer gaps, and Pareto frontier rows that expose quality, runtime, complexity, failure, and generalization trade-offs.

Evidence references: `robustness_summary.csv`, `worst_generalization_gaps.csv`, `pareto_frontier.csv`.

## Failure Analysis

Failure analysis reports invalid code, unsafe code, timeout, overfitting, poor transfer, complexity, feasibility boundary, and routing trade-off patterns instead of hiding rejected or weak candidates.

Evidence references: `failure_taxonomy.csv`, `failure_cards`.

## Limitations

The evidence package is deterministic and local by default. Live Gemini mutation remains environment-gated, external fixtures are intentionally small, CVRPLIB and time-window routing are deferred, and runtime frontier values use a deterministic proxy.

Evidence references: `README.md`, `TASK_MEMORY.md`, `ROADMAP.md`.

## Conclusion

O2 supports a conservative claim: constrained program search can discover compact heuristics that improve selected trade-offs under strict evaluator and sandbox constraints. It does not establish universal dominance over classical OR baselines.

Evidence references: `final_report.md`, `technical_report.md`.

## Evidence Snapshot

- Benchmarks summarized: `3`.
- Robustness slices: `15`.
- Failure categories: `9`.
- External benchmark: `bin_packing_external`.
- Ablation best method: `crossover_only`.
- Pareto frontier rows: `8`.

## Next Phase

Phase 13: Program Semantics and Novelty.
