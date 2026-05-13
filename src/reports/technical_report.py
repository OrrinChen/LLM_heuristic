from __future__ import annotations

from typing import Dict, Mapping, Optional, Sequence

from reports.final_report import build_final_report

TECHNICAL_REPORT_TITLE = "Sandboxed LLM Program Search for OR Heuristic Discovery"

TECHNICAL_REPORT_SECTIONS = (
    "problem",
    "why_heuristic_discovery_matters",
    "system_design",
    "sandbox_and_safety_boundary",
    "benchmarks",
    "trading_signal_rule_search",
    "search_loop",
    "external_benchmark_evidence",
    "ablation",
    "llm_as_operator",
    "program_semantics_and_novelty",
    "generalization",
    "failure_analysis",
    "failure_taxonomy_v2",
    "limitations",
    "conclusion",
)

TECHNICAL_REPORT_ABSTRACT = (
    "This project studies whether compact heuristic scoring programs can be "
    "discovered through constrained program search. The system uses LLM or "
    "deterministic mutation operators, static validation, subprocess sandboxing, "
    "benchmark evaluators, evolutionary selection, rerun manifests, and "
    "held-out generalization tests. Results show that generated heuristics can "
    "improve selected trade-offs on bin packing and routing-style benchmarks. "
    "The same constrained interface is extended to PIT trading-rule search "
    "without claiming tradable alpha, while failure analysis shows clear limits "
    "under external transfer and strong classical baselines."
)


def build_phase18_report(
    *,
    final_report: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    source = final_report if final_report is not None else build_final_report()
    benchmarks = source["killer_experiment"]["benchmarks"]
    evidence = source["evidence"]
    external = source["external_benchmark"]
    routing_external = source["routing_external"]
    ablation = source["search_ablation"]
    live_llm = source["live_llm"]
    semantic = source["semantic_novelty"]
    frontier = source["pareto_frontier"]
    trading_signal = source["trading_signal"]
    failure_v2 = source["failure_taxonomy_v2"]

    sections = (
        _section(
            "problem",
            "Problem",
            (
                "Operations research heuristics are often hand-designed for a "
                "specific objective, benchmark family, or operational setting. "
                "O2 frames heuristic design as constrained program search over "
                "small scoring functions rather than full solver generation."
            ),
            ("project_thesis", "generated_scoring_function_contract"),
        ),
        _section(
            "why_heuristic_discovery_matters",
            "Why Heuristic Discovery Matters",
            (
                "Compact scoring heuristics are inspectable, cheap to rerun, "
                "and easier to audit than opaque end-to-end solvers. This makes "
                "them useful for studying quality-runtime-generalization "
                "trade-offs under explicit evaluator constraints."
            ),
            ("pareto_frontier.csv", "failure_taxonomy.csv"),
        ),
        _section(
            "system_design",
            "System Design",
            (
                "The system connects seed programs, mutation operators, static "
                "validation, sandbox execution, benchmark evaluators, archive "
                "selection, rerun manifests, and report artifact export. "
                "Generated code only implements narrow scoring functions."
            ),
            ("architecture", "rerun_manifest.json", "top_programs"),
        ),
        _section(
            "sandbox_and_safety_boundary",
            "Sandbox and Safety Boundary",
            (
                "Generated functions are statically checked before execution "
                "and can run inside subprocess isolation with wall-clock "
                "timeouts and optional platform memory limits. File access, "
                "network access, imports, dangerous calls, and hidden labels "
                "remain outside the candidate interface."
            ),
            ("tests/test_program_sandbox.py", "tests/test_hardening_milestone.py"),
        ),
        _section(
            "benchmarks",
            "Benchmarks",
            (
                "Evidence covers online bin packing, simple routing, "
                "Amazon-style routing fixtures, and parser-backed external "
                "bin-packing and TSPLIB-style routing benchmark-style "
                "instances. The trading signal extension adds a separate "
                "PIT-constrained scoring benchmark. OR benchmarks are compared "
                "against deterministic classical baselines."
            ),
            (
                "bin_packing",
                "simple_routing",
                "amazon_routing",
                "external_bin_packing",
                "external_routing",
                "trading_signal",
            ),
        ),
        _section(
            "trading_signal_rule_search",
            "Trading Signal Rule Search",
            (
                "The trading extension keeps the generated-code interface "
                "narrow: `score_signal(features)` returns a finite target "
                "position in [-1, 1]. Static checks block future returns, "
                "labels, future midprices, post-trade PnL, and hallucinated "
                "features, while evaluator gates track leverage, turnover, "
                "drawdown, net return, and program complexity."
            ),
            (
                "trading_signal_summary.csv",
                "trading_signal_pareto.csv",
                "trading_signal_frontier.json",
                trading_signal["benchmark"],
            ),
        ),
        _section(
            "search_loop",
            "Search Loop",
            (
                "Evolutionary selection evaluates generated candidates under "
                "fixed interfaces, records lineage, filters exact duplicate "
                "programs, and keeps elite candidates for held-out evaluation."
            ),
            ("generation_curve_by_method.json", "artifacts/rerun_manifest.json"),
        ),
        _section(
            "external_benchmark_evidence",
            "External Benchmark Evidence",
            (
                "External evidence uses BPPLIB / OR-Library-style bin packing "
                "fixtures and TSPLIB-style routing fixtures with train, "
                "validation, and test splits. The report compares "
                "synthetic-selected and external-selected programs without "
                "claiming SOTA, LKH, CVRP, or universal transfer."
            ),
            (
                "external_generalization.csv",
                "routing_external_generalization.csv",
                external["benchmark"],
                routing_external["benchmark"],
            ),
        ),
        _section(
            "ablation",
            "Ablation",
            (
                "The ablation fixes candidate budget, benchmark split, timeout, "
                "evaluation budget, and seeds while comparing seed-only, random "
                "mutation, deterministic templates, crossover, LLM-proxy "
                "mutation, and repair-style operators."
            ),
            ("ablation_summary.csv", "generation_curve_by_method.json"),
        ),
        _section(
            "llm_as_operator",
            "LLM As Operator",
            (
                "Phase 12 treats live Gemini as one mutation operator inside "
                "the constrained search loop. Candidate audit rows record "
                "model, prompt version, temperature, parent ids, response "
                "hashes, static-check outcome, sandbox outcome, score, tokens, "
                "latency, and cost proxy without storing raw responses or "
                "secrets."
            ),
            ("llm_operator_comparison.csv", "llm_candidate_audit.csv"),
        ),
        _section(
            "program_semantics_and_novelty",
            "Program Semantics And Novelty",
            (
                "Phase 13 adds probe-based behavior fingerprints for "
                "`score_bin` candidates, separates exact code novelty from "
                "behavior, feature, and performance novelty, and reports "
                "duplicate behavior clusters where different programs rank "
                "candidate actions identically."
            ),
            (
                "novelty_table.csv",
                "behavior_fingerprint.json",
                "duplicate_behavior_clusters.csv",
            ),
        ),
        _section(
            "generalization",
            "Generalization",
            (
                "Generalization evidence combines held-out benchmark slices, "
                "external bin-packing transfer gaps, and Pareto frontier rows "
                "that expose quality, runtime, complexity, failure, and "
                "generalization trade-offs."
            ),
            (
                "robustness_summary.csv",
                "worst_generalization_gaps.csv",
                "pareto_frontier.csv",
            ),
        ),
        _section(
            "failure_analysis",
            "Failure Analysis",
            (
                "Failure analysis reports invalid code, unsafe code, timeout, "
                "overfitting, poor transfer, complexity, feasibility boundary, "
                "and routing trade-off patterns instead of hiding rejected or "
                "weak candidates."
            ),
            ("failure_taxonomy.csv", "failure_taxonomy_v2.csv"),
        ),
        _section(
            "failure_taxonomy_v2",
            "Failure Taxonomy v2",
            (
                "Phase 14 converts failure categories into auditable cards. "
                "Each card records an example program, trigger condition, "
                "validator or evaluator source, score impact, and possible "
                "repair strategy, plus deterministic repair success rows where "
                "repair was attempted."
            ),
            (
                "failure_cards.md",
                "failure_taxonomy_v2.csv",
                "repair_success_rate.csv",
            ),
        ),
        _section(
            "limitations",
            "Limitations",
            (
                "The evidence package is deterministic and local by default. "
                "Live Gemini mutation remains environment-gated, external "
                "fixtures are intentionally small, broader crossover remains "
                "optional, and runtime frontier values use a deterministic "
                "proxy."
            ),
            ("README.md", "TASK_MEMORY.md", "ROADMAP.md"),
        ),
        _section(
            "conclusion",
            "Conclusion",
            (
                "O2 supports a conservative claim: constrained program search "
                "can discover compact heuristics that improve selected "
                "trade-offs under strict evaluator and sandbox constraints. It "
                "does not establish universal dominance over classical OR "
                "baselines."
            ),
            ("final_report.md", "technical_report.md"),
        ),
    )

    return {
        "phase": 18,
        "title": TECHNICAL_REPORT_TITLE,
        "abstract": TECHNICAL_REPORT_ABSTRACT,
        "sections": sections,
        "claim_boundaries": {
            "supports": source["claims"]["conservative"],
            "does_not_claim": source["claims"]["does_not_claim"],
            "live_llm_status": source["claims"]["live_llm_status"],
        },
        "evidence_snapshot": {
            "benchmark_count": len(benchmarks),
            "robustness_slice_count": evidence["robustness"]["slice_count"],
            "failure_category_count": (
                evidence["failure_analysis"]["failure_category_count"]
            ),
            "external_benchmark": external["benchmark"],
            "ablation_best_method": ablation["best_method"],
            "live_llm_best_method": live_llm["best_method"],
            "semantic_behavior_clusters": semantic["behavior_cluster_count"],
            "pareto_frontier_count": frontier["frontier_count"],
            "trading_signal_frontier_count": trading_signal["pareto_frontier_count"],
            "failure_card_count": failure_v2["failure_card_count"],
        },
        "recommended_next_phase": (
            "No required phase remains; project is release-frozen and "
            "portfolio-ready. Optional future work: broader crossover, paid "
            "cloud execution, or larger public benchmark corpora."
        ),
    }


def render_technical_report_markdown(report: Mapping[str, object]) -> str:
    lines = [
        f"# {report['title']}",
        "",
        "## Abstract",
        "",
        str(report["abstract"]),
        "",
        "## Claim Boundary",
        "",
        f"Supported claim: {report['claim_boundaries']['supports']}",
        "",
        (
            "The system does not claim universal dominance: "
            f"{report['claim_boundaries']['does_not_claim']}"
        ),
        "",
    ]
    for section in report["sections"]:
        lines.extend(
            [
                f"## {section['title']}",
                "",
                str(section["body"]),
                "",
                "Evidence references: "
                + ", ".join(f"`{item}`" for item in section["evidence_refs"])
                + ".",
                "",
            ]
        )
    snapshot = report["evidence_snapshot"]
    lines.extend(
        [
            "## Evidence Snapshot",
            "",
            f"- Benchmarks summarized: `{snapshot['benchmark_count']}`.",
            f"- Robustness slices: `{snapshot['robustness_slice_count']}`.",
            f"- Failure categories: `{snapshot['failure_category_count']}`.",
            f"- External benchmark: `{snapshot['external_benchmark']}`.",
            f"- Ablation best method: `{snapshot['ablation_best_method']}`.",
            f"- Pareto frontier rows: `{snapshot['pareto_frontier_count']}`.",
            f"- Failure cards: `{snapshot['failure_card_count']}`.",
            "",
            "## Next Phase",
            "",
            str(report["recommended_next_phase"]),
            "",
        ]
    )
    return "\n".join(lines)


def _section(
    section_id: str,
    title: str,
    body: str,
    evidence_refs: Sequence[object],
) -> Dict[str, object]:
    return {
        "id": section_id,
        "title": title,
        "body": body,
        "evidence_refs": tuple(str(item) for item in evidence_refs),
    }
