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

