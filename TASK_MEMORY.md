# O2 Task Memory

## Latest Status

Current branch: `codex/financial-evidence-release-packaging`
Latest commit: `docs: add s-level portfolio visuals`
Current phase: S-level portfolio polish only; project is release-frozen and portfolio-ready
Main blocker: None; broader crossover, paid cloud execution, and larger public benchmark corpora remain optional future work
Next recommended action: stop at the release-frozen portfolio package unless a future task explicitly requests an extension

## Current Project State

Date initialized: 2026-04-30
Project folder: `/Users/orynwilder/Documents/New project 2/llm-or-heuristic-discovery`
Project identity: O2 Heuristic Discovery
Project name: LLM-Driven Program Search for OR Heuristics

This folder is the O2 project root. It now contains the Codex workflow skeleton, Python package scaffold, Phase 1 program-search modules, sandbox tests, Phase 2 bin packing benchmark modules, bin packing evaluator tests, Phase 3 evolution-loop modules, evolution-loop tests, Phase 4 simple routing modules, routing validity tests, Phase 5 Amazon routing evaluator modules, Amazon evaluator tests, Phase 6 Amazon discovery modules, Amazon discovery tests, Phase 7 robustness reporting modules, robustness reporting tests, Phase 8 failure-analysis reporting modules, failure-analysis tests, final report packaging modules, final report tests, report table/plot artifacts, an optional Gemini live-mutation provider, subprocess sandbox isolation, rerun manifests, artifact export, generated evidence files, a deterministic CLI, Phase 9 BPPLIB / OR-Library-style external bin packing evidence, Phase 10 TSPLIB-style, CVRPLIB-style, and time-window external routing evidence, Phase 11 search mechanism ablation evidence, Phase 12 controlled live LLM mutation evidence, Phase 13 semantic novelty evidence, Phase 14 failure taxonomy v2 evidence, Phase 15 Pareto frontier evidence, Phase 16 reproducibility package profiles, Phase 17 local parallel runner evidence, Phase 18 research-style technical report packaging, Phase 19 resume / portfolio packaging, and release-frozen portfolio-ready summary docs.

It now also includes S-level portfolio polish artifacts: a README-first
representative heuristic snippet, `examples/top_program_before_after.md`, a
short `docs/safety_boundary.md`, a deterministic stdlib-only
`reports/plots/pareto_frontier_main.svg`, and release-summary language making
clear that default reproduction does not require an API key.

## Roadmap Update

2026-05-02:

- Added the post-hardening roadmap to `ROADMAP.md` using the project constraint
  that work should now strengthen evidence and presentation instead of adding
  disconnected features.
- Set Phase 9 as the next implementation phase: external bin packing benchmark
  evidence with BPPLIB / OR-Library-style parsing, external splits, baseline
  comparison, synthetic-to-external generalization gap, CLI support, and
  `external_generalization.csv`.
- Recorded the recommended job-search sequence as Phase 9 -> Phase 11 -> Phase
  15 -> Phase 18 -> Phase 19.
- Explicitly deferred routing external evidence, live LLM expansion, semantic
  novelty, failure taxonomy v2, reproducibility v2, and cloud-scale execution
  until after the external bin packing evidence phase.

2026-05-02 Phase 9 completion:

- Completed external bin packing benchmark evidence only; no TSPLIB, CVRPLIB,
  live LLM, broader crossover, or cloud execution was added.
- Added BPPLIB / OR-Library-style parsers, tiny deterministic external
  benchmark-style fixtures, external train / validation / test splits, external
  baseline comparison, synthetic-to-external transfer reporting,
  `external_generalization.csv`, final report Markdown coverage, and
  `bin_packing_external` CLI support.
- Updated the recommended next phase to Phase 11 search mechanism ablation.

2026-05-02 Phase 11 completion:

- Completed search mechanism ablation under a fixed deterministic local budget;
  no TSPLIB, CVRPLIB, live LLM expansion, semantic novelty, Pareto frontier, or
  cloud execution was added.
- Added an ablation runner comparing seed-only, random mutation, deterministic
  template mutation, crossover-only, mutation plus crossover, deterministic
  LLM-proxy mutation, deterministic LLM-proxy repair, and mutation plus repair
  using the same benchmark split, timeout, candidate budget, and seeds.
- Added `search_ablation` CLI support and report export for
  `ablation_summary.csv`, `invalid_code_rate_by_method.csv`,
  `best_score_by_budget.csv`, and `generation_curve_by_method.json`.
- Updated final report and recommended next steps so Phase 15 Pareto frontier
  reporting is now the next implementation phase.

2026-05-02 Phase 15 completion:

- Completed Pareto frontier reporting only; no external routing, live LLM
  expansion, semantic novelty, failure taxonomy v2, reproducibility profile, or
  cloud execution was added.
- Added a deterministic Phase 15 report comparing objective quality, runtime,
  program complexity, failure rate, generalization gap, and Amazon-style
  driver-likeness / operational realism.
- Added `pareto_frontier.csv`, `frontier_plot_series.json`, and
  `artifacts/frontier_programs/*.py` exports.
- Updated final report and recommended next steps so Phase 18 research-style
  technical reporting is now the next implementation phase.

2026-05-02 Phase 18 completion:

- Completed research-style technical report packaging only; no README-first
  portfolio rewrite, external routing evidence, live LLM expansion, semantic
  novelty, failure taxonomy v2, reproducibility profile, or cloud execution was
  added.
- Added a structured Phase 18 technical report builder and Markdown renderer
  covering the problem, why heuristic discovery matters, system design, sandbox
  and safety boundary, benchmarks, search loop, external benchmark evidence,
  ablation, generalization, failure analysis, limitations, and conclusion.
- Added `reports/technical_report.md` to the deterministic report artifact
  export and CLI evidence package.
- Updated final report next-step recommendations so Phase 19 resume /
  portfolio packaging is now the next implementation phase.

2026-05-02 Phase 19 completion:

- Completed resume / portfolio packaging only; no external routing evidence,
  live LLM expansion, semantic novelty, failure taxonomy v2, reproducibility
  profile, or cloud execution was added.
- Added a structured Phase 19 portfolio package with resume bullets,
  one-command demo command, architecture diagram text, benchmark evidence rows,
  safety boundary, limitations, conservative claim boundaries, and an optional
  next phase.
- Added `reports/portfolio_brief.md` to the deterministic report artifact
  export and CLI evidence package.
- Rewrote the README first screen around what the system does, why it matters,
  one-command demo, core architecture, benchmark results, safety boundary, and
  limitations.
- Updated final report next-step recommendations so optional Phase 10 external
  routing evidence is now the next extension after the completed job-search
  portfolio track.

2026-05-02 Phase 10 completion:

- Completed the Phase 10A TSPLIB-style external routing evidence slice only; no
  CVRPLIB, time-window routing, live LLM expansion, semantic novelty,
  reproduction profile, or cloud execution was added.
- Added TSPLIB-style EUC_2D parsing, directory/file loading, deterministic
  external train / validation / test splits, default tiny local fixtures,
  distance-matrix construction, nearest-neighbor / cheapest-insertion / 2-opt
  baseline reuse, external `score_next_stop` candidate reruns, and
  synthetic-to-external routing transfer reporting.
- Added `routing_external` CLI support and
  `reports/tables/routing_external_generalization.csv` export.
- Updated final report, report tables, technical report, portfolio brief,
  README, RUNBOOK, ROADMAP, VALIDATION, and task memory so optional Phase 12
  live LLM mutation v1 is now the next research extension.

2026-05-03 Phase 12 completion:

- Completed controlled live LLM mutation v1 only; no semantic novelty, failure
  taxonomy v2, CVRPLIB/time-window routing, reproduction profile, or cloud
  execution was added.
- Added provider metadata records with model name, prompt version, temperature,
  response/code hashes, token counts, latency, and cost proxy while preserving
  the existing `generate(prompt) -> code` provider behavior.
- Added deterministic fallback and repair providers plus a Phase 12 experiment
  runner that evaluates generated `score_bin` programs only through existing
  static validation and sandboxed bin-packing scoring.
- Added hash-only candidate audit rows for parent ids, static-check result,
  sandbox result, score, failure reason, runtime, and repair source without
  storing raw responses or API keys.
- Added `live_llm` CLI support and report exports for
  `reports/tables/llm_operator_comparison.csv` and
  `reports/tables/llm_candidate_audit.csv`.
- Updated final report, report tables, technical report, portfolio brief,
  README, RUNBOOK, ROADMAP, VALIDATION, and task memory so optional Phase 13
  program semantics and novelty is now the next research extension.

2026-05-03 Phase 13 completion:

- Completed program semantics and novelty only; no failure taxonomy v2,
  CVRPLIB/time-window routing, reproduction profile, or cloud execution was
  added.
- Added deterministic bin-packing behavior probes, `score_bin` behavior
  fingerprints, behavior hash equivalence clusters, semantic novelty scoring,
  feature usage summaries, performance novelty, and complexity decomposition.
- Added `semantic_novelty` CLI support and report exports for
  `reports/tables/novelty_table.csv`,
  `reports/tables/duplicate_behavior_clusters.csv`, and
  `reports/plots/behavior_fingerprint.json`.
- Updated final report, report tables, plot series, technical report,
  portfolio brief, README, RUNBOOK, ROADMAP, VALIDATION, and task memory so
  optional Phase 14 failure taxonomy v2 is now the next research extension.

2026-05-04 Phase 14 completion:

- Completed failure taxonomy v2 only; no CVRPLIB/time-window routing,
  reproduction profile, cloud execution, or live LLM campaign was added.
- Added deterministic failure cards covering invalid syntax, unsafe code,
  timeout, over-complex code, overfit small instances, poor external transfer,
  baseline domination, runtime too slow, behavior duplicates, LLM hallucinated
  features, and objective gaming.
- Each failure card records an example program, trigger condition,
  validator/evaluator source, score impact, and possible repair strategy.
- Added deterministic repair success rows for syntax, unsafe-code, timeout,
  and LLM hallucinated-feature routes while keeping the claim boundary below
  arbitrary automated repair.
- Added report exports for `reports/failure_cards.md`,
  `reports/tables/failure_taxonomy_v2.csv`, and
  `reports/tables/repair_success_rate.csv`.
- Updated final report, report tables, technical report, portfolio brief,
  README, RUNBOOK, ROADMAP, VALIDATION, and task memory so optional Phase 16
  reproducibility package v2 is now the next research extension.

2026-05-04 Phase 16 completion:

- Completed reproducibility package v2 only; no CVRPLIB/time-window routing,
  cloud execution, or live LLM campaign was added.
- Added deterministic local reproduction profiles for `local_demo`,
  `external_small`, and `llm_optional`.
- Added `python3 -m heuristic_discovery reproduce` CLI support that regenerates
  report artifacts, reruns the top-candidate manifest, writes
  `artifacts/reproduction_manifest.json`, and writes
  `artifacts/reproduction_summary.md`.
- Added `make reproduce`, `make test`, `make report`, and `make demo` targets.
- Updated README, RUNBOOK, ROADMAP, VALIDATION, technical report, portfolio
  brief, final-report next steps, and tests so optional Phase 17 local parallel
  runner / cloud-scale search is now the next research extension.

2026-05-05 Phase 17 completion:

- Completed local parallel runner evidence only; no paid cloud execution,
  provider binding, CVRPLIB, or time-window routing was added.
- Added process-parallel bin-packing candidate evaluation that matches
  sequential selected top programs and result signatures under the same
  deterministic candidate set.
- Added checkpoint/resume JSON support, worker-exception failure records,
  cost-budget stopping, and a dry-run cloud adapter boundary.
- Added `parallel_runner` CLI support plus report exports for
  `reports/tables/parallel_runner_summary.csv`,
  `reports/tables/checkpoint_resume.csv`, and
  `artifacts/phase17_checkpoint.json`.
- Updated README, RUNBOOK, ROADMAP, VALIDATION, report tables, technical
  report, portfolio brief, final-report next steps, and tests so no required
  roadmap phase remains.

2026-05-05 Phase 10B completion:

- Completed the optional CVRPLIB-style capacitated routing evidence slice only;
  no time-window routing, paid cloud execution, live LLM campaign, or CVRP
  solver comparison was added.
- Added CVRPLIB-style parsing for `TYPE: CVRP`, EUC_2D coordinates, demands,
  depot section, and vehicle capacity.
- Extended routing instances and route scoring with stop demand,
  `vehicle_capacity`, capacity-aware depot-return splitting, capacity
  violation metrics, and vehicle-count metrics while preserving the narrow
  `score_next_stop` program interface.
- Added `routing_external --external-format cvrplib` CLI support and default
  tiny CVRPLIB-style local fixtures alongside the existing TSPLIB-style
  fixtures.
- Updated `routing_external_generalization.csv`, final report, technical
  report, portfolio brief, README, RUNBOOK, ROADMAP, VALIDATION, and tests so
  Phase 10B is complete and only optional time-window routing remains deferred.

2026-05-05 Phase 10C completion:

- Completed the optional time-window routing evidence slice only; no paid cloud
  execution, live LLM campaign, public CVRPTW corpus, or VRPTW solver comparison
  was added.
- Extended the CVRPLIB-style parser with `TIME_WINDOW_SECTION` and
  `SERVICE_TIME_SECTION` support while preserving the existing demand, depot,
  capacity, and coordinate parser behavior.
- Updated capacity-aware route time-window violation scoring so depot returns
  triggered by vehicle capacity are included in elapsed-time accounting.
- Added time-window instance counts and held-out time-window violation metrics
  to the external routing report table and final report narrative.
- Updated checked-in evidence artifacts, README, RUNBOOK, ROADMAP, VALIDATION,
  technical report, portfolio brief, and tests so Phase 10C is complete and
  broader crossover is now the next optional extension.
- Validation:
  - `python3 -m pytest tests/test_external_routing_phase10.py -q` failed first
    as expected before implementation because time-window parsing and reporting
    were not present.
  - `python3 -m pytest tests/test_external_routing_phase10.py -q` passed, 13
    tests.
  - `python3 -m pytest tests/test_external_routing_phase10.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_technical_report_phase18.py tests/test_portfolio_packaging_phase19.py tests/test_failure_taxonomy_v2_phase14.py tests/test_reproducibility_package_phase16.py -q`
    passed, 48 tests.
  - `python3 -m pytest -q` passed, 166 tests before formatting; a subsequent
    full-suite rerun was manually interrupted after a slow tail with 154 tests
    already passed and no assertion failure shown, then the tail slice was
    rerun directly and passed.
  - `python3 -m pytest tests/test_search_ablation_phase11.py tests/test_semantic_novelty_phase13.py tests/test_technical_report_phase18.py -q`
    passed, 15 tests.
  - Final post-format `python3 -m pytest -q` passed, 166 tests.
  - `python3 -m ruff check .` passed.
  - `python3 -m ruff format --check .` passed after formatting
    `src/benchmarks/routing/external.py` and
    `tests/test_external_routing_phase10.py`.
  - `git diff --check -- .` passed.
  - Phase 10C direct smoke printed `external_formats ['cvrplib', 'tsplib']`,
    `time_window_instance_count 3`, `best_external_test_capacity_violation
    0.0`, `best_external_test_time_window_violation 15.205163`, and the
    CVRP/VRPTW-safe claim boundary.
  - `PYTHONPATH=src python3 -m heuristic_discovery run --benchmark routing_external --output-dir /tmp/o2-phase10c-routing-default-final`
    passed and wrote a routing external summary.
  - `PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-phase10c-reproduce-external-final --top-k 2`
    passed with deterministic rerun checks and no API key or large external data
    requirement.

2026-05-05 release polish:

- Scope is final release polish only; no Phase 20, new benchmark feature,
  broader crossover, cloud execution, or expanded live LLM experiment was added.
- Added `RELEASE_SUMMARY.md` as the 3-minute portfolio summary covering thesis,
  architecture, evidence artifacts, one-command reproduction, conservative
  claim boundary, limitations, resume bullets, and interview talking points.
- Tightened the README first screen around what O2 is, why it matters,
  one-command demo, architecture, benchmark evidence, safety boundary, and
  limitations without the long phase-by-phase dump at the top.
- Added a release validation checklist covering pytest, ruff, format check,
  `local_demo` reproduction, `external_small` reproduction, report export,
  secret scan, and large-file scan.
- Marked the project release-frozen and portfolio-ready in ROADMAP, RUNBOOK,
  VALIDATION, and task memory.
- Optional future work remains broader crossover, paid cloud execution, and
  larger public benchmark corpora.
- Validation:
  - `python3 -m pytest tests/test_release_polish.py -q` failed first as
    expected because `RELEASE_SUMMARY.md`, release-frozen status markers, and
    release validation checklist were not present yet.
  - `python3 -m pytest tests/test_release_polish.py tests/test_portfolio_packaging_phase19.py tests/test_final_report.py tests/test_technical_report_phase18.py tests/test_failure_taxonomy_v2_phase14.py tests/test_live_llm_phase12.py tests/test_pareto_frontier_phase15.py tests/test_semantic_novelty_phase13.py tests/test_search_ablation_phase11.py -q`
    passed, 45 tests.
  - `python3 -m pytest tests/test_release_polish.py -q` passed, 5 tests after
    tightening the release secret-scan pattern.
  - `PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir . --top-k 5`
    passed and regenerated checked-in report and reproduction artifacts.
  - `PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-release-external --top-k 3`
    passed with deterministic rerun checks and no API key or large external data
    requirement.
  - `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-release-report --top-k 3`
    passed and exported final report, tables, plot-ready JSON, portfolio brief,
    technical report, top programs, and frontier programs.
  - Release secret scan with key-shaped patterns passed with no matches.
  - Release large-file scan passed with no files over 5 MB.
  - `python3 -m ruff check .` passed.
  - `python3 -m ruff format --check .` passed.
  - `git diff --check -- .` passed.
  - Final `python3 -m pytest -q` passed, 171 tests.

2026-05-06 S-level portfolio polish:

- Scope is presentation-only S-level portfolio polish; no Phase 20, new
  benchmark feature, broader crossover, cloud execution, or expanded live LLM
  experiment was added.
- Tightened the README first screen with a representative before/after
  heuristic snippet, a compact Pareto evidence table, a retitled Search Flow
  diagram, links to the release summary, top-program example, safety-boundary
  doc, and an explicit API-key-free default reproduction statement.
- Added `examples/top_program_before_after.md` to show the selected archived
  `seed-001-load_balancer` `score_bin` program and explain it line by line as a
  scoring function rather than a full solver.
- Added `docs/safety_boundary.md` as a short interviewer-friendly explanation
  of interface restrictions, static validation, subprocess sandbox execution,
  timeout/memory limits, structured failures, and no file/network/import/
  credential access.
- Added deterministic stdlib-only Pareto SVG export at
  `reports/plots/pareto_frontier_main.svg` from existing Pareto rows; this is
  a rendered evidence artifact, not a new experiment.
- Updated `RELEASE_SUMMARY.md`, ROADMAP, RUNBOOK, VALIDATION, and tests to keep
  the release-frozen claim boundary conservative and make clear that default
  reproduction does not require an API key.
- Validation:
  - `python3 -m pytest tests/test_release_polish.py tests/test_hardening_milestone.py tests/test_report_tables_plots_and_live_llm.py -q`
    failed first as expected before the SVG renderer and release-polish docs
    were implemented.
  - `python3 -m pytest tests/test_release_polish.py tests/test_hardening_milestone.py tests/test_report_tables_plots_and_live_llm.py -q`
    passed, 29 tests.
  - `python3 -m pytest tests/test_release_polish.py tests/test_portfolio_packaging_phase19.py -q`
    passed, 13 tests.
  - `python3 -m pytest -q` passed, 175 tests.
  - `python3 -m ruff check .` passed.
  - `python3 -m ruff format --check .` passed after formatting
    `src/reports/plots.py`.
  - `git diff --check -- .` passed.
  - `PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir . --top-k 5`
    passed and regenerated checked-in evidence, including
    `reports/plots/pareto_frontier_main.svg`.
  - `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-s-polish-report --top-k 3`
    passed and exported final report, tables, JSON plot series, top programs,
    frontier programs, and the deterministic Pareto SVG.
  - `PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-s-polish-external --top-k 3`
    passed with deterministic rerun checks and no API key or large external
    data requirement.
  - Release secret scan with key-shaped patterns passed with no matches.
  - Release large-file scan passed with no files over 5 MB.

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

### Phase 4: Simple Routing Benchmark

Commit: `feat: add simple routing benchmark`

What changed:

- Created deterministic routing instance generation in `src/benchmarks/routing/instances.py`.
- Implemented uniform, clustered, line, and held-out synthetic route distributions with depot, stops, distance matrix, optional time windows, and held-out stop counts.
- Implemented random route, nearest neighbor, cheapest insertion, 2-opt, and nearest neighbor plus 2-opt baselines in `src/benchmarks/routing/baselines.py` and `src/benchmarks/routing/local_search.py`.
- Implemented `score_next_stop` sandbox evaluation, route construction, local-search evaluation, candidate-suite comparison, and Phase 4 report generation in `src/benchmarks/routing/evaluator.py`.
- Added `tests/test_routing_validity.py`.
- Added Phase 4 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-04-30: `python3 -m pytest tests/test_routing_validity.py -q` failed as expected before implementation because `benchmarks.routing` did not exist.
- 2026-04-30: `python3 -m pytest tests/test_routing_validity.py -q` passed, 12 tests.
- 2026-04-30: `python3 -m pytest -q` passed, 50 tests.
- 2026-04-30: `python3 -m ruff check .` passed.
- 2026-04-30: `python3 -m ruff format --check .` passed.
- 2026-04-30: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 4 smoke check printed deterministic report values: 8 candidates, validation score 8.626646, local-search validation score 7.227464, held-out test score 18.407699, 8 held-out instances, top program `route-seed-003-slack_aware`.

Known limitations:

- Routing instances are synthetic Euclidean benchmarks, not TSPLIB or Amazon-derived routes.
- Candidate generation remains deterministic and template-based until live LLM mutation is connected.
- The current routing evaluator supports the `score_next_stop` contract only; insertion-scoring programs remain deferred.
- 2-opt is accepted in evaluator reports only when the weighted distance plus time-window score does not worsen.

### Phase 5: Amazon Last-Mile Routing Evaluator

Commit: `feat: add amazon routing evaluator`

What changed:

- Created local Amazon-style route loading in `src/benchmarks/amazon_routing/loader.py`.
- Added immutable route, stop, package, depot, travel-time, historical sequence, and quality-label records without requiring proprietary data.
- Added route and stop feature extraction in `src/benchmarks/amazon_routing/features.py`.
- Added pairwise precedence accuracy, Kendall tau distance, zone transition similarity, and route compactness metrics in `src/benchmarks/amazon_routing/route_similarity.py`.
- Implemented nearest neighbor, cheapest insertion, 2-opt, and driver-aware baselines in `src/benchmarks/amazon_routing/baselines.py`.
- Implemented `score_next_stop` sandbox evaluation, candidate-suite evaluation, failure taxonomy, held-out reporting, and Phase 5 report generation in `src/benchmarks/amazon_routing/evaluator.py`.
- Added `tests/test_amazon_routing_evaluator.py`.
- Added Phase 5 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-04-30: `python3 -m pytest tests/test_amazon_routing_evaluator.py -q` failed as expected before implementation because `benchmarks.amazon_routing` did not exist.
- 2026-04-30: `python3 -m pytest tests/test_amazon_routing_evaluator.py -q` passed, 9 tests.
- 2026-04-30: `python3 -m pytest -q` passed, 59 tests.
- 2026-04-30: `python3 -m ruff check .` passed.
- 2026-04-30: `python3 -m ruff format --check .` passed.
- 2026-04-30: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 5 smoke check printed deterministic report values: 8 candidates, failure rate 0.125, best program `amazon-seed-000-nearest`, validation score 12.666667, held-out test score 12.666667, 2 held-out routes, failure taxonomy `['dangerous_call']`.

Known limitations:

- The evaluator uses local synthetic Amazon-shaped records until public or user-provided route files are configured.
- The driver-aware baseline can replay the historical sequence, but generated programs do not receive quality labels or historical positions in their candidate features.
- Package features currently include counts, weight, service time, and time windows; richer package dimensions remain deferred.
- Reports are serializable except for the in-memory `splits["test_routes"]` convenience field used for rerun tests.

### Phase 6: LLM Heuristic Discovery on Amazon Routing

Commit: `feat: add amazon heuristic discovery`

What changed:

- Added the Phase 6 candidate feature contract in `src/benchmarks/amazon_routing/features.py`.
- Added travel-time, same-zone, zone transition, time-window slack, package count, service time, stop density, depot distance, angle proxy, cluster compactness, and remaining-route features.
- Added deterministic `ml_next_stop_ranker` and `hybrid_ml_plus_local_search` baselines in `src/benchmarks/amazon_routing/baselines.py`.
- Created deterministic Amazon heuristic discovery in `src/benchmarks/amazon_routing/discovery.py`.
- Reused archive, novelty filtering, tournament selection, complexity scoring, sandbox execution, and held-out reruns for Amazon `score_next_stop` programs.
- Added `tests/test_amazon_heuristic_discovery.py`.
- Added Phase 6 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-05-01: `python3 -m pytest tests/test_amazon_heuristic_discovery.py -q` failed as expected before implementation because `benchmarks.amazon_routing.discovery` did not exist.
- 2026-05-01: `python3 -m pytest tests/test_amazon_heuristic_discovery.py -q` passed, 5 tests.
- 2026-05-01: `python3 -m pytest tests/test_amazon_routing_evaluator.py tests/test_amazon_heuristic_discovery.py -q` passed, 14 tests.
- 2026-05-01: `python3 -m pytest -q` passed, 64 tests.
- 2026-05-01: `python3 -m ruff check .` passed.
- 2026-05-01: `python3 -m ruff format --check .` passed.
- 2026-05-01: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 6 smoke check printed deterministic report values: 3 generations, final best score 10.855333, top program `phase6-seed-000-travel_fast`, held-out top score 10.833333, 4 trade-off callouts, 4 frontier improvements, failure taxonomy `['dangerous_call']`, rerun ok `True`.

Known limitations:

- Live LLM mutation remains deferred; Phase 6 uses deterministic seed, mutation, and crossover templates.
- Amazon routes remain synthetic Amazon-shaped fixtures until public or user-provided route files are configured.
- The ML next-stop baseline is a deterministic linear proxy, not a trained model.
- Trade-off reports are dictionary artifacts only; plotted Pareto/frontier charts remain deferred.

### Phase 7: Generalization and Robustness

Commit: `feat: add robustness reporting`

What changed:

- Created `src/reports/robustness.py`.
- Added cross-benchmark robustness summaries for bin packing, simple routing, and Amazon routing.
- Reported train score, validation score, test score, runtime, failure rate, program complexity, and validation-to-test generalization gap for one deterministic top program per benchmark.
- Added robustness slice rows for held-out random seeds, held-out item-size distributions, held-out routing instance sizes, synthetic Amazon station-code/city slices, small versus large routes, dense urban versus sparse suburban routes, and high versus medium quality historical routes.
- Added worst generalization gap reporting and combined failure taxonomy reporting.
- Added `tests/test_robustness_reporting.py`.
- Added Phase 7 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-05-01: `python3 -m pytest tests/test_robustness_reporting.py -q` failed as expected before implementation because `reports.robustness` did not exist.
- 2026-05-01: `python3 -m pytest tests/test_robustness_reporting.py -q` passed, 4 tests.
- 2026-05-01: `python3 -m pytest tests/test_robustness_reporting.py -v` passed, 4 tests.
- 2026-05-01: `python3 -m pytest -q` passed, 68 tests.
- 2026-05-01: `python3 -m ruff check .` passed.
- 2026-05-01: `python3 -m ruff format --check .` passed.
- 2026-05-01: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 7 smoke check printed deterministic report values: 3 benchmarks, 15 slice rows, benchmark keys `('bin_packing', 'simple_routing', 'amazon_routing')`, top programs `seed-000-tight_fit`, `route-seed-011-return_aware`, and `phase6-seed-000-travel_fast`, generalization gaps `0.833333`, `9.907981`, and `0.0`, worst gap slice `routing-large-routes`, worst gap `68.753356`, failure taxonomy `['dangerous_call']`.

Known limitations:

- Amazon city, density, and quality robustness slices are deterministic Amazon-shaped fixtures until public or user-provided data is configured.
- Runtime values are local smoke metrics and should not be compared across machines.
- The report is a dictionary artifact; plotted robustness dashboards remain deferred.

### Phase 8: Failure Analysis

Commit: `feat: add failure analysis reporting`

What changed:

- Created `src/reports/failure_analysis.py`.
- Added a Phase 8 failure taxonomy covering generated invalid code, timeout, hardcoded heuristic, overfit to small instances, poor generalization, routing feasibility violation, excessive complexity, travel-time versus driver-likeness harm, and driver-likeness versus runtime harm.
- Aggregated failure-rate and invalid-code-rate rows from Phase 3 bin-packing evolution and Phase 6 Amazon routing discovery generation curves.
- Extracted top rejected programs from evolution/discovery archives and added deterministic diagnostic probes for timeout and excessive complexity.
- Reported top surviving programs, worked patterns, failed patterns, taxonomy evidence, and known limitations.
- Added `tests/test_failure_analysis.py`.
- Added Phase 8 implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-05-01: `python3 -m pytest tests/test_failure_analysis.py -q` failed as expected before implementation because `reports.failure_analysis` did not exist.
- 2026-05-01: `python3 -m pytest tests/test_failure_analysis.py -q` passed, 5 tests.
- 2026-05-01: `python3 -m pytest tests/test_failure_analysis.py -v` passed, 5 tests.
- 2026-05-01: `python3 -m pytest -q` passed, 73 tests.
- 2026-05-01: `python3 -m ruff check .` passed.
- 2026-05-01: `python3 -m ruff format --check .` passed.
- 2026-05-01: `PYTHONPATH=src python3 - <<'PY' ... PY` Phase 8 smoke check printed deterministic report values: 9 failure categories, 7 generation rows, 8 rejected programs, 8 surviving programs, 7 generated-invalid-code observations, 1 timeout observation, 2 poor-generalization observations, 4 travel-time/driver-likeness trade-off observations, and failed patterns `('unsafe_data_access', 'routing_large_slice_generalization_gap', 'travel_time_driver_likeness_tradeoff', 'driver_like_timeout')`.

Known limitations:

- Timeout, excessive-complexity, and driver-likeness-too-slow rows use deterministic diagnostic probes so the taxonomy remains visible without adding unsafe live LLM execution.
- Routing feasibility violations are structurally prevented by the current next-stop evaluator because generated programs rank remaining stops rather than emitting full routes.
- The report is a dictionary artifact; polished final-report tables and plots remain deferred.

### Final Report Packaging

Commit: `feat: add final report packaging`

What changed:

- Created `src/reports/final_report.py`.
- Added structured final report composition across Phase 2 bin packing, Phase 4 simple routing, Phase 6 Amazon discovery, Phase 7 robustness, and Phase 8 failure analysis.
- Added killer-experiment benchmark summaries for online bin packing, simple routing, and Amazon-style routing.
- Added conservative claim boundaries that explicitly avoid universal-dominance claims.
- Added Markdown rendering for the final report.
- Added `tests/test_final_report.py`.
- Added final report implementation plan under `docs/superpowers/plans/`.
- Updated `README.md`, `ROADMAP.md`, and `VALIDATION.md`.

Validation:

- 2026-05-01: `python3 -m pytest tests/test_final_report.py -q` failed as expected before implementation because `reports.final_report` did not exist.
- 2026-05-01: `python3 -m pytest tests/test_final_report.py -q` passed, 5 tests.
- 2026-05-01: `python3 -m pytest tests/test_final_report.py -v` passed, 5 tests.
- 2026-05-01: `python3 -m pytest -q` passed, 78 tests.
- 2026-05-01: `python3 -m ruff check .` passed.
- 2026-05-01: `python3 -m ruff format --check .` passed.
- 2026-05-01: `PYTHONPATH=src python3 - <<'PY' ... PY` final report smoke check printed deterministic values: 3 killer-experiment benchmarks, 15 robustness slices, 9 failure-analysis categories, top programs `seed-000-tight_fit`, `route-seed-003-slack_aware`, and `phase6-seed-000-travel_fast`, first recommended next step `optional_live_llm_integration`, and Markdown checks for `do not universally dominate` and `selected trade-offs` returned `True`.

Known limitations:

- The final report is structured data plus Markdown; rendered plots and publication-ready tables remain deferred.
- Live LLM mutation remains deferred until explicit provider approval and environment-variable configuration are supplied.
- Amazon route evidence still uses deterministic local Amazon-shaped fixtures.

### Report Tables and Plots / Optional Live LLM Integration

Commit: `feat: add report tables plots and live llm`

What changed:

- Created `src/reports/tables.py` for deterministic benchmark comparison, robustness, worst-gap, failure-taxonomy, and next-step tables.
- Created `src/reports/plots.py` for plot-ready generation-curve, robustness-gap, and failure-rate series plus ASCII plot previews.
- Created `src/llm/model_client.py` with a stdlib-only Gemini `generateContent` mutation provider behind `GEMINI_API_KEY`.
- Added `tests/test_report_tables_plots_and_live_llm.py`.
- Added report table/plot and Gemini-client validation commands to `VALIDATION.md`.
- Updated `README.md`, `ROADMAP.md`, and `TASK_MEMORY.md`.

Validation:

- 2026-05-01: `python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -q` failed as expected before implementation because `llm.model_client` did not exist.
- 2026-05-01: `python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -q` passed, 9 tests.
- 2026-05-01: `python3 -m pytest tests/test_report_tables_plots_and_live_llm.py -v` passed, 9 tests.
- 2026-05-01: `python3 -m pytest -q` passed, 87 tests.
- 2026-05-01: `python3 -m ruff check .` passed.
- 2026-05-01: `python3 -m ruff format --check .` passed after formatting the new test file.
- 2026-05-01: `PYTHONPATH=src python3 - <<'PY' ... PY` report artifact smoke check printed deterministic table/plot signatures: 5 tables, 16 benchmark rows, 9 failure rows, 4 plots, 15 robustness-gap points, Markdown checks `True`, and missing-env Gemini check `GEMINI_API_KEY`.
- 2026-05-01: `PYTHONPATH=src python3 - <<'PY' ... PY` final-report smoke check printed the stable final-report signature.
- 2026-05-01: optional Gemini live smoke with a user-supplied `GEMINI_API_KEY` and `GEMINI_MODEL=gemini-2.5-flash` returned `def score_candidate(state, candidate):`, static validation `True`, and failure reason `None`.
- 2026-05-01: required docs are present and non-empty.
- 2026-05-01: `git diff --check -- .` passed.

Known limitations:

- Gemini integration is optional and only configured through environment variables; API keys are not stored in repository files.
- The default provider uses the Gemini REST API over the Python standard library, not a vendor SDK.
- Report plots are deterministic text/series artifacts rather than rendered PNG/SVG figures.

### Hardening Milestone

Commit: `feat: harden evidence package`

What changed:

- Created `src/sandbox/subprocess_exec.py` for child-process scoring-function execution with wall-clock timeout handling and optional platform memory limits.
- Updated `src/sandbox/restricted_exec.py` so the public single-call sandbox API routes through subprocess isolation by default while preserving an in-process helper for trusted internal use.
- Created `src/program_search/rerun_manifest.py` to record candidate id, code hash, generation, parent ids, score, failure reason, runtime, Python version, package version, and deterministic random seeds.
- Created `src/reports/artifacts.py` to export `reports/final_report.md`, CSV tables, JSON plot series, top program `.py` files, and `artifacts/rerun_manifest.json`.
- Created the `heuristic_discovery` CLI with `run`, `report`, `inspect`, and `rerun-manifest` commands.
- Added `tests/test_hardening_milestone.py`.
- Generated the checked-in evidence package under `reports/` and `artifacts/`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, and `TASK_MEMORY.md`.

Validation:

- 2026-05-01: `python3 -m pytest tests/test_hardening_milestone.py -q` failed as expected before implementation because `program_search.rerun_manifest` did not exist.
- 2026-05-01: `python3 -m pytest tests/test_hardening_milestone.py -q` passed, 11 tests.
- 2026-05-01: `python3 -m pytest tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_hardening_milestone.py -q` passed, 25 tests.
- 2026-05-01: `python3 -m pytest -q` passed, 98 tests.
- 2026-05-01: `python3 -m ruff check .` passed.
- 2026-05-01: `python3 -m ruff format --check .` passed.
- 2026-05-01: subprocess hardening smoke printed `True`, `6.0`, `True`, `None`.
- 2026-05-01: CLI smoke checks for `run`, `report`, `inspect`, and `rerun-manifest` passed against `/tmp/o2-cli-*` output folders.
- 2026-05-01: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5` generated the evidence package in the repository.
- 2026-05-01: final-report smoke printed the stable signature with first recommended next step `external_benchmark_adapter`.
- 2026-05-01: report artifact smoke printed deterministic table/plot signatures and missing-env Gemini check `GEMINI_API_KEY`.
- 2026-05-01: required docs are present and non-empty.
- 2026-05-01: `git diff --check -- .` passed.
- 2026-05-01: secret scan for the user-supplied Gemini key in repository content returned no matches.

Known limitations:

- Subprocess memory limits depend on host `resource` support. If unsupported, requested memory limits fail closed with `memory_limit_unsupported`.
- The committed report plots are JSON series, not mandatory PNGs; PNG rendering remains optional when matplotlib is available.
- The hardening milestone does not add external BPPLIB, OR-Library, TSPLIB, or CVRPLIB data adapters.

### Phase 9: External Benchmark Evidence

Commit: `feat: add external bin packing evidence`

What changed:

- Created `src/benchmarks/bin_packing/external.py` with OR-Library-style and
  BPPLIB-style parsers, user-file loading, deterministic external splitting,
  tiny benchmark-style local fixtures, and `build_phase9_report`.
- Extended `BinPackingInstance` with `EXTERNAL`, `instance_id`, `source`, and
  `known_optimum` metadata while preserving existing synthetic defaults.
- Updated bin packing `PackingResult` waste metrics to use instance capacity so
  external instances with capacities other than `1.0` report waste correctly.
- Added Phase 9 report integration to `reports/final_report.py`,
  `reports/tables.py`, and artifact export through
  `reports/tables/external_generalization.csv`.
- Added `bin_packing_external` support to the deterministic CLI, with optional
  `--external-path` and `--external-format` arguments for user-provided files.
- Added `tests/test_external_bin_packing_phase9.py`.
- Regenerated `reports/final_report.md`,
  `reports/tables/external_generalization.csv`, and
  `reports/tables/recommended_next_steps.csv`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, and
  `TASK_MEMORY.md`.

Validation:

- 2026-05-02: `python3 -m pytest tests/test_external_bin_packing_phase9.py -q`
  failed as expected before implementation because
  `benchmarks.bin_packing.external` did not exist.
- 2026-05-02: `python3 -m pytest tests/test_external_bin_packing_phase9.py -q`
  passed, 8 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_external_bin_packing_phase9.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_hardening_milestone.py -q`
  passed, 33 tests.
- 2026-05-02: `python3 -m pytest -q` passed, 106 tests.
- 2026-05-02: `python3 -m ruff check .` passed.
- 2026-05-02: `python3 -m ruff format --check .` passed, 62 files already
  formatted.
- 2026-05-02: Phase 9 smoke printed `bin_packing_external`, test count `2`,
  top program `seed-000-tight_fit`, external held-out score `5.0`, baseline
  presence `True`, and the conservative claim boundary.
- 2026-05-02: CLI smoke for `run --benchmark bin_packing_external` wrote
  `/tmp/o2-phase9-external/run_summary.json` and printed top program
  `seed-000-tight_fit`.
- 2026-05-02: CLI smoke for local `bin_packing`, `inspect`, `report`, and
  `rerun-manifest` passed against `/tmp/o2-*` output folders.
- 2026-05-02: final-report smoke printed the stable signature with
  `search_mechanism_ablation` as the first recommended next step and confirmed
  the external section, conservative dominance boundary, and selected trade-off
  language.
- 2026-05-02: report artifact smoke printed six tables including
  `external_generalization`, 16 benchmark rows, 5 external-generalization rows,
  9 failure rows, 4 plot series, 15 robustness-gap points, Markdown checks
  `True`, and missing-env Gemini check `GEMINI_API_KEY`.

Known limitations:

- Phase 9 includes parser-backed, small benchmark-style fixtures for local,
  deterministic validation. Large public BPPLIB or OR-Library files are not
  committed.
- The external evidence is bin packing only; TSPLIB / CVRPLIB routing evidence
  remains deferred.
- The report compares transfer and baselines conservatively and does not claim
  SOTA or universal dominance.
- Live LLM mutation remains optional and was not expanded in this phase.

### Phase 11: Search Mechanism Ablation

Commit: `feat: add search mechanism ablation`

What changed:

- Created `src/program_search/ablation.py` to compare seed-only, random
  mutation, deterministic template mutation, crossover-only, mutation plus
  crossover, deterministic LLM-proxy mutation, deterministic LLM-proxy repair,
  and mutation plus repair under one fixed local evaluation budget.
- Kept all LLM-labelled methods as deterministic local proxies; no live LLM
  provider, API key, paid service, TSPLIB, CVRPLIB, semantic novelty, Pareto
  frontier, or cloud execution was added.
- Added `search_ablation` support to the deterministic CLI.
- Integrated ablation output into final report, report tables, plot series, and
  artifact export.
- Added generated evidence files:
  `reports/tables/ablation_summary.csv`,
  `reports/tables/invalid_code_rate_by_method.csv`,
  `reports/tables/best_score_by_budget.csv`, and
  `reports/plots/generation_curve_by_method.json`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, and this
  task memory to mark Phase 11 complete and move the next recommended phase to
  Phase 15 Pareto frontier reporting.

Validation:

- 2026-05-02: `python3 -m pytest tests/test_search_ablation_phase11.py -q`
  failed as expected before implementation because `program_search.ablation`
  did not exist.
- 2026-05-02: `python3 -m pytest tests/test_search_ablation_phase11.py -q`
  passed, 7 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_search_ablation_phase11.py tests/test_report_tables_plots_and_live_llm.py tests/test_final_report.py tests/test_hardening_milestone.py -q`
  passed, 32 tests.
- 2026-05-02: `python3 -m pytest -q` passed, 113 tests.
- 2026-05-02: `python3 -m ruff check .` passed.
- 2026-05-02: `python3 -m ruff format --check .` passed, 64 files already
  formatted.
- 2026-05-02: Phase 11 smoke printed benchmark `bin_packing`, 8 methods,
  candidate budget `16`, best method `llm_mutation` for the smaller smoke
  slice, and the conservative no-live-LLM claim boundary.
- 2026-05-02: CLI smoke for `run --benchmark search_ablation` wrote
  `/tmp/o2-phase11-ablation/run_summary.json` and printed best method
  `crossover_only` for the default item-count CLI slice.
- 2026-05-02: CLI smoke for local `bin_packing`, `bin_packing_external`,
  `report`, `inspect`, and `rerun-manifest` passed against `/tmp/o2-*` output
  folders.
- 2026-05-02: final-report smoke printed first recommended next step
  `pareto_frontier_report` and confirmed external evidence, search ablation,
  conservative dominance boundary, and selected trade-off language.
- 2026-05-02: report artifact smoke printed nine tables including the three
  ablation tables, five plot series including `generation_curve_by_method`, 32
  ablation curve points, Markdown checks `True`, and missing-env Gemini check
  `GEMINI_API_KEY`.
- 2026-05-02: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`
  regenerated the checked-in evidence package.
- 2026-05-02: required docs are present and non-empty.
- 2026-05-02: repository content secret scan for API-key-like Gemini material
  returned no matches.
- 2026-05-02: large-file scan found no files larger than 1 MB in this project
  tree.
- 2026-05-02: `git diff --check -- .` passed.

Known limitations:

- The ablation is a deterministic local operator comparison; it does not prove
  live Gemini or other live LLM behavior.
- Several methods tie on validation score in the default local suite, so the
  report should be read as fixed-budget mechanism evidence rather than a claim
  of a universally best operator.
- The ablation is bin packing only. External routing evidence, semantic
  novelty, failure taxonomy v2, Pareto frontier analysis, and cloud-scale
  search remain deferred.

### Phase 15: Pareto Frontier Report

Commit: `feat: add pareto frontier reporting`

What changed:

- Created `src/reports/pareto.py` to build deterministic Pareto frontier rows
  across bin packing, simple routing, and Amazon-style routing candidates.
- Compared objective quality, runtime, program complexity, failure rate,
  generalization gap, and operational realism / driver-likeness where
  available.
- Computed nondominated frontier rows within each benchmark, not across
  unrelated benchmarks.
- Added `pareto_frontier` to report tables and `frontier_plot_series` to report
  plots.
- Added artifact export for `reports/tables/pareto_frontier.csv`,
  `reports/plots/frontier_plot_series.json`, and
  `artifacts/frontier_programs/*.py`.
- Updated the final report to include a Pareto Frontier section and moved the
  next recommended phase to Phase 18 research-style technical reporting.
- Added `tests/test_pareto_frontier_phase15.py`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, and this
  task memory.

Validation:

- 2026-05-02: `python3 -m pytest tests/test_pareto_frontier_phase15.py -q`
  failed as expected before implementation because `reports.pareto` did not
  exist.
- 2026-05-02: `python3 -m pytest tests/test_pareto_frontier_phase15.py -q`
  passed, 4 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_pareto_frontier_phase15.py tests/test_report_tables_plots_and_live_llm.py tests/test_final_report.py tests/test_hardening_milestone.py -q`
  passed, 29 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_search_ablation_phase11.py tests/test_pareto_frontier_phase15.py tests/test_final_report.py -q`
  passed, 16 tests after updating the previous next-step expectation.
- 2026-05-02: `python3 -m pytest -q` passed, 117 tests.
- 2026-05-02: `python3 -m ruff check .` passed.
- 2026-05-02: `python3 -m ruff format --check .` passed, 74 files already
  formatted.
- 2026-05-02: Phase 15 smoke printed phase `15`, 17 candidate rows, 8 frontier
  rows, benchmark tuple `('amazon_routing', 'bin_packing', 'simple_routing')`,
  first frontier row `amazon_routing`, program
  `phase6-seed-000-travel_fast`, and the conservative frontier claim boundary.
- 2026-05-02: final-report smoke printed first recommended next step
  `research_style_report`, frontier count `8`, and confirmed external
  evidence, search ablation, Pareto frontier, conservative dominance boundary,
  and selected trade-off language.
- 2026-05-02: report artifact smoke printed ten tables including
  `pareto_frontier`, six plot series including `frontier_plot_series`, 17
  frontier plot points, Markdown checks `True`, and missing-env Gemini check
  `GEMINI_API_KEY`.
- 2026-05-02: CLI smoke for local `bin_packing`, `bin_packing_external`,
  `search_ablation`, `report`, `inspect`, and `rerun-manifest` passed against
  `/tmp/o2-*` output folders.
- 2026-05-02: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`
  regenerated the checked-in evidence package.
- 2026-05-02: required docs are present and non-empty.
- 2026-05-02: repository content secret scan for API-key-like Gemini material
  returned no matches.
- 2026-05-02: large-file scan found no files larger than 1 MB in this project
  tree.
- 2026-05-02: `git diff --check -- .` passed.

Known limitations:

- The frontier uses deterministic local benchmark candidates and a deterministic
  runtime proxy; it should not be read as hardware-independent runtime
  benchmarking.
- Pareto dominance is computed within each benchmark because bin packing,
  routing, and Amazon-style routing scores are not directly comparable.
- Amazon operational realism uses available driver-likeness metrics from local
  Amazon-shaped fixtures, not proprietary or public Amazon route data.
- External routing evidence, semantic novelty, failure taxonomy v2,
  reproduction profiles, and cloud-scale search remain deferred.

### Phase 18: Research-Style Technical Report

Commit: `docs: add research-style technical report`

What changed:

- Created `src/reports/technical_report.py` with a deterministic Phase 18
  report builder and Markdown renderer.
- Used the working title `Sandboxed LLM Program Search for OR Heuristic
  Discovery`.
- Covered the paper-style structure requested in the roadmap: problem, why
  heuristic discovery matters, system design, sandbox and safety boundary,
  benchmarks, search loop, external benchmark evidence, ablation,
  generalization, failure analysis, limitations, and conclusion.
- Mapped each major section to existing evidence artifacts such as
  `external_generalization.csv`, `ablation_summary.csv`,
  `generation_curve_by_method.json`, `robustness_summary.csv`,
  `worst_generalization_gaps.csv`, `pareto_frontier.csv`,
  `failure_taxonomy.csv`, and `artifacts/rerun_manifest.json`.
- Added `reports/technical_report.md` to `export_report_artifacts()` and the
  deterministic `python -m heuristic_discovery report` CLI package.
- Updated final report next steps and `reports/tables/recommended_next_steps.csv`
  so Phase 19 resume / portfolio packaging is next.
- Added `tests/test_technical_report_phase18.py`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, and this
  task memory.

Validation:

- 2026-05-02: `python3 -m pytest tests/test_technical_report_phase18.py -q`
  failed as expected before implementation because `reports.technical_report`
  did not exist.
- 2026-05-02:
  `python3 -m pytest tests/test_technical_report_phase18.py tests/test_hardening_milestone.py -q`
  passed, 15 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_technical_report_phase18.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py -q`
  passed, 18 tests.
- 2026-05-02: `python3 -m pytest -q` passed, 121 tests.
- 2026-05-02: `python3 -m ruff check .` passed.
- 2026-05-02: `python3 -m ruff format --check .` passed, 76 files already
  formatted.
- 2026-05-02: `git diff --check -- .` passed.
- 2026-05-02: Phase 18 smoke printed phase `18`, 12 sections, 3 benchmarks, 8
  Pareto frontier rows, next phase `Phase 19: Resume / Portfolio Packaging`,
  and confirmed sandbox, external evidence, and universal-dominance boundary
  text in Markdown.
- 2026-05-02: final-report smoke printed first recommended next step
  `resume_portfolio_packaging`, frontier count `8`, and confirmed external
  evidence, search ablation, Pareto frontier, conservative dominance boundary,
  and selected trade-off language.
- 2026-05-02: report artifact smoke wrote `/tmp/o2-phase18-report` with
  `reports/final_report.md`, `reports/technical_report.md`,
  `reports/tables/recommended_next_steps.csv`, and
  `reports/tables/pareto_frontier.csv`.
- 2026-05-02: report table/plot smoke printed ten tables, six plot series, 17
  frontier plot points, next-step Markdown check `True`, and missing-env Gemini
  check `GEMINI_API_KEY`.
- 2026-05-02: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`
  regenerated the checked-in evidence package and wrote
  `reports/technical_report.md`.
- 2026-05-02: required docs are present and non-empty.
- 2026-05-02: repository content secret scan for API-key-like Gemini material
  returned no matches.
- 2026-05-02: large-file scan found no files larger than 1 MB in this project
  tree.
- 2026-05-05: `python3 -m pytest tests/test_external_routing_phase10.py -q`
  failed as expected before implementation because
  `route_capacity_violation` was not available.
- 2026-05-05: `python3 -m pytest tests/test_external_routing_phase10.py -q`
  passed, 12 tests.
- 2026-05-05:
  `python3 -m pytest tests/test_external_routing_phase10.py tests/test_report_tables_plots_and_live_llm.py tests/test_final_report.py tests/test_technical_report_phase18.py tests/test_portfolio_packaging_phase19.py tests/test_failure_taxonomy_v2_phase14.py tests/test_reproducibility_package_phase16.py -q`
  passed, 47 tests.
- 2026-05-05: `python3 -m pytest -q` passed, 165 tests.
- 2026-05-05: `python3 -m ruff check .` passed.
- 2026-05-05: `python3 -m ruff format --check .` passed, 90 files already
  formatted after applying formatter.
- 2026-05-05: direct Phase 10B smoke printed external formats
  `['cvrplib', 'tsplib']`, capacitated instance count `3`, capacity violation
  `0.0`, vehicle count `2.0`, and the conservative claim boundary.
- 2026-05-05: CLI smoke for default `routing_external` and explicit
  `routing_external --external-format cvrplib` wrote run summaries with
  capacity violation `0.0`.
- 2026-05-05: `reproduce --profile external_small` wrote a deterministic
  evidence package to `/tmp/o2-phase10b-reproduce-external` with score and code
  hash rerun checks passing.

Known limitations:

- The technical report is a deterministic Markdown evidence package, not a
  peer-reviewed paper.
- Live LLM mutation remains optional and gated by environment variables; the
  report does not claim live LLM superiority.
- External routing evidence, semantic novelty, failure taxonomy v2,
  reproducibility profiles, and cloud-scale search remain deferred.
- Phase 19 README-first portfolio packaging was completed after this phase.

### Phase 19: Resume / Portfolio Packaging

Commit: `docs: package portfolio-ready project evidence`

What changed:

- Created `src/reports/portfolio.py` with a deterministic Phase 19 portfolio
  package builder and Markdown renderer.
- Added resume bullets, a one-command demo command, architecture diagram text,
  benchmark evidence rows, safety boundary, limitations, and conservative claim
  boundaries for interview and GitHub presentation.
- Added `reports/portfolio_brief.md` to `export_report_artifacts()` and the
  deterministic `python -m heuristic_discovery report` CLI package.
- Rewrote the README first screen to include what the system does, why it
  matters, one-command demo, core architecture, benchmark results, safety
  boundary, and limitations before the longer status log.
- Updated final report next steps and `reports/tables/recommended_next_steps.csv`
  so optional Phase 10 external routing evidence is next after the completed
  portfolio track.
- Added `tests/test_portfolio_packaging_phase19.py`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, and this
  task memory.

Validation:

- 2026-05-02: `python3 -m pytest tests/test_portfolio_packaging_phase19.py -q`
  failed as expected before implementation because `reports.portfolio` did not
  exist.
- 2026-05-02:
  `python3 -m pytest tests/test_portfolio_packaging_phase19.py tests/test_hardening_milestone.py -q`
  passed, 16 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_portfolio_packaging_phase19.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_pareto_frontier_phase15.py tests/test_search_ablation_phase11.py -q`
  passed, 30 tests.
- 2026-05-02: `python3 -m pytest -q` passed, 126 tests.
- 2026-05-02: `python3 -m ruff check .` passed.
- 2026-05-02: `python3 -m ruff format --check .` passed, 78 files already
  formatted.
- 2026-05-02: `git diff --check -- .` passed.
- 2026-05-02: Phase 19 smoke printed phase `19`, six benchmark evidence rows,
  next phase `Optional Phase 10: External Routing Evidence`, and confirmed the
  resume bullet, one-command demo, core architecture, and conservative README
  claim boundary.
- 2026-05-02: final-report smoke printed first recommended next step
  `external_routing_evidence`, frontier count `8`, and confirmed external
  evidence, search ablation, Pareto frontier, conservative dominance boundary,
  and selected trade-off language.
- 2026-05-02: CLI report artifact smoke wrote `/tmp/o2-phase19-report` with
  `reports/final_report.md`, `reports/technical_report.md`,
  `reports/portfolio_brief.md`, and `reports/tables/recommended_next_steps.csv`.
- 2026-05-02: report table/plot smoke printed ten tables, six plot series, 17
  frontier plot points, next-step Markdown check `True`, and missing-env Gemini
  check `GEMINI_API_KEY`.
- 2026-05-02: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`
  regenerated the checked-in evidence package and wrote
  `reports/portfolio_brief.md`.
- 2026-05-02: required docs are present and non-empty.
- 2026-05-02: repository content secret scan for API-key-like Gemini material
  returned no matches.
- 2026-05-02: large-file scan found no files larger than 1 MB in this project
  tree.

Known limitations:

- Phase 19 packages the existing evidence; it does not add new benchmark
  results.
- External routing evidence, live LLM experiment runs, semantic novelty,
  failure taxonomy v2, reproducibility profiles, and cloud-scale search remain
  deferred.
- The README claim remains deliberately conservative and does not claim
  universal dominance or SOTA solver performance.

### Phase 10: External Routing Evidence

Commit: `feat: add external routing benchmark evidence`

What changed:

- Created `src/benchmarks/routing/external.py` with TSPLIB-style EUC_2D parsing,
  file/directory loading, deterministic small local fixtures, external
  train / validation / test splitting, distance-matrix construction, external
  baseline comparison, and `build_phase10_report`.
- Extended `RoutingInstance` with `EXTERNAL`, `instance_id`, and `source`
  metadata while preserving existing synthetic defaults.
- Reused simple-routing nearest-neighbor, cheapest-insertion, and 2-opt
  baselines for external test comparison.
- Reran `score_next_stop` candidate programs selected on synthetic routing and
  external validation suites to report synthetic-to-external transfer and
  external generalization gaps.
- Added `routing_external` deterministic CLI support with optional
  `--external-path` and `--external-format tsplib` inputs.
- Integrated Phase 10 evidence into final report, report tables, technical
  report, portfolio package, and artifact export through
  `reports/tables/routing_external_generalization.csv`.
- Added `tests/test_external_routing_phase10.py`.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, this task
  memory, and the Phase 10 implementation plan.

Validation:

- 2026-05-02: `python3 -m pytest tests/test_external_routing_phase10.py -q`
  failed as expected before implementation because
  `benchmarks.routing.external` did not exist.
- 2026-05-02: `python3 -m pytest tests/test_external_routing_phase10.py -q`
  passed, 8 tests.
- 2026-05-02:
  `python3 -m pytest tests/test_external_routing_phase10.py tests/test_technical_report_phase18.py tests/test_portfolio_packaging_phase19.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_pareto_frontier_phase15.py tests/test_search_ablation_phase11.py -q`
  passed, 42 tests.
- 2026-05-02: `python3 -m pytest -q` passed, 134 tests.
- 2026-05-02: `python3 -m ruff check .` passed.
- 2026-05-02: `python3 -m ruff format --check .` passed, 80 files already
  formatted.
- 2026-05-02: `git diff --check -- .` passed.
- 2026-05-02: Phase 10 direct smoke printed phase `10`, benchmark
  `routing_external`, test count `2`, top program `route-seed-000-nearest`,
  external baseline presence `True`, and the conservative claim boundary.
- 2026-05-02: CLI smoke for `run --benchmark routing_external` wrote
  `/tmp/o2-routing-external/run_summary.json` and printed top program
  `route-seed-000-nearest`.
- 2026-05-02: CLI smoke for `bin_packing`, `bin_packing_external`,
  `routing_external`, `search_ablation`, `report`, `inspect`, and
  `rerun-manifest` passed against `/tmp/o2-cli-*` output folders.
- 2026-05-02: final-report smoke printed first recommended next step
  `live_llm_mutation_v1`, frontier count `8`, and confirmed external bin
  packing evidence, external routing evidence, search ablation, Pareto
  frontier, conservative dominance boundary, and selected trade-off language.
- 2026-05-02: report table/plot smoke printed eleven tables including
  `routing_external_generalization`, six plot series, 17 frontier plot points,
  next-step Markdown check `True`, and missing-env Gemini check
  `GEMINI_API_KEY`.
- 2026-05-02: `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`
  regenerated the checked-in evidence package and wrote
  `reports/tables/routing_external_generalization.csv`.
- 2026-05-02: required docs are present and non-empty.
- 2026-05-02: repository content secret scan for API-key-like Gemini material
  returned no matches.
- 2026-05-02: large-file scan found no files larger than 1 MB in this project
  tree.

Known limitations:

- Phase 10 now covers TSPLIB-style TSP, CVRPLIB-style capacitated routing, and
  local time-window section parsing slices.
- The default external routing fixtures are small parser-backed examples for
  deterministic local validation, not a committed large TSPLIB/CVRPLIB/CVRPTW
  corpus.
- Results compare compact `score_next_stop` programs against reused local
  baselines and do not claim LKH, CVRP solver, SOTA, real Amazon, or universal
  superiority.

### Phase 12: LLM Live Mutation v1

Commit: `feat: add controlled live llm mutation evidence`

What changed:

- Added `src/llm/live_experiment.py` with deterministic fallback providers,
  scripted/fake-provider support for tests, repair-provider handling, and
  `build_phase12_report`.
- Extended `src/llm/model_client.py` with metadata-producing generation records
  while preserving the existing `GeminiMutationProvider.generate(prompt)` API.
- Added prompt versioning to `PromptBuilder`.
- Added `live_llm` CLI support with deterministic defaults and optional
  `--use-live-llm` environment-gated Gemini execution.
- Added final-report, report-table, technical-report, and portfolio integration
  for live LLM as one constrained mutation operator.
- Added generated table artifacts:
  `reports/tables/llm_operator_comparison.csv` and
  `reports/tables/llm_candidate_audit.csv`.
- Added `tests/test_live_llm_phase12.py` and updated report integration tests.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, this task
  memory, and the Phase 12 implementation plan.

Validation:

- 2026-05-03: `python3 -m pytest tests/test_live_llm_phase12.py -q` failed as
  expected before implementation because `llm.live_experiment` did not exist.
- 2026-05-03: `python3 -m pytest tests/test_live_llm_phase12.py -q` passed, 5
  tests.
- 2026-05-03:
  `python3 -m pytest tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_pareto_frontier_phase15.py tests/test_search_ablation_phase11.py tests/test_portfolio_packaging_phase19.py tests/test_technical_report_phase18.py tests/test_live_llm_phase12.py -q`
  passed, 39 tests.
- 2026-05-03: `python3 -m pytest -q` passed, 139 tests.
- 2026-05-03: `python3 -m ruff check .` passed.
- 2026-05-03: `python3 -m ruff format --check .` passed, 82 files already
  formatted.
- 2026-05-03: `git diff --check -- .` passed.
- 2026-05-03: Phase 12 direct smoke printed phase `12`, benchmark
  `live_llm_mutation`, live provider configured `False`, three operator rows,
  six candidate audit rows, first method `deterministic_fallback`, prompt
  version `score-bin-mutation-v1`, and the conservative LLM-as-operator claim
  boundary.
- 2026-05-03: report tables / plots smoke printed thirteen tables including
  `llm_operator_comparison` and `llm_candidate_audit`, six plot series,
  frontier point count `17`, next-step Markdown check `True`, and missing-env
  Gemini check `GEMINI_API_KEY`.
- 2026-05-03: final-report smoke printed first recommended next step
  `semantic_novelty` and confirmed external evidence, LLM live mutation,
  ablation, Pareto frontier, conservative dominance boundary, and selected
  trade-off language.
- 2026-05-03: CLI smoke for `bin_packing`, `bin_packing_external`,
  `routing_external`, `search_ablation`, `live_llm`, `report`, `inspect`, and
  `rerun-manifest` passed against `/tmp/o2-cli-*` output folders; `live_llm`
  wrote eight audited candidates with `live_provider_configured` set to
  `False`.
- 2026-05-03: portfolio / technical-report smoke printed portfolio phase `19`
  with eight benchmark rows, technical report phase `18` with thirteen
  sections, and recommended next phase `Phase 13: Program Semantics and
  Novelty`.
- 2026-05-03:
  `PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5`
  regenerated the checked-in evidence package and wrote
  `reports/tables/llm_operator_comparison.csv` plus
  `reports/tables/llm_candidate_audit.csv`.
- 2026-05-03: required docs are present and non-empty.
- 2026-05-03: repository content secret scan for API-key-like Gemini material
  returned zero matches.
- 2026-05-03: large-file scan found no files larger than 1 MB in this project
  tree.

Known limitations:

- Default Phase 12 runs use deterministic fallback and repair providers. Live
  Gemini execution remains optional, environment-gated, and excluded from
  required tests.
- Candidate audit records store hashes and metadata, not raw LLM responses.
- Phase 12 compares LLM-as-operator plumbing and safety boundaries; it does not
  claim live LLM superiority or universal dominance.

### Phase 13: Program Semantics and Novelty

Commit: `feat: add semantic novelty evidence`

What changed:

- Added `src/program_search/semantic_novelty.py` with deterministic
  bin-packing behavior probes, behavior fingerprints, semantic novelty scoring,
  feature usage summaries, complexity decomposition, and duplicate behavior
  cluster detection.
- Added `semantic_novelty` CLI support with deterministic local defaults.
- Added final-report, report-table, plot-series, technical-report, and
  portfolio integration for program semantics and novelty evidence.
- Added generated artifacts:
  `reports/tables/novelty_table.csv`,
  `reports/tables/duplicate_behavior_clusters.csv`, and
  `reports/plots/behavior_fingerprint.json`.
- Added `tests/test_semantic_novelty_phase13.py` and updated report
  integration tests.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, this task
  memory, and the Phase 13 implementation plan.

Validation:

- 2026-05-03: `python3 -m pytest tests/test_semantic_novelty_phase13.py -q`
  failed as expected before implementation because
  `program_search.semantic_novelty` did not exist.
- 2026-05-03: `python3 -m pytest tests/test_semantic_novelty_phase13.py -q`
  passed, 4 tests.
- 2026-05-03:
  `python3 -m pytest tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py tests/test_pareto_frontier_phase15.py tests/test_portfolio_packaging_phase19.py tests/test_technical_report_phase18.py tests/test_search_ablation_phase11.py tests/test_live_llm_phase12.py tests/test_semantic_novelty_phase13.py -q`
  passed, 43 tests.
- 2026-05-03:
  `python3 -m pytest tests/test_semantic_novelty_phase13.py tests/test_report_tables_plots_and_live_llm.py -q`
  passed, 13 tests.
- 2026-05-03:
  `python3 -m pytest tests/test_final_report.py tests/test_pareto_frontier_phase15.py tests/test_portfolio_packaging_phase19.py tests/test_technical_report_phase18.py tests/test_search_ablation_phase11.py tests/test_live_llm_phase12.py -q`
  passed, 30 tests.
- 2026-05-03: `python3 -m pytest -q` passed, 143 tests.
- 2026-05-03: `python3 -m ruff check .` passed.
- 2026-05-03: `python3 -m ruff format --check .` passed, 84 files
  already formatted.
- 2026-05-03: `git diff --check -- .` passed.
- 2026-05-03: Phase 13 direct smoke returned phase 13,
  `bin_packing_semantic_novelty`, 12 candidates, 5 probes, 4 behavior
  clusters, 3 duplicate behavior clusters, top row
  `seed-010-prefer_used_bins`, and the conservative claim boundary.
- 2026-05-03: `semantic_novelty` CLI smoke wrote `/tmp/o2-cli-semantic`
  with 24 candidates, 7 behavior clusters, and 4 duplicate behavior clusters.
- 2026-05-03: report artifact smoke wrote Phase 13 artifacts to
  `/tmp/o2-phase13-report`, including 24 novelty rows, 4 duplicate behavior
  cluster rows, 24 behavior-fingerprint points, and a final-report Program
  Semantics And Novelty section.
- 2026-05-03: report table/plot smoke confirmed 15 tables, 7 plot series, 24
  novelty rows, 4 duplicate behavior clusters, 24 behavior-fingerprint points,
  and next step `failure_taxonomy_v2`; missing live key check returned
  `GEMINI_API_KEY` as expected.
- 2026-05-03: final-report smoke confirmed next step
  `failure_taxonomy_v2`, Pareto frontier evidence, LLM live mutation evidence,
  search ablation evidence, and Program Semantics And Novelty evidence.
- 2026-05-03: portfolio and technical-report smoke confirmed Phase 19 has 9
  benchmark rows, Phase 18 has 14 sections, and both recommend Phase 14 failure
  taxonomy v2.
- 2026-05-03: CLI smoke confirmed `bin_packing`, `bin_packing_external`,
  `routing_external`, `search_ablation`, `live_llm`, `semantic_novelty`,
  `report`, `inspect`, and `rerun-manifest` commands work with deterministic
  local defaults.
- 2026-05-03: docs non-empty check confirmed `AGENTS.md`, `ROADMAP.md`,
  `README.md`, `TASK_MEMORY.md`, `VALIDATION.md`, and `RUNBOOK.md` are present
  and non-empty.
- 2026-05-03: strict secret scan found zero committed API keys or long token
  patterns; large-file scan found no files larger than 1 MB.

Known limitations:

- Phase 13 semantic novelty is probe-based and bin-packing focused; it detects
  equivalent ranking behavior on fixed `score_bin` probes, not human-level
  semantic equivalence.
- Feature novelty is derived from static AST feature references and does not
  infer latent mathematical intent.
- Performance novelty is a deterministic local score-distance signal, not a
  claim of universal performance improvement.

### Phase 14: Failure Taxonomy v2

Commit: `feat: add failure taxonomy v2 evidence`

What changed:

- Added `src/reports/failure_taxonomy_v2.py` with deterministic failure cards
  for invalid syntax, unsafe code, timeout, over-complex code, overfit small
  instances, poor external transfer, baseline domination, runtime too slow,
  behavior duplicate, LLM hallucinated feature, and objective gaming.
- Each failure card includes an example program, trigger condition,
  validator/evaluator source, score impact, and repair strategy.
- Added repair success rows for deterministic syntax, unsafe-code, timeout,
  and LLM hallucinated-feature repair routes.
- Added generated artifacts:
  `reports/failure_cards.md`,
  `reports/tables/failure_taxonomy_v2.csv`, and
  `reports/tables/repair_success_rate.csv`.
- Updated final-report, table export, artifact export, technical-report, and
  portfolio integration so the next optional phase is Phase 16 reproducibility
  package v2.
- Updated `README.md`, `ROADMAP.md`, `RUNBOOK.md`, `VALIDATION.md`, this task
  memory, and the Phase 14 implementation plan.

Validation:

- 2026-05-04:
  `python3 -m pytest tests/test_failure_taxonomy_v2_phase14.py -q` failed as
  expected before implementation because `reports.failure_taxonomy_v2` did not
  exist.
- 2026-05-04:
  `python3 -m pytest tests/test_failure_taxonomy_v2_phase14.py -q` passed, 6
  tests.
- 2026-05-04:
  `python3 -m pytest tests/test_failure_taxonomy_v2_phase14.py tests/test_final_report.py tests/test_report_tables_plots_and_live_llm.py -q`
  passed, 20 tests.
- 2026-05-04:
  `python3 -m pytest tests/test_technical_report_phase18.py tests/test_portfolio_packaging_phase19.py tests/test_search_ablation_phase11.py tests/test_live_llm_phase12.py tests/test_semantic_novelty_phase13.py tests/test_pareto_frontier_phase15.py -q`
  passed, 29 tests.
- 2026-05-04: `python3 -m pytest -q` passed, 149 tests.
- 2026-05-04: `python3 -m ruff check .` passed.
- 2026-05-04: `python3 -m ruff format --check .` passed, 86 files already
  formatted.
- 2026-05-04: `git diff --check -- .` passed.
- 2026-05-04: Phase 14 direct smoke returned phase 14,
  `failure_taxonomy_v2`, 11 failure cards, 11 repair success rows,
  first category `invalid_syntax`, first repair category
  `llm_hallucinated_feature`, next phase
  `Phase 16: Reproducibility Package v2`, and the conservative claim boundary.
- 2026-05-04: report table/plot smoke confirmed 17 tables, 7 plot series, 11
  failure taxonomy v2 rows, 11 repair success rows, 24 behavior-fingerprint
  points, and missing live key check returned `GEMINI_API_KEY` as expected.
- 2026-05-04: final-report smoke confirmed 11 failure cards, next step
  `reproducibility_package_v2`, Failure Taxonomy v2 section, and repair
  success wording.
- 2026-05-04: portfolio and technical-report smoke confirmed Phase 19 has 10
  benchmark rows, Phase 18 has 15 sections, and both recommend Phase 16
  reproducibility package v2.
- 2026-05-04: CLI report smoke wrote `/tmp/o2-cli-phase14`, including
  `reports/failure_cards.md`, 11 `failure_taxonomy_v2.csv` rows, 11
  `repair_success_rate.csv` rows, final report, technical report, and
  portfolio brief.
- 2026-05-04: docs non-empty check confirmed `AGENTS.md`, `ROADMAP.md`,
  `README.md`, `TASK_MEMORY.md`, `VALIDATION.md`, and `RUNBOOK.md` are present
  and non-empty.
- 2026-05-04: strict secret scan found zero committed API keys or long token
  patterns; large-file scan found no files larger than 1 MB.

Known limitations:

- Phase 14 repair rows are deterministic local evidence records; they do not
  prove arbitrary LLM-generated failures can be repaired automatically.
- Failure cards explain representative failure modes from existing report
  evidence and diagnostic probes, not an exhaustive taxonomy for every OR
  benchmark family.
- Time-window routing, one-command reproduction profiles, and cloud execution
  remain deferred.

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
- [x] Create `src/benchmarks/routing/instances.py`.
- [x] Create `src/benchmarks/routing/baselines.py`.
- [x] Create `src/benchmarks/routing/local_search.py`.
- [x] Create `src/benchmarks/routing/evaluator.py`.
- [x] Add `tests/test_routing_validity.py`.
- [x] Create the Amazon routing evaluator scaffold without requiring proprietary data.
- [x] Connect Amazon routing to the heuristic search/evolution loop and report trade-offs.
- [x] Add cross-benchmark generalization and robustness reporting.
- [x] Add cross-benchmark failure-analysis reporting.
- [x] Package the final report around the killer experiment.
- [x] Add report tables and plots.
- [x] Add optional Gemini live-LLM mutation behind environment-variable
  configuration.
- [x] Add subprocess sandbox isolation, rerun manifests, artifact export, and
  deterministic CLI hardening.
- [x] Add an external benchmark adapter for public BPPLIB / OR-Library-style
  bin packing data.
- [x] Add fixed-budget search mechanism ablation across deterministic local
  mutation, crossover, and LLM-proxy operators.
- [x] Add controlled live LLM mutation evidence with deterministic fallback,
  repair, prompt versioning, hash-only audit logs, and sandboxed scoring.
- [x] Add Pareto frontier reporting across quality, runtime, complexity,
  failure rate, and generalization gap.
- [x] Package a research-style technical report.
- [x] Package README-first resume / portfolio evidence.
- [x] Add TSPLIB-style external routing evidence.

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
- Should CVRPLIB-style capacitated routing or time-window routing be added after the TSPLIB-style TSP slice?
- Which Amazon routing data split and quality labels are available locally?

## Resume Bullet Draft

> Built a FunSearch-inspired OR heuristic discovery system that evolves compact bin-packing and routing algorithms through LLM code mutation, sandboxed execution, automated evaluation, and held-out generalization tests, then benchmarked discovered heuristics against nearest-neighbor, insertion, 2-opt, and Amazon last-mile routing baselines.
