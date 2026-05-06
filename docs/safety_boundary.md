# Safety Boundary

O2 is not letting an LLM write arbitrary code. It treats the LLM or deterministic
proxy as one mutation operator that can propose a narrow scoring function, then
checks and runs that function inside a constrained evaluator.

## What Generated Code Can Do

- Fill a narrow scoring-function interface such as `score_bin` or
  `score_next_stop`.
- Read only the explicit state and candidate fields passed by the evaluator.
- Return a numeric score used by a benchmark-specific route or packing
  constructor.

## What Generated Code Cannot Do

- No file access.
- No network access.
- No unrestricted imports.
- No process spawning.
- No credential access.
- No hidden labels, private data, or benchmark answer keys.
- No full solver generation.

## Enforcement Layers

- Interface restriction: candidate programs must define only the expected
  scoring function.
- static validation: AST checks reject imports, dangerous names, dangerous
  calls, dunder access, disallowed globals, file access, and network/process
  hooks before execution.
- subprocess sandbox: hardened scoring calls run outside the main process.
- wall-clock timeout: infinite loops and slow candidates fail closed.
- memory limit: supported platforms can apply a subprocess memory limit.
- structured failure: invalid, unsafe, timed-out, or runtime-failing programs are
  recorded with explicit failure reasons instead of being hidden.

## Why This Matters

The LLM path does not bypass the evaluator. A candidate must pass static
validation, execute in the subprocess sandbox, and score on held-out benchmark
slices before it appears in evidence artifacts. Default reproduction uses
deterministic local providers and does not require an API key.
