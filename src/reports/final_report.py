from __future__ import annotations

from typing import Dict, Mapping

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
)
from benchmarks.bin_packing.evaluator import build_phase2_report
from benchmarks.bin_packing.external import build_phase9_report
from benchmarks.routing.evaluator import build_phase4_report
from program_search.ablation import build_phase11_report
from reports.failure_analysis import build_phase8_report
from reports.robustness import build_phase7_report

FINAL_REPORT_SECTIONS = (
    "executive_summary",
    "system_architecture",
    "killer_experiment",
    "benchmark_results",
    "external_benchmark_evidence",
    "search_mechanism_ablation",
    "generalization_and_robustness",
    "failure_analysis",
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
    phase11 = build_phase11_report(
        candidate_budget=32,
        generations=3,
        item_count=20,
        random_seed=23,
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
        "search_ablation": _search_ablation_summary(phase11),
        "evidence": _evidence_summary(phase6, phase7, phase8),
        "limitations": (
            "Live LLM mutation is optional and remains gated behind "
            "environment-variable configuration.",
            "External bin packing evidence uses parser-backed, small "
            "benchmark-style local fixtures by default; large public benchmark "
            "files are intentionally not committed.",
            "Amazon routing data is represented by deterministic local "
            "Amazon-shaped fixtures until public or user-provided data is "
            "configured.",
            "Rendered report artifacts are deterministic local files; PNG plot "
            "rendering remains optional when matplotlib is available.",
            "The current routing generated-program interface ranks next stops "
            "rather than emitting full routes.",
            "Subprocess memory limits are applied only on platforms that expose "
            "compatible resource limits.",
        ),
        "recommended_next_steps": (
            {
                "step": "pareto_frontier_report",
                "reason": (
                    "Report objective-quality, runtime, complexity, failure, "
                    "and generalization trade-offs instead of a single winner."
                ),
            },
            {
                "step": "research_style_report",
                "reason": (
                    "Package the system design, sandbox boundary, external "
                    "evidence, ablation, limitations, and conclusions."
                ),
            },
            {
                "step": "resume_portfolio_packaging",
                "reason": (
                    "Turn the evidence package into a concise README-first "
                    "portfolio narrative and interview-ready demo."
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
    ablation = report["search_ablation"]
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
