from __future__ import annotations

import math
from html import escape
from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
)
from benchmarks.trading_signal import build_trading_signal_report
from program_search.ablation import build_phase11_report
from program_search.evolution_loop import EvolutionConfig, build_phase3_report
from program_search.semantic_novelty import build_phase13_report
from reports.failure_analysis import build_phase8_report
from reports.pareto import build_phase15_report
from reports.robustness import build_phase7_report

PlotPoints = List[Mapping[str, object]]


def build_report_plots(
    *,
    phase3_report: Optional[Mapping[str, object]] = None,
    phase6_report: Optional[Mapping[str, object]] = None,
    phase11_report: Optional[Mapping[str, object]] = None,
    phase13_report: Optional[Mapping[str, object]] = None,
    phase15_report: Optional[Mapping[str, object]] = None,
    trading_signal_report: Optional[Mapping[str, object]] = None,
    robustness_report: Optional[Mapping[str, object]] = None,
    failure_report: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    phase3 = phase3_report or build_phase3_report(
        config=EvolutionConfig(
            generations=3,
            population_size=16,
            offspring_per_generation=12,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        ),
        item_count=20,
    )
    phase6 = phase6_report or build_phase6_report(
        config=AmazonDiscoveryConfig(
            generations=2,
            population_size=12,
            offspring_per_generation=8,
            elite_size=4,
            tournament_size=3,
            random_seed=23,
        )
    )
    phase11 = phase11_report or build_phase11_report(
        candidate_budget=32,
        generations=3,
        item_count=20,
        random_seed=23,
    )
    phase13 = phase13_report or build_phase13_report()
    phase15 = phase15_report or build_phase15_report()
    trading_signal = trading_signal_report or build_trading_signal_report()
    robustness = robustness_report or build_phase7_report()
    failures = failure_report or build_phase8_report()

    plots = {
        "bin_packing_evolution_best_score": _generation_score_plot(
            title="Bin Packing Evolution Best Score",
            rows=phase3["generation_curve"],
        ),
        "amazon_discovery_best_score": _generation_score_plot(
            title="Amazon Discovery Best Score",
            rows=phase6["generation_curve"],
        ),
        "robustness_generalization_gaps": _robustness_gap_plot(
            robustness["slice_summary"]
        ),
        "generation_curve_by_method": _ablation_curve_plot(
            phase11["generation_curve_by_method"]
        ),
        "behavior_fingerprint": _behavior_fingerprint_plot(phase13),
        "frontier_plot_series": _frontier_plot(phase15["candidate_rows"]),
        "trading_signal_frontier": _trading_signal_frontier_plot(
            trading_signal["candidate_rows"]
        ),
        "failure_rate_by_generation": _failure_rate_plot(
            failures["failure_rate_by_generation"]
        ),
    }
    return {
        "phase": "report_plots",
        "plots": tuple(plots),
        **plots,
    }


def render_report_plots_markdown(plots: Mapping[str, object]) -> str:
    lines = ["# Report Plots", ""]
    for plot_name in plots["plots"]:
        plot = plots[str(plot_name)]
        lines.extend(
            [
                f"## {plot['title']}",
                "",
                "```text",
                plot["ascii"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def render_pareto_frontier_svg(
    plot: Mapping[str, object],
    *,
    width: int = 760,
    height: int = 440,
) -> str:
    points = list(plot["points"])
    margin_left = 80
    margin_right = 40
    margin_top = 52
    margin_bottom = 76
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    runtimes = [float(point["runtime"]) for point in points]
    qualities = [float(point["objective_quality"]) for point in points]
    min_runtime = min(runtimes) if runtimes else 0.0
    max_runtime = max(runtimes) if runtimes else 1.0
    min_quality = min(qualities) if qualities else 0.0
    max_quality = max(qualities) if qualities else 1.0
    min_log_runtime = math.log10(max(min_runtime, 1e-9))
    max_log_runtime = math.log10(max(max_runtime, 1e-9))
    benchmark_colors = {
        "amazon_routing": "#2563eb",
        "bin_packing": "#059669",
        "simple_routing": "#d97706",
    }

    def scale_x(runtime: float) -> float:
        value = math.log10(max(runtime, 1e-9))
        if max_log_runtime == min_log_runtime:
            return margin_left + plot_width / 2
        return (
            margin_left
            + ((value - min_log_runtime) / (max_log_runtime - min_log_runtime))
            * plot_width
        )

    def scale_y(quality: float) -> float:
        if max_quality == min_quality:
            return margin_top + plot_height / 2
        return (
            margin_top
            + ((max_quality - quality) / (max_quality - min_quality)) * plot_height
        )

    point_elements = []
    for point in sorted(
        points,
        key=lambda row: (
            str(row["benchmark"]),
            not bool(row["is_pareto_frontier"]),
            str(row["program_id"]),
        ),
    ):
        benchmark = str(point["benchmark"])
        color = benchmark_colors.get(benchmark, "#64748b")
        is_frontier = bool(point["is_pareto_frontier"])
        radius = 6 if is_frontier else 4
        fill = color if is_frontier else "#ffffff"
        opacity = "1.0" if is_frontier else "0.58"
        stroke_width = "2" if is_frontier else "1.5"
        title = (
            f"{point['program_id']} | {benchmark} | runtime={point['runtime']} | "
            f"objective quality={point['objective_quality']} | "
            f"{'frontier' if is_frontier else 'dominated'}"
        )
        point_elements.append(
            f'<circle cx="{scale_x(float(point["runtime"])):.2f}" '
            f'cy="{scale_y(float(point["objective_quality"])):.2f}" '
            f'r="{radius}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{stroke_width}" opacity="{opacity}">'
            f"<title>{escape(title)}</title></circle>"
        )

    legend_y = margin_top + 10
    legend_items = []
    for index, (benchmark, color) in enumerate(benchmark_colors.items()):
        x = margin_left + index * 150
        legend_items.extend(
            [
                f'<circle cx="{x}" cy="{legend_y}" r="5" fill="{color}" />',
                (
                    f'<text x="{x + 10}" y="{legend_y + 4}" '
                    f'class="legend">{escape(benchmark)}</text>'
                ),
            ]
        )

    return "\n".join(
        [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
                f'height="{height}" viewBox="0 0 {width} {height}" '
                'role="img" aria-labelledby="title desc">'
            ),
            '<title id="title">Pareto Frontier Quality Runtime</title>',
            (
                '<desc id="desc">Runtime on the x-axis, objective quality on '
                "the y-axis, with frontier and dominated candidates shown by "
                "marker style.</desc>"
            ),
            "<style>",
            "text { font-family: Arial, sans-serif; fill: #0f172a; }",
            ".title { font-size: 20px; font-weight: 700; }",
            ".axis { font-size: 12px; fill: #475569; }",
            ".legend { font-size: 12px; fill: #334155; }",
            ".note { font-size: 11px; fill: #64748b; }",
            "line { stroke: #94a3b8; stroke-width: 1; }",
            "</style>",
            '<rect width="100%" height="100%" fill="#ffffff" />',
            (
                f'<text x="{margin_left}" y="30" class="title">Pareto Frontier '
                "Quality Runtime</text>"
            ),
            (
                f'<line x1="{margin_left}" y1="{margin_top + plot_height}" '
                f'x2="{margin_left + plot_width}" '
                f'y2="{margin_top + plot_height}" />'
            ),
            (
                f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" '
                f'y2="{margin_top + plot_height}" />'
            ),
            (
                f'<text x="{margin_left + plot_width / 2 - 70:.2f}" '
                f'y="{height - 24}" class="axis">runtime, log scale</text>'
            ),
            (
                f'<text x="18" y="{margin_top + plot_height / 2 + 72:.2f}" '
                'class="axis" transform="rotate(-90 18 '
                f'{margin_top + plot_height / 2 + 72:.2f})">'
                "objective quality</text>"
            ),
            (
                f'<text x="{margin_left}" y="{height - 46}" class="note">'
                f"runtime range {min_runtime:.6g} to {max_runtime:.6g}; "
                f"objective quality range {min_quality:.6g} to {max_quality:.6g}"
                "</text>"
            ),
            *legend_items,
            *point_elements,
            (
                f'<circle cx="{width - 168}" cy="{height - 52}" r="6" '
                'fill="#334155" stroke="#334155" stroke-width="2" />'
            ),
            (
                f'<text x="{width - 154}" y="{height - 48}" class="legend">'
                "frontier</text>"
            ),
            (
                f'<circle cx="{width - 88}" cy="{height - 52}" r="4" '
                'fill="#ffffff" stroke="#334155" stroke-width="1.5" '
                'opacity="0.58" />'
            ),
            (
                f'<text x="{width - 76}" y="{height - 48}" class="legend">'
                "dominated</text>"
            ),
            "</svg>",
        ]
    )


def render_ascii_bar_plot(
    points: Sequence[Mapping[str, object]],
    *,
    label_key: str,
    value_key: str,
    width: int = 32,
) -> str:
    if not points:
        return ""
    values = [float(point[value_key]) for point in points]
    max_value = max(values)
    scale = width / max_value if max_value else 1.0
    lines = []
    for point, value in zip(points, values):
        label = str(point[label_key])
        bar = "#" * max(1, round(value * scale)) if value > 0 else ""
        lines.append(f"{label}: {bar} {_format_plot_number(value)}")
    return "\n".join(lines)


def _generation_score_plot(
    *,
    title: str,
    rows: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    points: PlotPoints = [
        {
            "generation": row["generation"],
            "label": f"generation={row['generation']} {row['best_program_id']}",
            "best_score": row["best_score"],
            "median_score": row["median_score"],
            "best_program_id": row["best_program_id"],
        }
        for row in rows
    ]
    return {
        "title": title,
        "x": "generation",
        "y": "best_score",
        "points": points,
        "ascii": render_ascii_bar_plot(
            points,
            label_key="label",
            value_key="best_score",
        ),
    }


def _robustness_gap_plot(rows: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    points: PlotPoints = [
        {
            "slice_name": row["slice_name"],
            "label": row["slice_name"],
            "benchmark": row["benchmark"],
            "generalization_gap": row["generalization_gap"],
            "program_id": row["program_id"],
        }
        for row in rows
    ]
    sorted_points = sorted(
        points,
        key=lambda point: (
            float(point["generalization_gap"]),
            str(point["slice_name"]),
        ),
        reverse=True,
    )
    return {
        "title": "Robustness Generalization Gaps",
        "x": "slice_name",
        "y": "generalization_gap",
        "points": points,
        "ascii": render_ascii_bar_plot(
            sorted_points[:8],
            label_key="label",
            value_key="generalization_gap",
        ),
    }


def _failure_rate_plot(rows: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    points: PlotPoints = [
        {
            "benchmark": row["benchmark"],
            "generation": row["generation"],
            "label": f"{row['benchmark']} generation={row['generation']}",
            "failure_rate": row["failure_rate"],
            "best_program_id": row["best_program_id"],
        }
        for row in rows
    ]
    return {
        "title": "Failure Rate By Generation",
        "x": "generation",
        "y": "failure_rate",
        "points": points,
        "ascii": render_ascii_bar_plot(
            points,
            label_key="label",
            value_key="failure_rate",
        ),
    }


def _ablation_curve_plot(
    curves: Mapping[str, Sequence[Mapping[str, object]]],
) -> Mapping[str, object]:
    points: PlotPoints = []
    for method, rows in curves.items():
        for row in rows:
            points.append(
                {
                    "method": method,
                    "generation": row["generation"],
                    "evaluated_candidates": row["evaluated_candidates"],
                    "best_score": row["best_score"],
                    "median_score": row["median_score"],
                    "failure_rate": row["failure_rate"],
                    "invalid_code_rate": row["invalid_code_rate"],
                    "best_program_id": row["best_program_id"],
                    "label": f"{method} generation={row['generation']}",
                }
            )
    latest_points = [
        point
        for point in points
        if point["generation"]
        == max(
            int(candidate["generation"])
            for candidate in points
            if candidate["method"] == point["method"]
        )
    ]
    return {
        "title": "Generation Curve By Method",
        "x": "evaluated_candidates",
        "y": "best_score",
        "points": points,
        "ascii": render_ascii_bar_plot(
            latest_points,
            label_key="label",
            value_key="best_score",
        ),
    }


def _frontier_plot(rows: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    points: PlotPoints = [
        {
            "benchmark": row["benchmark"],
            "program_id": row["program_id"],
            "runtime": row["runtime"],
            "objective_quality": row["objective_quality"],
            "program_complexity": row["program_complexity"],
            "generalization_gap": row["generalization_gap"],
            "failure_rate": row["failure_rate"],
            "operational_penalty": row["operational_penalty"],
            "is_pareto_frontier": row["is_pareto_frontier"],
            "label": f"{row['benchmark']} {row['program_id']}",
        }
        for row in rows
    ]
    frontier_points = [point for point in points if bool(point["is_pareto_frontier"])]
    return {
        "title": "Pareto Frontier Quality Runtime",
        "x": "runtime",
        "y": "objective_quality",
        "points": points,
        "ascii": render_ascii_bar_plot(
            sorted(
                frontier_points,
                key=lambda point: (
                    str(point["benchmark"]),
                    float(point["objective_quality"]),
                    str(point["program_id"]),
                ),
            ),
            label_key="label",
            value_key="objective_quality",
        ),
    }


def _trading_signal_frontier_plot(
    rows: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    points: PlotPoints = [
        {
            "benchmark": "trading_signal",
            "program_id": row["program_id"],
            "net_return": row["net_return"],
            "turnover": row["turnover"],
            "max_drawdown": row["max_drawdown"],
            "program_complexity": row["program_complexity"],
            "is_pareto_frontier": row["is_pareto_frontier"],
            "failure_reason": row["failure_reason"],
            "label": f"trading_signal {row['program_id']}",
        }
        for row in rows
    ]
    frontier_points = [point for point in points if bool(point["is_pareto_frontier"])]
    return {
        "title": "Trading Signal Net Return Turnover Frontier",
        "x": "turnover",
        "y": "net_return",
        "points": points,
        "ascii": render_ascii_bar_plot(
            sorted(
                frontier_points,
                key=lambda point: (
                    -float(point["net_return"]),
                    float(point["turnover"]),
                    str(point["program_id"]),
                ),
            ),
            label_key="label",
            value_key="net_return",
        ),
    }


def _behavior_fingerprint_plot(phase13: Mapping[str, object]) -> Mapping[str, object]:
    points: PlotPoints = [
        {
            "program_id": row["program_id"],
            "behavior_hash": row["behavior_hash"],
            "semantic_novelty_score": row["semantic_novelty_score"],
            "behavior_novelty": row["behavior_novelty"],
            "feature_novelty": row["feature_novelty"],
            "label": f"{row['program_id']} {str(row['behavior_hash'])[:8]}",
        }
        for row in phase13["novelty_rows"]
    ]
    return {
        "title": "Behavior Fingerprint",
        "x": "program_id",
        "y": "semantic_novelty_score",
        "points": points,
        "probe_schema": phase13["probe_schema"],
        "program_fingerprints": phase13["behavior_fingerprints"],
        "duplicate_behavior_clusters": phase13["duplicate_behavior_clusters"],
        "ascii": render_ascii_bar_plot(
            sorted(
                points,
                key=lambda point: (
                    -float(point["semantic_novelty_score"]),
                    str(point["program_id"]),
                ),
            )[:8],
            label_key="label",
            value_key="semantic_novelty_score",
        ),
    }


def _format_plot_number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")
