# AGENTS.md

You are working on this repository as an autonomous coding agent.

## Project Goal

This project is **O2: LLM-Driven Program Search for OR Heuristics**.

Read these files before making changes:

1. `AGENTS.md`
2. `ROADMAP.md`
3. `TASK_MEMORY.md`
4. `VALIDATION.md`
5. `RUNBOOK.md`
6. `README.md` if it exists

Your job is to advance the next incomplete roadmap phase, not to invent unrelated features.

## Project Thesis

The core thesis is:

```text
heuristic design can be automated as constrained program search
```

The project should build a FunSearch-inspired system where an LLM proposes compact heuristic scoring functions, a sandbox executes them safely, OR evaluators score them, and an evolutionary loop archives and mutates stronger candidates.

## Hard Constraints

Do not:

- Change the project direction without explicit instruction.
- Build only a routing heuristic and call it the whole project.
- Let the LLM write a full solver.
- Allow generated programs to access files, network, hidden labels, credentials, or unrestricted imports.
- Evaluate only on training instances.
- Start Amazon routing before the bin packing and sandbox foundation works.
- Claim universal dominance over classical OR baselines.
- Add paid external services without explicit approval and environment-variable configuration.
- Add heavy dependencies unless they are justified in `TASK_MEMORY.md`.
- Rewrite large modules unnecessarily.
- Hide failed experiments or failed tests.
- Generate misleading reports.
- Commit secrets, credentials, tokens, private data, or raw proprietary datasets.
- Perform destructive git or filesystem actions without explicit approval.

## Workflow

Before starting:

1. Run `git status --short`.
2. Read `ROADMAP.md`.
3. Read `TASK_MEMORY.md`.
4. Read `VALIDATION.md`.
5. Identify the next incomplete phase and the smallest useful task inside it.
6. Inspect relevant files before editing.

During work:

1. Make small, testable changes.
2. Keep generated-program interfaces narrow.
3. Add or update tests for sandbox, evaluator, and evolution behavior.
4. Update `README.md` when user-facing behavior changes.
5. Update `TASK_MEMORY.md` with what changed, what was verified, and what remains.
6. Record failed generated programs and failed experiments instead of hiding them.

Validation:

1. Run the commands listed in `VALIDATION.md`.
2. Always run relevant unit tests for touched code.
3. Run smoke checks for touched CLI, benchmark, or report paths.
4. Run `git diff --check`.
5. Do not claim completion until validation output has been checked.

Commit:

- Commit each completed phase or coherent milestone.
- Use clear commit messages:
  - `feat: ...`
  - `fix: ...`
  - `docs: ...`
  - `test: ...`
  - `chore: ...`
- Do not commit unrelated workspace changes.

## Phase Selection

When asked to continue autonomously:

1. Use the `Current State` section in `ROADMAP.md`.
2. Use the `Latest Status` and `Next Steps` sections in `TASK_MEMORY.md`.
3. Select the earliest incomplete phase whose prerequisites are met.
4. Work until that phase's acceptance criteria are satisfied or a stopping rule is triggered.

## Stopping Rules

Only stop and ask for help if:

- Tests cannot pass after reasonable debugging.
- Product direction is ambiguous.
- Implementation risks data loss.
- Credentials, paid APIs, or unavailable local data are required.
- A task would violate the hard constraints.
- Sandbox safety is uncertain.
- Benchmark licensing or data access constraints are unclear.

When stopping, report:

- What was attempted.
- What passed.
- What failed.
- The exact blocker.
- The recommended next step.

