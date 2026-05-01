from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random
from statistics import median
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from benchmarks.amazon_routing.baselines import AMAZON_BASELINE_ROUTE_BUILDERS
from benchmarks.amazon_routing.evaluator import (
    AmazonProgramEvaluation,
    AmazonRoutingEvaluator,
    SeedAmazonProgram,
)
from benchmarks.amazon_routing.features import AMAZON_CANDIDATE_FEATURES
from benchmarks.amazon_routing.loader import AmazonRoute, load_route_record
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
class AmazonDiscoveryConfig:
    generations: int = 3
    population_size: int = 16
    offspring_per_generation: int = 12
    elite_size: int = 4
    tournament_size: int = 3
    random_seed: int = 0
    score_weights: ScoreWeights = ScoreWeights()


@dataclass(frozen=True)
class AmazonGenerationReport:
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
class AmazonTopCandidate:
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
    test_metrics: Mapping[str, float]

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
            "test_metrics": dict(self.test_metrics),
            "code": self.code,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class AmazonDiscoveryRunResult:
    generation_reports: List[AmazonGenerationReport]
    archive: ProgramArchive
    top_candidates: List[AmazonTopCandidate]
    failure_taxonomy: Mapping[str, int]
    evaluator: AmazonRoutingEvaluator

    def rerun_candidate(
        self,
        program_id: str,
        routes: Sequence[AmazonRoute],
        *,
        apply_local_search: bool = False,
    ) -> AmazonProgramEvaluation:
        candidate = self.archive.get(program_id)
        return self.evaluator.evaluate_program(
            candidate.code,
            routes,
            program_id=program_id,
            apply_local_search=apply_local_search,
        )


class AmazonDiscoveryLoop:
    def __init__(self, *, config: Optional[AmazonDiscoveryConfig] = None) -> None:
        self.config = config or AmazonDiscoveryConfig()
        self.evaluator = AmazonRoutingEvaluator()
        self.rng = Random(self.config.random_seed)

    def run(
        self,
        *,
        train_routes: Sequence[AmazonRoute],
        validation_routes: Sequence[AmazonRoute],
        test_routes: Sequence[AmazonRoute],
    ) -> AmazonDiscoveryRunResult:
        self._last_test_routes = test_routes
        archive = ProgramArchive()
        novelty = ExactCodeNoveltyFilter()
        failure_taxonomy: Counter[str] = Counter()
        selector = TournamentSelector(
            tournament_size=self.config.tournament_size,
            random_seed=self.config.random_seed,
        )
        seed_programs = build_phase6_seed_programs(self.config.population_size)
        population = [
            self._evaluate_seed(
                seed,
                train_routes,
                validation_routes,
                test_routes,
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
            ] or population
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
                        parent_a,
                        parent_b,
                        generation,
                        attempts,
                    )
                else:
                    parent = selector.select_one(parents)
                    candidate = self._make_mutation(parent, generation, attempts)
                if not novelty.is_novel(candidate.code):
                    continue
                offspring.append(
                    self._evaluate_candidate(
                        candidate,
                        train_routes,
                        validation_routes,
                        test_routes,
                        archive,
                        novelty,
                        failure_taxonomy,
                    )
                )
            combined = population + offspring
            population = sorted(
                combined,
                key=lambda candidate: (candidate.final_score, candidate.program_id),
            )[: self.config.population_size]
            reports.append(self._build_generation_report(generation, population))

        top_candidates = [
            self._top_candidate(candidate)
            for candidate in sorted(
                population,
                key=lambda candidate: (candidate.final_score, candidate.program_id),
            )[: self.config.elite_size]
            if candidate.failure_reason is None
        ]
        return AmazonDiscoveryRunResult(
            generation_reports=reports,
            archive=archive,
            top_candidates=top_candidates,
            failure_taxonomy=dict(sorted(failure_taxonomy.items())),
            evaluator=self.evaluator,
        )

    def _evaluate_seed(
        self,
        seed: SeedAmazonProgram,
        train_routes: Sequence[AmazonRoute],
        validation_routes: Sequence[AmazonRoute],
        test_routes: Sequence[AmazonRoute],
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
            train_routes,
            validation_routes,
            test_routes,
            archive,
            novelty,
            failure_taxonomy,
        )

    def _evaluate_candidate(
        self,
        candidate: CandidateProgram,
        train_routes: Sequence[AmazonRoute],
        validation_routes: Sequence[AmazonRoute],
        test_routes: Sequence[AmazonRoute],
        archive: ProgramArchive,
        novelty: ExactCodeNoveltyFilter,
        failure_taxonomy: Counter[str],
    ) -> ScoredCandidate:
        novelty.add(candidate.code)
        train = self.evaluator.evaluate_program(
            candidate.code,
            train_routes,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        validation = self.evaluator.evaluate_program(
            candidate.code,
            validation_routes,
            program_id=candidate.program_id,
            apply_local_search=True,
        )
        test = self.evaluator.evaluate_program(
            candidate.code,
            test_routes,
            program_id=candidate.program_id,
            apply_local_search=True,
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
                benchmark_name="amazon_routing_discovery",
                failure_reason=failure_reason or "candidate_failed",
                runtime=recorded_candidate.runtime or 0.0,
                metrics=validation.metrics,
            )
        else:
            evaluation = EvaluationResult.success(
                candidate_id=candidate.program_id,
                benchmark_name="amazon_routing_discovery",
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
        self,
        parent: ScoredCandidate,
        generation: int,
        attempt: int,
    ) -> CandidateProgram:
        parameter = self.rng.random()
        template_name = self.rng.choice(
            ["travel", "zone", "window", "dense", "invalid"]
        )
        if template_name == "invalid" and attempt % 7 == 0:
            code = """
def score_next_stop(state, candidate_stop):
    return open("training_labels.json").read()
"""
        elif template_name == "zone":
            code = f"""
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        + {parameter:.4f} * candidate_stop["zone_transition_cost"]
        - {parameter / 2:.4f} * candidate_stop["same_zone"]
    )
"""
        elif template_name == "window":
            code = f"""
def score_next_stop(state, candidate_stop):
    urgency = max(0, -candidate_stop["time_window_slack"])
    return candidate_stop["travel_time"] + {1 + parameter:.4f} * urgency
"""
        elif template_name == "dense":
            code = f"""
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        - {parameter:.4f} * candidate_stop["package_count"]
        - {parameter / 2:.4f} * candidate_stop["cluster_compactness"]
    )
"""
        else:
            code = f"""
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        + {parameter / 4:.4f} * candidate_stop["distance_to_depot"]
    )
"""
        return CandidateProgram(
            program_id=f"az-g{generation:02d}-m{attempt:03d}-{parent.program_id}",
            parent_id=parent.program_id,
            generation=generation,
            code=code.strip() + "\n",
            prompt=f"amazon mutation from {parent.program_id} using {template_name}",
        )

    def _make_crossover(
        self,
        parent_a: ScoredCandidate,
        parent_b: ScoredCandidate,
        generation: int,
        attempt: int,
    ) -> CandidateProgram:
        mix = 0.25 + self.rng.random() * 0.5
        zone_weight = self.rng.random()
        code = f"""
def score_next_stop(state, candidate_stop):
    travel = candidate_stop["travel_time"]
    zone = candidate_stop["zone_transition_cost"] - candidate_stop["same_zone"]
    urgency = max(0, -candidate_stop["time_window_slack"])
    density = candidate_stop["package_count"] + candidate_stop["cluster_compactness"]
    return (
        {mix:.4f} * travel
        + {zone_weight:.4f} * zone
        + {1 - mix:.4f} * urgency
        - {zone_weight / 2:.4f} * density
    )
"""
        return CandidateProgram(
            program_id=(
                f"az-g{generation:02d}-x{attempt:03d}-"
                f"{parent_a.program_id}-{parent_b.program_id}"
            ),
            parent_id=parent_a.program_id,
            generation=generation,
            code=code.strip() + "\n",
            prompt=(
                f"amazon crossover from {parent_a.program_id} and {parent_b.program_id}"
            ),
        )

    def _build_generation_report(
        self,
        generation: int,
        population: Sequence[ScoredCandidate],
    ) -> AmazonGenerationReport:
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
        return AmazonGenerationReport(
            generation=generation,
            population_size=len(population),
            best_score=min(scores),
            median_score=median(scores),
            failure_rate=len(failures) / len(population),
            invalid_code_rate=len(invalid) / len(population),
            best_program_id=best.program_id,
        )

    def _top_candidate(self, candidate: ScoredCandidate) -> AmazonTopCandidate:
        test_metrics = dict(
            self.evaluator.evaluate_program(
                candidate.code,
                self._last_test_routes,
                program_id=candidate.program_id,
                apply_local_search=True,
            ).metrics
        )
        return AmazonTopCandidate(
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
            test_metrics=test_metrics,
        )

    @property
    def _last_test_routes(self) -> Sequence[AmazonRoute]:
        return self.__dict__["last_test_routes"]

    @_last_test_routes.setter
    def _last_test_routes(self, routes: Sequence[AmazonRoute]) -> None:
        self.__dict__["last_test_routes"] = tuple(routes)


def build_phase6_seed_programs(count: int = 120) -> List[SeedAmazonProgram]:
    if count < 1:
        raise ValueError("count must be positive")
    templates = [
        (
            "travel_fast",
            """
def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"]
""",
            "Travel-time minimizing rule that can trade off driver-likeness.",
        ),
        (
            "same_zone",
            """
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        + {weight} * candidate_stop["zone_transition_cost"]
        - {bonus} * candidate_stop["same_zone"]
    )
""",
            "Favors same-zone continuity while still considering travel time.",
        ),
        (
            "window_slack",
            """
def score_next_stop(state, candidate_stop):
    urgency = max(0, -candidate_stop["time_window_slack"])
    return candidate_stop["travel_time"] + {penalty} * urgency
""",
            "Protects time windows when slack becomes negative.",
        ),
        (
            "dense_cluster",
            """
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        - {bonus} * candidate_stop["package_count"]
        - {weight} * candidate_stop["cluster_compactness"]
    )
""",
            "Prefers dense package stops in compact remaining clusters.",
        ),
        (
            "return_aware",
            """
def score_next_stop(state, candidate_stop):
    return (
        candidate_stop["travel_time"]
        + {weight} * candidate_stop["distance_to_depot"]
        + 0.1 * candidate_stop["remaining_zone_count"]
    )
""",
            "Balances immediate travel with depot return and remaining-zone spread.",
        ),
        (
            "unsafe_probe",
            """
def score_next_stop(state, candidate_stop):
    return open("hidden_labels.json").read()
""",
            "Invalid safety probe retained to measure sandbox failure taxonomy.",
        ),
    ]
    candidates = []
    for index in range(count):
        name, template, explanation = templates[index % len(templates)]
        parameter = round(0.5 + (index % 13) * 0.2, 4)
        code = template.format(
            weight=parameter,
            bonus=round(parameter / 2, 4),
            penalty=round(2.0 + parameter, 4),
        )
        candidates.append(
            SeedAmazonProgram(
                program_id=f"phase6-seed-{index:03d}-{name}",
                code=code.strip() + "\n",
                explanation=explanation,
            )
        )
    return candidates


def default_phase6_train_validation_test_routes() -> Tuple[
    Tuple[AmazonRoute, ...],
    Tuple[AmazonRoute, ...],
    Tuple[AmazonRoute, ...],
]:
    return (
        tuple(
            load_route_record(_phase6_route_payload(f"train-{index}"))
            for index in range(2)
        ),
        tuple(
            load_route_record(_phase6_route_payload(f"validation-{index}"))
            for index in range(2)
        ),
        tuple(
            load_route_record(_phase6_route_payload(f"test-{index}"))
            for index in range(2)
        ),
    )


def build_phase6_report(
    *,
    config: Optional[AmazonDiscoveryConfig] = None,
) -> Dict[str, object]:
    config = config or AmazonDiscoveryConfig()
    train, validation, test = default_phase6_train_validation_test_routes()
    loop = AmazonDiscoveryLoop(config=config)
    loop._last_test_routes = test
    result = loop.run(
        train_routes=train, validation_routes=validation, test_routes=test
    )
    top = result.top_candidates[0]
    rerun = result.rerun_candidate(top.program_id, test, apply_local_search=True)
    baseline_scores = _baseline_scores(validation)
    baseline_test_metrics = _baseline_metrics(test)
    tradeoffs = _tradeoff_programs(result.top_candidates, baseline_test_metrics)
    return {
        "generation_count": len(result.generation_reports),
        "generation_curve": [
            report.as_curve_point() for report in result.generation_reports
        ],
        "failure_taxonomy": dict(result.failure_taxonomy),
        "baseline_scores": baseline_scores,
        "baseline_test_metrics": baseline_test_metrics,
        "feature_contract": tuple(AMAZON_CANDIDATE_FEATURES),
        "variants": {
            "llm_heuristic": "score_next_stop only",
            "llm_heuristic_plus_2opt": "score_next_stop with accepted 2-opt",
            "feasibility_repair": "route validity checked and invalid routes rejected",
            "local_search": "2-opt accepted only when weighted score improves",
        },
        "frontier_improvements": _frontier_improvements(
            result.top_candidates,
            baseline_test_metrics,
        ),
        "tradeoff_programs": tradeoffs,
        "held_out": {
            "route_count": len(test),
            "best_score": top.test_score,
            "rerun_score": rerun.score,
        },
        "splits": {
            "train_route_ids": tuple(route.route_id for route in train),
            "validation_route_ids": tuple(route.route_id for route in validation),
            "test_route_ids": tuple(route.route_id for route in test),
            "test_routes": test,
        },
        "top_candidates": [candidate.as_dict() for candidate in result.top_candidates],
        "rerun_top": {
            "program_id": top.program_id,
            "ok": rerun.ok,
            "score": rerun.score,
        },
    }


def _baseline_scores(routes: Sequence[AmazonRoute]) -> Dict[str, float]:
    scores = {}
    for name, builder in AMAZON_BASELINE_ROUTE_BUILDERS.items():
        rows = [builder(route).metrics for route in routes]
        scores[name] = _objective_score(_average_metrics(rows))
    return scores


def _baseline_metrics(
    routes: Sequence[AmazonRoute],
) -> Dict[str, Mapping[str, float]]:
    return {
        name: _average_metrics([builder(route).metrics for route in routes])
        for name, builder in AMAZON_BASELINE_ROUTE_BUILDERS.items()
    }


def _frontier_improvements(
    candidates: Sequence[AmazonTopCandidate],
    baseline_metrics: Mapping[str, Mapping[str, float]],
) -> List[Mapping[str, object]]:
    reference = baseline_metrics["driver_aware"]
    improvements = []
    for candidate in candidates:
        metrics = candidate.test_metrics
        travel_delta = metrics["average_travel_time"] - reference["travel_time"]
        if travel_delta < 0:
            improvements.append(
                {
                    "program_id": candidate.program_id,
                    "metric": "travel_time",
                    "delta": travel_delta,
                    "reference": "driver_aware",
                }
            )
    return improvements


def _tradeoff_programs(
    candidates: Sequence[AmazonTopCandidate],
    baseline_metrics: Mapping[str, Mapping[str, float]],
) -> List[Mapping[str, object]]:
    reference = baseline_metrics["driver_aware"]
    tradeoffs = []
    for candidate in candidates:
        metrics = candidate.test_metrics
        travel_delta = metrics["average_travel_time"] - reference["travel_time"]
        driver_delta = metrics["average_driver_likeness"] - reference["driver_likeness"]
        if travel_delta < 0 and driver_delta < 0:
            tradeoffs.append(
                {
                    "program_id": candidate.program_id,
                    "pattern": "improves_travel_time_hurts_driver_likeness",
                    "travel_time_delta": travel_delta,
                    "driver_likeness_delta": driver_delta,
                    "explanation": candidate.explanation,
                }
            )
    return tradeoffs


def _average_metrics(rows: Sequence[Mapping[str, float]]) -> Mapping[str, float]:
    if not rows:
        return {
            "travel_time": 0.0,
            "time_window_violation": 0.0,
            "driver_likeness": 0.0,
            "zone_transition_similarity": 0.0,
            "route_compactness": 0.0,
        }
    return {
        "travel_time": _mean(row["travel_time"] for row in rows),
        "time_window_violation": _mean(row["time_window_violation"] for row in rows),
        "driver_likeness": _mean(row["driver_likeness"] for row in rows),
        "zone_transition_similarity": _mean(
            row["zone_transition_similarity"] for row in rows
        ),
        "route_compactness": _mean(row["route_compactness"] for row in rows),
    }


def _objective_score(metrics: Mapping[str, float]) -> float:
    return (
        metrics["travel_time"]
        + metrics["time_window_violation"] * 10.0
        + (1.0 - metrics["driver_likeness"]) * 5.0
        + (1.0 - metrics["zone_transition_similarity"]) * 3.0
        + (1.0 - metrics["route_compactness"]) * 2.0
    )


def _phase6_route_payload(route_id: str) -> Mapping[str, object]:
    return {
        "route_id": route_id,
        "station_code": "DLA9",
        "quality_label": "High",
        "depot": {
            "stop_id": "depot",
            "zone_id": "DEPOT",
            "x": 0.0,
            "y": 0.0,
        },
        "stops": [
            _stop("S1", "A", 1.0, 0.0, 1),
            _stop("S2", "A", 2.0, 0.0, 2),
            _stop("S3", "B", 1.0, 1.0, 1),
            _stop("S4", "B", 2.0, 1.0, 2),
        ],
        "actual_sequence": ["S1", "S2", "S3", "S4"],
        "travel_times": {
            "depot": {"depot": 0.0, "S1": 1.0, "S2": 5.0, "S3": 2.0, "S4": 6.0},
            "S1": {"depot": 1.0, "S1": 0.0, "S2": 5.0, "S3": 1.0, "S4": 6.0},
            "S2": {"depot": 5.0, "S1": 5.0, "S2": 0.0, "S3": 1.0, "S4": 1.0},
            "S3": {"depot": 2.0, "S1": 1.0, "S2": 1.0, "S3": 0.0, "S4": 5.0},
            "S4": {"depot": 1.0, "S1": 6.0, "S2": 1.0, "S3": 5.0, "S4": 0.0},
        },
    }


def _stop(
    stop_id: str,
    zone_id: str,
    x: float,
    y: float,
    package_count: int,
) -> Mapping[str, object]:
    return {
        "stop_id": stop_id,
        "zone_id": zone_id,
        "x": x,
        "y": y,
        "service_time": 1.0,
        "time_window": [0.0, 100.0],
        "packages": [
            {"package_id": f"{stop_id}-p{index}", "weight": 1.0}
            for index in range(package_count)
        ],
    }


def _failure_code(failure_reason: str) -> str:
    return failure_reason.split(":", 1)[0]


def _mean(values: Sequence[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
