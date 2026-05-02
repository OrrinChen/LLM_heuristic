# O2 Portfolio Brief

## Resume Bullets

- Built a sandboxed LLM-driven OR heuristic discovery system that evolves compact bin-packing and routing scoring programs through subprocess-isolated execution, evolutionary selection, external benchmark evaluation, rerun manifests, robustness analysis, and failure taxonomy reporting.
- Benchmarked discovered heuristics against First Fit, Best Fit, FFD/BFD, nearest-neighbor, insertion, and 2-opt baselines, reporting quality-runtime-generalization Pareto frontiers across synthetic and external benchmark-style instances.

## Interview Demo

```bash
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-demo --top-k 3
```

## Core Architecture

```text
seed heuristic library
-> deterministic or LLM mutation operator
-> static validation
-> subprocess sandbox
-> OR benchmark evaluator
-> archive and rerun manifest
-> report artifacts and portfolio evidence
```

## Benchmark Evidence

| benchmark | evidence | top_program | reported_metric | claim |
| --- | --- | --- | --- | --- |
| Online Bin Packing | held-out synthetic distributions | seed-000-tight_fit | 9.333333333333334 | compact score_bin heuristic under evaluator constraints |
| External Bin Packing | BPPLIB / OR-Library-style local fixtures | seed-000-tight_fit | 5.0 | external transfer evidence without SOTA claim |
| External Routing | TSPLIB-style local fixtures | route-seed-000-nearest | 27.040973499999996 | routing transfer evidence without LKH or CVRP claim |
| Simple Routing | held-out route sizes with local-search comparison | route-seed-003-slack_aware | 18.407699375000004 | score_next_stop heuristic plus 2-opt comparison |
| Amazon-Style Routing | deterministic Amazon-shaped route fixtures | phase6-seed-000-travel_fast | 10.833333333333332 | travel-time and driver-likeness frontier trade-off |
| Search Ablation | fixed local candidate budget | crossover_only-000 | 7.1 | operator comparison without live LLM superiority claim |
| Pareto Frontier | quality-runtime-complexity-generalization rows | 8 frontier rows | 17 | selected trade-offs, not universal dominance |

## Safety Boundary

Generated programs are limited to narrow scoring functions. Static checks reject imports, file access, network/process names, dangerous builtins, disallowed globals, and dunder access before subprocess sandbox execution with wall-clock timeout handling.

## Conservative Claim

Supported: A sandboxed LLM program-search loop can discover compact heuristics that improve selected trade-offs on held-out OR benchmark distributions.

Does not claim: universal dominance, SOTA solver performance, or live LLM superiority.

## Limitations

- Live LLM mutation is optional and requires environment variables.
- External bin packing fixtures are small and committed only as parser-backed benchmark-style examples.
- External routing fixtures are small TSPLIB-style examples, not large TSPLIB benchmark corpora.
- Amazon-style routing uses deterministic local fixtures, not proprietary or public Amazon route data.
- The project reports selected trade-offs and does not claim universal dominance or SOTA solver performance.

## Recommended Next Phase

Optional Phase 12: Live LLM Mutation v1
