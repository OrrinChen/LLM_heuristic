# RUNBOOK.md

Operational notes for O2.

## Start a Work Session

Run from the project root:

```bash
pwd
git status --short
sed -n '1,220p' AGENTS.md
sed -n '1,220p' ROADMAP.md
sed -n '1,220p' TASK_MEMORY.md
sed -n '1,220p' VALIDATION.md
```

Then identify the next incomplete phase in `ROADMAP.md`.

## Validate Current Docs-Only State

```bash
git diff --check
for f in AGENTS.md ROADMAP.md TASK_MEMORY.md VALIDATION.md RUNBOOK.md; do test -s "$f" || exit 1; done
```

## First Implementation Command Sequence

Once implementation begins, the first useful sequence is:

```bash
mkdir -p configs src/llm src/program_search src/sandbox src/benchmarks/bin_packing src/benchmarks/routing src/benchmarks/amazon_routing src/reports tests notebooks
```

Then create:

```text
pyproject.toml
configs/bin_packing.yaml
configs/evolution.yaml
configs/sandbox.yaml
src/program_search/candidate_program.py
src/sandbox/static_checks.py
src/sandbox/restricted_exec.py
tests/test_program_sandbox.py
```

Use `apply_patch` for file edits.

## Generated Program Safety Checklist

Before executing generated code, verify:

- The candidate only defines the allowed function.
- Imports are absent or whitelisted.
- No file access is present.
- No network access is present.
- No subprocess calls are present.
- No eval or exec is present inside candidate code.
- No hidden test labels or instance IDs are accessible.
- Runtime timeout is configured.
- Failure reasons are recorded.
- For single-call hardening checks, use `execute_scoring_function_subprocess`
  so generated scoring code runs in a child process with a wall-clock timeout.
- If a memory limit is requested on a platform without compatible support, the
  subprocess sandbox must fail closed with a structured reason.

## Evidence Package Commands

Generate the local evidence package:

```bash
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir . --top-k 5
```

Expected generated files:

```text
reports/final_report.md
reports/failure_cards.md
reports/technical_report.md
reports/portfolio_brief.md
reports/tables/*.csv
reports/tables/external_generalization.csv
reports/tables/routing_external_generalization.csv
reports/tables/ablation_summary.csv
reports/tables/invalid_code_rate_by_method.csv
reports/tables/best_score_by_budget.csv
reports/tables/llm_operator_comparison.csv
reports/tables/llm_candidate_audit.csv
reports/tables/novelty_table.csv
reports/tables/duplicate_behavior_clusters.csv
reports/tables/failure_taxonomy_v2.csv
reports/tables/repair_success_rate.csv
reports/tables/pareto_frontier.csv
reports/tables/parallel_runner_summary.csv
reports/tables/checkpoint_resume.csv
reports/plots/plot_series.json
reports/plots/generation_curve_by_method.json
reports/plots/behavior_fingerprint.json
reports/plots/frontier_plot_series.json
artifacts/top_programs/*.py
artifacts/frontier_programs/*.py
artifacts/rerun_manifest.json
artifacts/phase17_checkpoint.json
artifacts/reproduction_manifest.json
artifacts/reproduction_summary.md
```

Run deterministic CLI checks:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing --generations 1
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing_external --output-dir /tmp/o2-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark routing_external --output-dir /tmp/o2-routing-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark search_ablation --candidate-budget 16 --generations 3 --output-dir /tmp/o2-ablation
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark live_llm --candidate-count 4 --output-dir /tmp/o2-live-llm
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark semantic_novelty --candidate-count 24 --output-dir /tmp/o2-semantic
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark parallel_runner --candidate-count 12 --max-workers 2 --output-dir /tmp/o2-parallel
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-report --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery inspect --top-k 5
PYTHONPATH=src python3 -m heuristic_discovery rerun-manifest --output-dir . --top-k 5
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-reproduce-local --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-reproduce-external --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile llm_optional --output-dir /tmp/o2-reproduce-llm --top-k 3
```

The reproduction profiles are deterministic and local. They do not require
`GEMINI_API_KEY`, paid services, or large external benchmark files.

Make targets are available for the fresh-clone path:

```bash
make reproduce
make test
make report
make demo
```

## Release-Frozen Portfolio Package

O2 is release-frozen and portfolio-ready. This means the current repository is a
defensible evidence package, not an open-ended feature branch. Do not add a new
roadmap phase, benchmark feature, broader crossover operator, paid cloud
execution path, or expanded live LLM campaign during release polish.

Release validation command sequence:

```bash
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
git diff --check -- .
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-release-local --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile external_small --output-dir /tmp/o2-release-external --top-k 3
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir /tmp/o2-release-report --top-k 3
git grep -nE 'AIza[0-9A-Za-z_-]{20,}|(GEMINI_API_KEY|OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY)=[A-Za-z0-9_/\+=-]{12,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY' -- . ':!.git' || true
find . -type f -size +5M -not -path './.git/*' -print
```

Expected release artifacts:

```text
RELEASE_SUMMARY.md
README.md
reports/final_report.md
reports/technical_report.md
reports/portfolio_brief.md
reports/tables/*.csv
reports/plots/*.json
artifacts/reproduction_manifest.json
artifacts/reproduction_summary.md
```

Optional future work is limited to broader crossover, paid cloud execution, and
larger public benchmark corpora. Keep those out of the release-frozen package
unless a new task explicitly asks for them.

## External Bin Packing Evidence

Phase 9 supports tiny deterministic BPPLIB / OR-Library-style fixtures by
default and user-provided files through the CLI:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark bin_packing_external \
  --external-path path/to/instances.txt \
  --external-format auto \
  --output-dir /tmp/o2-external
```

Do not commit large public benchmark files. Keep large or licensed data outside
the repository and commit only parser tests, small fixtures, reports, and
manifests.

## External Routing Evidence

Phase 10 supports tiny deterministic TSPLIB-style EUC_2D and CVRPLIB-style
capacitated/time-window fixtures by default and user-provided files through the
CLI:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark routing_external \
  --external-path path/to/instances \
  --external-format auto \
  --output-dir /tmp/o2-routing-external
```

Do not claim LKH, CVRP/VRPTW solver, SOTA, or superiority on Amazon data from
this evidence. It is external routing-style transfer evidence for the existing
`score_next_stop` evaluator. Do not commit large TSPLIB/CVRPLIB corpora; commit
only small fixtures, parser tests, and generated summary artifacts.

## Search Mechanism Ablation

Phase 11 compares search operators under one deterministic local budget. It
does not call live LLM providers and does not claim that live LLM behavior has
been proven:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark search_ablation \
  --candidate-budget 16 \
  --generations 3 \
  --output-dir /tmp/o2-ablation
```

Expected artifacts after a report export:

```text
reports/tables/ablation_summary.csv
reports/tables/invalid_code_rate_by_method.csv
reports/tables/best_score_by_budget.csv
reports/plots/generation_curve_by_method.json
```

## Live LLM Mutation V1

Phase 12 makes live Gemini mutation a controlled experiment path. Default runs
use deterministic fallback and repair providers, so validation does not require
an API key:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark live_llm \
  --candidate-count 4 \
  --output-dir /tmp/o2-live-llm
```

Optional live Gemini smoke checks require an exported `GEMINI_API_KEY` and an
explicit CLI flag:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark live_llm \
  --use-live-llm \
  --candidate-count 1 \
  --output-dir /tmp/o2-live-gemini
```

Do not commit API keys, raw responses, raw generated proprietary data, or large
logs. Phase 12 artifacts should store prompt version, model, temperature,
parent ids, response/code hashes, static-check result, sandbox result, scores,
token counts, latency, and cost proxies.

Expected artifacts after a report export:

```text
reports/tables/llm_operator_comparison.csv
reports/tables/llm_candidate_audit.csv
```

## Program Semantics And Novelty

Phase 13 fingerprints bin-packing `score_bin` programs on fixed probe states
and separates exact code novelty from behavior, feature, performance, and
complexity novelty:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run \
  --benchmark semantic_novelty \
  --candidate-count 24 \
  --output-dir /tmp/o2-semantic
```

Expected artifacts after a report export:

```text
reports/tables/novelty_table.csv
reports/tables/duplicate_behavior_clusters.csv
reports/plots/behavior_fingerprint.json
```

This evidence is probe-based. It detects equivalent ranking behavior on fixed
bin-packing probes and does not claim human-level semantic understanding.

## Pareto Frontier Evidence

Phase 15 reports nondominated trade-offs per benchmark. It compares objective
quality, runtime, complexity, failure rate, generalization gap, and
driver-likeness where applicable:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.pareto import build_phase15_report

report = build_phase15_report()
print(report["phase"])
print(len(report["frontier_rows"]))
print(report["claim_boundary"])
PY
```

Expected artifacts after a report export:

```text
reports/tables/pareto_frontier.csv
reports/plots/frontier_plot_series.json
artifacts/frontier_programs/*.py
```

## Failure Taxonomy v2

Phase 14 explains deterministic failure modes as cards:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.failure_taxonomy_v2 import (
    build_phase14_report,
    render_failure_cards_markdown,
)

report = build_phase14_report()
markdown = render_failure_cards_markdown(report)
print(report["phase"])
print(len(report["failure_cards"]))
print(len(report["repair_success_rows"]))
print(report["recommended_next_phase"])
print("Repair Strategy" in markdown)
PY
```

Expected artifacts after a report export:

```text
reports/failure_cards.md
reports/tables/failure_taxonomy_v2.csv
reports/tables/repair_success_rate.csv
```

## Research-Style Technical Report

Phase 18 packages the evidence into a paper-style Markdown report:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.technical_report import (
    build_phase18_report,
    render_technical_report_markdown,
)

report = build_phase18_report()
markdown = render_technical_report_markdown(report)
print(report["phase"])
print(len(report["sections"]))
print(report["recommended_next_phase"])
print("Sandbox and Safety Boundary" in markdown)
print("The system does not claim universal dominance" in markdown)
PY
```

Expected artifact after a report export:

```text
reports/technical_report.md
```

## Portfolio Brief

Phase 19 packages the project for resumes, GitHub, demos, and interviews:

```bash
PYTHONPATH=src python3 - <<'PY'
from reports.portfolio import (
    build_phase19_package,
    render_portfolio_brief_markdown,
)

package = build_phase19_package()
markdown = render_portfolio_brief_markdown(package)
print(package["phase"])
print(len(package["benchmark_results"]))
print(package["recommended_next_phase"])
print("Resume Bullets" in markdown)
print("universal dominance" in markdown)
PY
```

Expected artifact after a report export:

```text
reports/portfolio_brief.md
```

## Benchmark Progression

Follow this order:

```text
1. Sandbox tests.
2. Bin packing instances.
3. Bin packing baselines.
4. Bin packing evaluator.
5. Candidate archive and lineage.
6. Evolution loop.
7. Held-out bin packing generalization.
8. Simple routing.
9. Amazon routing evaluator.
```

Do not start Amazon routing until the sandbox, bin packing evaluator, and evolution archive are working.

## Common Failure Handling

### Generated Code Is Invalid

Record:

- Program ID.
- Parent ID.
- Generation.
- Static-check failure reason.
- Prompt that produced it.

Do not silently discard invalid programs.

### Candidate Times Out

Record:

- Program ID.
- Benchmark instance.
- Timeout threshold.
- Partial runtime if available.

Assign the candidate a failure penalty and continue the run.

### Candidate Improves Training Score But Fails Held-Out Tests

Treat this as overfitting. Record:

- Training score.
- Validation score.
- Test score.
- Program complexity.
- Instance distributions where it fails.

### Routing Heuristic Improves Travel Time But Hurts Driver-Likeness

Do not collapse this into a single success metric. Report it as a frontier trade-off:

- Travel time.
- Driver-likeness.
- Time-window violations.
- Route fragmentation.
- Runtime.

## Updating Task Memory

After any meaningful work, update `TASK_MEMORY.md` with:

- Current branch.
- Current phase.
- What changed.
- Validation commands and results.
- Known limitations.
- Next recommended action.
