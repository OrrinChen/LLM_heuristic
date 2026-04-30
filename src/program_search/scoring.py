from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScoredCandidate:
    program_id: str
    code: str
    generation: int
    final_score: float
    benchmark_score: float
    runtime: float
    complexity: int
    train_score: Optional[float] = None
    validation_score: Optional[float] = None
    test_score: Optional[float] = None
    failure_reason: Optional[str] = None
    parent_id: Optional[str] = None
    prompt: str = ""
    generalization_gap: float = 0.0


@dataclass(frozen=True)
class ScoreWeights:
    runtime_penalty: float = 0.0
    complexity_penalty: float = 0.002
    instability_penalty: float = 0.5
    failure_penalty: float = 1000.0


def compute_program_complexity(code: str) -> int:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return len(code.splitlines()) + 100
    return sum(1 for _ in ast.walk(tree))


def compute_final_score(
    *,
    benchmark_score: Optional[float],
    runtime: float,
    complexity: int,
    generalization_gap: float,
    weights: ScoreWeights,
    failed: bool = False,
) -> float:
    if benchmark_score is None or failed:
        base_score = weights.failure_penalty
    else:
        base_score = benchmark_score
    return (
        base_score
        + runtime * weights.runtime_penalty
        + complexity * weights.complexity_penalty
        + generalization_gap * weights.instability_penalty
    )
