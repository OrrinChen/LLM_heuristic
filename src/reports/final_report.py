from __future__ import annotations

from typing import Dict, Mapping

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
)
from benchmarks.bin_packing.evaluator import build_phase2_report
from benchmarks.routing.evaluator import build_phase4_report
from reports.failure_analysis import build_phase8_report
from reports.robustness import build_phase7_report

FINAL_REPORT_SECTIONS = (
    "executive_summary",
    "system_architecture",
    "killer_experiment",
    "benchmark_results",
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
            "live_llm_status": "deferred",
        },
        "killer_experiment": {
            "benchmarks": {
                "bin_packing": _bin_packing_summary(phase2),
                "simple_routing": _simple_routing_summary(phase4),
                "amazon_routing": _amazon_routing_summary(phase6),
            },
        },
        "evidence": _evidence_summary(phase6, phase7, phase8),
        "limitations": (
            "Live LLM mutation remains deferred behind explicit provider and "
            "environment-variable configuration.",
            "Amazon routing data is represented by deterministic local "
            "Amazon-shaped fixtures until public or user-provided data is "
            "configured.",
            "Reports are structured dictionaries and markdown text; polished "
            "plots and notebook dashboards remain future packaging work.",
            "The current routing generated-program interface ranks next stops "
            "rather than emitting full routes.",
        ),
        "recommended_next_steps": (
            {
                "step": "optional_live_llm_integration",
                "reason": (
                    "Connect the existing mutation protocol to a provider only "
                    "after explicit approval and env-var configuration."
                ),
            },
            {
                "step": "report_tables_and_plots",
                "reason": (
                    "Turn structured report dictionaries into publication-ready "
                    "tables, curves, and frontier charts."
                ),
            },
            {
                "step": "external_benchmark_data",
                "reason": (
                    "Add public or user-provided Amazon-style routes without "
                    "committing raw proprietary data."
                ),
            },
        ),
    }
    return report


def render_final_report_markdown(report: Mapping[str, object]) -> str:
    project = report["project"]
    claims = report["claims"]
    killer = report["killer_experiment"]["benchmarks"]
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
            "validation, run in a restricted sandbox, enter OR evaluators, and "
            "feed archive, selection, robustness, and failure-analysis reports."
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
