from __future__ import annotations

from random import Random
from typing import List, Sequence

from program_search.scoring import ScoredCandidate


class TournamentSelector:
    def __init__(self, *, tournament_size: int = 3, random_seed: int = 0) -> None:
        if tournament_size < 1:
            raise ValueError("tournament_size must be positive")
        self.tournament_size = tournament_size
        self.rng = Random(random_seed)

    def select_one(self, candidates: Sequence[ScoredCandidate]) -> ScoredCandidate:
        if not candidates:
            raise ValueError("candidate pool cannot be empty")
        sample_size = min(self.tournament_size, len(candidates))
        sampled = self.rng.sample(list(candidates), sample_size)
        return min(
            sampled, key=lambda candidate: (candidate.final_score, candidate.program_id)
        )

    def select_many(
        self, candidates: Sequence[ScoredCandidate], *, count: int
    ) -> List[ScoredCandidate]:
        if count < 0:
            raise ValueError("count must be non-negative")
        return [self.select_one(candidates) for _ in range(count)]
