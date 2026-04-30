from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Protocol

from program_search.candidate_program import CandidateProgram


@dataclass(frozen=True)
class EvaluationResult:
    """Structured result for evaluating a candidate on one benchmark."""

    candidate_id: str
    benchmark_name: str
    ok: bool
    score: Optional[float]
    runtime: float
    failure_reason: Optional[str] = None
    metrics: Mapping[str, float] = field(default_factory=dict)

    @classmethod
    def success(
        cls,
        *,
        candidate_id: str,
        benchmark_name: str,
        score: float,
        runtime: float,
        metrics: Optional[Mapping[str, float]] = None,
    ) -> "EvaluationResult":
        return cls(
            candidate_id=candidate_id,
            benchmark_name=benchmark_name,
            ok=True,
            score=float(score),
            runtime=runtime,
            metrics=dict(metrics or {}),
        )

    @classmethod
    def failure(
        cls,
        *,
        candidate_id: str,
        benchmark_name: str,
        failure_reason: str,
        runtime: float,
        metrics: Optional[Mapping[str, float]] = None,
    ) -> "EvaluationResult":
        return cls(
            candidate_id=candidate_id,
            benchmark_name=benchmark_name,
            ok=False,
            score=None,
            runtime=runtime,
            failure_reason=failure_reason,
            metrics=dict(metrics or {}),
        )


class BenchmarkEvaluator(Protocol):
    """Protocol implemented by future OR benchmark evaluators."""

    benchmark_name: str

    def evaluate(self, candidate: CandidateProgram) -> EvaluationResult:
        """Evaluate a candidate and return a structured result."""
        raise NotImplementedError
