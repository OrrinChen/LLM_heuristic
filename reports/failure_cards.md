# Failure Cards

Claim boundary: failure taxonomy v2 explains deterministic failure modes and repair routes; it does not prove automated repair success on arbitrary LLM code.

## Invalid Syntax

- Category: `invalid_syntax`.
- Example program: `phase14-probe-invalid-syntax` on `bin_packing`.
- Trigger condition: Python parser cannot build an AST for the generated function.
- Detected by: static validation: ast.parse before sandbox execution
- Score impact: Candidate receives no score and never reaches the evaluator.
- Repair Strategy: Regenerate a complete scoring function and rerun static validation.
- Expected effect: A parseable function can proceed to static safety checks.

```python
def score_bin(item_size, bin_remaining_capacity, bin_features): if item_size < bin_remaining_capacity return 0
```

## Unsafe Code

- Category: `unsafe_code`.
- Example program: `phase6-seed-005-unsafe_probe` on `amazon_routing_discovery`.
- Trigger condition: dangerous_call: call to 'open' is blocked at line 2
- Detected by: static validation: dangerous call / file-access guard
- Score impact: Candidate is rejected before sandbox execution to preserve safety.
- Repair Strategy: Remove file, network, process, global, and hidden-label access.
- Expected effect: The repaired program can be sandbox-scored with the same interface.

```python
def score_next_stop(state, candidate_stop): return open("hidden_labels.json").read()
```

## Timeout

- Category: `timeout`.
- Example program: `phase8-probe-driver_like_timeout` on `amazon_routing_discovery`.
- Trigger condition: timeout: candidate exceeded 0.01 seconds
- Detected by: sandbox timeout during generated scoring execution
- Score impact: Unbounded scoring receives no objective score and is recorded.
- Repair Strategy: Replace unbounded loops with straight-line feature scoring.
- Expected effect: Runtime becomes bounded by the evaluator timeout budget.

```python
def score_next_stop(state, candidate_stop): while True: pass
```

## Over-Complex Code

- Category: `over_complex_code`.
- Example program: `phase8-probe-excessive_complexity` on `bin_packing_evolution`.
- Trigger condition: Complexity exceeds the deterministic threshold.
- Detected by: program complexity decomposition and Phase 8 diagnostic probe
- Score impact: Equivalent simpler scoring rules can dominate this program.
- Repair Strategy: Collapse repeated terms into compact residual-capacity scoring.
- Expected effect: Lower complexity improves auditability and frontier fit.

```python
term_0 + term_1 + ... + term_44 complexity probe
```

## Overfit Small Instances

- Category: `overfit_small_instances`.
- Example program: `route-seed-011-return_aware` on `simple_routing`.
- Trigger condition: Held-out slice generalization gap is high on a larger or denser instance family.
- Detected by: Phase 7 robustness slice evaluator
- Score impact: Worst observed gap 68.753356 on routing-large-routes.
- Repair Strategy: Select candidates on larger and denser validation slices.
- Expected effect: Reduces dependence on small-instance structure.

```python
slice=routing-large-routes
```

## Poor External Transfer

- Category: `poor_external_transfer`.
- Example program: `route-seed-000-nearest` on `routing_external`.
- Trigger condition: Synthetic-selected heuristic loses quality on external fixtures.
- Detected by: Phase 9 / Phase 10 transfer tables
- Score impact: Largest deterministic synthetic-to-external gap is 22.971303.
- Repair Strategy: Use external validation splits and report transfer gaps.
- Expected effect: Keeps transfer claims bounded by held-out evidence.

```python
synthetic-selected routing program rerun on TSPLIB fixtures
```

## Baseline-Dominated

- Category: `baseline_dominated`.
- Example program: `route-seed-000-nearest` on `routing_external`.
- Trigger condition: Best discovered candidate does not improve over the baseline.
- Detected by: external baseline comparison table
- Score impact: Best external score 31.597950; strongest baseline 31.928311.
- Repair Strategy: Report baseline dominance and avoid solver-superiority claims.
- Expected effect: Keeps evaluation honest when baselines are strong.

```python
candidate compared with nearest-neighbor, insertion, 2-opt
```

## Runtime Too Slow

- Category: `runtime_too_slow`.
- Example program: `route-seed-001-return_aware` on `simple_routing`.
- Trigger condition: Runtime proxy is high enough to be Pareto dominated.
- Detected by: Phase 15 quality-runtime-complexity frontier
- Score impact: Runtime proxy 0.004284; dominated by 1 peer(s).
- Repair Strategy: Use cheaper score terms when quality is similar.
- Expected effect: Improves quality-runtime trade-off without changing benchmarks.

```python
Balances immediate travel time with eventual return-to-depot cost.
```

## Behavior Duplicate

- Category: `behavior_duplicate`.
- Example program: `seed-000-tight_fit` on `bin_packing_semantic_novelty`.
- Trigger condition: Different code hashes produce identical probe rankings.
- Detected by: Phase 13 behavior fingerprint equivalence detector
- Score impact: 9 programs collapse into one behavior cluster.
- Repair Strategy: Bias mutation toward feature or behavior changes.
- Expected effect: Increases behavior novelty under the fixed probe suite.

```python
9 programs share ranking ((0, 1, 2), (0, 1, 2), (2, 1, 0), (1, 2, 0), (1, 0, 2))
```

## LLM Hallucinated Feature

- Category: `llm_hallucinated_feature`.
- Example program: `llm_repair-000` on `live_llm_mutation`.
- Trigger condition: Generated code references unavailable globals or hidden labels.
- Detected by: Phase 12 static-check audit and repair source metadata
- Score impact: Repair rows record the original dangerous-name failure and only score cleaned code after validation.
- Repair Strategy: Prompt repair with static failure reason and feature contract.
- Expected effect: Hallucinated access is removed before sandbox scoring.

```python
invalid parent used globals()["hidden_solution"] before repair
```

## Objective Gaming

- Category: `objective_gaming`.
- Example program: `phase6-seed-000-travel_fast` on `amazon_routing`.
- Trigger condition: Candidate improves one axis while worsening operational realism.
- Detected by: Phase 15 frontier and Amazon driver-likeness metrics
- Score impact: Operational penalty 0.166667 is reported with objective quality instead of hidden.
- Repair Strategy: Select against Pareto axes including realism and generalization.
- Expected effect: Prevents a single metric from defining success.

```python
Travel-time minimizing rule that can trade off driver-likeness.
```
