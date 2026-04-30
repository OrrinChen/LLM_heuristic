from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LineageRecord:
    """One node in a candidate's parent chain."""

    program_id: str
    parent_id: Optional[str]
    generation: int
    failure_reason: Optional[str]
