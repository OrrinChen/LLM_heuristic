from __future__ import annotations

import re
from typing import Set


class ExactCodeNoveltyFilter:
    """Reject exact duplicate candidate programs after whitespace normalization."""

    def __init__(self) -> None:
        self._seen: Set[str] = set()

    def is_novel(self, code: str) -> bool:
        return self._normalize(code) not in self._seen

    def add(self, code: str) -> None:
        self._seen.add(self._normalize(code))

    @staticmethod
    def _normalize(code: str) -> str:
        return re.sub(r"\s+", " ", code.strip())
