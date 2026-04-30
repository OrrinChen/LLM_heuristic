from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random
from statistics import median
from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    SeedCandidateProgram,
    build_seed_candidate_programs,
)
from benchmarks.bin_packing.instances import (
    BinPackingInstance,
    default_train_validation_test_suites,
)
from program_search.archive import ProgramArchive
from program_search.candidate_program import CandidateProgram
from program_search.evaluator import EvaluationResult
from program_search.novelty_filter import ExactCodeNoveltyFilter
from program_search.scoring import (
    ScoredCandidate,
    ScoreWeights,
    compute_final_score,
    compute_program_complexity,
)
from program_search.tournament_selection import TournamentSelector


@dataclass(frozen=True)
class EvolutionConfig:
    generations: int = 3
    population_size: int = 16
    offspring_per_generation: int = 12
    elite_size: int = 4
    tournament_size: int = 3
    random_seed: int = 0
    score_weights: ScoreWeights = ScoreWeights()


@dataclass(frozen=True)
class GenerationReport:
    generation: int
    population_size: int
    best_score: float
    median_score: float
    failure_rate: float
    invalid_code_rate: float
    best_program_id: str

    def as_curve_point(self) -> Mapping[str, object]:
        return {
            "generation": self.generation,
            "best_score": round(self.best_score, 6),
            "median_score": round(self.median_score, 6),
            "failure_rate": round(self.failure_rate, 6),
            "invalid_code_rate": round(self.invalid_code_rate, 6),
            "best_program_id": self.best_program_id,
        }


@dataclass(frozen=True)
class TopCandidate:
    program_id: str
    code: str
    generation: int
    final_score: float
    train_score: Optional[float]
    validation_score: Optional[float]
    test_score: Optional[float]
    complexity: int
    generalization_gap: float
    explanation: str

    def as_dict(self) -> Mapping[str, object]:
        return {
            "program_id": self.program_id,
            "generation": self.generation,
            "final_score": self.final_score,
            "train_score": self.train_score,
            "validation_score": self.validation_score,
            "test_score": self.test_score,
            "complexity": self.complexity,
            "generalization_gap": self.generalization_gap,
            "code": self.code,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class EvolutionRunResult:
    generation_reports: List[GenerationReport]
    archive: ProgramArchive
    top_candidates: List[TopCandidate]
    failure_taxonomy: Mapping[str, int]
    evaluator: BinPackingEvaluator

    def rerun_candidate(self, program_id: str, instances: Sequence[BinPackingInstance]):
        candidate = self.archive.get(program_id)
        return self.evaluator.evaluate_program(
            candidate.code, instances, program_id=program_id
        )


class EvolutionLoop:
    def __init__(self, *, config: Optional[EvolutionConfig] = None) -> None:
        self.config = config or EvolutionConfig()
        self.evaluator = BinPackingEvaluator()
        self.rng = Random(self.config.random_seed)

    def run(
        self,
        *,
        train_instances: Sequence[BinPackingInstance],
        validation_instances: Sequence[BinPackingInstance],
        test_instances: Sequence[BinPackingInstance],
    ) -> EvolutionRunResult:
        archive = ProgramArchive()
        novelty = ExactCodeNoveltyFilter()
        failure_taxonomy: Counter[str] = Counter()
        selector = TournamentSelector(
            tournament_size=self.config.tournament_size,
            random_seed=self.config.random_seed,
        )
        seed_programs = build_seed_candidate_programs(self.config.population_size)
        population = [
            self._evaluate_seed(
                seed,
                train_instances,
                validation_instances,
                test_instances,
                archive,
                novelty,
                failure_taxonomy,
            )
            for seed in seed_programs
        ]
        reports = [self._build_generation_report(0, population)]

        for generation in range(1, self.config.generations + 1):
            parents = [
                candidate
                for candidate in population
                if candidate.failure_reason is None
            ]
            if not parents:
                parents = population
            offspring = []
            attempts = 0
            while (
                len(offspring) < self.config.offspring_per_generation
                and attempts < self.config.offspring_per_generation * 4
            ):
                attempts += 1
                if attempts % 5 == 0 and len(parents) >= 2:
                    parent_a, parent_b = selector.select_many(parents, count=2)
                    candidate = self._make_crossover(
                        parent_a, parent_b, generation, attempts
                    )
                else:
                    parent = selector.select_one(parents)
                    candidate = self._make_mutation(parent, generation, attempts)
                if not novelty.is_novel(candidate.code):
                    continue
                scored = self._evaluate_candidate(
                    candidate,
                    train_instances,
                    validation_instances,
                    test_instances,
                    archive,
                    novelty,
                    failure_taxonomy,
                )
                offspring.append(scored)

            combined = population + offspring
            population = sorted(
                combined,
                key=lambda candidate: (candidate.final_score, candidate.program_id),
            )[: self.config.population_size]
            reports.append(self._build_generation_report(generation, population))

        top_candidates = [
            TopCandidate(
                program_id=candidate.program_id,
                code=candidate.code,
                generation=candidate.generation,
                final_score=candidate.final_score,
                train_score=candidate.train_score,
                validation_score=candidate.validation_score,
                test_score=candidate.test_score,
                complexity=candidate.complexity,
                generalization_gap=candidate.generalization_gap,
                explanation=candidate.prompt,
            )
            for candidate in sorted(
                population,
                key=lambda candidate: (candidate.final_score, candidate.program_id),
            )[: self.config.elite_size]
            if candidate.failure_reason is None
        ]
        return EvolutionRunResult(
            generation_reports=reports,
            archive=archive,
            top_candidates=top_candidates,
            failure_taxonomy=dict(sorted(failure_taxonomy.items())),
            evaluator=self.evaluator,
        )

    def _evaluate_seed(
        self,
        seed: SeedCandidateProgram,
        train_instances: Sequence[BinPackingInstance],
        validation_instances: Sequence[BinPackingInstance],
        test_instances: Sequence[BinPackingInstance],
        archive: ProgramArchive,
        novelty: ExactCodeNoveltyFilter,
        failure_taxonomy: Counter[str],
    ) -> ScoredCandidate:
        candidate = CandidateProgram(
            program_id=seed.program_id,
            parent_id=None,
            generation=0,
            code=seed.code,
            prompt=seed.explanation,
        )
        return self._evaluate_candidate(
            candidate,
            train_instances,
            validation_instances,
            test_instances,
            archive,
            novelty,
            failure_taxonomy,
        )

    def _evaluate_candidate(
        self,
        candidate: CandidateProgram,
        train_instances: Sequence[BinPackingInstance],
        validation_instances: Sequence[BinPackingInstance],
        test_instances: Sequence[BinPackingInstance],
        archive: ProgramArchive,
        novelty: ExactCodeNoveltyFilter,
        failure_taxonomy: Counter[str],
    ) -> ScoredCandidate:
        novelty.add(candidate.code)
        train = self.evaluator.evaluate_program(
            candidate.code, train_instances, program_id=candidate.program_id
        )
        validation = self.evaluator.evaluate_program(
            candidate.code, validation_instances, program_id=candidate.program_id
        )
        test = self.evaluator.evaluate_program(
            candidate.code, test_instances, program_id=candidate.program_id
        )
        failure_reason = validation.failure_reason or train.failure_reason
        if failure_reason:
            failure_taxonomy[_failure_code(failure_reason)] += 1
        complexity = compute_program_complexity(candidate.code)
        generalization_gap = abs((train.score or 0.0) - (validation.score or 0.0))
        final_score = compute_final_score(
            benchmark_score=validation.score,
            runtime=train.runtime + validation.runtime + test.runtime,
            complexity=complexity,
            generalization_gap=generalization_gap,
            weights=self.config.score_weights,
            failed=validation.score is None,
        )
        recorded_candidate = CandidateProgram.create(
            code=candidate.code,
            prompt=candidate.prompt,
            parent_id=candidate.parent_id,
            generation=candidate.generation,
            benchmark_scores={
                "train": train.score or 0.0,
                "validation": validation.score or 0.0,
                "test": test.score or 0.0,
                "final": final_score,
            },
            runtime=train.runtime + validation.runtime + test.runtime,
            failure_reason=failure_reason,
        )
        # Preserve the generated ID for stable archive references in this run.
        recorded_candidate = CandidateProgram(
            program_id=candidate.program_id,
            parent_id=recorded_candidate.parent_id,
            generation=recorded_candidate.generation,
            code=recorded_candidate.code,
            prompt=recorded_candidate.prompt,
            benchmark_scores=recorded_candidate.benchmark_scores,
            runtime=recorded_candidate.runtime,
            failure_reason=recorded_candidate.failure_reason,
            created_at=recorded_candidate.created_at,
        )
        if validation.score is None:
            evaluation = EvaluationResult.failure(
                candidate_id=candidate.program_id,
                benchmark_name="bin_packing_evolution",
                failure_reason=failure_reason or "candidate_failed",
                runtime=recorded_candidate.runtime or 0.0,
                metrics=validation.metrics,
            )
        else:
            evaluation = EvaluationResult.success(
                candidate_id=candidate.program_id,
                benchmark_name="bin_packing_evolution",
                score=final_score,
                runtime=recorded_candidate.runtime or 0.0,
                metrics=validation.metrics,
            )
        archive.record(recorded_candidate, evaluation)
        return ScoredCandidate(
            program_id=candidate.program_id,
            code=candidate.code,
            generation=candidate.generation,
            final_score=final_score,
            benchmark_score=(
                validation.score or self.config.score_weights.failure_penalty
            ),
            runtime=recorded_candidate.runtime or 0.0,
            complexity=complexity,
            train_score=train.score,
            validation_score=validation.score,
            test_score=test.score,
            failure_reason=failure_reason,
            parent_id=candidate.parent_id,
            prompt=candidate.prompt,
            generalization_gap=generalization_gap,
        )

    def _make_mutation(
        self, parent: ScoredCandidate, generation: int, attempt: int
    ) -> CandidateProgram:
        parameter = self.rng.random()
        template_name = self.rng.choice(["tight", "balance", "used", "invalid"])
        if template_name == "invalid" and attempt % 7 == 0:
            code = """
def score_bin(item_size, bin_remaining_capacity, bin_features):
    return open("training_labels.json").read()
"""
        elif template_name == "balance":
            code = f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - {parameter:.4f})
"""
        elif template_name == "used":
            code = f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected - {parameter / 10:.4f} * bin_features["items_in_bin"]
"""
        else:
            code = f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected + {parameter / 20:.4f} * bin_features["current_load"]
"""
        return CandidateProgram(
            program_id=f"g{generation:02d}-m{attempt:03d}-{parent.program_id}",
            parent_id=parent.program_id,
            generation=generation,
            code=code.strip() + "\n",
            prompt=f"mutation from {parent.program_id} using {template_name}",
        )

    def _make_crossover(
        self,
        parent_a: ScoredCandidate,
        parent_b: ScoredCandidate,
        generation: int,
        attempt: int,
    ) -> CandidateProgram:
        mix = 0.25 + (self.rng.random() * 0.5)
        bonus = self.rng.random() / 10
        code = f"""
def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    tight_fit = projected
    balance = abs(projected - {mix:.4f})
    used_bin_bonus = {bonus:.4f} * bin_features["items_in_bin"]
    return ({mix:.4f} * tight_fit) + ((1 - {mix:.4f}) * balance) - used_bin_bonus
"""
        return CandidateProgram(
            program_id=(
                f"g{generation:02d}-x{attempt:03d}-"
                f"{parent_a.program_id}-{parent_b.program_id}"
            ),
            parent_id=parent_a.program_id,
            generation=generation,
            code=code.strip() + "\n",
            prompt=(
                f"crossover from {parent_a.program_id} and {parent_b.program_id} "
                f"at attempt {attempt}"
            ),
        )

    def _build_generation_report(
        self, generation: int, population: Sequence[ScoredCandidate]
    ) -> GenerationReport:
        scores = [candidate.final_score for candidate in population]
        failures = [candidate for candidate in population if candidate.failure_reason]
        invalid = [
            candidate
            for candidate in failures
            if "dangerous_call" in (candidate.failure_reason or "")
            or "import_not_allowed" in (candidate.failure_reason or "")
        ]
        best = min(
            population,
            key=lambda candidate: (candidate.final_score, candidate.program_id),
        )
        return GenerationReport(
            generation=generation,
            population_size=len(population),
            best_score=min(scores),
            median_score=median(scores),
            failure_rate=len(failures) / len(population),
            invalid_code_rate=len(invalid) / len(population),
            best_program_id=best.program_id,
        )


def build_phase3_report(
    *,
    config: Optional[EvolutionConfig] = None,
    item_count: int = 25,
) -> Dict[str, object]:
    train, validation, test = default_train_validation_test_suites(
        item_count=item_count
    )
    result = EvolutionLoop(config=config).run(
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )
    top = result.top_candidates[0]
    rerun = result.rerun_candidate(top.program_id, test)
    return {
        "generation_count": len(result.generation_reports),
        "generation_curve": [
            report.as_curve_point() for report in result.generation_reports
        ],
        "failure_taxonomy": dict(result.failure_taxonomy),
        "top_candidates": [candidate.as_dict() for candidate in result.top_candidates],
        "rerun_top": {
            "program_id": top.program_id,
            "ok": rerun.ok,
            "score": rerun.score,
        },
    }


def _failure_code(failure_reason: str) -> str:
    return failure_reason.split(":", 1)[0]
