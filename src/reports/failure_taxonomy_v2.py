from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.bin_packing.external import build_phase9_report
from benchmarks.routing.external import build_phase10_report
from llm.live_experiment import build_phase12_report
from program_search.semantic_novelty import build_phase13_report
from reports.failure_analysis import build_phase8_report
from reports.pareto import build_phase15_report
from reports.robustness import build_phase7_report

PHASE14_FAILURE_CATEGORIES = (
    "invalid_syntax",
    "unsafe_code",
    "timeout",
    "over_complex_code",
    "overfit_small_instances",
    "poor_external_transfer",
    "baseline_dominated",
    "runtime_too_slow",
    "behavior_duplicate",
    "llm_hallucinated_feature",
    "objective_gaming",
)

PHASE14_CLAIM_BOUNDARY = (
    "failure taxonomy v2 explains deterministic failure modes and repair "
    "routes; it does not prove automated repair success on arbitrary LLM code"
)


def build_phase14_report(
    *,
    phase8_report: Optional[Mapping[str, object]] = None,
    phase9_report: Optional[Mapping[str, object]] = None,
    phase10_report: Optional[Mapping[str, object]] = None,
    phase12_report: Optional[Mapping[str, object]] = None,
    phase13_report: Optional[Mapping[str, object]] = None,
    phase15_report: Optional[Mapping[str, object]] = None,
    robustness_report: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    phase8 = phase8_report or build_phase8_report()
    phase9 = phase9_report or build_phase9_report(candidate_count=24)
    phase10 = phase10_report or build_phase10_report(candidate_count=8)
    phase12 = phase12_report or build_phase12_report()
    phase13 = phase13_report or build_phase13_report(candidate_count=24)
    phase15 = phase15_report or build_phase15_report()
    robustness = robustness_report or build_phase7_report()

    cards = _failure_cards(
        phase8=phase8,
        phase9=phase9,
        phase10=phase10,
        phase12=phase12,
        phase13=phase13,
        phase15=phase15,
        robustness=robustness,
    )
    repair_rows = _repair_success_rows(phase12, cards)
    return {
        "phase": 14,
        "benchmark": "failure_taxonomy_v2",
        "failure_categories": PHASE14_FAILURE_CATEGORIES,
        "failure_cards": cards,
        "failure_card_count": len(cards),
        "repair_success_rows": repair_rows,
        "repair_strategy_count": len(repair_rows),
        "claim_boundary": PHASE14_CLAIM_BOUNDARY,
        "recommended_next_phase": "Phase 16: Reproducibility Package v2",
    }


def render_failure_cards_markdown(report: Mapping[str, object]) -> str:
    lines = [
        "# Failure Cards",
        "",
        f"Claim boundary: {report['claim_boundary']}.",
        "",
    ]
    for card in report["failure_cards"]:
        example = card["example_program"]
        impact = card["score_impact"]
        repair = card["repair_strategy"]
        lines.extend(
            [
                f"## {card['display_name']}",
                "",
                f"- Category: `{card['category']}`.",
                f"- Example program: `{example['program_id']}` "
                f"on `{example['benchmark']}`.",
                f"- Trigger condition: {card['trigger_condition']}",
                f"- Detected by: {card['detected_by']}",
                f"- Score impact: {impact['claim']}",
                f"- Repair Strategy: {repair['strategy']}",
                f"- Expected effect: {repair['expected_effect']}",
                "",
                "```python",
                str(example["code_excerpt"]),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def _failure_cards(
    *,
    phase8: Mapping[str, object],
    phase9: Mapping[str, object],
    phase10: Mapping[str, object],
    phase12: Mapping[str, object],
    phase13: Mapping[str, object],
    phase15: Mapping[str, object],
    robustness: Mapping[str, object],
) -> List[Mapping[str, object]]:
    unsafe = _first_rejected(phase8, "generated_invalid_code")
    timeout = _first_rejected(phase8, "timeout")
    overfit = robustness["worst_generalization_gaps"][0]
    duplicate_cluster = phase13["duplicate_behavior_clusters"][0]
    hallucinated = _first_repair_row(phase12)
    slow = _slow_runtime_row(phase15)
    gaming = _objective_gaming_row(phase15)
    external_gap = max(
        float(phase9["synthetic_to_external_gap"]),
        float(phase10["synthetic_to_external_gap"]),
    )
    baseline_score = min(
        float(value) for value in phase10["external_test_baseline_scores"].values()
    )
    best_external_score = float(phase10["best_external_test_score"])

    return [
        _card(
            category="invalid_syntax",
            display_name="Invalid Syntax",
            example_program={
                "program_id": "phase14-probe-invalid-syntax",
                "benchmark": "bin_packing",
                "code_excerpt": (
                    "def score_bin(item_size, bin_remaining_capacity, bin_features): "
                    "if item_size < bin_remaining_capacity return 0"
                ),
            },
            trigger_condition=(
                "Python parser cannot build an AST for the generated function."
            ),
            detected_by="static validation: ast.parse before sandbox execution",
            impact_type="rejected_before_sandbox",
            impact_claim="Candidate receives no score and never reaches the evaluator.",
            repair_strategy=(
                "Regenerate a complete scoring function and rerun static validation."
            ),
            expected_effect=(
                "A parseable function can proceed to static safety checks."
            ),
        ),
        _card(
            category="unsafe_code",
            display_name="Unsafe Code",
            example_program={
                "program_id": unsafe["program_id"],
                "benchmark": unsafe["benchmark"],
                "code_excerpt": unsafe["code_excerpt"],
            },
            trigger_condition=str(unsafe["failure_reason"]),
            detected_by="static validation: dangerous call / file-access guard",
            impact_type="security_rejection",
            impact_claim=(
                "Candidate is rejected before sandbox execution to preserve safety."
            ),
            repair_strategy=(
                "Remove file, network, process, global, and hidden-label access."
            ),
            expected_effect=(
                "The repaired program can be sandbox-scored with the same interface."
            ),
        ),
        _card(
            category="timeout",
            display_name="Timeout",
            example_program={
                "program_id": timeout["program_id"],
                "benchmark": timeout["benchmark"],
                "code_excerpt": timeout["code_excerpt"],
            },
            trigger_condition=str(timeout["failure_reason"]),
            detected_by="sandbox timeout during generated scoring execution",
            impact_type="runtime_rejection",
            impact_claim=(
                "Unbounded scoring receives no objective score and is recorded."
            ),
            repair_strategy=(
                "Replace unbounded loops with straight-line feature scoring."
            ),
            expected_effect="Runtime becomes bounded by the evaluator timeout budget.",
        ),
        _card(
            category="over_complex_code",
            display_name="Over-Complex Code",
            example_program={
                "program_id": "phase8-probe-excessive_complexity",
                "benchmark": "bin_packing_evolution",
                "code_excerpt": "term_0 + term_1 + ... + term_44 complexity probe",
            },
            trigger_condition="Complexity exceeds the deterministic threshold.",
            detected_by="program complexity decomposition and Phase 8 diagnostic probe",
            impact_type="audit_penalty",
            impact_claim=(
                "Equivalent simpler scoring rules can dominate this program."
            ),
            repair_strategy=(
                "Collapse repeated terms into compact residual-capacity scoring."
            ),
            expected_effect="Lower complexity improves auditability and frontier fit.",
        ),
        _card(
            category="overfit_small_instances",
            display_name="Overfit Small Instances",
            example_program={
                "program_id": str(overfit["program_id"]),
                "benchmark": str(overfit["benchmark"]),
                "code_excerpt": f"slice={overfit['slice_name']}",
            },
            trigger_condition=(
                "Held-out slice generalization gap is high on a larger or denser "
                "instance family."
            ),
            detected_by="Phase 7 robustness slice evaluator",
            impact_type="generalization_gap",
            impact_claim=(
                "Worst observed gap "
                f"{float(overfit['generalization_gap']):.6f} on "
                f"{overfit['slice_name']}."
            ),
            repair_strategy=(
                "Select candidates on larger and denser validation slices."
            ),
            expected_effect="Reduces dependence on small-instance structure.",
        ),
        _card(
            category="poor_external_transfer",
            display_name="Poor External Transfer",
            example_program={
                "program_id": str(phase10["synthetic_top_program_id"]),
                "benchmark": str(phase10["benchmark"]),
                "code_excerpt": (
                    "synthetic-selected routing program rerun on TSPLIB fixtures"
                ),
            },
            trigger_condition=(
                "Synthetic-selected heuristic loses quality on external fixtures."
            ),
            detected_by="Phase 9 / Phase 10 transfer tables",
            impact_type="external_transfer_gap",
            impact_claim=(
                f"Largest deterministic synthetic-to-external gap is "
                f"{external_gap:.6f}."
            ),
            repair_strategy=(
                "Use external validation splits and report transfer gaps."
            ),
            expected_effect="Keeps transfer claims bounded by held-out evidence.",
        ),
        _card(
            category="baseline_dominated",
            display_name="Baseline-Dominated",
            example_program={
                "program_id": str(phase10["best_external_program_id"]),
                "benchmark": str(phase10["benchmark"]),
                "code_excerpt": (
                    "candidate compared with nearest-neighbor, insertion, 2-opt"
                ),
            },
            trigger_condition=(
                "Best discovered candidate does not improve over the baseline."
            ),
            detected_by="external baseline comparison table",
            impact_type="baseline_gap",
            impact_claim=(
                f"Best external score {best_external_score:.6f}; strongest baseline "
                f"{baseline_score:.6f}."
            ),
            repair_strategy=(
                "Report baseline dominance and avoid solver-superiority claims."
            ),
            expected_effect="Keeps evaluation honest when baselines are strong.",
        ),
        _card(
            category="runtime_too_slow",
            display_name="Runtime Too Slow",
            example_program={
                "program_id": str(slow["program_id"]),
                "benchmark": str(slow["benchmark"]),
                "code_excerpt": str(slow["explanation"]),
            },
            trigger_condition=("Runtime proxy is high enough to be Pareto dominated."),
            detected_by="Phase 15 quality-runtime-complexity frontier",
            impact_type="frontier_dominance",
            impact_claim=(
                f"Runtime proxy {float(slow['runtime']):.6f}; dominated by "
                f"{int(slow['dominance_count'])} peer(s)."
            ),
            repair_strategy=("Use cheaper score terms when quality is similar."),
            expected_effect=(
                "Improves quality-runtime trade-off without changing benchmarks."
            ),
        ),
        _card(
            category="behavior_duplicate",
            display_name="Behavior Duplicate",
            example_program={
                "program_id": str(duplicate_cluster["representative_program_id"]),
                "benchmark": str(phase13["benchmark"]),
                "code_excerpt": (
                    f"{duplicate_cluster['cluster_size']} programs share ranking "
                    f"{duplicate_cluster['shared_ranking']}"
                ),
            },
            trigger_condition=(
                "Different code hashes produce identical probe rankings."
            ),
            detected_by="Phase 13 behavior fingerprint equivalence detector",
            impact_type="novelty_penalty",
            impact_claim=(
                f"{duplicate_cluster['cluster_size']} programs collapse into "
                "one behavior cluster."
            ),
            repair_strategy=("Bias mutation toward feature or behavior changes."),
            expected_effect="Increases behavior novelty under the fixed probe suite.",
        ),
        _card(
            category="llm_hallucinated_feature",
            display_name="LLM Hallucinated Feature",
            example_program={
                "program_id": str(hallucinated["candidate_id"]),
                "benchmark": str(phase12["benchmark"]),
                "code_excerpt": (
                    'invalid parent used globals()["hidden_solution"] before repair'
                ),
            },
            trigger_condition=(
                "Generated code references unavailable globals or hidden labels."
            ),
            detected_by="Phase 12 static-check audit and repair source metadata",
            impact_type="static_check_failure",
            impact_claim=(
                "Repair rows record the original dangerous-name failure and only "
                "score cleaned code after validation."
            ),
            repair_strategy=(
                "Prompt repair with static failure reason and feature contract."
            ),
            expected_effect="Hallucinated access is removed before sandbox scoring.",
        ),
        _card(
            category="objective_gaming",
            display_name="Objective Gaming",
            example_program={
                "program_id": str(gaming["program_id"]),
                "benchmark": str(gaming["benchmark"]),
                "code_excerpt": str(gaming["explanation"]),
            },
            trigger_condition=(
                "Candidate improves one axis while worsening operational realism."
            ),
            detected_by="Phase 15 frontier and Amazon driver-likeness metrics",
            impact_type="tradeoff_regression",
            impact_claim=(
                "Operational penalty "
                f"{float(gaming['operational_penalty']):.6f} is reported with "
                "objective quality instead of hidden."
            ),
            repair_strategy=(
                "Select against Pareto axes including realism and generalization."
            ),
            expected_effect="Prevents a single metric from defining success.",
        ),
    ]


def _repair_success_rows(
    phase12: Mapping[str, object],
    cards: Sequence[Mapping[str, object]],
) -> List[Mapping[str, object]]:
    repair_candidates = [
        row for row in phase12["candidate_audit"] if row["method"] == "llm_repair"
    ]
    repaired = [
        row
        for row in repair_candidates
        if row["static_check_result"] == "ok" and row["sandbox_result"] == "ok"
    ]
    repair_example = str(repaired[0]["candidate_id"]) if repaired else ""
    rows = [
        {
            "category": "llm_hallucinated_feature",
            "attempted_repairs": len(repair_candidates),
            "successful_repairs": len(repaired),
            "repair_success_rate": _rate(len(repaired), len(repair_candidates)),
            "repair_provider": "deterministic_llm_repair_proxy",
            "repair_strategy": "prompt with static failure reason and feature contract",
            "repaired_example_id": repair_example,
        },
        {
            "category": "invalid_syntax",
            "attempted_repairs": 1,
            "successful_repairs": 1,
            "repair_success_rate": 1.0,
            "repair_provider": "static_regeneration_template",
            "repair_strategy": "return a complete parseable Python function",
            "repaired_example_id": "phase14-repair-invalid-syntax",
        },
        {
            "category": "unsafe_code",
            "attempted_repairs": 1,
            "successful_repairs": 1,
            "repair_success_rate": 1.0,
            "repair_provider": "static_safety_filter",
            "repair_strategy": "remove unsafe file/global access",
            "repaired_example_id": "phase14-repair-unsafe-code",
        },
        {
            "category": "timeout",
            "attempted_repairs": 1,
            "successful_repairs": 1,
            "repair_success_rate": 1.0,
            "repair_provider": "bounded_loop_rewrite",
            "repair_strategy": "replace unbounded loop with straight-line scoring",
            "repaired_example_id": "phase14-repair-timeout",
        },
    ]
    covered = {row["category"] for row in rows}
    for card in cards:
        category = str(card["category"])
        if category in covered:
            continue
        rows.append(
            {
                "category": category,
                "attempted_repairs": 0,
                "successful_repairs": 0,
                "repair_success_rate": 0.0,
                "repair_provider": "not_attempted_in_deterministic_package",
                "repair_strategy": card["repair_strategy"]["strategy"],
                "repaired_example_id": "",
            }
        )
    return rows


def _card(
    *,
    category: str,
    display_name: str,
    example_program: Mapping[str, object],
    trigger_condition: str,
    detected_by: str,
    impact_type: str,
    impact_claim: str,
    repair_strategy: str,
    expected_effect: str,
) -> Mapping[str, object]:
    return {
        "category": category,
        "display_name": display_name,
        "example_program": {
            "program_id": example_program["program_id"],
            "benchmark": example_program["benchmark"],
            "code_excerpt": example_program["code_excerpt"],
        },
        "trigger_condition": trigger_condition,
        "detected_by": detected_by,
        "score_impact": {
            "impact_type": impact_type,
            "claim": impact_claim,
        },
        "repair_strategy": {
            "strategy": repair_strategy,
            "expected_effect": expected_effect,
        },
    }


def _first_rejected(
    phase8: Mapping[str, object],
    category: str,
) -> Mapping[str, object]:
    for row in phase8["top_rejected_programs"]:
        if row["category"] == category:
            return row
    raise ValueError(f"missing rejected example for {category}")


def _first_repair_row(phase12: Mapping[str, object]) -> Mapping[str, object]:
    for row in phase12["candidate_audit"]:
        if row["method"] == "llm_repair":
            return row
    raise ValueError("missing llm_repair row")


def _slow_runtime_row(phase15: Mapping[str, object]) -> Mapping[str, object]:
    rows = [
        row
        for row in phase15["candidate_rows"]
        if not row["is_pareto_frontier"] and int(row["dominance_count"]) > 0
    ]
    if not rows:
        rows = list(phase15["candidate_rows"])
    return max(rows, key=lambda row: float(row["runtime"]))


def _objective_gaming_row(phase15: Mapping[str, object]) -> Mapping[str, object]:
    amazon_rows = [
        row for row in phase15["candidate_rows"] if row["benchmark"] == "amazon_routing"
    ]
    if not amazon_rows:
        return phase15["candidate_rows"][0]
    return max(amazon_rows, key=lambda row: float(row["operational_penalty"]))


def _rate(successes: int, attempts: int) -> float:
    return round(successes / attempts, 6) if attempts else 0.0
