from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, List

from program_search.candidate_program import CandidateProgram
from program_search.evaluator import EvaluationResult
from program_search.lineage import LineageRecord


class ProgramArchive:
    """In-memory archive for candidate programs, evaluations, and lineage."""

    def __init__(self) -> None:
        self._programs: Dict[str, CandidateProgram] = {}
        self._evaluations: DefaultDict[str, List[EvaluationResult]] = defaultdict(list)

    def record(
        self, candidate: CandidateProgram, evaluation: EvaluationResult
    ) -> CandidateProgram:
        if evaluation.candidate_id != candidate.program_id:
            raise ValueError("evaluation candidate_id does not match candidate")
        self._programs[candidate.program_id] = candidate
        self._evaluations[candidate.program_id].append(evaluation)
        return candidate

    def get(self, program_id: str) -> CandidateProgram:
        return self._programs[program_id]

    def evaluations_for(self, program_id: str) -> List[EvaluationResult]:
        return list(self._evaluations.get(program_id, []))

    def survivors(self) -> List[CandidateProgram]:
        return [
            candidate
            for candidate in self._programs.values()
            if candidate.failure_reason is None
            and self._evaluations.get(candidate.program_id)
            and all(result.ok for result in self._evaluations[candidate.program_id])
        ]

    def failures(self) -> List[CandidateProgram]:
        return [
            candidate
            for candidate in self._programs.values()
            if candidate.failure_reason is not None
            or any(not result.ok for result in self._evaluations[candidate.program_id])
        ]

    def lineage_for(self, program_id: str) -> List[LineageRecord]:
        records: List[LineageRecord] = []
        current = self._programs[program_id]
        while True:
            records.append(
                LineageRecord(
                    program_id=current.program_id,
                    parent_id=current.parent_id,
                    generation=current.generation,
                    failure_reason=current.failure_reason,
                )
            )
            if current.parent_id is None or current.parent_id not in self._programs:
                break
            current = self._programs[current.parent_id]
        return list(reversed(records))
