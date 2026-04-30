# O2 Task Memory

## Latest Status

Current branch: `codex/ashare-radar-phase1a`
Latest commit: `feat: add evolution loop`
Current phase: Phase 4 - Simple Routing Benchmark
Main blocker: simple routing instances, baselines, evaluator, local-search bridge, and routing validity tests are not created yet
Next recommended action: create `src/benchmarks/routing/instances.py`, `src/benchmarks/routing/baselines.py`, `src/benchmarks/routing/evaluator.py`, `src/benchmarks/routing/local_search.py`, and `tests/test_routing_validity.py`

## Current Project State

Date initialized: 2026-04-30
Project folder: `/Users/orynwilder/Documents/New project 2/llm-or-heuristic-discovery`
Project identity: O2 Heuristic Discovery
Project name: LLM-Driven Program Search for OR Heuristics

This folder is the O2 project root. It now contains the Codex workflow skeleton, Python package scaffold, Phase 1 program-search modules, sandbox tests, Phase 2 bin packing benchmark modules, bin packing evaluator tests, Phase 3 evolution-loop modules, and evolution-loop tests.

## Completed Phases

### Phase 0: Planning and Workflow Skeleton

Commit: not committed yet
What changed:

- Created `ROADMAP.md`.
- Created `TASK_MEMORY.md`.
- Created `AGENTS.md`.
- Created `VALIDATION.md`.
- Created `RUNBOOK.md`.

Validation:

- 2026-04-30: docs-only workflow validation passed.
- Ran `git diff --check`.
- Confirmed `AGENTS.md`, `ROADMAP.md`, `TASK_MEMORY.md`, `VALIDATION.md`, and `RUNBOOK.md` are present and non-empty.
- Confirmed no trailing whitespace in project Markdown files.

Known limitations:

- Phase 0 docs were created before the first O2 implementation commit and are included with the Phase 1 commit.
- No bin packing benchmark exists yet.

### Phase 1: Program-Search Skeleton

Commit: `feat: complete O2 program search skeleton`

What changed:

- Created `pyproject.toml` with package metadata, pytest configuration, and ruff settings.
- Created immutable candidate program records in `src/program_search/candidate_program.py`.
- Created static AST validation in `src/sandbox/static_checks.py`.
- Created restricted scoring-function execution with timeout and structured failures in `src/sandbox/restricted_exec.py`.
- Created prompt and deterministic mutation interfaces in `src/llm/`.
- Created evaluator result records, in-memory archive, and lineage records in `src/program_search/`.
- Added `tests/test_program_sandbox.py`.
- Added `README.md`.
- Updated `ROADMAP.md` and `VALIDATION.md` for the scaffolded state.

Validation:

- 2026-04-30: `PYTHONPATH=src python3 -m pytest tests/test_program_sandbox.py -q` failed as expected before implementation because `llm` did not exist.
- 2026-04-30: `python3 -m pytest tests/test_program_sandbox.py -q` passed, 19 tests.
- 2026-04-30: `python3 -m pytest -q` passed, 19 tests.
- 2026-04-30: `python3 -m pytest` passed, 19 tests.
- 2026-04-30: `python3 -m pytest tests/test_program_sandbox.py -v` passed, 19 tests.
- 2026-04-30: `python3 -m ruff check .` passed.
- 2026-04-30: `python3 -m ruff format --check .` passed.
- 2026-04-30: `PYTHONPATH=src python3 - <<'PY' ... PY` smoke check printed `True 6.0`.
- 2026-04-30: `git diff --check -- .` passed.
- 2026-04-30: required workflow docs plus `README.md` are present and non-empty.

Known limitations:

- Live LLM integration remains deferred; mutation uses a provider protocol and deterministic test provider.
- The sandbox uses AST checks, restricted builtins, and Unix signal timeouts; subprocess isolation and memory limits are not implemented yet.
- The archive is in-memory only.
- No evolution loop, routing evaluator, or Amazon evaluator exists yet.

### Phase 2: Clean Benchmark - Online Bin Packing

Commit: `feat: add bin packing benchmark`

What changed:

- Created deterministic bin packing instance generation in `src/benchmarks/bin_packing/instances.py`.
- Implemented uniform-small, uniform-mixed, heavy-tail, tiny-plus-large, adversarial, and held-out distributions.
- Implemented First Fit, Best Fit, Worst Fit, First Fit Decreasing, Best Fit Decreasing, handwritten score heuristic, and deterministic random baseline in `src/benchmarks/bin_packing/baselines.py`.
- Implemented `score_bin` sandbox evaluation, candidate-suite evaluation, held-out report generation, and seed candidate archive support in `src/benchmarks/bin_packing/evaluator.py`.
- Added `tests/test_bin_packing_evaluator.py`.
- Added Phase 2 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-04-30: `python3 -m pytest tests/test_bin_packing_evaluator.py -q` failed as expected before implementation because `benchmarks` did not exist.
- 2026-04-30: `python3 -m pytest tests/test_bin_packing_evaluator.py -q` passed, 12 tests.
- 2026-04-30: `python3 -m pytest tests/test_bin_packing_evaluator.py -v` passed, 12 tests.
- 2026-04-30: `python3 -m pytest -q` passed, 31 tests.
- 2026-04-30: `python3 -m pytest` passed, 31 tests.
- 2026-04-30: `python3 -m ruff check .` passed.
- 2026-04-30: `python3 -m ruff format --check .` passed.
- 2026-04-30: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 2 smoke check printed deterministic report values for 120 candidates.
- 2026-04-30: `git diff --check -- .` passed.
- 2026-04-30: required workflow docs plus `README.md` are present and non-empty.

Known limitations:

- Candidate generation is deterministic and template-based until live LLM mutation is connected.
- The best seed candidate improves over random and worst-fit baselines on the default validation suite, but does not beat decreasing offline baselines.
- Runtime metrics are captured, but the evaluator is optimized for correctness and reproducibility rather than high-throughput search.
- Reports are returned as serializable dictionaries; no file-based report artifact is generated yet.

### Phase 3: Evolution Loop

Commit: `feat: add evolution loop`

What changed:

- Created deterministic tournament selection in `src/program_search/tournament_selection.py`.
- Created exact-code novelty filtering in `src/program_search/novelty_filter.py`.
- Created score accounting and program complexity tracking in `src/program_search/scoring.py`.
- Created deterministic mutation/crossover evolution loop, generation reports, failure taxonomy, elite archive reporting, and top-candidate reruns in `src/program_search/evolution_loop.py`.
- Added `tests/test_evolution_loop.py`.
- Added Phase 3 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-04-30: `python3 -m pytest tests/test_evolution_loop.py -q` failed as expected before implementation because `program_search.evolution_loop` did not exist.
- 2026-04-30: `python3 -m pytest tests/test_evolution_loop.py -q` passed, 7 tests.
- 2026-04-30: `python3 -m pytest tests/test_evolution_loop.py -v` passed, 7 tests.
- 2026-04-30: `python3 -m pytest -q` passed, 38 tests.
- 2026-04-30: `python3 -m pytest` passed, 38 tests.
- 2026-04-30: `python3 -m ruff check .` passed.
- 2026-04-30: `python3 -m ruff format --check .` passed.
- 2026-04-30: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 3 smoke check printed deterministic generation and rerun values.
- 2026-04-30: `git diff --check -- .` passed.
- 2026-04-30: required workflow docs plus `README.md` are present and non-empty.

Known limitations:

- Live LLM mutation remains deferred; mutation and crossover are deterministic local templates.
- Default final-score weighting tracks runtime but uses zero runtime penalty so generation curves stay reproducible on local hardware.
- Novelty filtering rejects exact normalized code duplicates only.
- Evolution reports are returned as serializable dictionaries; no plotted generation-vs-score artifact is generated yet.

## Latest Strategic Decision

The old O2 idea, Driver-Aware Last-Mile Routing, is no longer the main project. It becomes a realistic evaluator / benchmark scene inside a broader LLM-driven OR heuristic discovery system.

New O2:

```text
LLM writes compact heuristic functions
-> sandbox validates and executes them
-> OR evaluator scores them
-> evolutionary loop selects, mutates, and archives better programs
-> discovered heuristics are tested on held-out instances
```

## Core Thesis

```text
heuristic design can be automated as constrained program search
```

The project should not claim that LLMs solve OR problems directly. The stronger and more credible claim is that LLM-generated programs, when constrained by strict evaluators, can discover compact heuristics that improve selected trade-offs.

## Scope Rules

Start with clean benchmarks before realistic routing:

```text
Layer 1:
  online bin packing
  optional knapsack
  simple routing

Layer 2:
  Amazon last-mile routing evaluator
```

MVP cut line:

```text
sandboxed program search
+ bin packing benchmark
+ evolution curve
+ held-out generalization
+ failure taxonomy
```

Amazon routing is an S-level extension, not a blocker for a complete MVP.

## Do Not Drift Into

- Do not build only a routing heuristic and call it O2.
- Do not let the LLM write a full solver.
- Do not evaluate only on training instances.
- Do not skip sandboxing.
- Do not allow file access, network access, unrestricted imports, or hidden labels.
- Do not claim universal dominance over classical OR baselines.
- Do not make Amazon data the first dependency.

## Allowed LLM Output Shape

The LLM should only modify small scoring functions.

General form:

```python
def score_candidate(state, candidate):
    """
    Lower score is better.
    """
    return score
```

Bin packing form:

```python
def score_bin(item_size, bin_remaining_capacity, bin_features):
    """
    Lower score means the bin is preferred.
    """
    return score
```

Routing form:

```python
def score_next_stop(state, candidate_stop):
    """
    Lower score means the stop is preferred.
    """
    return score
```

## Main Components To Build

```text
candidate program object
prompt builder
mutation engine
crossover engine
static checks
restricted execution sandbox
timeout and memory limits
benchmark evaluator interface
program archive
tournament selection
lineage tracking
baseline implementations
reporting tables and plots
```

## Highest-Priority Next Tasks

- [x] Create `pyproject.toml` with package metadata, pytest configuration, and ruff configuration. Scientific and LLM-client dependencies remain deferred until the benchmark and live LLM phases need them.
- [x] Create `src/program_search/candidate_program.py`.
- [x] Create `src/sandbox/static_checks.py` with AST validation.
- [x] Create `src/sandbox/restricted_exec.py` for restricted scoring-function execution.
- [x] Add `tests/test_program_sandbox.py` before connecting any LLM.
- [x] Create `src/benchmarks/bin_packing/instances.py`.
- [x] Create `src/benchmarks/bin_packing/baselines.py`.
- [x] Create `src/benchmarks/bin_packing/evaluator.py`.
- [x] Add `tests/test_bin_packing_evaluator.py`.
- [x] Implement a non-LLM seed heuristic archive.
- [x] Add the mutation loop only after sandbox and evaluator tests pass.

## First Milestone Definition

Milestone 1 is complete when:

```text
1. Candidate programs are represented with code, parent, generation, score, and failure reason.
2. Static checks reject imports, file access, network access, and disallowed globals.
3. A scoring function can be executed in a restricted sandbox with timeout.
4. Bin packing instances and baselines run deterministically.
5. At least one seed scoring heuristic is evaluated against First Fit and Best Fit.
```

## Second Milestone Definition

Milestone 2 is complete when:

```text
1. The system evaluates 100+ candidate programs.
2. Each generation reports best score, median score, and invalid-code rate.
3. Top programs are archived and reproducible.
4. Held-out item distributions are evaluated.
5. The report includes a generation-vs-score plot and failure taxonomy.
```

## Amazon Routing Integration Rule

Do not start Amazon routing until:

- The bin packing evaluator is stable.
- The sandbox rejects unsafe code.
- The evolution loop has archived reproducible candidates.
- Simple routing baselines work.

When Amazon routing begins, it should be introduced as an evaluator with operational metrics:

```text
travel time
driver-likeness
pairwise precedence accuracy
Kendall tau distance
zone transition similarity
time-window violations
route compactness
runtime
```

## Report Claims To Protect

Strong claim:

> LLM-discovered programs improve the objective-quality, runtime, and operational-realism frontier under strict evaluator constraints.

Conservative claim:

> A sandboxed LLM program-search loop can discover compact heuristics that outperform simple hand-written baselines on selected OR benchmark distributions and can be stress-tested for generalization.

Use the conservative claim until held-out routing and Amazon evaluator results support the strong claim.

## Open Questions

- Which LLM provider and model should be used for mutation and repair?
- Should the sandbox use pure Python AST checks first, or add subprocess isolation immediately?
- Should bin packing optimize raw bin count, waste, or a weighted score with runtime and complexity penalties?
- Should simple routing use Euclidean synthetic instances first or a TSPLIB-style benchmark?
- Which Amazon routing data split and quality labels are available locally?

## Resume Bullet Draft

> Built a FunSearch-inspired OR heuristic discovery system that evolves compact bin-packing and routing algorithms through LLM code mutation, sandboxed execution, automated evaluation, and held-out generalization tests, then benchmarked discovered heuristics against nearest-neighbor, insertion, 2-opt, and Amazon last-mile routing baselines.
