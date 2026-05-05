from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from program_search.parallel_runner import build_phase17_report
from reports.failure_analysis import build_phase8_report
from reports.failure_taxonomy_v2 import build_phase14_report
from reports.final_report import build_final_report
from reports.robustness import build_phase7_report

TableRows = List[Mapping[str, object]]


def build_report_tables(
    *,
    final_report: Optional[Mapping[str, object]] = None,
    robustness_report: Optional[Mapping[str, object]] = None,
    failure_report: Optional[Mapping[str, object]] = None,
    phase14_report: Optional[Mapping[str, object]] = None,
    phase17_report: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    final = final_report or build_final_report()
    robustness = robustness_report or build_phase7_report()
    failures = failure_report or build_phase8_report()
    phase14 = (
        phase14_report or final.get("failure_taxonomy_v2") or build_phase14_report()
    )
    phase17 = phase17_report or build_phase17_report()

    tables = {
        "benchmark_comparison": {
            "title": "Benchmark Comparison",
            "columns": (
                "benchmark",
                "method",
                "split",
                "score",
                "top_program_id",
            ),
            "rows": _benchmark_rows(final),
        },
        "robustness_summary": {
            "title": "Robustness Summary",
            "columns": (
                "benchmark",
                "program_id",
                "validation_score",
                "test_score",
                "generalization_gap",
                "failure_rate",
                "program_complexity",
            ),
            "rows": _robustness_rows(robustness),
        },
        "worst_generalization_gaps": {
            "title": "Worst Generalization Gaps",
            "columns": (
                "rank",
                "slice_name",
                "benchmark",
                "dimension",
                "score",
                "generalization_gap",
            ),
            "rows": _worst_gap_rows(robustness),
        },
        "external_generalization": {
            "title": "External Generalization",
            "columns": (
                "benchmark",
                "selection_source",
                "program_id",
                "validation_score",
                "external_test_score",
                "synthetic_to_external_gap",
                "baseline_reference",
                "claim",
            ),
            "rows": _external_generalization_rows(final),
        },
        "routing_external_generalization": {
            "title": "Routing External Generalization",
            "columns": (
                "benchmark",
                "selection_source",
                "program_id",
                "validation_score",
                "external_test_score",
                "synthetic_to_external_gap",
                "capacity_violation",
                "time_window_violation",
                "vehicle_count",
                "baseline_reference",
                "claim",
            ),
            "rows": _routing_external_generalization_rows(final),
        },
        "ablation_summary": {
            "title": "Ablation Summary",
            "columns": (
                "method",
                "evaluated_candidates",
                "best_validation_score",
                "best_test_score",
                "failure_rate",
                "invalid_code_rate",
                "operator_source",
                "live_llm_required",
            ),
            "rows": _ablation_summary_rows(final),
        },
        "invalid_code_rate_by_method": {
            "title": "Invalid Code Rate By Method",
            "columns": (
                "method",
                "invalid_code_rate",
                "evaluated_candidates",
                "operator_source",
            ),
            "rows": _invalid_code_rate_rows(final),
        },
        "best_score_by_budget": {
            "title": "Best Score By Budget",
            "columns": (
                "method",
                "candidate_budget",
                "best_validation_score",
                "best_test_score",
                "best_program_id",
            ),
            "rows": _best_score_by_budget_rows(final),
        },
        "llm_operator_comparison": {
            "title": "LLM Operator Comparison",
            "columns": (
                "method",
                "provider_status",
                "model_name",
                "evaluated_candidates",
                "best_validation_score",
                "invalid_code_rate",
                "average_latency_seconds",
                "total_tokens",
                "estimated_cost_usd",
                "live_llm_required",
            ),
            "rows": _llm_operator_rows(final),
        },
        "llm_candidate_audit": {
            "title": "LLM Candidate Audit",
            "columns": (
                "candidate_id",
                "method",
                "model_name",
                "prompt_version",
                "temperature",
                "parent_ids",
                "raw_response_hash",
                "cleaned_code_hash",
                "static_check_result",
                "sandbox_result",
                "score",
                "test_score",
                "failure_reason",
                "runtime_seconds",
                "latency_seconds",
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "estimated_cost_usd",
                "repair_of_failure_reason",
            ),
            "rows": _llm_candidate_audit_rows(final),
        },
        "novelty_table": {
            "title": "Novelty Table",
            "columns": (
                "program_id",
                "source",
                "generation",
                "code_hash",
                "behavior_hash",
                "code_novelty",
                "behavior_novelty",
                "feature_novelty",
                "performance_novelty",
                "semantic_novelty_score",
                "feature_usage",
                "complexity_nodes",
                "complexity_branches",
                "complexity_operations",
                "complexity_literals",
                "validation_score",
                "test_score",
                "failure_reason",
            ),
            "rows": _novelty_rows(final),
        },
        "duplicate_behavior_clusters": {
            "title": "Duplicate Behavior Clusters",
            "columns": (
                "behavior_hash",
                "cluster_size",
                "program_ids",
                "representative_program_id",
                "shared_ranking",
                "explanation",
            ),
            "rows": _duplicate_behavior_cluster_rows(final),
        },
        "pareto_frontier": {
            "title": "Pareto Frontier",
            "columns": (
                "benchmark",
                "program_id",
                "source",
                "objective_quality",
                "runtime",
                "program_complexity",
                "failure_rate",
                "generalization_gap",
                "driver_likeness_or_realism",
                "operational_penalty",
                "is_pareto_frontier",
                "dominance_count",
                "selected_tradeoff",
            ),
            "rows": _pareto_frontier_rows(final),
        },
        "failure_taxonomy": {
            "title": "Failure Taxonomy",
            "columns": (
                "category",
                "count",
                "evidence_count",
            ),
            "rows": _failure_taxonomy_rows(failures),
        },
        "failure_taxonomy_v2": {
            "title": "Failure Taxonomy v2",
            "columns": (
                "category",
                "display_name",
                "example_program_id",
                "trigger_condition",
                "detected_by",
                "score_impact",
                "repair_strategy",
            ),
            "rows": _failure_taxonomy_v2_rows(phase14),
        },
        "repair_success_rate": {
            "title": "Repair Success Rate",
            "columns": (
                "category",
                "attempted_repairs",
                "successful_repairs",
                "repair_success_rate",
                "repair_provider",
                "repair_strategy",
                "repaired_example_id",
            ),
            "rows": _repair_success_rows(phase14),
        },
        "parallel_runner_summary": {
            "title": "Parallel Runner Summary",
            "columns": ("metric", "value", "claim"),
            "rows": _parallel_runner_rows(phase17),
        },
        "checkpoint_resume": {
            "title": "Checkpoint Resume",
            "columns": ("evidence", "value", "claim"),
            "rows": _checkpoint_resume_rows(phase17),
        },
        "recommended_next_steps": {
            "title": "Recommended Next Steps",
            "columns": ("step", "reason"),
            "rows": _next_step_rows(final),
        },
    }
    return {
        "phase": "report_tables",
        "tables": tuple(tables),
        **tables,
    }


def render_report_tables_markdown(tables: Mapping[str, object]) -> str:
    lines = ["# Report Tables", ""]
    for table_name in tables["tables"]:
        table = tables[str(table_name)]
        lines.extend(
            [
                f"## {table['title']}",
                "",
                render_markdown_table(table["rows"], table["columns"]),
                "",
            ]
        )
    return "\n".join(lines)


def render_markdown_table(
    rows: Sequence[Mapping[str, object]],
    columns: Sequence[str],
) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| "
        + " | ".join(_markdown_cell(row.get(column, "")) for column in columns)
        + " |"
        for row in rows
    ]
    return "\n".join([header, divider] + body)


def _benchmark_rows(final_report: Mapping[str, object]) -> TableRows:
    rows: TableRows = []
    benchmarks = final_report["killer_experiment"]["benchmarks"]
    for benchmark in benchmarks.values():
        for method, comparison in benchmark["comparisons"].items():
            rows.append(
                {
                    "benchmark": benchmark["label"],
                    "method": method,
                    "split": comparison["split"],
                    "score": _format_number(comparison["score"]),
                    "top_program_id": benchmark["top_program_id"],
                }
            )
    return rows


def _robustness_rows(robustness_report: Mapping[str, object]) -> TableRows:
    rows: TableRows = []
    for benchmark, summary in robustness_report["benchmarks"].items():
        rows.append(
            {
                "benchmark": benchmark,
                "program_id": summary["program_id"],
                "validation_score": _format_number(summary["validation_score"]),
                "test_score": _format_number(summary["test_score"]),
                "generalization_gap": _format_number(summary["generalization_gap"]),
                "failure_rate": _format_number(summary["failure_rate"]),
                "program_complexity": summary["program_complexity"],
            }
        )
    return rows


def _worst_gap_rows(robustness_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "rank": index + 1,
            "slice_name": row["slice_name"],
            "benchmark": row["benchmark"],
            "dimension": row["dimension"],
            "score": _format_number(row["test_score"]),
            "generalization_gap": _format_number(row["generalization_gap"]),
        }
        for index, row in enumerate(robustness_report["worst_generalization_gaps"][:5])
    ]


def _external_generalization_rows(final_report: Mapping[str, object]) -> TableRows:
    external = final_report["external_benchmark"]
    baselines = external["external_test_baseline_scores"]
    claim = external["claim_boundary"]
    rows: TableRows = [
        {
            "benchmark": external["benchmark"],
            "selection_source": "external_validation",
            "program_id": external["best_external_program_id"],
            "validation_score": _format_number(
                external["best_external_validation_score"]
            ),
            "external_test_score": _format_number(external["best_external_test_score"]),
            "synthetic_to_external_gap": _format_number(
                external["external_generalization_gap"]
            ),
            "baseline_reference": "",
            "claim": claim,
        },
        {
            "benchmark": external["benchmark"],
            "selection_source": "synthetic_validation",
            "program_id": external["synthetic_top_program_id"],
            "validation_score": "",
            "external_test_score": _format_number(
                external["synthetic_top_external_test_score"]
            ),
            "synthetic_to_external_gap": _format_number(
                external["synthetic_to_external_gap"]
            ),
            "baseline_reference": "",
            "claim": claim,
        },
    ]
    for name in ("first_fit", "best_fit", "best_fit_decreasing"):
        rows.append(
            {
                "benchmark": external["benchmark"],
                "selection_source": "external_test_baseline",
                "program_id": "",
                "validation_score": "",
                "external_test_score": _format_number(baselines[name]),
                "synthetic_to_external_gap": "",
                "baseline_reference": name,
                "claim": claim,
            }
        )
    return rows


def _routing_external_generalization_rows(
    final_report: Mapping[str, object],
) -> TableRows:
    external = final_report["routing_external"]
    baselines = external["external_test_baseline_scores"]
    claim = external["claim_boundary"]
    rows: TableRows = [
        {
            "benchmark": external["benchmark"],
            "selection_source": "external_validation",
            "program_id": external["best_external_program_id"],
            "validation_score": _format_number(
                external["best_external_validation_score"]
            ),
            "external_test_score": _format_number(external["best_external_test_score"]),
            "synthetic_to_external_gap": _format_number(
                external["external_generalization_gap"]
            ),
            "capacity_violation": _format_number(
                external["best_external_test_capacity_violation"]
            ),
            "time_window_violation": _format_number(
                external["best_external_test_time_window_violation"]
            ),
            "vehicle_count": _format_number(
                external["best_external_test_vehicle_count"]
            ),
            "baseline_reference": "",
            "claim": claim,
        },
        {
            "benchmark": external["benchmark"],
            "selection_source": "synthetic_validation",
            "program_id": external["synthetic_top_program_id"],
            "validation_score": "",
            "external_test_score": _format_number(
                external["synthetic_top_external_test_score"]
            ),
            "synthetic_to_external_gap": _format_number(
                external["synthetic_to_external_gap"]
            ),
            "capacity_violation": _format_number(
                external["synthetic_top_external_capacity_violation"]
            ),
            "time_window_violation": _format_number(
                external["synthetic_top_external_time_window_violation"]
            ),
            "vehicle_count": "",
            "baseline_reference": "",
            "claim": claim,
        },
    ]
    for name in ("nearest_neighbor", "cheapest_insertion", "two_opt"):
        rows.append(
            {
                "benchmark": external["benchmark"],
                "selection_source": "external_test_baseline",
                "program_id": "",
                "validation_score": "",
                "external_test_score": _format_number(baselines[name]),
                "synthetic_to_external_gap": "",
                "capacity_violation": "",
                "time_window_violation": "",
                "vehicle_count": "",
                "baseline_reference": name,
                "claim": claim,
            }
        )
    return rows


def _ablation_summary_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "method": row["method"],
            "evaluated_candidates": row["evaluated_candidates"],
            "best_validation_score": _format_number(row["best_validation_score"]),
            "best_test_score": _format_number(row["best_test_score"]),
            "failure_rate": _format_number(row["failure_rate"]),
            "invalid_code_rate": _format_number(row["invalid_code_rate"]),
            "operator_source": row["operator_source"],
            "live_llm_required": row["live_llm_required"],
        }
        for row in final_report["search_ablation"]["summary_rows"]
    ]


def _invalid_code_rate_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "method": row["method"],
            "invalid_code_rate": _format_number(row["invalid_code_rate"]),
            "evaluated_candidates": row["evaluated_candidates"],
            "operator_source": row["operator_source"],
        }
        for row in final_report["search_ablation"]["invalid_code_rate_by_method"]
    ]


def _best_score_by_budget_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "method": row["method"],
            "candidate_budget": row["candidate_budget"],
            "best_validation_score": _format_number(row["best_validation_score"]),
            "best_test_score": _format_number(row["best_test_score"]),
            "best_program_id": row["best_program_id"],
        }
        for row in final_report["search_ablation"]["best_score_by_budget"]
    ]


def _llm_operator_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "method": row["method"],
            "provider_status": row["provider_status"],
            "model_name": row["model_name"],
            "evaluated_candidates": row["evaluated_candidates"],
            "best_validation_score": _format_number(row["best_validation_score"]),
            "invalid_code_rate": _format_number(row["invalid_code_rate"]),
            "average_latency_seconds": _format_number(row["average_latency_seconds"]),
            "total_tokens": row["total_tokens"],
            "estimated_cost_usd": _format_number(row["estimated_cost_usd"]),
            "live_llm_required": row["live_llm_required"],
        }
        for row in final_report["live_llm"]["operator_comparison"]
    ]


def _llm_candidate_audit_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "candidate_id": row["candidate_id"],
            "method": row["method"],
            "model_name": row["model_name"],
            "prompt_version": row["prompt_version"],
            "temperature": _format_number(row["temperature"]),
            "parent_ids": ";".join(str(parent) for parent in row["parent_ids"]),
            "raw_response_hash": row["raw_response_hash"],
            "cleaned_code_hash": row["cleaned_code_hash"],
            "static_check_result": row["static_check_result"],
            "sandbox_result": row["sandbox_result"],
            "score": _format_number(row["score"]),
            "test_score": _format_number(row["test_score"]),
            "failure_reason": row["failure_reason"] or "",
            "runtime_seconds": _format_number(row["runtime_seconds"]),
            "latency_seconds": _format_number(row["latency_seconds"]),
            "input_tokens": row["input_tokens"],
            "output_tokens": row["output_tokens"],
            "total_tokens": row["total_tokens"],
            "estimated_cost_usd": _format_number(row["estimated_cost_usd"]),
            "repair_of_failure_reason": row["repair_of_failure_reason"],
        }
        for row in final_report["live_llm"]["candidate_audit"]
    ]


def _novelty_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "program_id": row["program_id"],
            "source": row["source"],
            "generation": row["generation"],
            "code_hash": row["code_hash"],
            "behavior_hash": row["behavior_hash"],
            "code_novelty": _format_number(row["code_novelty"]),
            "behavior_novelty": _format_number(row["behavior_novelty"]),
            "feature_novelty": _format_number(row["feature_novelty"]),
            "performance_novelty": _format_number(row["performance_novelty"]),
            "semantic_novelty_score": _format_number(row["semantic_novelty_score"]),
            "feature_usage": ";".join(str(feature) for feature in row["feature_usage"]),
            "complexity_nodes": row["complexity_nodes"],
            "complexity_branches": row["complexity_branches"],
            "complexity_operations": row["complexity_operations"],
            "complexity_literals": row["complexity_literals"],
            "validation_score": _format_number(row["validation_score"]),
            "test_score": _format_number(row["test_score"]),
            "failure_reason": row["failure_reason"] or "",
        }
        for row in final_report["semantic_novelty"]["novelty_rows"]
    ]


def _duplicate_behavior_cluster_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "behavior_hash": row["behavior_hash"],
            "cluster_size": row["cluster_size"],
            "program_ids": ";".join(
                str(program_id) for program_id in row["program_ids"]
            ),
            "representative_program_id": row["representative_program_id"],
            "shared_ranking": row["shared_ranking"],
            "explanation": row["explanation"],
        }
        for row in final_report["semantic_novelty"]["duplicate_behavior_clusters"]
    ]


def _pareto_frontier_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "benchmark": row["benchmark"],
            "program_id": row["program_id"],
            "source": row["source"],
            "objective_quality": _format_number(row["objective_quality"]),
            "runtime": _format_number(row["runtime"]),
            "program_complexity": row["program_complexity"],
            "failure_rate": _format_number(row["failure_rate"]),
            "generalization_gap": _format_number(row["generalization_gap"]),
            "driver_likeness_or_realism": _format_number(
                row["driver_likeness_or_realism"]
            ),
            "operational_penalty": _format_number(row["operational_penalty"]),
            "is_pareto_frontier": row["is_pareto_frontier"],
            "dominance_count": row["dominance_count"],
            "selected_tradeoff": row["selected_tradeoff"],
        }
        for row in final_report["pareto_frontier"]["candidate_rows"]
    ]


def _failure_taxonomy_rows(failure_report: Mapping[str, object]) -> TableRows:
    taxonomy = failure_report["failure_taxonomy"]
    return [
        {
            "category": category,
            "count": row["count"],
            "evidence_count": len(row["evidence"]),
        }
        for category, row in taxonomy.items()
    ]


def _failure_taxonomy_v2_rows(phase14_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "category": card["category"],
            "display_name": card["display_name"],
            "example_program_id": card["example_program"]["program_id"],
            "trigger_condition": card["trigger_condition"],
            "detected_by": card["detected_by"],
            "score_impact": card["score_impact"]["claim"],
            "repair_strategy": card["repair_strategy"]["strategy"],
        }
        for card in phase14_report["failure_cards"]
    ]


def _repair_success_rows(phase14_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "category": row["category"],
            "attempted_repairs": row["attempted_repairs"],
            "successful_repairs": row["successful_repairs"],
            "repair_success_rate": _format_number(row["repair_success_rate"]),
            "repair_provider": row["repair_provider"],
            "repair_strategy": row["repair_strategy"],
            "repaired_example_id": row["repaired_example_id"],
        }
        for row in phase14_report["repair_success_rows"]
    ]


def _parallel_runner_rows(phase17_report: Mapping[str, object]) -> TableRows:
    claim = phase17_report["claim_boundary"]
    return [
        {
            "metric": "parallel_matches_sequential",
            "value": phase17_report["parallel_matches_sequential"],
            "claim": claim,
        },
        {
            "metric": "sequential_top_program_ids",
            "value": ";".join(
                str(program_id)
                for program_id in phase17_report["sequential_top_program_ids"]
            ),
            "claim": claim,
        },
        {
            "metric": "parallel_top_program_ids",
            "value": ";".join(
                str(program_id)
                for program_id in phase17_report["parallel_top_program_ids"]
            ),
            "claim": claim,
        },
        {
            "metric": "failed_worker_recorded",
            "value": phase17_report["failed_worker_recorded"],
            "claim": claim,
        },
        {
            "metric": "cloud_adapter_status",
            "value": phase17_report["cloud_adapter_status"],
            "claim": claim,
        },
    ]


def _checkpoint_resume_rows(phase17_report: Mapping[str, object]) -> TableRows:
    claim = phase17_report["claim_boundary"]
    return [
        {
            "evidence": "checkpoint_resume_matches_full",
            "value": phase17_report["checkpoint_resume_matches_full"],
            "claim": claim,
        },
        {
            "evidence": "cost_budget_stop_reason",
            "value": phase17_report["cost_budget_stop_reason"],
            "claim": claim,
        },
        {
            "evidence": "cost_budget_evaluated_candidates",
            "value": phase17_report["cost_budget_evaluated_candidates"],
            "claim": claim,
        },
        {
            "evidence": "estimated_cost",
            "value": _format_number(phase17_report["estimated_cost"]),
            "claim": claim,
        },
    ]


def _next_step_rows(final_report: Mapping[str, object]) -> TableRows:
    return [
        {
            "step": row["step"],
            "reason": row["reason"],
        }
        for row in final_report["recommended_next_steps"]
    ]


def _format_number(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.6f}"
    return value


def _markdown_cell(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")
