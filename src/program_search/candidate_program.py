from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True)
class CandidateProgram:
    """Immutable record for one generated or seed scoring program."""

    program_id: str
    parent_id: Optional[str]
    generation: int
    code: str
    prompt: str
    benchmark_scores: Mapping[str, float] = field(default_factory=dict)
    runtime: Optional[float] = None
    failure_reason: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)

    @classmethod
    def create(
        cls,
        *,
        code: str,
        prompt: str,
        parent_id: Optional[str] = None,
        generation: int = 0,
        benchmark_scores: Optional[Mapping[str, float]] = None,
        runtime: Optional[float] = None,
        failure_reason: Optional[str] = None,
    ) -> "CandidateProgram":
        if generation < 0:
            raise ValueError("generation must be non-negative")
        return cls(
            program_id=f"prog-{uuid4().hex}",
            parent_id=parent_id,
            generation=generation,
            code=code,
            prompt=prompt,
            benchmark_scores=dict(benchmark_scores or {}),
            runtime=runtime,
            failure_reason=failure_reason,
        )
