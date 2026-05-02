from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from benchmarks.bin_packing.external import (
    build_phase9_report,
    load_external_bin_packing_instances,
)
from benchmarks.routing.external import (
    build_phase10_report,
    load_external_routing_instances,
)
from program_search.ablation import build_phase11_report
from program_search.evolution_loop import EvolutionConfig, build_phase3_report
from program_search.rerun_manifest import (
    build_bin_packing_rerun_manifest,
    rerun_manifest_entries,
)
from reports.artifacts import export_report_artifacts


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return _run(args)
    if args.command == "report":
        return _report(args)
    if args.command == "inspect":
        return _inspect(args)
    if args.command == "rerun-manifest":
        return _rerun_manifest(args)
    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="heuristic_discovery",
        description="Deterministic O2 heuristic discovery CLI.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="Run a deterministic local search.")
    run.add_argument(
        "--benchmark",
        choices=(
            "bin_packing",
            "bin_packing_external",
            "routing_external",
            "search_ablation",
        ),
        default="bin_packing",
    )
    run.add_argument("--generations", type=int, default=3)
    run.add_argument("--population-size", type=int, default=16)
    run.add_argument("--offspring-per-generation", type=int, default=12)
    run.add_argument("--candidate-count", type=int, default=48)
    run.add_argument("--candidate-budget", type=int, default=32)
    run.add_argument("--item-count", type=int, default=20)
    run.add_argument("--random-seed", type=int, default=23)
    run.add_argument("--external-path")
    run.add_argument(
        "--external-format",
        choices=("auto", "or_library", "bpplib", "tsplib"),
        default="auto",
    )
    run.add_argument("--output-dir", default=".")

    report = subcommands.add_parser("report", help="Export report artifacts.")
    report.add_argument("--output-dir", default=".")
    report.add_argument("--top-k", type=int, default=5)
    report.add_argument("--render-png", action="store_true")

    inspect = subcommands.add_parser("inspect", help="Inspect top local programs.")
    inspect.add_argument("--top-k", type=int, default=5)

    manifest = subcommands.add_parser(
        "rerun-manifest",
        help="Build and rerun a deterministic manifest.",
    )
    manifest.add_argument("--output-dir", default=".")
    manifest.add_argument("--top-k", type=int, default=5)
    manifest.add_argument("--manifest")

    return parser


def _run(args: argparse.Namespace) -> int:
    if args.benchmark == "bin_packing_external":
        external_instances = None
        if args.external_path:
            external_instances = load_external_bin_packing_instances(
                args.external_path,
                parser=args.external_format,
            )
        report = build_phase9_report(
            candidate_count=args.candidate_count,
            synthetic_item_count=args.item_count,
            external_instances=external_instances,
        )
    elif args.benchmark == "routing_external":
        external_instances = None
        if args.external_path:
            parser_name = (
                "tsplib" if args.external_format == "auto" else args.external_format
            )
            if parser_name != "tsplib":
                raise SystemExit(
                    "routing_external supports --external-format auto or tsplib"
                )
            external_instances = load_external_routing_instances(
                args.external_path,
                parser=parser_name,
            )
        report = build_phase10_report(
            candidate_count=args.candidate_count,
            synthetic_stop_count=args.item_count,
            external_instances=external_instances,
        )
    elif args.benchmark == "search_ablation":
        report = build_phase11_report(
            candidate_budget=args.candidate_budget,
            generations=args.generations,
            item_count=args.item_count,
            random_seed=args.random_seed,
        )
    else:
        report = build_phase3_report(
            config=EvolutionConfig(
                generations=args.generations,
                population_size=args.population_size,
                offspring_per_generation=args.offspring_per_generation,
                elite_size=4,
                tournament_size=3,
                random_seed=args.random_seed,
            ),
            item_count=args.item_count,
        )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "run_summary.json"
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if args.benchmark in {"bin_packing_external", "routing_external"}:
        payload = {
            "benchmark": args.benchmark,
            "best_external_program_id": report["best_external_program_id"],
            "path": str(output_path),
        }
    elif args.benchmark == "search_ablation":
        payload = {
            "benchmark": args.benchmark,
            "best_method": report["best_method"],
            "path": str(output_path),
        }
    else:
        payload = {
            "benchmark": args.benchmark,
            "generation_count": report["generation_count"],
            "path": str(output_path),
        }
    print(json.dumps(payload))
    return 0


def _report(args: argparse.Namespace) -> int:
    summary = export_report_artifacts(
        args.output_dir,
        top_k=args.top_k,
        render_png=args.render_png,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _inspect(args: argparse.Namespace) -> int:
    manifest = build_bin_packing_rerun_manifest(top_k=args.top_k)
    rows = [
        {
            "candidate_id": entry["candidate_id"],
            "score": entry["score"],
            "code_hash": entry["code_hash"],
        }
        for entry in manifest["entries"]
    ]
    print(json.dumps({"top_candidates": rows}, indent=2, sort_keys=True))
    return 0


def _rerun_manifest(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    else:
        manifest = build_bin_packing_rerun_manifest(top_k=args.top_k)
    manifest_path = artifacts_dir / "rerun_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    rerun = rerun_manifest_entries(manifest)
    print(json.dumps(rerun, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
