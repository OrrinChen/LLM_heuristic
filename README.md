# LLM-Driven Program Search for OR Heuristics

O2 is a FunSearch-inspired program-search system for operations research
heuristics. The project constrains generated Python to compact scoring
functions, validates the code statically, runs it in a restricted sandbox, and
records evaluation results with archive and lineage metadata.

Current status:

- Phase 0 complete: project direction, roadmap, task memory, and workflow docs.
- Phase 1 complete: program-search skeleton, static checks, restricted
  execution, mutation interface, evaluator records, archive, and lineage.
- Current phase: Phase 2, online bin packing benchmark and baselines.

## Setup

Use Python 3.9 or newer.

```bash
python3 -m pip install -e ".[dev]"
```

## Tests

```bash
python3 -m pytest
python3 -m ruff check .
git diff --check
```

Sandbox-specific validation:

```bash
python3 -m pytest tests/test_program_sandbox.py -v
```

## Smoke Check

```bash
PYTHONPATH=src python3 - <<'PY'
from sandbox.restricted_exec import execute_scoring_function

code = """
def score_candidate(state, candidate):
    remaining = state["capacity"] - candidate["size"]
    if remaining < 0:
        return 1000000
    return remaining
"""

result = execute_scoring_function(code, {"capacity": 10}, {"size": 4})
print(result.ok, result.value)
PY
```

Expected output:

```text
True 6.0
```

## Safety Boundary

Generated programs must define only the configured scoring function. Static
checks reject extra top-level statements, helper functions, imports, file
access, network/process names, dangerous builtins, dunder attribute access, and
disallowed globals before code reaches restricted execution.

The current sandbox is a local Python AST and restricted-builtins boundary with
Unix signal timeouts. Subprocess isolation and memory limits are deferred until
later hardening work.
