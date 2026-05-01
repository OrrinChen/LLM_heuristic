from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    AmazonDiscoveryLoop,
    build_phase6_report,
    default_phase6_train_validation_test_routes,
)
from benchmarks.amazon_routing.evaluator import AmazonRoutingEvaluator
from benchmarks.bin_packing.instances import (
    default_train_validation_test_suites as default_bin_packing_suites,
)
from program_search.archive import ProgramArchive
from program_search.candidate_program import CandidateProgram
from program_search.evolution_loop import EvolutionConfig, EvolutionLoop
from program_search.scoring import compute_program_complexity
from reports.robustness import build_phase7_report

PHASE8_FAILURE_CATEGORIES = (
    "generated_invalid_code",
    "timeout",
    "hardcoded_heuristic",
    "overfit_to_small_instances",
    "poor_generalization",
    "routing_feasibility_violation",
    "excessive_complexity",
    "improves_travel_time_but_hurts_driver_likeness",
    "improves_driver_likeness_but_too_slow",
)

COMPLEXITY_THRESHOLD = 120
POOR_GENERALIZATION_GAP = 20.0


@dataclass(frozen=True)
class DiagnosticProbe:
    program_id: str
    benchmark: str
    category: str
    failure_reason: str
    generation: int
    complexity: int
    runtime: float
    code: str

    def as_rejected_program(self) -> Mapping[str, object]:
        return {
            "benchmark": self.benchmark,
            "program_id": self.program_id,
            "generation": self.generation,
            "category": self.category,
            "failure_reason": self.failure_reason,
            "complexity": self.complexity,
            "runtime": round(self.runtime, 6),
            "score": None,
            "code_excerpt": _code_excerpt(self.code),
        }


def build_phase8_report() -> Dict[str, object]:
    bin_result = _run_bin_packing_evolution()
    amazon_result = _run_amazon_discovery()
    amazon_report = build_phase6_report(config=_amazon_config())
    robustness_report = build_phase7_report()
    probes = _diagnostic_probes()

    rejected = (
        _archive_rejections("bin_packing_evolution", bin_result.archive)
        + _archive_rejections("amazon_routing_discovery", amazon_result.archive)
        + [probe.as_rejected_program() for probe in probes]
    )
    surviving = _surviving_candidates(
        "bin_packing_evolution", bin_result.top_candidates
    ) + _surviving_candidates(
        "amazon_routing_discovery",
        amazon_result.top_candidates,
    )
    generation_rows = _generation_rows(
        "bin_packing_evolution", bin_result.generation_reports
    ) + _generation_rows("amazon_routing_discovery", amazon_result.generation_reports)
    taxonomy = _build_taxonomy(
        rejected=rejected,
        robustness_report=robustness_report,
        amazon_report=amazon_report,
        probes=probes,
    )

    return {
        "phase": 8,
        "failure_categories": PHASE8_FAILURE_CATEGORIES,
        "failure_taxonomy": taxonomy,
        "failure_rate_by_generation": generation_rows,
        "invalid_code_rate_by_generation": [
            {
                "benchmark": row["benchmark"],
                "generation": row["generation"],
                "invalid_code_rate": row["invalid_code_rate"],
            }
            for row in generation_rows
        ],
        "top_rejected_programs": _rank_rejected(rejected),
        "top_surviving_programs": _rank_surviving(surviving),
        "patterns_that_worked": _patterns_that_worked(
            surviving=surviving,
            amazon_report=amazon_report,
        ),
        "patterns_that_failed": _patterns_that_failed(
            rejected=rejected,
            robustness_report=robustness_report,
            amazon_report=amazon_report,
            probes=probes,
        ),
        "known_limitations": (
            "Timeout, excessive-complexity, and driver-likeness-too-slow rows "
            "use deterministic diagnostic probes to keep the failure taxonomy "
            "visible without adding unsafe LLM execution.",
            "Routing feasibility violations are structurally prevented by the "
            "current next-stop evaluator, so that category can be zero while "
            "the full route-generation interface remains deferred.",
        ),
    }


def _run_bin_packing_evolution():
    train, validation, test = default_bin_packing_suites(item_count=20)
    return EvolutionLoop(config=_evolution_config()).run(
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )


def _run_amazon_discovery():
    train, validation, test = default_phase6_train_validation_test_routes()
    return AmazonDiscoveryLoop(config=_amazon_config()).run(
        train_routes=train,
        validation_routes=validation,
        test_routes=test,
    )


def _evolution_config() -> EvolutionConfig:
    return EvolutionConfig(
        generations=3,
        population_size=16,
        offspring_per_generation=12,
        elite_size=4,
        tournament_size=3,
        random_seed=23,
    )


def _amazon_config() -> AmazonDiscoveryConfig:
    return AmazonDiscoveryConfig(
        generations=2,
        population_size=12,
        offspring_per_generation=8,
        elite_size=4,
        tournament_size=3,
        random_seed=23,
    )


def _diagnostic_probes() -> List[DiagnosticProbe]:
    _, _, test_routes = default_phase6_train_validation_test_routes()
    timeout_code = (
        """
def score_next_stop(state, candidate_stop):
    while True:
        pass
""".strip()
        + "\n"
    )
    timeout = AmazonRoutingEvaluator(timeout_seconds=0.01).evaluate_program(
        timeout_code,
        test_routes[:1],
        program_id="phase8-probe-driver_like_timeout",
        apply_local_search=True,
    )

    complex_code = _complex_program()
    complexity = compute_program_complexity(complex_code)
    return [
        DiagnosticProbe(
            program_id="phase8-probe-driver_like_timeout",
            benchmark="amazon_routing_discovery",
            category="timeout",
            failure_reason=timeout.failure_reason or "timeout_not_triggered",
            generation=-1,
            complexity=compute_program_complexity(timeout_code),
            runtime=timeout.runtime,
            code=timeout_code,
        ),
        DiagnosticProbe(
            program_id="phase8-probe-excessive_complexity",
            benchmark="bin_packing_evolution",
            category="excessive_complexity",
            failure_reason=(
                f"complexity {complexity} exceeds threshold {COMPLEXITY_THRESHOLD}"
            ),
            generation=-1,
            complexity=complexity,
            runtime=0.0,
            code=complex_code,
        ),
    ]


def _complex_program() -> str:
    lines = [
        "def score_bin(item_size, bin_remaining_capacity, bin_features):",
        "    projected = bin_remaining_capacity - item_size",
        "    if projected < 0:",
        "        return 1000000",
    ]
    for index in range(45):
        lines.append(f"    term_{index} = abs(projected - {index / 100:.2f})")
    expression = " + ".join(f"term_{index}" for index in range(45))
    lines.append(f"    return projected + ({expression}) / 45")
    return "\n".join(lines) + "\n"


def _generation_rows(
    benchmark: str,
    reports: Sequence[object],
) -> List[Mapping[str, object]]:
    return [
        {
            "benchmark": benchmark,
            "generation": report.generation,
            "population_size": report.population_size,
            "failure_rate": report.failure_rate,
            "invalid_code_rate": report.invalid_code_rate,
            "best_score": report.best_score,
            "median_score": report.median_score,
            "best_program_id": report.best_program_id,
        }
        for report in reports
    ]


def _archive_rejections(
    benchmark: str,
    archive: ProgramArchive,
) -> List[Mapping[str, object]]:
    rows = []
    for candidate in archive.failures():
        evaluations = archive.evaluations_for(candidate.program_id)
        failure_reason = _failure_reason(candidate, evaluations)
        rows.append(
            {
                "benchmark": benchmark,
                "program_id": candidate.program_id,
                "generation": candidate.generation,
                "category": _category_for_failure(candidate, failure_reason),
                "failure_reason": failure_reason,
                "complexity": compute_program_complexity(candidate.code),
                "runtime": round(float(candidate.runtime or 0.0), 6),
                "score": None,
                "code_excerpt": _code_excerpt(candidate.code),
            }
        )
    return rows


def _surviving_candidates(
    benchmark: str,
    candidates: Sequence[object],
) -> List[Mapping[str, object]]:
    rows = []
    for candidate in candidates:
        rows.append(
            {
                "benchmark": benchmark,
                "program_id": candidate.program_id,
                "generation": candidate.generation,
                "score": candidate.final_score,
                "train_score": candidate.train_score,
                "validation_score": candidate.validation_score,
                "test_score": candidate.test_score,
                "complexity": candidate.complexity,
                "generalization_gap": candidate.generalization_gap,
                "pattern": _worked_pattern(candidate.program_id, candidate.code),
                "code_excerpt": _code_excerpt(candidate.code),
            }
        )
    return rows


def _build_taxonomy(
    *,
    rejected: Sequence[Mapping[str, object]],
    robustness_report: Mapping[str, object],
    amazon_report: Mapping[str, object],
    probes: Sequence[DiagnosticProbe],
) -> Dict[str, Mapping[str, object]]:
    counts: Counter[str] = Counter()
    evidence: Dict[str, List[str]] = {
        category: [] for category in PHASE8_FAILURE_CATEGORIES
    }

    for row in rejected:
        category = str(row["category"])
        counts[category] += 1
        evidence[category].append(str(row["program_id"]))
        code_excerpt = str(row.get("code_excerpt", ""))
        if "hidden_labels" in code_excerpt or "training_labels" in code_excerpt:
            counts["hardcoded_heuristic"] += 1
            evidence["hardcoded_heuristic"].append(str(row["program_id"]))

    for row in robustness_report["slice_summary"]:
        gap = float(row["generalization_gap"])
        if gap >= POOR_GENERALIZATION_GAP:
            counts["poor_generalization"] += 1
            evidence["poor_generalization"].append(str(row["slice_name"]))
        if (
            row["dimension"] == "small_routes_vs_large_routes"
            and row["tags"].get("route_size") == "large"
            and gap >= POOR_GENERALIZATION_GAP
        ):
            counts["overfit_to_small_instances"] += 1
            evidence["overfit_to_small_instances"].append(str(row["slice_name"]))

    tradeoffs = amazon_report["tradeoff_programs"]
    counts["improves_travel_time_but_hurts_driver_likeness"] += len(tradeoffs)
    evidence["improves_travel_time_but_hurts_driver_likeness"].extend(
        str(row["program_id"]) for row in tradeoffs
    )

    if any(probe.category == "timeout" for probe in probes):
        counts["improves_driver_likeness_but_too_slow"] += 1
        evidence["improves_driver_likeness_but_too_slow"].append(
            "phase8-probe-driver_like_timeout"
        )

    return {
        category: {
            "category": category,
            "count": counts[category],
            "severity": _severity(category, counts[category]),
            "evidence": tuple(evidence[category][:5]),
            "rationale": _taxonomy_rationale(category, counts[category]),
        }
        for category in PHASE8_FAILURE_CATEGORIES
    }


def _patterns_that_worked(
    *,
    surviving: Sequence[Mapping[str, object]],
    amazon_report: Mapping[str, object],
) -> List[Mapping[str, object]]:
    return [
        {
            "pattern": "tight_fit_bin_packing",
            "evidence": _first_program_with(surviving, "tight_fit"),
            "summary": (
                "Best-fit style residual-capacity scoring remains compact "
                "and reproducible."
            ),
        },
        {
            "pattern": "return_aware_routing",
            "evidence": _first_program_with(surviving, "return_aware"),
            "summary": (
                "Return-aware route scores survive held-out simple-routing tests."
            ),
        },
        {
            "pattern": "amazon_travel_time_frontier",
            "evidence": amazon_report["frontier_improvements"][0]["program_id"],
            "summary": (
                "Travel-time focused Amazon programs improve the driver-aware "
                "travel frontier."
            ),
        },
    ]


def _patterns_that_failed(
    *,
    rejected: Sequence[Mapping[str, object]],
    robustness_report: Mapping[str, object],
    amazon_report: Mapping[str, object],
    probes: Sequence[DiagnosticProbe],
) -> List[Mapping[str, object]]:
    worst_gap = robustness_report["worst_generalization_gaps"][0]
    timeout_probe = next(probe for probe in probes if probe.category == "timeout")
    return [
        {
            "pattern": "unsafe_data_access",
            "evidence": _first_category(rejected, "generated_invalid_code"),
            "summary": (
                "Programs that try to read hidden or training labels are "
                "rejected by static checks."
            ),
        },
        {
            "pattern": "routing_large_slice_generalization_gap",
            "evidence": worst_gap["slice_name"],
            "summary": (
                "A compact routing rule can overfit smaller validation routes "
                "and lose quality on larger slices."
            ),
        },
        {
            "pattern": "travel_time_driver_likeness_tradeoff",
            "evidence": amazon_report["tradeoff_programs"][0]["program_id"],
            "summary": "Fast travel-time programs can reduce pairwise driver-likeness.",
        },
        {
            "pattern": "driver_like_timeout",
            "evidence": timeout_probe.program_id,
            "summary": (
                "Unbounded scoring logic is terminated and classified before "
                "it can dominate runtime."
            ),
        },
    ]


def _rank_rejected(
    rejected: Sequence[Mapping[str, object]],
) -> List[Mapping[str, object]]:
    priority = {
        "generated_invalid_code": 0,
        "timeout": 1,
        "excessive_complexity": 2,
        "hardcoded_heuristic": 3,
        "routing_feasibility_violation": 4,
    }
    return sorted(
        rejected,
        key=lambda row: (
            priority.get(str(row["category"]), 99),
            int(row["generation"]),
            str(row["program_id"]),
        ),
    )[:8]


def _rank_surviving(
    surviving: Sequence[Mapping[str, object]],
) -> List[Mapping[str, object]]:
    return sorted(
        surviving,
        key=lambda row: (
            float(row["score"]),
            str(row["benchmark"]),
            str(row["program_id"]),
        ),
    )[:8]


def _failure_reason(
    candidate: CandidateProgram,
    evaluations: Sequence[object],
) -> str:
    if candidate.failure_reason:
        return candidate.failure_reason
    for evaluation in evaluations:
        if evaluation.failure_reason:
            return evaluation.failure_reason
    return "candidate_failed"


def _category_for_failure(candidate: CandidateProgram, failure_reason: str) -> str:
    code = candidate.code
    if "timeout" in failure_reason:
        return "timeout"
    if "missing_stops" in failure_reason or "duplicate_stops" in failure_reason:
        return "routing_feasibility_violation"
    if compute_program_complexity(code) > COMPLEXITY_THRESHOLD:
        return "excessive_complexity"
    if any(
        token in failure_reason
        for token in (
            "dangerous_call",
            "dangerous_name",
            "import_not_allowed",
            "syntax_error",
            "disallowed_global",
            "non_numeric_score",
        )
    ):
        return "generated_invalid_code"
    if "hidden_labels" in code or "training_labels" in code:
        return "hardcoded_heuristic"
    return "generated_invalid_code"


def _worked_pattern(program_id: str, code: str) -> str:
    if "tight_fit" in program_id or "projected" in code:
        return "tight_fit_bin_packing"
    if "return_aware" in program_id or "distance_to_depot" in code:
        return "return_aware_routing"
    if "travel_fast" in program_id or 'candidate_stop["travel_time"]' in code:
        return "amazon_travel_time_frontier"
    return "compact_score_rule"


def _first_program_with(rows: Sequence[Mapping[str, object]], token: str) -> str:
    for row in rows:
        if token in str(row["program_id"]) or token in str(row.get("pattern", "")):
            return str(row["program_id"])
    return ""


def _first_category(rows: Sequence[Mapping[str, object]], category: str) -> str:
    for row in rows:
        if row["category"] == category:
            return str(row["program_id"])
    return ""


def _severity(category: str, count: int) -> str:
    if count == 0:
        return "none"
    if category in {
        "generated_invalid_code",
        "timeout",
        "hardcoded_heuristic",
        "routing_feasibility_violation",
    }:
        return "high"
    if category in {
        "poor_generalization",
        "overfit_to_small_instances",
        "improves_travel_time_but_hurts_driver_likeness",
    }:
        return "medium"
    return "low"


def _taxonomy_rationale(category: str, count: int) -> str:
    if category == "routing_feasibility_violation" and count == 0:
        return (
            "No observed route feasibility violation because generated programs "
            "score one remaining stop at a time instead of emitting full routes."
        )
    if count == 0:
        return "No deterministic observation in the current Phase 8 report run."
    return f"{count} deterministic observation(s) classified for this failure mode."


def _code_excerpt(code: str) -> str:
    lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
    return " ".join(lines[:3])
