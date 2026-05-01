from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.amazon_routing.discovery import (
    AmazonDiscoveryConfig,
    build_phase6_report,
)
from program_search.evolution_loop import EvolutionConfig, build_phase3_report
from reports.failure_analysis import build_phase8_report
from reports.robustness import build_phase7_report

PlotPoints = List[Mapping[str, object]]


def build_report_plots(
    *,
    phase3_report: Optional[Mapping[str, object]] = None,
    phase6_report: Optional[Mapping[str, object]] = None,
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


def _format_plot_number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")
