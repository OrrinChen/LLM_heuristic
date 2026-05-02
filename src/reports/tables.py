from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from reports.failure_analysis import build_phase8_report
from reports.final_report import build_final_report
from reports.robustness import build_phase7_report

TableRows = List[Mapping[str, object]]


def build_report_tables(
    *,
    final_report: Optional[Mapping[str, object]] = None,
    robustness_report: Optional[Mapping[str, object]] = None,
    failure_report: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    final = final_report or build_final_report()
    robustness = robustness_report or build_phase7_report()
    failures = failure_report or build_phase8_report()

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
    for name in ("nearest_neighbor", "cheapest_insertion", "two_opt"):
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
