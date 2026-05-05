from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Union

from program_search.rerun_manifest import PACKAGE_VERSION, rerun_manifest_entries
from reports.artifacts import export_report_artifacts

REPRODUCTION_PROFILE_NAMES = (
    "local_demo",
    "external_small",
    "llm_optional",
)

PHASE16_CLAIM_BOUNDARY = (
    "deterministic local reproduction package only; no API key, paid service, "
    "large external data, SOTA, or universal dominance claim"
)

REQUIRED_OUTPUTS = (
    "reports/final_report.md",
    "reports/tables/benchmark_comparison.csv",
    "reports/tables/external_generalization.csv",
    "reports/tables/routing_external_generalization.csv",
    "reports/tables/ablation_summary.csv",
    "reports/tables/pareto_frontier.csv",
    "reports/plots/plot_series.json",
    "artifacts/rerun_manifest.json",
    "artifacts/top_programs",
    "artifacts/reproduction_manifest.json",
    "artifacts/reproduction_summary.md",
)


def build_phase16_package(
    *,
    profile: str = "local_demo",
    output_dir: Union[str, Path] = ".",
    artifact_summary: Optional[Mapping[str, object]] = None,
    rerun_summary: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    config = _profile_config(profile)
    root = Path(output_dir)
    generated_artifacts = (
        _relative_artifact_paths(root, artifact_summary)
        if artifact_summary is not None
        else tuple(REQUIRED_OUTPUTS)
    )
    return {
        "schema_version": 1,
        "phase": 16,
        "profile": profile,
        "description": config["description"],
        "deterministic": True,
        "requires_api_key": False,
        "requires_large_external_data": False,
        "live_llm_required": False,
        "external_data": config["external_data"],
        "commands": {
            "reproduce": (
                "PYTHONPATH=src python3 -m heuristic_discovery reproduce "
                f"--profile {profile} --output-dir {root}"
            ),
            "report": (
                "PYTHONPATH=src python3 -m heuristic_discovery report "
                f"--output-dir {root} --top-k 5"
            ),
            "validate": (
                "python3 -m pytest tests/test_reproducibility_package_phase16.py -q"
            ),
        },
        "required_outputs": tuple(REQUIRED_OUTPUTS),
        "evidence_focus": config["evidence_focus"],
        "generated_artifacts": generated_artifacts,
        "rerun_checks": _rerun_checks(rerun_summary),
        "python_version": platform.python_version(),
        "package_version": PACKAGE_VERSION,
        "random_seeds": {
            "evolution": 23,
            "ablation": 23,
            "live_llm_fallback": 23,
            "fixture_source": "built_in_small_deterministic",
        },
        "claim_boundary": PHASE16_CLAIM_BOUNDARY,
        "recommended_next_phase": (
            "No required phase remains; project is release-frozen and "
            "portfolio-ready. Optional future work: broader crossover, paid "
            "cloud execution, or larger public benchmark corpora."
        ),
    }


def export_reproduction_package(
    output_dir: Union[str, Path],
    *,
    profile: str = "local_demo",
    top_k: int = 5,
    render_png: bool = False,
) -> Dict[str, object]:
    _profile_config(profile)
    root = Path(output_dir)
    artifact_summary = export_report_artifacts(
        root,
        top_k=top_k,
        render_png=render_png,
    )
    artifacts_dir = root / "artifacts"
    manifest_path = artifacts_dir / "rerun_manifest.json"
    rerun_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rerun_summary = rerun_manifest_entries(rerun_manifest)
    package = build_phase16_package(
        profile=profile,
        output_dir=root,
        artifact_summary=artifact_summary,
        rerun_summary=rerun_summary,
    )

    reproduction_manifest_path = artifacts_dir / "reproduction_manifest.json"
    reproduction_manifest_path.write_text(
        json.dumps(package, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    reproduction_summary_path = artifacts_dir / "reproduction_summary.md"
    reproduction_summary_path.write_text(
        render_reproduction_summary_markdown(package),
        encoding="utf-8",
    )

    return {
        "profile": profile,
        "deterministic": package["deterministic"],
        "requires_api_key": package["requires_api_key"],
        "requires_large_external_data": package["requires_large_external_data"],
        "reproduction_manifest": str(reproduction_manifest_path),
        "reproduction_summary": str(reproduction_summary_path),
        "rerun_checks": package["rerun_checks"],
        "report_artifacts": artifact_summary,
    }


def render_reproduction_summary_markdown(package: Mapping[str, object]) -> str:
    lines = [
        "# O2 Reproduction Summary",
        "",
        f"Profile: `{package['profile']}`",
        "",
        str(package["description"]),
        "",
        "No API key required. No large external benchmark data required.",
        "",
        "## Commands",
        "",
    ]
    commands = package["commands"]
    for name in ("reproduce", "report", "validate"):
        lines.extend(["```bash", str(commands[name]), "```", ""])
    lines.extend(["## Required Outputs", ""])
    for path in package["required_outputs"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Evidence Focus", ""])
    for path in package["evidence_focus"]:
        lines.append(f"- `{path}`")
    checks = package["rerun_checks"]
    lines.extend(
        [
            "",
            "## Rerun Checks",
            "",
            f"- Result count: `{checks['result_count']}`",
            f"- Code hashes match: `{checks['all_code_hashes_match']}`",
            f"- Scores match: `{checks['all_scores_match']}`",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for path in package["generated_artifacts"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            str(package["claim_boundary"]),
            "",
            "## Recommended Next Phase",
            "",
            str(package["recommended_next_phase"]),
            "",
        ]
    )
    return "\n".join(lines)


def _profile_config(profile: str) -> Mapping[str, object]:
    profiles: Mapping[str, Mapping[str, object]] = {
        "local_demo": {
            "description": (
                "Fresh-clone local demo profile that regenerates the evidence "
                "package from deterministic built-in benchmark slices."
            ),
            "external_data": "built-in synthetic and tiny fixture data",
            "evidence_focus": (
                "reports/final_report.md",
                "reports/tables/benchmark_comparison.csv",
                "reports/plots/plot_series.json",
                "artifacts/top_programs",
            ),
        },
        "external_small": {
            "description": (
                "External-small profile that highlights parser-backed "
                "BPPLIB / OR-Library and TSPLIB/CVRPLIB-style local fixtures."
            ),
            "external_data": "built-in tiny external benchmark-style fixtures",
            "evidence_focus": (
                "reports/tables/external_generalization.csv",
                "reports/tables/routing_external_generalization.csv",
                "reports/final_report.md",
            ),
        },
        "llm_optional": {
            "description": (
                "LLM-optional profile that uses deterministic fallback and "
                "repair providers; live Gemini remains environment-gated and "
                "is not required."
            ),
            "external_data": "built-in deterministic fallback responses",
            "evidence_focus": (
                "reports/tables/llm_operator_comparison.csv",
                "reports/tables/llm_candidate_audit.csv",
                "reports/final_report.md",
            ),
        },
    }
    if profile not in profiles:
        raise ValueError(
            "unknown reproduction profile: "
            f"{profile}. Expected one of {', '.join(REPRODUCTION_PROFILE_NAMES)}"
        )
    return profiles[profile]


def _rerun_checks(
    rerun_summary: Optional[Mapping[str, object]],
) -> Mapping[str, object]:
    if rerun_summary is None:
        return {
            "result_count": 0,
            "all_code_hashes_match": None,
            "all_scores_match": None,
            "results": (),
        }
    rows = []
    for row in rerun_summary["results"]:
        score = float(row["score"]) if row["score"] is not None else None
        expected = (
            float(row["expected_score"]) if row["expected_score"] is not None else None
        )
        scores_match = score == expected
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "ok": row["ok"],
                "score": score,
                "expected_score": expected,
                "code_hash_matches": row["code_hash_matches"],
                "score_matches": scores_match,
            }
        )
    return {
        "result_count": len(rows),
        "all_code_hashes_match": all(bool(row["code_hash_matches"]) for row in rows),
        "all_scores_match": all(bool(row["score_matches"]) for row in rows),
        "results": tuple(rows),
    }


def _relative_artifact_paths(
    root: Path,
    artifact_summary: Mapping[str, object],
) -> Sequence[str]:
    paths = set(REQUIRED_OUTPUTS)
    for key, value in artifact_summary.items():
        if key in {"output_dir", "png_rendered"}:
            continue
        if isinstance(value, str):
            paths.add(_relative_path(root, value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    paths.add(_relative_path(root, item))
    return tuple(sorted(paths))


def _relative_path(root: Path, value: str) -> str:
    path = Path(value)
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
