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
PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5
```

Expected generated files:

```text
reports/final_report.md
reports/technical_report.md
reports/tables/*.csv
reports/tables/external_generalization.csv
reports/tables/ablation_summary.csv
reports/tables/invalid_code_rate_by_method.csv
reports/tables/best_score_by_budget.csv
reports/tables/pareto_frontier.csv
reports/plots/plot_series.json
reports/plots/generation_curve_by_method.json
reports/plots/frontier_plot_series.json
artifacts/top_programs/*.py
artifacts/frontier_programs/*.py
artifacts/rerun_manifest.json
```

Run deterministic CLI checks:

```bash
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing --generations 1
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark bin_packing_external --output-dir /tmp/o2-external
PYTHONPATH=src python3 -m heuristic_discovery run --benchmark search_ablation --candidate-budget 16 --generations 3 --output-dir /tmp/o2-ablation
PYTHONPATH=src python3 -m heuristic_discovery inspect --top-k 5
PYTHONPATH=src python3 -m heuristic_discovery rerun-manifest --output-dir . --top-k 5
```

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
