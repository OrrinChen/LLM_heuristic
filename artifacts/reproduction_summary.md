# O2 Reproduction Summary

Profile: `local_demo`

Fresh-clone local demo profile that regenerates the evidence package from deterministic built-in benchmark slices.

No API key required. No large external benchmark data required.

## Commands

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir .
```

```bash
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5
```

```bash
python3 -m pytest tests/test_reproducibility_package_phase16.py -q
```

## Required Outputs

- `reports/final_report.md`
- `reports/tables/benchmark_comparison.csv`
- `reports/tables/external_generalization.csv`
- `reports/tables/routing_external_generalization.csv`
- `reports/tables/ablation_summary.csv`
- `reports/tables/pareto_frontier.csv`
- `reports/plots/plot_series.json`
- `artifacts/rerun_manifest.json`
- `artifacts/top_programs`
- `artifacts/reproduction_manifest.json`
- `artifacts/reproduction_summary.md`

## Evidence Focus

- `reports/final_report.md`
- `reports/tables/benchmark_comparison.csv`
- `reports/plots/plot_series.json`
- `artifacts/top_programs`

## Rerun Checks

- Result count: `5`
- Code hashes match: `True`
- Scores match: `True`

## Generated Artifacts

- `artifacts/frontier_programs/amazon_routing-phase6-seed-000-travel_fast.py`
- `artifacts/frontier_programs/amazon_routing-phase6-seed-006-travel_fast.py`
- `artifacts/frontier_programs/bin_packing-seed-001-load_balancer.py`
- `artifacts/frontier_programs/bin_packing-seed-005-load_balancer.py`
- `artifacts/frontier_programs/simple_routing-route-seed-000-nearest.py`
- `artifacts/frontier_programs/simple_routing-route-seed-002-window_guard.py`
- `artifacts/frontier_programs/simple_routing-route-seed-005-nearest.py`
- `artifacts/frontier_programs/simple_routing-route-seed-007-window_guard.py`
- `artifacts/reproduction_manifest.json`
- `artifacts/reproduction_summary.md`
- `artifacts/rerun_manifest.json`
- `artifacts/top_programs`
- `artifacts/top_programs/g01-m001-seed-001-load_balancer.py`
- `artifacts/top_programs/g01-m002-seed-005-load_balancer.py`
- `artifacts/top_programs/seed-001-load_balancer.py`
- `artifacts/top_programs/seed-005-load_balancer.py`
- `artifacts/top_programs/seed-009-load_balancer.py`
- `reports/failure_cards.md`
- `reports/final_report.md`
- `reports/plots/behavior_fingerprint.json`
- `reports/plots/frontier_plot_series.json`
- `reports/plots/generation_curve_by_method.json`
- `reports/plots/plot_series.json`
- `reports/portfolio_brief.md`
- `reports/tables/ablation_summary.csv`
- `reports/tables/benchmark_comparison.csv`
- `reports/tables/best_score_by_budget.csv`
- `reports/tables/duplicate_behavior_clusters.csv`
- `reports/tables/external_generalization.csv`
- `reports/tables/failure_taxonomy.csv`
- `reports/tables/failure_taxonomy_v2.csv`
- `reports/tables/invalid_code_rate_by_method.csv`
- `reports/tables/llm_candidate_audit.csv`
- `reports/tables/llm_operator_comparison.csv`
- `reports/tables/novelty_table.csv`
- `reports/tables/pareto_frontier.csv`
- `reports/tables/recommended_next_steps.csv`
- `reports/tables/repair_success_rate.csv`
- `reports/tables/robustness_summary.csv`
- `reports/tables/routing_external_generalization.csv`
- `reports/tables/worst_generalization_gaps.csv`
- `reports/technical_report.md`

## Claim Boundary

deterministic local reproduction package only; no API key, paid service, large external data, SOTA, or universal dominance claim

## Recommended Next Phase

Optional Phase 17: Local Parallel Runner / Cloud-Scale Search
