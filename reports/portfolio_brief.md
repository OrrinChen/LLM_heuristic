# O2 Portfolio Brief

## Resume Bullets

- Built a sandboxed LLM-driven OR heuristic discovery system that evolves compact bin-packing and routing scoring programs through subprocess-isolated execution, evolutionary selection, external benchmark evaluation, rerun manifests, robustness analysis, and failure taxonomy reporting.
- Benchmarked discovered heuristics against First Fit, Best Fit, FFD/BFD, nearest-neighbor, insertion, and 2-opt baselines, reporting quality-runtime-generalization Pareto frontiers across synthetic and external benchmark-style instances.
- Extended O2 into sandboxed trading-rule program search, constraining generated strategies to PIT market features and evaluating them with lookahead validators, turnover/leverage gates, and net-return/turnover/drawdown/complexity Pareto frontiers.

## Interview Demo

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-demo --top-k 3
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
| External Routing | TSPLIB/CVRPLIB-style local fixtures | route-seed-000-nearest | 183.649583 | routing transfer evidence without LKH or CVRP/VRPTW-solver claim |
| Simple Routing | held-out route sizes with local-search comparison | route-seed-003-slack_aware | 18.407699375000004 | score_next_stop heuristic plus 2-opt comparison |
| Amazon-Style Routing | deterministic Amazon-shaped route fixtures | phase6-seed-000-travel_fast | 10.833333333333332 | travel-time and driver-likeness frontier trade-off |
| Search Ablation | fixed local candidate budget | crossover_only-000 | 7.1 | operator comparison without live LLM superiority claim |
| LLM Live Mutation v1 | hash-only candidate audit with deterministic fallback | deterministic_fallback | 5.8 | LLM as one sandboxed mutation operator, not a solver |
| Program Semantics | behavior fingerprints and duplicate behavior clusters | 7 behavior clusters | 21 | semantic novelty is probe-based, not human-level meaning |
| Pareto Frontier | quality-runtime-complexity-generalization rows | 8 frontier rows | 17 | selected trade-offs, not universal dominance |
| Trading Signal | PIT-only signal fixture with optional LOB adapter | signal-seed-003-spread_guard | 0.005419600000000001 | sandboxed rule search, not tradable-alpha claim |
| Failure Taxonomy v2 | failure cards and deterministic repair rows | 11 failure cards | 11 | explains failure modes, not arbitrary auto-repair |

## Safety Boundary

Generated programs are limited to narrow scoring functions. Static checks reject imports, file access, network/process names, dangerous builtins, disallowed globals, and dunder access before subprocess sandbox execution with wall-clock timeout handling.

## Conservative Claim

Supported: A sandboxed LLM program-search loop can discover compact heuristics that improve selected trade-offs on held-out OR benchmark distributions.

Does not claim: universal dominance, SOTA solver performance, or live LLM superiority.

## Limitations

- Live Gemini mutation is controlled and environment-gated; default runs use deterministic fallback providers.
- Semantic novelty is based on fixed probe behavior fingerprints and does not prove human-level semantic understanding.
- External bin packing fixtures are small and committed only as parser-backed benchmark-style examples.
- External routing fixtures are small TSPLIB/CVRPLIB-style examples, not large public benchmark corpora.
- Amazon-style routing uses deterministic local fixtures, not proprietary or public Amazon route data.
- The project reports selected trade-offs and does not claim universal dominance or SOTA solver performance.
- Failure repair evidence is deterministic and local; it does not prove arbitrary LLM-generated failures can be repaired.
- Trading signal evidence is a PIT-constrained benchmark extension; it does not claim investment advice, tradable alpha, or live execution readiness.

## Recommended Next Phase

No required phase remains; project is release-frozen and portfolio-ready. Optional future work: broader crossover, paid cloud execution, or larger public benchmark corpora.
