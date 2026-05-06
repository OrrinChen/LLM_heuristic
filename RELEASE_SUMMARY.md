# O2 Release Summary

O2 is release-frozen and portfolio-ready. The project is packaged as a
defensible evidence bundle for interviews, resume review, and technical
discussion rather than as a production solver.

## Project Thesis

```text
heuristic design can be automated as constrained program search
```

The system studies whether compact heuristic scoring programs can be generated,
validated, sandboxed, evaluated, selected, and rerun across OR-style benchmark
slices.

## System Architecture

```text
seed heuristic library
-> deterministic or LLM mutation operator
-> static validation
-> subprocess sandbox
-> OR benchmark evaluator
-> archive and rerun manifest
-> report artifacts and portfolio evidence
```

Generated code is restricted to narrow scoring functions such as `score_bin` and
`score_next_stop`. The LLM path is one optional mutation operator inside this
constrained system, not an unrestricted solver.

## Main Evidence Artifacts

- `reports/final_report.md`: executive evidence summary with conservative
  claims, limitations, and recommended next steps.
- `reports/technical_report.md`: research-style narrative covering problem,
  system design, benchmarks, search loop, external evidence, ablation,
  generalization, failure analysis, and limitations.
- `reports/portfolio_brief.md`: resume and interview-oriented project brief.
- `reports/tables/external_generalization.csv`: external bin-packing transfer
  evidence from BPPLIB / OR-Library-style local fixtures.
- `reports/tables/routing_external_generalization.csv`: TSPLIB/CVRPLIB-style
  routing transfer evidence with capacity and time-window metrics.
- `reports/tables/ablation_summary.csv`: fixed-budget comparison of seed,
  mutation, crossover, deterministic LLM-proxy, and repair operators.
- `reports/tables/pareto_frontier.csv`: quality-runtime-complexity-
  generalization trade-off rows.
- `reports/plots/pareto_frontier_main.svg`: deterministic stdlib-only main
  Pareto visual.
- `reports/failure_cards.md` and `reports/tables/failure_taxonomy_v2.csv`:
  failure modes, trigger conditions, detector source, score impact, and repair
  strategy.
- `artifacts/rerun_manifest.json` and
  `artifacts/reproduction_manifest.json`: deterministic rerun and reproduction
  records.
- `artifacts/top_programs/*.py` and `artifacts/frontier_programs/*.py`:
  standalone discovered or frontier scoring programs.

## What The Heuristic Looks Like

The release includes a before/after example at
`examples/top_program_before_after.md`. The representative archived program is
`seed-001-load_balancer`:

```python
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.01)
```

This is a compact scoring function evaluated under constraints, not a full
solver.

Portfolio shorthand:

| Before heuristic | Discovered heuristic | Score/runtime trade-off |
| --- | --- | --- |
| choose the feasible bin with the smallest leftover capacity | `seed-001-load_balancer` | score `7.75`, runtime `0.023680`, complexity `32`; selected trade-off evidence, not a solver-level claim |

## One-Command Reproduction

```bash
make portfolio-demo
```

Manual equivalent:

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-demo --top-k 3
```

The default reproduction path is deterministic, local, and does not require an
API key or large external benchmark corpus. In short: default reproduction does not require an API key.
Live Gemini mutation is optional, environment-gated, and never part of the
default reproduction path.

## Conservative Claim Boundary

O2 supports this claim:

```text
The system discovers compact heuristic programs that improve selected
quality-runtime-generalization trade-offs under strict evaluator constraints.
```

O2 does not claim universal dominance, SOTA solver performance, live LLM
superiority, production routing capability, or LKH/CVRP/VRPTW solver
comparison; superiority on Amazon data is not claimed.

## Known Limitations

- External benchmark evidence uses small parser-backed fixtures by default; a
  larger public benchmark corpus is optional future work.
- Amazon-style routing uses deterministic local fixtures and does not use
  proprietary or public Amazon route data.
- Live Gemini mutation is optional and environment-gated; deterministic fallback
  providers are the default.
- Semantic novelty uses fixed behavior probes, not full semantic equivalence.
- Failure repair evidence is deterministic and local; it does not prove
  arbitrary generated failures can be repaired.
- Local parallel evidence uses process parallelism and a dry-run cloud adapter;
  paid cloud execution remains optional future work.
- Broader crossover remains optional future work.

## Resume Bullets

- Built a Sandboxed LLM-driven OR heuristic discovery system that evolves
  compact bin-packing and routing scoring programs through subprocess-isolated
  execution, evolutionary selection, external benchmark evaluation, rerun
  manifests, robustness analysis, and failure taxonomy reporting.
- Benchmarked discovered scoring heuristics against First Fit, Best Fit,
  FFD/BFD, nearest-neighbor, insertion, and 2-opt baselines, reporting
  quality-runtime-generalization Pareto frontiers across synthetic and
  benchmark-style external fixtures.

## Interview Talking Points

- Why the generated program interface is intentionally narrow.
- How static validation and subprocess sandboxing create a safety boundary.
- How train / validation / test splits and rerun manifests make claims
  auditable.
- Why external fixtures are useful evidence without implying solver-level
  comparisons.
- What the search ablation says about seed, mutation, crossover, deterministic
  LLM-proxy, and repair operators under the same local budget.
- How failure cards and Pareto frontiers make the project defensible by showing
  limits instead of only successes.
- What to do next if the project becomes research work: broader crossover,
  larger public benchmark corpora, or optional paid cloud execution.
