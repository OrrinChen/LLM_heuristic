# Top Program Before / After

This example shows what a discovered heuristic looks like as code. The selected
program is an archived scoring function evaluated by O2 under sandbox and
benchmark constraints; it is not a full solver.

## Before

A simple bin-packing rule can choose the bin with the smallest leftover capacity
after placing the item:

```text
for each feasible bin:
    projected_remaining = bin_remaining_capacity - item_size
    choose the bin with the smallest projected_remaining
```

That rule is compact and intuitive, but it is handwritten and does not expose a
search process for variants.

## After

Archived top program: `seed-001-load_balancer`

Source artifact: `artifacts/top_programs/seed-001-load_balancer.py`

| Before heuristic | Discovered heuristic | Score/runtime trade-off |
| --- | --- | --- |
| choose the feasible bin with the smallest leftover capacity | `seed-001-load_balancer` | score `7.75`, runtime `0.023680`, complexity `32`; selected Pareto evidence, not a universal claim |

```python
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.01)
```

## Line-by-line

- `def score_bin(...)`: the generated program can only score one candidate bin;
  it cannot create a solver, read files, call the network, or inspect hidden
  labels.
- `projected = ...`: compute remaining capacity after placing the item.
- `if projected < 0`: reject infeasible placements that exceed bin capacity.
- `return 1000000`: give infeasible bins a very large penalty.
- `return abs(projected - 0.01)`: prefer bins that leave a tiny positive amount
  of slack, which encourages tight packing while avoiding overflow.

## What This Does And Does Not Prove

This is evidence that O2 can archive and rerun compact heuristic scoring
programs under strict evaluator constraints. It is not evidence that the system
creates a general-purpose OR solver, beats specialized solvers, or universally
dominates classical heuristics.
