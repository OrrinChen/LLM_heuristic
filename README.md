# O2: LLM-Guided Program Search for OR Heuristics and Trading Rules

A sandboxed LLM program-search loop can discover compact heuristics that improve selected trade-offs on held-out OR benchmark distributions.

This work is a companion to the agent-evaluation project at https://github.com/OrrinChen/Sandbox.

Generated programs fill only a narrow scoring function (`score_bin`, `score_next_stop`, or `score_signal`). The search flow is seed heuristic library, mutation, static validation, subprocess sandbox, evaluator, then archive. The project does not claim universal dominance over classical OR baselines. See [docs/safety_boundary.md](docs/safety_boundary.md) and [reports/final_report.md](reports/final_report.md).

## Key Results

Numbers below are copied from the checked-in evidence. Each row keeps the qualifier already recorded with that number.

| Slice | Recorded result | Qualifier already in the repo |
| --- | --- | --- |
| Online bin packing | Top program `seed-000-tight_fit`. Held-out test score `9.333333333333334`. | Held-out item distributions in `reports/final_report.md`. Not a universal-dominance claim. |
| Bin-packing Pareto row | `seed-001-load_balancer`: objective quality `7.750000`, runtime `0.023680`, complexity `32`. | `reports/tables/pareto_frontier.csv` quality-runtime-generalization frontier row. This is not the held-out test score above. |
| Simple routing | Top program `route-seed-003-slack_aware`. Held-out test score `18.407699375000004`. | Held-out route sizes in `reports/final_report.md`. |
| Amazon-style routing | Top program `phase6-seed-000-travel_fast`. Held-out test score `10.833333333333332`. | Deterministic local Amazon-shaped fixtures. Superiority on Amazon data is not claimed. |
| External bin packing | `seed-000-tight_fit` external held-out test score `5.0` (`5.000000` in the table). | Same external test score as the `first_fit`, `best_fit`, and `best_fit_decreasing` rows in `reports/tables/external_generalization.csv`. External benchmark-style evidence only; no SOTA or universal dominance claim. |
| External routing | `route-seed-000-nearest` external held-out test score `183.649583`. Capacity violation `0.0`. Time-window violation `15.205163333333333`. | `reports/final_report.md`: 3 capacitated and 3 time-window external instances. On `reports/tables/routing_external_generalization.csv` the same external test score is lower than the `nearest_neighbor` (`239.723262`), `cheapest_insertion` (`605.342644`), and `two_opt` (`434.122920`) rows. Routing scores are minimized. No LKH, CVRP/VRPTW solver, Amazon, SOTA, or universal dominance claim. |
| Search ablation | Named best method `crossover_only`. Best validation score `7.1`. | `reports/tables/ablation_summary.csv` records best validation score `7.100000` for every listed method under the fixed local budget. Live LLM behavior is not claimed. |
| Live LLM mutation | Best method `deterministic_fallback`. Best validation score `5.8`. Live provider configured by default: `False`. | LLM is one mutation operator. Live LLM superiority is not claimed. |
| Semantic novelty | `24` candidates fingerprinted, `5` behavior probes, `7` behavior clusters, `21` equivalent-program members. | Probe-based equivalence on fixed states. Not human-level semantic understanding. |
| Pareto frontier | `17` candidate rows, `8` frontier rows. Benchmarks: `amazon_routing`, `bin_packing`, `simple_routing`. | Selected quality-runtime-generalization trade-offs, not universal dominance. |
| Trading signal | Best program `signal-seed-003-spread_guard`. Best validation net return `0.005419600000000001`. Pareto rows: `7`. | `reports/tables/trading_signal_summary.csv` also records best test net return `0.005040`, turnover `0.677500`, and max drawdown `0.000000`. PIT rule-search evidence only; no tradable alpha, investment advice, or live execution claim. |
| Robustness | `3` benchmarks, `15` held-out slices. Worst observed gap slice: `routing-large-routes`. | From `reports/final_report.md`. |
| Failure analysis | `9` failure categories, `11` failure cards, `11` repair success rows. | Deterministic failure and repair records. Not proof that arbitrary LLM failures can be repaired. |

## Quickstart

Python 3.9 or newer. The default path is local and does not require an API key.

```bash
python3 -m pip install -e ".[dev]"
make portfolio-demo
```

`make portfolio-demo` runs:

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-portfolio-demo --top-k 3
```

## Reproduction

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m ruff format --check .
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-demo --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-reproduce-external --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-release-report --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark trading_signal --candidate-count 8 --output-dir /tmp/o2-trading-signal
```

`local_demo` and `external_small` are deterministic and do not need an API key or a large external corpus. Live Gemini mutation is optional, environment-gated, and is not part of the default reproduction path. Larger benchmark files stay outside the repository.

## Limitations

- Default runs are deterministic and local. Live Gemini mutation stays behind environment variables and still passes static validation and the sandbox.
- External bin-packing and routing evidence uses small parser-backed fixtures. Large public corpora are not committed.
- Amazon-style routing uses deterministic local Amazon-shaped fixtures, not proprietary or public Amazon route data.
- Pareto runtime is a deterministic local proxy, not a hardware-independent benchmark.
- Generated routing programs rank the next stop. They do not emit a full route or a full solver.
- Subprocess memory limits apply only on platforms that expose compatible resource limits.
- Semantic novelty detects behavior equivalence on fixed probes.
- Trading-signal evidence is point-in-time benchmark evidence. It does not claim tradable alpha, investment advice, live execution readiness, or production risk control.
- Failure-repair rows are deterministic evidence records.
- The checked-in package does not claim universal dominance, SOTA solver performance, LKH/CVRP/VRPTW solver comparison, or live LLM superiority.

Licensed under the MIT License. Copyright (c) 2026 Orrin Chen.
