from __future__ import annotations

from typing import Dict, Mapping, Optional

from reports.final_report import build_final_report

PORTFOLIO_README_REQUIRED_HEADINGS = (
    "## What It Does",
    "## Why It Matters",
    "## One-Command Demo",
    "## Core Architecture",
    "## Benchmark Results",
    "## Safety Boundary",
    "## Limitations",
)

PORTFOLIO_DEMO_COMMAND = (
    "PYTHONPATH=src python3 -m heuristic_discovery report --output-dir "
    "/tmp/o2-demo --top-k 3"
)

PRIMARY_RESUME_BULLET = (
    "Built a sandboxed LLM-driven OR heuristic discovery system that evolves "
    "compact bin-packing and routing scoring programs through "
    "subprocess-isolated execution, evolutionary selection, external benchmark "
    "evaluation, rerun manifests, robustness analysis, and failure taxonomy "
    "reporting."
)

BENCHMARK_RESUME_BULLET = (
    "Benchmarked discovered heuristics against First Fit, Best Fit, FFD/BFD, "
    "nearest-neighbor, insertion, and 2-opt baselines, reporting "
    "quality-runtime-generalization Pareto frontiers across synthetic and "
    "external benchmark-style instances."
)

ARCHITECTURE_DIAGRAM = """seed heuristic library
-> deterministic or LLM mutation operator
-> static validation
-> subprocess sandbox
-> OR benchmark evaluator
-> archive and rerun manifest
-> report artifacts and portfolio evidence"""


def build_phase19_package(
    *,
    final_report: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    final = final_report if final_report is not None else build_final_report()
    benchmarks = final["killer_experiment"]["benchmarks"]
    external = final["external_benchmark"]
    ablation = final["search_ablation"]
    frontier = final["pareto_frontier"]
    evidence = final["evidence"]

    benchmark_rows = (
        {
            "benchmark": "Online Bin Packing",
            "evidence": "held-out synthetic distributions",
            "top_program": benchmarks["bin_packing"]["top_program_id"],
            "reported_metric": benchmarks["bin_packing"]["test_score"],
            "claim": "compact score_bin heuristic under evaluator constraints",
        },
        {
            "benchmark": "External Bin Packing",
            "evidence": "BPPLIB / OR-Library-style local fixtures",
            "top_program": external["best_external_program_id"],
            "reported_metric": external["best_external_test_score"],
            "claim": "external transfer evidence without SOTA claim",
        },
        {
            "benchmark": "External Routing",
            "evidence": "TSPLIB-style local fixtures",
            "top_program": final["routing_external"]["best_external_program_id"],
            "reported_metric": final["routing_external"]["best_external_test_score"],
            "claim": "routing transfer evidence without LKH or CVRP claim",
        },
        {
            "benchmark": "Simple Routing",
            "evidence": "held-out route sizes with local-search comparison",
            "top_program": benchmarks["simple_routing"]["top_program_id"],
            "reported_metric": benchmarks["simple_routing"]["test_score"],
            "claim": "score_next_stop heuristic plus 2-opt comparison",
        },
        {
            "benchmark": "Amazon-Style Routing",
            "evidence": "deterministic Amazon-shaped route fixtures",
            "top_program": benchmarks["amazon_routing"]["top_program_id"],
            "reported_metric": benchmarks["amazon_routing"]["test_score"],
            "claim": "travel-time and driver-likeness frontier trade-off",
        },
        {
            "benchmark": "Search Ablation",
            "evidence": "fixed local candidate budget",
            "top_program": ablation["best_program_id"],
            "reported_metric": ablation["best_validation_score"],
            "claim": "operator comparison without live LLM superiority claim",
        },
        {
            "benchmark": "Pareto Frontier",
            "evidence": "quality-runtime-complexity-generalization rows",
            "top_program": f"{frontier['frontier_count']} frontier rows",
            "reported_metric": frontier["candidate_count"],
            "claim": "selected trade-offs, not universal dominance",
        },
    )

    return {
        "phase": 19,
        "title": "O2 Portfolio Packaging",
        "resume_bullets": (PRIMARY_RESUME_BULLET, BENCHMARK_RESUME_BULLET),
        "demo_command": PORTFOLIO_DEMO_COMMAND,
        "architecture_diagram": ARCHITECTURE_DIAGRAM,
        "benchmark_results": benchmark_rows,
        "safety_boundary": (
            "Generated programs are limited to narrow scoring functions. "
            "Static checks reject imports, file access, network/process names, "
            "dangerous builtins, disallowed globals, and dunder access before "
            "subprocess sandbox execution with wall-clock timeout handling."
        ),
        "limitations": (
            "Live LLM mutation is optional and requires environment variables.",
            "External bin packing fixtures are small and committed only as "
            "parser-backed benchmark-style examples.",
            "External routing fixtures are small TSPLIB-style examples, not "
            "large TSPLIB benchmark corpora.",
            "Amazon-style routing uses deterministic local fixtures, not "
            "proprietary or public Amazon route data.",
            "The project reports selected trade-offs and does not claim "
            "universal dominance or SOTA solver performance.",
        ),
        "claim_boundaries": {
            "supports": final["claims"]["conservative"],
            "does_not_claim": (
                "universal dominance, SOTA solver performance, or live LLM superiority"
            ),
        },
        "evidence_snapshot": {
            "benchmarks": len(benchmarks),
            "robustness_slices": evidence["robustness"]["slice_count"],
            "failure_categories": evidence["failure_analysis"][
                "failure_category_count"
            ],
            "pareto_frontier_rows": frontier["frontier_count"],
        },
        "recommended_next_phase": "Optional Phase 12: Live LLM Mutation v1",
    }


def render_portfolio_brief_markdown(package: Mapping[str, object]) -> str:
    lines = [
        "# O2 Portfolio Brief",
        "",
        "## Resume Bullets",
        "",
    ]
    for bullet in package["resume_bullets"]:
        lines.append(f"- {bullet}")
    lines.extend(
        [
            "",
            "## Interview Demo",
            "",
            "```bash",
            str(package["demo_command"]),
            "```",
            "",
            "## Core Architecture",
            "",
            "```text",
            str(package["architecture_diagram"]),
            "```",
            "",
            "## Benchmark Evidence",
            "",
            "| benchmark | evidence | top_program | reported_metric | claim |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in package["benchmark_results"]:
        lines.append(
            "| "
            + " | ".join(
                str(row[column])
                for column in (
                    "benchmark",
                    "evidence",
                    "top_program",
                    "reported_metric",
                    "claim",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            str(package["safety_boundary"]),
            "",
            "## Conservative Claim",
            "",
            f"Supported: {package['claim_boundaries']['supports']}",
            "",
            f"Does not claim: {package['claim_boundaries']['does_not_claim']}.",
            "",
            "## Limitations",
            "",
        ]
    )
    for limitation in package["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(
        [
            "",
            "## Recommended Next Phase",
            "",
            str(package["recommended_next_phase"]),
            "",
        ]
    )
    return "\n".join(lines)
