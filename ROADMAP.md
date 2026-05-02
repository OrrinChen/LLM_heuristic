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
- Phase 5: Amazon last-mile routing evaluator scaffold with route loading,
  route/stop/package features, reproducible baselines, driver-likeness metrics,
  and sandboxed `score_next_stop` evaluation.
- Phase 6: Deterministic Amazon heuristic discovery with seed/mutated
  `score_next_stop` programs, held-out route scoring, local-search variants,
  feature contract reporting, and travel-time versus driver-likeness trade-off
  callouts.
- Phase 7: Cross-benchmark generalization and robustness reporting across
  held-out item distributions, routing sizes, synthetic Amazon city/density/
  quality slices, runtime, failure rate, complexity, and generalization gaps.
- Phase 8: Failure analysis across invalid code, timeout, overfitting,
  generalization gaps, complexity, feasibility boundaries, and
  travel-time/driver-likeness trade-offs.
- Final report packaging: structured and Markdown final report around the
  killer experiment, conservative claims, robustness evidence, failure
  analysis, limitations, and next steps.
- Report tables and plots / optional live LLM integration: deterministic
  Markdown tables, plot-ready series, ASCII plot previews, and a stdlib-only
  Gemini mutation provider behind `GEMINI_API_KEY`.
- Hardening milestone: subprocess scoring-function isolation, wall-clock
  timeout handling, optional platform memory limits, rerun manifests, exported
  report artifacts, top-program evidence files, and deterministic CLI commands.
- Phase 9: BPPLIB / OR-Library-style bin packing loader, external parser,
  train / validation / test split, external baseline comparison,
  synthetic-to-external transfer gap, report table, and CLI support.
- Phase 11: Search mechanism ablation across seed-only, random mutation,
  deterministic template mutation, crossover, mutation+crossover,
  deterministic LLM-proxy mutation, deterministic LLM-proxy repair, and
  mutation+repair under one fixed local budget.
- Phase 15: Pareto frontier reporting across objective quality, runtime,
  program complexity, failure rate, generalization gap, and Amazon-style
  driver-likeness / operational realism.

Current phase:

- Original roadmap and hardening milestone are complete.
- Phase 9 external bin packing benchmark evidence is complete.
- Phase 11 search mechanism ablation is complete.
- Phase 15 Pareto frontier reporting is complete.
- Next implementation phase is Phase 18: Research-Style Technical Report.

Deferred:

- External routing benchmark evidence on TSPLIB / CVRPLIB-style data.
- Research-style and resume / portfolio packaging.
- Crossover beyond simple mutation.
- Cloud execution.
- Paid API usage.
- Production live-LLM experiment runs beyond optional local smoke checks.

Next autonomous action:

```text
Execute Phase 18 only: package the system design, sandbox boundary, benchmark
evidence, ablation, Pareto frontier, failure analysis, and limitations into a
research-style technical report.
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

- [x] Route-level features.
- [x] Stop-level features.
- [x] Package-level features.
- [x] Travel-time matrix.
- [x] Historical driver sequence.
- [x] Route quality label if available in the chosen data split.

Evaluator dimensions:

- [x] Travel time.
- [x] Driver-likeness.
- [x] Pairwise precedence accuracy.
- [x] Kendall tau distance.
- [x] Zone transition similarity.
- [x] Time-window violations.
- [x] Route compactness.
- [x] Runtime.

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

- [x] Amazon routes can be loaded.
- [x] Nearest neighbor, 2-opt, insertion, and a driver-aware hand heuristic are reproducible.
- [x] Route similarity metrics are computed consistently.
- [x] LLM-discovered route heuristics can be evaluated without special casing.

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

- [x] Travel time from current stop.
- [x] Same-zone indicator.
- [x] Zone transition cost.
- [x] Time-window slack.
- [x] Package count.
- [x] Service time.
- [x] Stop density.
- [x] Distance to depot.
- [x] Angle or direction proxy.
- [x] Cluster compactness.
- [x] Remaining route structure.

Baselines:

- [x] Nearest neighbor.
- [x] Cheapest insertion.
- [x] 2-opt.
- [x] Driver-aware handwritten heuristic.
- [x] ML next-stop ranker.
- [x] Hybrid ML plus OR local search.

Variants:

- [x] LLM heuristic only.
- [x] LLM heuristic plus 2-opt.
- [x] LLM heuristic plus feasibility repair.
- [x] LLM heuristic plus local search.

Acceptance criteria:

- [x] The LLM heuristic improves at least one meaningful trade-off frontier, not necessarily every metric.
- [x] Held-out routes are evaluated.
- [x] Top discovered programs are shown and analyzed.
- [x] Programs that improve travel time but harm driver-likeness are called out.

## Phase 7: Generalization and Robustness

Testing dimensions:

- [x] Held-out random seeds.
- [x] Held-out item-size distributions.
- [x] Held-out routing instance sizes.
- [x] Held-out Amazon cities if available.
- [x] Small routes vs large routes.
- [x] Dense urban routes vs sparse suburban routes.
- [x] High-quality vs medium-quality historical routes.

Required reporting:

- [x] Train score.
- [x] Validation score.
- [x] Test score.
- [x] Runtime.
- [x] Failure rate.
- [x] Program complexity.
- [x] Generalization gap.

## Phase 8: Failure Analysis

Failure taxonomy:

- [x] Generated invalid code.
- [x] Timeout.
- [x] Hardcoded heuristic.
- [x] Overfit to small instances.
- [x] Poor generalization.
- [x] Routing feasibility violation.
- [x] Excessive complexity.
- [x] Improves travel time but hurts driver-likeness.
- [x] Improves driver-likeness but is too slow.

Final report must include:

- [x] Failure taxonomy.
- [x] Failure rate by generation.
- [x] Invalid-code rate.
- [x] Top rejected programs.
- [x] Top surviving programs.
- [x] Patterns that worked.
- [x] Patterns that failed.

## Post-Hardening Roadmap

The core system is complete. The remaining work should strengthen evidence and
presentation rather than add disconnected features.

Main line:

```text
core system complete
-> external benchmark credibility
-> search mechanism evidence
-> LLM-as-operator evidence
-> paper / resume / demo packaging
```

Recommended execution order for a job-search portfolio:

```text
Phase 9 -> Phase 11 -> Phase 15 -> Phase 18 -> Phase 19
```

Full research route:

```text
Phase 9 -> Phase 10 -> Phase 11 -> Phase 12 -> Phase 13 -> Phase 14
-> Phase 15 -> Phase 16 -> Phase 18 -> Phase 19
```

Engineering-platform route:

```text
Phase 9 -> Phase 11 -> Phase 16 -> Phase 17 -> Phase 19
```

Phase 9, Phase 11, and Phase 15 are complete. The current priority is Phase
18. Do not implement later phases while Phase 18 is in progress.

## Phase 9: External Benchmark Evidence

Goal: show that discovered bin packing heuristics are not only tuned to
synthetic in-repo generators.

Scope discipline:

- [x] Do bin packing first.
- [x] Do not add TSPLIB, CVRPLIB, live LLM changes, or cloud execution in this
  phase.
- [x] Do not commit large benchmark files.
- [x] Do not claim SOTA or universal dominance.

Required components:

- [x] BPPLIB / OR-Library-style bin packing loader.
- [x] External instance parser.
- [x] External train / validation / test split.
- [x] External baseline comparison.
- [x] Synthetic-to-external generalization gap.
- [x] External benchmark report table.
- [x] CLI support for `bin_packing_external`.

Core question:

```text
Do discovered heuristics transfer to public benchmark-style bin packing
instances under the same sandbox, baseline, and held-out evaluation discipline?
```

Acceptance criteria:

- [x] Full pytest suite passes.
- [x] Ruff check passes.
- [x] Ruff format check passes.
- [x] CLI can run `bin_packing_external`.
- [x] `reports/final_report.md` includes an external benchmark section.
- [x] `reports/tables/external_generalization.csv` is exported.
- [x] No large benchmark data files are committed.
- [x] Claims remain conservative.

## Phase 10: External Routing Evidence

Goal: evaluate routing-style discovery on public-format routing instances
without jumping directly to complex CVRPTW.

Recommended sequence:

- [ ] 10A: TSPLIB-style TSP loader.
- [ ] 10B: CVRPLIB-style capacitated routing loader.
- [ ] 10C: Optional time-window extension.

First implementation slice:

- [ ] TSPLIB coordinate parser.
- [ ] Distance matrix builder.
- [ ] Nearest neighbor / insertion / 2-opt baseline reuse.
- [ ] `score_next_stop` candidate rerun.
- [ ] External routing split.
- [ ] Routing external generalization table.

Conservative claim:

> The same heuristic discovery loop can be evaluated on external routing-style
> instances, but performance depends on instance structure and baseline
> strength.

Do not claim superiority over OR solvers, LKH, state-of-the-art CVRP solvers, or
real Amazon operations.

## Phase 11: Search Mechanism Ablation

Goal: show that improvements are not just seed heuristics or random chance.

Methods to compare under one evaluation budget:

- [x] Seed-only baseline.
- [x] Random mutation.
- [x] Deterministic template mutation.
- [x] Crossover only.
- [x] Mutation plus crossover.
- [x] LLM mutation.
- [x] LLM repair.
- [x] LLM mutation plus repair.

Controls:

- [x] Same number of candidates.
- [x] Same benchmark split.
- [x] Same timeout.
- [x] Same evaluation budget.
- [x] Same seeds.

Required outputs:

- [x] `reports/tables/ablation_summary.csv`.
- [x] `reports/plots/generation_curve_by_method.json`.
- [x] `reports/tables/invalid_code_rate_by_method.csv`.
- [x] `reports/tables/best_score_by_budget.csv`.

## Phase 12: LLM Live Mutation v1

Goal: make Gemini live mutation a controlled experiment module while keeping
deterministic local providers as the default.

Required components:

- [ ] Provider abstraction polish.
- [ ] Gemini mutation provider.
- [ ] LLM repair provider.
- [ ] Prompt template versioning.
- [ ] LLM response logging without secrets.
- [ ] Cost / token / latency tracking.
- [ ] Invalid-code-rate tracking.
- [ ] Deterministic provider fallback.

Each LLM candidate should record:

```text
model name
prompt version
temperature
parent program ids
raw response hash
cleaned code hash
static check result
sandbox result
score
failure reason
```

Acceptance criteria:

- [ ] Tests pass without `GEMINI_API_KEY`.
- [ ] Optional live smoke runs with `GEMINI_API_KEY`.
- [ ] LLM output never bypasses sandboxing.
- [ ] Reports can compare deterministic and live LLM search.
- [ ] No API key or raw secret is committed.

Core framing:

> LLM is one mutation operator inside a constrained program-search system.

## Phase 13: Program Semantics and Novelty

Goal: distinguish code novelty from behavioral novelty.

Required components:

- [ ] Behavioral fingerprinting on probe instances.
- [ ] Semantic novelty score.
- [ ] Feature usage summary.
- [ ] Program complexity decomposition.
- [ ] Equivalence detection on probe instances.

Novelty dimensions:

- [ ] Code novelty.
- [ ] Behavior novelty.
- [ ] Feature novelty.
- [ ] Performance novelty.

Required outputs:

- [ ] `reports/tables/novelty_table.csv`.
- [ ] `reports/plots/behavior_fingerprint.json`.
- [ ] `reports/tables/duplicate_behavior_clusters.csv`.

## Phase 14: Failure Taxonomy v2

Goal: explain why failures occur, not just count them.

Failure categories to cover:

- [ ] Invalid syntax.
- [ ] Unsafe code.
- [ ] Timeout.
- [ ] Over-complex code.
- [ ] Overfit small instances.
- [ ] Poor external transfer.
- [ ] Baseline-dominated.
- [ ] Runtime too slow.
- [ ] Behavior duplicate.
- [ ] LLM hallucinated feature.
- [ ] Objective gaming.

Each failure type should include:

- [ ] Example program.
- [ ] Trigger condition.
- [ ] Validator or evaluator that detected it.
- [ ] Score impact.
- [ ] Possible repair strategy.

Required outputs:

- [ ] `reports/failure_cards.md`.
- [ ] `reports/tables/failure_taxonomy_v2.csv`.
- [ ] `reports/tables/repair_success_rate.csv`.

## Phase 15: Pareto Frontier Report

Goal: report trade-off frontiers instead of only single-score winners.

Compare:

- [x] Objective quality.
- [x] Runtime.
- [x] Program complexity.
- [x] Failure rate.
- [x] Generalization gap.
- [x] Driver-likeness / operational realism where applicable.

Required outputs:

- [x] `reports/tables/pareto_frontier.csv`.
- [x] `artifacts/frontier_programs/*.py`.
- [x] `reports/plots/frontier_plot_series.json`.

Conservative upgraded claim:

> The system discovers compact heuristic programs that improve selected
> quality-runtime-generalization trade-offs, rather than universally dominating
> classical baselines.

## Phase 16: Reproducibility Package v2

Goal: make core results reproducible from a fresh clone without paid services
or large external files.

Commands may be Make targets or CLI profiles:

```text
make reproduce
make test
make report
make demo
```

or:

```bash
python -m heuristic_discovery reproduce --profile local_demo
python -m heuristic_discovery reproduce --profile external_small
python -m heuristic_discovery reproduce --profile llm_optional
```

Required outputs:

- [ ] `artifacts/reproduction_manifest.json`.
- [ ] `artifacts/reproduction_summary.md`.
- [ ] `reports/final_report.md`.
- [ ] `reports/tables/*.csv`.
- [ ] `reports/plots/*.json`.

Acceptance criteria:

- [ ] Fresh clone can run `local_demo`.
- [ ] API key is not required.
- [ ] Large external data is not required.
- [ ] Results are deterministic.

## Phase 17: Optional Cloud-Scale Search

Goal: scale candidate evaluation only after evidence and reproducibility are
strong.

Priority order:

- [ ] 17A: Local parallel runner.
- [ ] 17B: Checkpoint / resume.
- [ ] 17C: Cloud adapter abstraction.
- [ ] 17D: Optional cloud execution.

Acceptance criteria:

- [ ] Same seed gives the same selected top programs.
- [ ] Parallel results equal sequential results.
- [ ] Failed workers do not corrupt the archive.
- [ ] Cost budget can stop an experiment.

## Phase 18: Research-Style Technical Report

Goal: produce a defendable paper-style narrative.

Working title:

```text
Sandboxed LLM Program Search for OR Heuristic Discovery
```

Report structure:

- [ ] Problem.
- [ ] Why heuristic discovery matters.
- [ ] System design.
- [ ] Sandbox and safety boundary.
- [ ] Benchmarks.
- [ ] Search loop.
- [ ] External benchmark evidence.
- [ ] Ablation.
- [ ] Generalization.
- [ ] Failure analysis.
- [ ] Limitations.
- [ ] Conclusion.

Conservative abstract:

> This project studies whether compact heuristic scoring programs can be
> discovered through constrained program search. The system uses LLM or
> deterministic mutation operators, static validation, subprocess sandboxing,
> benchmark evaluators, evolutionary selection, rerun manifests, and held-out
> generalization tests. Results show that generated heuristics can improve
> selected trade-offs on bin packing and routing-style benchmarks, while failure
> analysis shows clear limits under external transfer and strong classical
> baselines.

## Phase 19: Resume / Portfolio Packaging

Goal: make the project directly usable in resumes, GitHub, demos, and
interviews.

Resume bullet target:

> Built a sandboxed LLM-driven OR heuristic discovery system that evolves
> compact bin-packing and routing scoring programs through subprocess-isolated
> execution, evolutionary selection, external benchmark evaluation, rerun
> manifests, robustness analysis, and failure taxonomy reporting.

README first-screen requirements:

- [ ] What the system does.
- [ ] Why it matters.
- [ ] One-command demo.
- [ ] Core architecture diagram.
- [ ] Benchmark results table.
- [ ] Safety boundary.
- [ ] Limitations.

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

Completed foundation:

```text
1. Program-search skeleton.
2. Sandbox and static validation.
3. Bin packing evaluator and baselines.
4. Evolution loop.
5. Held-out bin packing generalization.
6. Simple routing evaluator and baselines.
7. Amazon routing evaluator.
8. Amazon heuristic discovery and failure analysis.
9. External bin packing benchmark evidence.
11. Search mechanism ablation.
15. Pareto frontier report.
```

Next recommended order:

```text
18. Research-style technical report.
19. Resume / portfolio packaging.
```

Phase 10, Phase 12, Phase 13, Phase 14, Phase 16, and Phase 17 remain optional
extensions unless the target audience requires deeper routing evidence, live LLM
experiments, semantic novelty, failure repair, reproduction profiles, or scale
infrastructure.

MVP cut line:

```text
sandboxed program search
+ bin packing benchmark
+ evolution curve
+ held-out generalization
+ failure taxonomy
```

Everything beyond that is an S-level extension.
