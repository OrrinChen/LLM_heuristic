from __future__ import annotations

from typing import Dict, Mapping

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
)
from benchmarks.bin_packing.evaluator import build_phase2_report
from benchmarks.bin_packing.external import build_phase9_report
from benchmarks.routing.evaluator import build_phase4_report
from benchmarks.routing.external import build_phase10_report
from llm.live_experiment import build_phase12_report
from program_search.ablation import build_phase11_report
from program_search.semantic_novelty import build_phase13_report
from reports.failure_analysis import build_phase8_report
from reports.failure_taxonomy_v2 import build_phase14_report
from reports.pareto import build_phase15_report
from reports.robustness import build_phase7_report

FINAL_REPORT_SECTIONS = (
    "executive_summary",
    "system_architecture",
    "killer_experiment",
    "benchmark_results",
    "external_benchmark_evidence",
    "routing_external_benchmark_evidence",
    "search_mechanism_ablation",
    "llm_live_mutation_v1",
    "program_semantics_and_novelty",
    "pareto_frontier_report",
    "generalization_and_robustness",
    "failure_analysis",
    "failure_taxonomy_v2",
    "limitations",
    "recommended_next_steps",
)

KILLER_EXPERIMENT_BENCHMARKS = (
    "bin_packing",
    "simple_routing",
    "amazon_routing",
)


def build_final_report() -> Dict[str, object]:
    phase2 = build_phase2_report(candidate_count=120, item_count=25)
    phase4 = build_phase4_report(candidate_count=8, stop_count=10)
    phase6 = build_phase6_report(
        config=AmazonDiscoveryConfig(
            generations=2,
            population_size=12,
            offspring_per_generation=8,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        )
    )
    phase7 = build_phase7_report()
    phase8 = build_phase8_report()
    phase9 = build_phase9_report(candidate_count=48, synthetic_item_count=25)
    phase10 = build_phase10_report(candidate_count=16, synthetic_stop_count=10)
    phase11 = build_phase11_report(
        candidate_budget=32,
        generations=3,
        item_count=20,
        random_seed=23,
    )
    phase12 = build_phase12_report()
    phase13 = build_phase13_report()
    phase15 = build_phase15_report()
    phase14 = build_phase14_report(
        phase8_report=phase8,
        phase9_report=phase9,
        phase10_report=phase10,
        phase12_report=phase12,
        phase13_report=phase13,
        phase15_report=phase15,
        robustness_report=phase7,
    )

    report: Dict[str, object] = {
        "phase": "final_report",
        "sections": FINAL_REPORT_SECTIONS,
        "project": {
            "project_id": "O2 Heuristic Discovery",
            "name": "LLM-Driven Program Search for OR Heuristics",
            "thesis": (
                "heuristic design can be automated as constrained program search"
            ),
            "resume_bullet": (
                "Built a FunSearch-inspired OR heuristic discovery system that "
                "evolves compact bin-packing and routing algorithms through "
                "sandboxed execution, automated evaluation, and held-out "
                "generalization tests."
            ),
        },
        "claims": {
            "conservative": (
                "A sandboxed LLM program-search loop can discover compact "
                "heuristics that improve selected trade-offs on held-out OR "
                "benchmark distributions."
            ),
            "does_not_claim": (
                "The report does not claim universal dominance over classical "
                "OR baselines or that LLMs solve OR problems directly."
            ),
            "live_llm_status": "optional_env_configured",
            "hardening_status": "subprocess_sandbox_manifest_artifacts_cli",
        },
        "killer_experiment": {
            "benchmarks": {
                "bin_packing": _bin_packing_summary(phase2),
                "simple_routing": _simple_routing_summary(phase4),
                "amazon_routing": _amazon_routing_summary(phase6),
            },
        },
        "external_benchmark": _external_bin_packing_summary(phase9),
        "routing_external": _external_routing_summary(phase10),
        "search_ablation": _search_ablation_summary(phase11),
        "live_llm": _live_llm_summary(phase12),
        "semantic_novelty": _semantic_novelty_summary(phase13),
        "pareto_frontier": _pareto_frontier_summary(phase15),
        "failure_taxonomy_v2": _failure_taxonomy_v2_summary(phase14),
        "evidence": _evidence_summary(phase6, phase7, phase8),
        "limitations": (
            "Live LLM mutation is optional and remains gated behind "
            "environment-variable configuration.",
            "External bin packing evidence uses parser-backed, small "
            "benchmark-style local fixtures by default; large public benchmark "
            "files are intentionally not committed.",
            "External routing evidence uses parser-backed, small TSPLIB-style "
            "and CVRPLIB-style local fixtures with time-window fields by "
            "default; large public benchmark files are intentionally not "
            "committed.",
            "Amazon routing data is represented by deterministic local "
            "Amazon-shaped fixtures until public or user-provided data is "
            "configured.",
            "Rendered report artifacts are deterministic local files; PNG plot "
            "rendering remains optional when matplotlib is available.",
            "Pareto frontier runtime is a deterministic local proxy for "
            "frontier comparison, not a hardware-independent benchmark.",
            "The current routing generated-program interface ranks next stops "
            "rather than emitting full routes.",
            "Subprocess memory limits are applied only on platforms that expose "
            "compatible resource limits.",
            "Semantic novelty is probe-based and detects behavior equivalence on "
            "fixed probe states; it does not prove human-level semantic "
            "understanding.",
            "Failure taxonomy v2 repair rows are deterministic evidence records, "
            "not proof that arbitrary LLM failures can be repaired automatically.",
        ),
        "recommended_next_steps": (
            {
                "step": "optional_routing_depth_or_release_polish",
                "reason": (
                    "No required job-search roadmap phase remains. Optional "
                    "extensions are broader crossover or release polish around "
                    "the existing evidence package."
                ),
            },
        ),
    }
    return report


def render_final_report_markdown(report: Mapping[str, object]) -> str:
    project = report["project"]
    claims = report["claims"]
    killer = report["killer_experiment"]["benchmarks"]
    external = report["external_benchmark"]
    routing_external = report["routing_external"]
    ablation = report["search_ablation"]
    live_llm = report["live_llm"]
    semantic = report["semantic_novelty"]
    frontier = report["pareto_frontier"]
    failure_v2 = report["failure_taxonomy_v2"]
    evidence = report["evidence"]

    lines = [
        "# LLM-Driven Program Search for OR Heuristics",
        "",
        "## Executive Summary",
        "",
        f"Thesis: {project['thesis']}.",
        "",
        claims["conservative"],
        "",
        (
            "The discovered heuristics do not universally dominate classical "
            "OR baselines; the evidence supports selected trade-offs under "
            "strict sandbox and evaluator constraints."
        ),
        "",
        "## System Architecture",
        "",
        (
            "Seed heuristics and generated scoring functions pass static "
            "validation, run in a restricted sandbox with subprocess isolation "
            "available for generated scoring calls, enter OR evaluators, and "
            "feed archive, manifest, artifact, robustness, and failure-analysis "
            "reports."
        ),
        "",
        "## Killer Experiment",
        "",
    ]
    for name in KILLER_EXPERIMENT_BENCHMARKS:
        benchmark = killer[name]
        lines.extend(
            [
                f"### {benchmark['label']}",
                "",
                benchmark["summary"],
                "",
                f"Top program: `{benchmark['top_program_id']}`.",
                f"Held-out test score: `{benchmark['test_score']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## External Benchmark Evidence",
            "",
            external["summary"],
            "",
            f"Benchmark: `{external['benchmark']}`.",
            f"External top program: `{external['best_external_program_id']}`.",
            (
                "External held-out test score: "
                f"`{external['best_external_test_score']}`."
            ),
            (
                "Synthetic-selected program external test score: "
                f"`{external['synthetic_top_external_test_score']}`."
            ),
            (
                "Claim boundary: this section does not claim SOTA or universal "
                "dominance."
            ),
            "",
        ]
    )
    lines.extend(
        [
            "## External Routing Evidence",
            "",
            routing_external["summary"],
            "",
            f"Benchmark: `{routing_external['benchmark']}`.",
            (
                "External routing top program: "
                f"`{routing_external['best_external_program_id']}`."
            ),
            (
                "External routing held-out test score: "
                f"`{routing_external['best_external_test_score']}`."
            ),
            (
                "External routing parser formats: "
                f"`{', '.join(routing_external['external_formats'])}`."
            ),
            (
                "Capacitated external instances: "
                f"`{routing_external['capacitated_instance_count']}`; "
                "top-program held-out capacity violation: "
                f"`{routing_external['best_external_test_capacity_violation']}`."
            ),
            (
                "Time-window external instances: "
                f"`{routing_external['time_window_instance_count']}`; "
                "top-program held-out time-window violation: "
                f"`{routing_external['best_external_test_time_window_violation']}`."
            ),
            (
                "Synthetic-selected routing program external test score: "
                f"`{routing_external['synthetic_top_external_test_score']}`."
            ),
            (
                "Claim boundary: this section does not claim LKH, CVRP/VRPTW "
                "solver, state-of-the-art solver, Amazon, or universal "
                "superiority."
            ),
            "",
        ]
    )
    lines.extend(
        [
            "## Search Mechanism Ablation",
            "",
            ablation["summary"],
            "",
            f"Best method under fixed local budget: `{ablation['best_method']}`.",
            f"Best validation score: `{ablation['best_validation_score']}`.",
            (
                "Methods compared: "
                + ", ".join(f"`{method}`" for method in ablation["methods"])
                + "."
            ),
            f"Claim boundary: {ablation['claim_boundary']}.",
            "",
        ]
    )
    lines.extend(
        [
            "## LLM Live Mutation v1",
            "",
            live_llm["summary"],
            "",
            f"Benchmark: `{live_llm['benchmark']}`.",
            f"Best method: `{live_llm['best_method']}`.",
            f"Best validation score: `{live_llm['best_validation_score']}`.",
            (
                "Live provider configured by default run: "
                f"`{live_llm['live_provider_configured']}`."
            ),
            f"Claim boundary: {live_llm['claim_boundary']}.",
            "",
        ]
    )
    lines.extend(
        [
            "## Program Semantics And Novelty",
            "",
            semantic["summary"],
            "",
            f"Benchmark: `{semantic['benchmark']}`.",
            f"Candidates fingerprinted: `{semantic['candidate_count']}`.",
            f"Behavior probes: `{semantic['probe_count']}`.",
            f"Behavior clusters: `{semantic['behavior_cluster_count']}`.",
            (
                "Equivalent-program members detected: "
                f"`{semantic['equivalent_program_count']}`."
            ),
            f"Claim boundary: {semantic['claim_boundary']}.",
            "",
        ]
    )
    lines.extend(
        [
            "## Pareto Frontier Report",
            "",
            frontier["summary"],
            "",
            f"Candidate rows: `{frontier['candidate_count']}`.",
            f"Frontier rows: `{frontier['frontier_count']}`.",
            (
                "Benchmarks covered: "
                + ", ".join(f"`{benchmark}`" for benchmark in frontier["benchmarks"])
                + "."
            ),
            f"Claim boundary: {frontier['claim_boundary']}",
            "",
        ]
    )
    lines.extend(
        [
            "## Generalization And Robustness",
            "",
            (
                f"The robustness report covers "
                f"{evidence['robustness']['benchmark_count']} benchmarks and "
                f"{evidence['robustness']['slice_count']} held-out slices."
            ),
            (
                f"Worst observed gap slice: "
                f"`{evidence['robustness']['worst_gap_slice']}`."
            ),
            "",
            "## Failure Analysis",
            "",
            (
                f"The failure report tracks "
                f"{evidence['failure_analysis']['failure_category_count']} "
                "failure categories, rejected programs, surviving programs, "
                "and worked/failed patterns."
            ),
            (
                f"Amazon trade-off callouts: "
                f"{evidence['amazon_tradeoffs']['tradeoff_count']}."
            ),
            "",
            "## Failure Taxonomy v2",
            "",
            failure_v2["summary"],
            "",
            f"Failure cards: `{failure_v2['failure_card_count']}`.",
            f"Repair success rows: `{failure_v2['repair_strategy_count']}`.",
            f"Claim boundary: {failure_v2['claim_boundary']}.",
            (
                "The report includes repair success evidence for deterministic "
                "syntax, unsafe-code, timeout, and LLM hallucinated-feature "
                "failure routes."
            ),
            "",
            "## Limitations",
            "",
        ]
    )
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(["", "## Recommended Next Steps", ""])
    for next_step in report["recommended_next_steps"]:
        lines.append(f"- `{next_step['step']}`: {next_step['reason']}")
    lines.append("")
    return "\n".join(lines)


def _bin_packing_summary(phase2: Mapping[str, object]) -> Mapping[str, object]:
    baseline_scores = phase2["baseline_scores"]
    return {
        "label": "Online Bin Packing",
        "top_program_id": phase2["best_program_id"],
        "test_score": phase2["test_score"],
        "summary": (
            "A compact `score_bin` heuristic is compared with online and "
            "offline bin-packing baselines on held-out item distributions."
        ),
        "comparisons": {
            "first_fit": _score_row(baseline_scores["first_fit"], "validation"),
            "best_fit": _score_row(baseline_scores["best_fit"], "validation"),
            "first_fit_decreasing": _score_row(
                baseline_scores["first_fit_decreasing"], "validation"
            ),
            "handwritten_score_heuristic": _score_row(
                baseline_scores["handwritten_score_heuristic"], "validation"
            ),
            "llm_discovered": _score_row(phase2["test_score"], "held_out_test"),
        },
    }


def _simple_routing_summary(phase4: Mapping[str, object]) -> Mapping[str, object]:
    baseline_scores = phase4["baseline_scores"]
    return {
        "label": "Simple Routing",
        "top_program_id": phase4["top_programs"][0]["program_id"],
        "test_score": phase4["test_score"],
        "summary": (
            "A constrained `score_next_stop` route heuristic is evaluated "
            "against nearest-neighbor, insertion, 2-opt, and local-search "
            "variants on held-out route sizes."
        ),
        "comparisons": {
            "nearest_neighbor": _score_row(
                baseline_scores["nearest_neighbor"], "validation"
            ),
            "cheapest_insertion": _score_row(
                baseline_scores["cheapest_insertion"], "validation"
            ),
            "two_opt": _score_row(baseline_scores["two_opt"], "validation"),
            "llm_discovered": _score_row(phase4["best_validation_score"], "validation"),
            "llm_discovered_plus_2opt": _score_row(
                phase4["test_score"], "held_out_test"
            ),
        },
    }


def _amazon_routing_summary(phase6: Mapping[str, object]) -> Mapping[str, object]:
    baseline_scores = phase6["baseline_scores"]
    top = phase6["top_candidates"][0]
    return {
        "label": "Amazon-Style Routing",
        "top_program_id": top["program_id"],
        "test_score": top["test_score"],
        "summary": (
            "Amazon-style route sequencing evaluates travel time, "
            "driver-likeness, zone behavior, local search, and explicit "
            "frontier trade-offs."
        ),
        "comparisons": {
            "nearest_neighbor": _score_row(
                baseline_scores["nearest_neighbor"], "validation"
            ),
            "two_opt": _score_row(baseline_scores["two_opt"], "validation"),
            "driver_aware": _score_row(baseline_scores["driver_aware"], "validation"),
            "ml_next_stop_ranker": _score_row(
                baseline_scores["ml_next_stop_ranker"], "validation"
            ),
            "llm_discovered": _score_row(top["validation_score"], "validation"),
            "llm_discovered_plus_local_search": _score_row(
                top["test_score"], "held_out_test"
            ),
        },
    }


def _external_bin_packing_summary(
    phase9: Mapping[str, object],
) -> Mapping[str, object]:
    return {
        "benchmark": phase9["benchmark"],
        "source": phase9["source"],
        "best_external_program_id": phase9["best_external_program_id"],
        "best_external_validation_score": phase9["best_external_validation_score"],
        "best_external_test_score": phase9["best_external_test_score"],
        "synthetic_top_program_id": phase9["synthetic_top_program_id"],
        "synthetic_top_external_test_score": (
            phase9["synthetic_top_external_test_score"]
        ),
        "synthetic_to_external_gap": phase9["synthetic_to_external_gap"],
        "external_generalization_gap": phase9["external_generalization_gap"],
        "external_test_baseline_scores": phase9["external_test_baseline_scores"],
        "claim_boundary": phase9["claim_boundary"],
        "summary": (
            "Phase 9 evaluates bin packing candidates on BPPLIB / "
            "OR-Library-style external fixtures with separate train, "
            "validation, and test splits, then compares synthetic-selected and "
            "external-selected programs against classical baselines."
        ),
    }


def _external_routing_summary(phase10: Mapping[str, object]) -> Mapping[str, object]:
    return {
        "benchmark": phase10["benchmark"],
        "source": phase10["source"],
        "best_external_program_id": phase10["best_external_program_id"],
        "best_external_validation_score": phase10["best_external_validation_score"],
        "best_external_test_score": phase10["best_external_test_score"],
        "synthetic_top_program_id": phase10["synthetic_top_program_id"],
        "synthetic_top_external_test_score": (
            phase10["synthetic_top_external_test_score"]
        ),
        "synthetic_to_external_gap": phase10["synthetic_to_external_gap"],
        "external_generalization_gap": phase10["external_generalization_gap"],
        "external_test_baseline_scores": phase10["external_test_baseline_scores"],
        "external_formats": phase10["external_formats"],
        "capacitated_instance_count": phase10["capacitated_instance_count"],
        "time_window_instance_count": phase10["time_window_instance_count"],
        "best_external_test_capacity_violation": phase10[
            "best_external_test_capacity_violation"
        ],
        "best_external_test_time_window_violation": phase10[
            "best_external_test_time_window_violation"
        ],
        "best_external_test_vehicle_count": phase10["best_external_test_vehicle_count"],
        "synthetic_top_external_capacity_violation": phase10[
            "synthetic_top_external_capacity_violation"
        ],
        "synthetic_top_external_time_window_violation": phase10[
            "synthetic_top_external_time_window_violation"
        ],
        "claim_boundary": phase10["claim_boundary"],
        "summary": (
            "Phase 10 evaluates `score_next_stop` routing candidates on "
            "TSPLIB-style EUC_2D and CVRPLIB-style capacitated external "
            "fixtures, including local time-window sections, with separate "
            "train, validation, and test splits. It reuses nearest-neighbor, "
            "cheapest-insertion, 2-opt, and candidate rerun machinery while "
            "keeping the claim boundary below LKH, CVRP/VRPTW solver, SOTA, or "
            "Amazon routing superiority."
        ),
    }


def _search_ablation_summary(phase11: Mapping[str, object]) -> Mapping[str, object]:
    return {
        "benchmark": phase11["benchmark"],
        "methods": phase11["methods"],
        "controls": phase11["controls"],
        "summary_rows": phase11["summary_rows"],
        "generation_curve_by_method": phase11["generation_curve_by_method"],
        "invalid_code_rate_by_method": phase11["invalid_code_rate_by_method"],
        "best_score_by_budget": phase11["best_score_by_budget"],
        "best_method": phase11["best_method"],
        "best_program_id": phase11["best_program_id"],
        "best_validation_score": phase11["best_validation_score"],
        "claim_boundary": phase11["claim_boundary"],
        "summary": (
            "Phase 11 compares seed-only, mutation, crossover, deterministic "
            "LLM-proxy, and repair operators under the same candidate budget, "
            "split, timeout, and random seed. This is a fixed local budget "
            "ablation, not evidence about live LLM behavior."
        ),
    }


def _live_llm_summary(phase12: Mapping[str, object]) -> Mapping[str, object]:
    return {
        "benchmark": phase12["benchmark"],
        "methods": phase12["methods"],
        "operator_comparison": phase12["operator_comparison"],
        "candidate_audit": phase12["candidate_audit"],
        "best_method": phase12["best_method"],
        "best_validation_score": phase12["best_validation_score"],
        "live_provider_configured": phase12["live_provider_configured"],
        "claim_boundary": phase12["claim_boundary"],
        "summary": (
            "Phase 12 turns Gemini/live LLM mutation into a controlled "
            "experiment path. Deterministic fallback and repair providers run "
            "by default; optional live Gemini runs are gated behind environment "
            "variables and every generated program is logged by hashes, then "
            "checked by static validation and sandboxed scoring. The framing is "
            "that LLM is one mutation operator inside a constrained "
            "program-search system."
        ),
    }


def _semantic_novelty_summary(phase13: Mapping[str, object]) -> Mapping[str, object]:
    return {
        "benchmark": phase13["benchmark"],
        "candidate_count": phase13["candidate_count"],
        "probe_count": phase13["probe_count"],
        "probe_schema": phase13["probe_schema"],
        "novelty_dimensions": phase13["novelty_dimensions"],
        "novelty_rows": phase13["novelty_rows"],
        "behavior_fingerprints": phase13["behavior_fingerprints"],
        "duplicate_behavior_clusters": phase13["duplicate_behavior_clusters"],
        "behavior_cluster_count": phase13["behavior_cluster_count"],
        "equivalent_program_count": phase13["equivalent_program_count"],
        "claim_boundary": phase13["claim_boundary"],
        "summary": (
            "Phase 13 adds probe-based behavior fingerprints for `score_bin` "
            "programs, then separates exact code novelty from behavior, "
            "feature, performance, and complexity evidence. It flags programs "
            "that look different in code but rank candidate bins identically "
            "on fixed probes."
        ),
    }


def _pareto_frontier_summary(phase15: Mapping[str, object]) -> Mapping[str, object]:
    return {
        "benchmarks": phase15["benchmarks"],
        "frontier_axes": phase15["frontier_axes"],
        "candidate_rows": phase15["candidate_rows"],
        "frontier_rows": phase15["frontier_rows"],
        "candidate_count": len(phase15["candidate_rows"]),
        "frontier_count": phase15["frontier_count"],
        "benchmark_summaries": phase15["benchmark_summaries"],
        "claim_boundary": phase15["claim_boundary"],
        "summary": (
            "Phase 15 reports nondominated quality-runtime-complexity-failure-"
            "generalization trade-offs per benchmark, with driver-likeness "
            "included for Amazon-style routing where that operational metric "
            "is available."
        ),
    }


def _failure_taxonomy_v2_summary(
    phase14: Mapping[str, object],
) -> Mapping[str, object]:
    return {
        "failure_categories": phase14["failure_categories"],
        "failure_cards": phase14["failure_cards"],
        "failure_card_count": phase14["failure_card_count"],
        "repair_success_rows": phase14["repair_success_rows"],
        "repair_strategy_count": phase14["repair_strategy_count"],
        "claim_boundary": phase14["claim_boundary"],
        "summary": (
            "Phase 14 upgrades failure analysis into cards with concrete "
            "example programs, trigger conditions, validator or evaluator "
            "sources, score impact, and possible repair strategies. Repair "
            "success rows remain deterministic evidence records."
        ),
    }


def _evidence_summary(
    phase6: Mapping[str, object],
    phase7: Mapping[str, object],
    phase8: Mapping[str, object],
) -> Mapping[str, object]:
    return {
        "phase_reports": (
            "phase2_bin_packing",
            "phase3_evolution",
            "phase4_simple_routing",
            "phase5_amazon_evaluator",
            "phase6_amazon_discovery",
            "phase7_robustness",
            "phase8_failure_analysis",
        ),
        "robustness": {
            "benchmark_count": phase7["benchmark_count"],
            "slice_count": len(phase7["slice_summary"]),
            "worst_gap_slice": phase7["worst_generalization_gaps"][0]["slice_name"],
        },
        "failure_analysis": {
            "failure_category_count": len(phase8["failure_categories"]),
            "top_rejected_count": len(phase8["top_rejected_programs"]),
            "top_surviving_count": len(phase8["top_surviving_programs"]),
        },
        "amazon_tradeoffs": {
            "tradeoff_count": len(phase6["tradeoff_programs"]),
            "frontier_improvement_count": len(phase6["frontier_improvements"]),
        },
    }


def _score_row(score: object, split: str) -> Mapping[str, object]:
    return {"score": score, "split": split}
