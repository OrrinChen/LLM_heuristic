from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Mapping, Sequence, Union

from program_search.rerun_manifest import build_bin_packing_rerun_manifest
from reports.final_report import build_final_report, render_final_report_markdown
from reports.plots import build_report_plots
from reports.tables import build_report_tables


def export_report_artifacts(
    output_dir: Union[str, Path],
    *,
    top_k: int = 5,
    render_png: bool = False,
) -> Dict[str, object]:
    root = Path(output_dir)
    reports_dir = root / "reports"
    tables_dir = reports_dir / "tables"
    plots_dir = reports_dir / "plots"
    artifacts_dir = root / "artifacts"
    top_programs_dir = artifacts_dir / "top_programs"
    frontier_programs_dir = artifacts_dir / "frontier_programs"
    directories = (
        reports_dir,
        tables_dir,
        plots_dir,
        artifacts_dir,
        top_programs_dir,
        frontier_programs_dir,
    )
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    final_report = build_final_report()
    final_report_path = reports_dir / "final_report.md"
    final_report_path.write_text(
        render_final_report_markdown(final_report),
        encoding="utf-8",
    )

    tables = build_report_tables(final_report=final_report)
    table_paths = _write_tables(tables, tables_dir)

    plots = build_report_plots()
    plot_series_path = plots_dir / "plot_series.json"
    plot_series_path.write_text(
        json.dumps(plots, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    extra_plot_paths = _write_extra_plot_series(plots, plots_dir)

    manifest = build_bin_packing_rerun_manifest(top_k=top_k)
    manifest_path = artifacts_dir / "rerun_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    top_program_paths = _write_top_programs(manifest, top_programs_dir)
    frontier_program_paths = _write_frontier_programs(
        final_report,
        frontier_programs_dir,
    )

    png_paths: Sequence[Path] = ()
    if render_png:
        png_paths = _try_write_png_placeholders(plots_dir)

    return {
        "output_dir": str(root),
        "final_report": str(final_report_path),
        "tables": [str(path) for path in table_paths],
        "plot_series": str(plot_series_path),
        "extra_plot_series": [str(path) for path in extra_plot_paths],
        "top_programs": [str(path) for path in top_program_paths],
        "frontier_programs": [str(path) for path in frontier_program_paths],
        "rerun_manifest": str(manifest_path),
        "png_rendered": bool(png_paths),
        "png_paths": [str(path) for path in png_paths],
    }


def _write_extra_plot_series(
    plots: Mapping[str, object],
    plots_dir: Path,
) -> Sequence[Path]:
    paths = []
    for plot_name in ("generation_curve_by_method", "frontier_plot_series"):
        if plot_name not in plots:
            continue
        path = plots_dir / f"{plot_name}.json"
        path.write_text(
            json.dumps(plots[plot_name], indent=2, sort_keys=True),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def _write_frontier_programs(
    final_report: Mapping[str, object],
    frontier_programs_dir: Path,
) -> Sequence[Path]:
    for stale_path in frontier_programs_dir.glob("*.py"):
        stale_path.unlink()
    paths = []
    for row in final_report["pareto_frontier"]["frontier_rows"]:
        candidate_id = str(row["program_id"])
        benchmark = str(row["benchmark"])
        path = (
            frontier_programs_dir
            / f"{_safe_name(benchmark)}-{_safe_name(candidate_id)}.py"
        )
        path.write_text(
            "\n".join(
                [
                    f"# candidate_id: {candidate_id}",
                    f"# benchmark: {benchmark}",
                    f"# source: {row['source']}",
                    f"# objective_quality: {row['objective_quality']}",
                    f"# runtime: {row['runtime']}",
                    f"# program_complexity: {row['program_complexity']}",
                    f"# generalization_gap: {row['generalization_gap']}",
                    f"# selected_tradeoff: {row['selected_tradeoff']}",
                    "",
                    "",
                    str(row["code"]).rstrip(),
                    "",
                ]
            ),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def _write_tables(tables: Mapping[str, object], tables_dir: Path) -> Sequence[Path]:
    paths = []
    for table_name in tables["tables"]:
        table = tables[str(table_name)]
        path = tables_dir / f"{table_name}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=list(table["columns"]),
                lineterminator="\n",
            )
            writer.writeheader()
            for row in table["rows"]:
                writer.writerow(
                    {column: row.get(column, "") for column in table["columns"]}
                )
        paths.append(path)
    return paths


def _write_top_programs(
    manifest: Mapping[str, object],
    top_programs_dir: Path,
) -> Sequence[Path]:
    paths = []
    for entry in manifest["entries"]:
        candidate_id = str(entry["candidate_id"])
        path = top_programs_dir / f"{_safe_name(candidate_id)}.py"
        path.write_text(
            "\n".join(
                [
                    f"# candidate_id: {candidate_id}",
                    f"# benchmark: {entry['benchmark_name']}",
                    f"# code_hash: {entry['code_hash']}",
                    f"# score: {entry['score']}",
                    "",
                    "",
                    str(entry["code"]).rstrip(),
                    "",
                ]
            ),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def _try_write_png_placeholders(plots_dir: Path) -> Sequence[Path]:
    try:
        import matplotlib.pyplot as plt  # type: ignore[import-not-found]
    except Exception:  # noqa: BLE001 - optional plotting dependency.
        return ()

    path = plots_dir / "artifact_export_available.png"
    figure = plt.figure(figsize=(4, 2))
    try:
        axis = figure.add_subplot(111)
        axis.text(0.5, 0.5, "O2 artifacts exported", ha="center", va="center")
        axis.set_axis_off()
        figure.savefig(path, bbox_inches="tight")
    finally:
        plt.close(figure)
    return (path,)


def _safe_name(value: str) -> str:
    return "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in value
    )
