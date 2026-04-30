# LLM-Driven Program Search for OR Heuristics Roadmap

## Current State

Completed:

- Phase 0: Project direction, roadmap, task memory, and Codex workflow skeleton.
- Phase 1: Program-search skeleton, static validation, restricted execution,
  evaluator records, archive, and lineage.
- Phase 2: Online bin packing instances, baselines, score-function evaluator,
  seed candidate sweep, held-out reporting, and seed archive.
- Phase 3: Deterministic mutation/crossover evolution loop, tournament
  selection, novelty filtering, generation metrics, complexity tracking, elite
  archive reporting, and rerunnable top candidates.
- Phase 4: Simple single-vehicle routing instances, baselines, `score_next_stop`
  evaluator, time-window penalties, 2-opt local search, held-out sizes, and
  rerunnable route scoring programs.

Current phase:

- Phase 5: Amazon Last-Mile Routing Evaluator.

Deferred:

- Live LLM integration.
- Crossover beyond simple mutation.
- Amazon last-mile routing evaluator.
- Cloud execution.
- Paid API usage.

Next autonomous action:

```text
Create the Amazon routing evaluator scaffold: loader contract, feature extraction, baseline hooks, and route-similarity metrics.
```

## Project Positioning

**Project ID:** O2 Heuristic Discovery
**Project name:** LLM-Driven Program Search for OR Heuristics
**Alternate name:** LLM-Driven Heuristic Discovery for Operations Research

This project is not a single routing solver. It is a program-search system that uses LLM-generated code, strict sandboxing, automated OR evaluators, and evolutionary selection to discover compact heuristics for operations research problems.

Main thesis:

```text
heuristic design can be automated as constrained program search
```

Resume-level story:

> Built a FunSearch-inspired OR heuristic discovery system that evolves compact routing and bin-packing algorithms through LLM code mutation, sandboxed execution, automated evaluation, and held-out generalization tests.

## Boundary With O1

O1 asks:

```text
Does better prediction lead to better decisions?
```

O2 asks:

```text
Can we automate the discovery of better OR heuristics?
```

O2 should not include demand forecasting, probabilistic inventory modeling, or inventory policy work. O2 owns program search, evolution, sandboxing, routing, bin packing, and Amazon last-mile evaluators.

## Scope Strategy

Do not start with full Amazon routing. Use a two-layer scope:

```text
Layer 1: clean OR benchmark
  online bin packing
  optional knapsack
  simple routing

Layer 2: realistic operational benchmark
  Amazon last-mile route sequencing evaluator
```

Rationale:

- Clean benchmarks make iteration fast and baselines clear.
- Realistic routing proves operational relevance.
- Amazon routing should be an evaluator / benchmark scene, not the only proof of the system.

## Target System Architecture

```text
seed heuristic library
-> LLM mutation / crossover
-> static code validation
-> sandbox execution
-> OR evaluator
-> tournament selection
-> archive of discovered programs
-> generalization tests
-> report discovered heuristic rules
```

LLM-generated programs must only fill a small scoring function, not a full solver.

Example interface:

```python
def score_candidate(state, candidate):
    """
    Return a score for choosing this candidate action.
    Lower score is better.
    """
    return score
```

## Intended Repository Structure

```text
llm-or-heuristic-discovery/
  README.md
  pyproject.toml
  ROADMAP.md
  TASK_MEMORY.md

  configs/
    bin_packing.yaml
    knapsack.yaml
    routing_simple.yaml
    amazon_routing.yaml
    evolution.yaml
    llm.yaml
    sandbox.yaml

  src/
    llm/
      prompt_builder.py
      mutation_engine.py
      crossover_engine.py
      code_repair.py
      model_client.py

    program_search/
      candidate_program.py
      archive.py
      tournament_selection.py
      novelty_filter.py
      evolution_loop.py
      lineage.py

    sandbox/
      static_checks.py
      restricted_exec.py
      timeout.py
      memory_limit.py
      safety.py

    benchmarks/
      bin_packing/
        instances.py
        baselines.py
        evaluator.py

      knapsack/
        instances.py
        baselines.py
        evaluator.py

      routing/
        instances.py
        baselines.py
        evaluator.py
        local_search.py

      amazon_routing/
        loader.py
        features.py
        route_similarity.py
        evaluator.py
        baselines.py

    reports/
      plots.py
      tables.py
      discovered_programs.py
      report_builder.py

  notebooks/
    01_bin_packing_poc.ipynb
    02_evolution_loop.ipynb
    03_discovered_heuristics_analysis.ipynb
    04_simple_routing_transfer.ipynb
    05_amazon_routing_benchmark.ipynb
    06_final_report.ipynb

  tests/
    test_program_sandbox.py
    test_bin_packing_evaluator.py
    test_routing_validity.py
    test_evolution_loop.py
```

## Phase 1: Program-Search Skeleton

Goal: make the LLM-to-code-to-evaluator loop stable before optimizing performance.

Components:

- [x] Candidate program representation.
- [x] Prompt template for constrained function edits.
- [x] LLM mutation interface.
- [x] Static code validation.
- [x] Sandboxed execution.
- [x] Evaluator interface.
- [x] Score logging.
- [x] Program archive.
- [x] Lineage tracking.

Candidate record fields:

```text
program_id
parent_id
generation
code
prompt
benchmark_scores
runtime
failure_reason
created_at
```

Acceptance criteria:

- [x] LLM can only modify an allowed function body.
- [x] Generated code passes static checks before execution.
- [x] Timeouts are killed and recorded.
- [x] Invalid programs get structured failure reasons.
- [x] Every surviving program has lineage.

## Phase 2: Clean Benchmark - Online Bin Packing

Goal: validate the system on a fast, explainable benchmark.

Baselines:

- [x] First Fit.
- [x] Best Fit.
- [x] Worst Fit.
- [x] First Fit Decreasing.
- [x] Best Fit Decreasing.
- [x] Handwritten score heuristic.
- [x] Random heuristic.

LLM-written function:

```python
def score_bin(item_size, bin_remaining_capacity, bin_features):
    """
    Return a score for placing item_size in this bin.
    Lower score is better.
    """
    return score
```

Evaluator metrics:

- [x] Number of bins used.
- [x] Average waste.
- [x] Runtime.
- [x] Failure rate.
- [x] Generalization to unseen item-size distributions.

Instance distributions:

- [x] Uniform small items.
- [x] Uniform mixed items.
- [x] Heavy-tail items.
- [x] Many tiny items plus a few large items.
- [x] Adversarial sequences.
- [x] Held-out random seeds.

Acceptance criteria:

- [x] The system can evaluate 100-1000 candidate programs.
- [x] At least some seed-discovered heuristics outperform naive baselines on selected distributions.
- [x] Top programs can be reproduced and explained.
- [x] Held-out distribution results are reported.

## Phase 3: Evolution Loop

Goal: turn one-shot generation into actual search.

Mechanisms:

- [x] Seed programs.
- [x] Mutation.
- [x] Crossover.
- [x] Tournament selection.
- [x] Elite archive.
- [x] Novelty filter.
- [x] Regression test suite.
- [x] Generalization score.

Scoring:

```text
final_score =
  benchmark_score
  - runtime_penalty
  - complexity_penalty
  - instability_penalty
```

Anti-cheating constraints:

- [x] No hardcoded instance IDs.
- [x] No access to test labels.
- [x] No file access.
- [x] No network access.
- [x] No imports outside a whitelist.
- [x] No global mutable hacks.
- [x] Deterministic output required.

Acceptance criteria:

- [x] Each generation reports best score, median score, and failure rate.
- [x] Generation-vs-score curves are reproducible.
- [x] Program complexity is tracked.
- [x] Top candidates can be rerun from archived code.

## Phase 4: Simple Routing Benchmark

Goal: bridge from clean packing to routing before Amazon.

Problem setup:

```text
single vehicle
given depot and stops
distance matrix
construct route visiting all stops
optional time windows
```

Baselines:

- [x] Random route.
- [x] Nearest neighbor.
- [x] Cheapest insertion.
- [x] 2-opt.
- [x] Nearest neighbor plus 2-opt.

LLM-written options:

```python
def score_next_stop(state, candidate_stop):
    """
    Return a score for choosing candidate_stop next.
    Lower score is better.
    """
    return score
```

or:

```python
def score_insertion(state, candidate_stop, insertion_position):
    """
    Return a score for inserting candidate_stop at insertion_position.
    Lower score is better.
    """
    return score
```

Evaluator metrics:

- [x] Total route length.
- [x] Time-window violation penalty.
- [x] Runtime.
- [x] Route validity.
- [x] Generalization to unseen instance sizes.

Acceptance criteria:

- [x] LLM-discovered scoring rules compete with nearest neighbor or insertion heuristics.
- [x] Adding local search improves route quality.
- [x] Discovered route scoring functions can be explained.

## Phase 5: Amazon Last-Mile Routing Evaluator

Goal: connect the old Driver-Aware Last-Mile Routing idea as a realistic evaluator.

Data concepts:

- [ ] Route-level features.
- [ ] Stop-level features.
- [ ] Package-level features.
- [ ] Travel-time matrix.
- [ ] Historical driver sequence.
- [ ] Route quality label if available in the chosen data split.

Evaluator dimensions:

- [ ] Travel time.
- [ ] Driver-likeness.
- [ ] Pairwise precedence accuracy.
- [ ] Kendall tau distance.
- [ ] Zone transition similarity.
- [ ] Time-window violations.
- [ ] Route compactness.
- [ ] Runtime.

Objective sketch:

```text
score(route) =
  travel_time
  + lambda_1 * driver_preference_penalty
  + lambda_2 * time_window_violation_penalty
  + lambda_3 * route_fragmentation_penalty
  + lambda_4 * runtime_penalty
```

Acceptance criteria:

- Amazon routes can be loaded.
- Nearest neighbor, 2-opt, insertion, and a driver-aware hand heuristic are reproducible.
- Route similarity metrics are computed consistently.
- LLM-discovered route heuristics can be evaluated without special casing.

## Phase 6: LLM Heuristic Discovery on Amazon Routing

Goal: search for routing scoring rules under realistic operational constraints.

LLM-editable function:

```python
def score_next_stop(state, candidate):
    """
    Lower score means the candidate stop is preferred.
    """
    return score
```

Allowed candidate features:

- [ ] Travel time from current stop.
- [ ] Same-zone indicator.
- [ ] Zone transition cost.
- [ ] Time-window slack.
- [ ] Package count.
- [ ] Service time.
- [ ] Stop density.
- [ ] Distance to depot.
- [ ] Angle or direction proxy.
- [ ] Cluster compactness.
- [ ] Remaining route structure.

Baselines:

- [ ] Nearest neighbor.
- [ ] Cheapest insertion.
- [ ] 2-opt.
- [ ] Driver-aware handwritten heuristic.
- [ ] ML next-stop ranker.
- [ ] Hybrid ML plus OR local search.

Variants:

- [ ] LLM heuristic only.
- [ ] LLM heuristic plus 2-opt.
- [ ] LLM heuristic plus feasibility repair.
- [ ] LLM heuristic plus local search.

Acceptance criteria:

- The LLM heuristic improves at least one meaningful trade-off frontier, not necessarily every metric.
- Held-out routes are evaluated.
- Top discovered programs are shown and analyzed.
- Programs that improve travel time but harm driver-likeness are called out.

## Phase 7: Generalization and Robustness

Testing dimensions:

- [ ] Held-out random seeds.
- [ ] Held-out item-size distributions.
- [ ] Held-out routing instance sizes.
- [ ] Held-out Amazon cities if available.
- [ ] Small routes vs large routes.
- [ ] Dense urban routes vs sparse suburban routes.
- [ ] High-quality vs medium-quality historical routes.

Required reporting:

- [ ] Train score.
- [ ] Validation score.
- [ ] Test score.
- [ ] Runtime.
- [ ] Failure rate.
- [ ] Program complexity.
- [ ] Generalization gap.

## Phase 8: Failure Analysis

Failure taxonomy:

- [ ] Generated invalid code.
- [ ] Timeout.
- [ ] Hardcoded heuristic.
- [ ] Overfit to small instances.
- [ ] Poor generalization.
- [ ] Routing feasibility violation.
- [ ] Excessive complexity.
- [ ] Improves travel time but hurts driver-likeness.
- [ ] Improves driver-likeness but is too slow.

Final report must include:

- [ ] Failure taxonomy.
- [ ] Failure rate by generation.
- [ ] Invalid-code rate.
- [ ] Top rejected programs.
- [ ] Top surviving programs.
- [ ] Patterns that worked.
- [ ] Patterns that failed.

## Killer Experiment

Credible target claim:

> LLM-discovered heuristics do not universally dominate, but they discover compact scoring rules that improve selected trade-offs and generalize better than naive heuristics on held-out operational instances.

Benchmarks:

```text
1. Online bin packing:
   First Fit
   Best Fit
   First Fit Decreasing
   handwritten scoring heuristic
   LLM-discovered heuristic

2. Simple routing:
   nearest neighbor
   cheapest insertion
   2-opt
   LLM-discovered next-stop heuristic
   LLM-discovered heuristic + 2-opt

3. Amazon routing:
   nearest neighbor
   2-opt
   handwritten driver-aware heuristic
   ML next-stop ranker
   LLM-discovered heuristic
   LLM-discovered heuristic + local search
```

## Execution Priority

Recommended order:

```text
1. Program-search skeleton.
2. Sandbox and static validation.
3. Bin packing evaluator and baselines.
4. Evolution loop.
5. Held-out bin packing generalization.
6. Simple routing evaluator and baselines.
7. Amazon routing evaluator.
8. Amazon heuristic discovery and failure analysis.
```

MVP cut line:

```text
sandboxed program search
+ bin packing benchmark
+ evolution curve
+ held-out generalization
+ failure taxonomy
```

Everything beyond that is an S-level extension.
