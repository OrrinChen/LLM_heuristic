from __future__ import annotations

import hashlib
import platform
from typing import Dict, List, Mapping, Optional

from benchmarks.bin_packing.evaluator import BinPackingEvaluator
from benchmarks.bin_packing.instances import default_train_validation_test_suites
from program_search.evolution_loop import EvolutionConfig, EvolutionLoop

PACKAGE_VERSION = "0.1.0"


def build_bin_packing_rerun_manifest(
    *,
    top_k: int = 5,
    generations: int = 2,
    population_size: int = 12,
    offspring_per_generation: int = 8,
    elite_size: Optional[int] = None,
    tournament_size: int = 3,
    item_count: int = 20,
    random_seed: int = 23,
) -> Dict[str, object]:
    if top_k < 1:
        raise ValueError("top_k must be positive")
    elite_size = elite_size or max(top_k, 4)
    train, validation, test = default_train_validation_test_suites(
        item_count=item_count
    )
    config = EvolutionConfig(
        generations=generations,
        population_size=population_size,
        offspring_per_generation=offspring_per_generation,
        elite_size=elite_size,
        tournament_size=tournament_size,
        random_seed=random_seed,
    )
    result = EvolutionLoop(config=config).run(
        train_instances=train,
        validation_instances=validation,
        test_instances=test,
    )
    entries: List[Mapping[str, object]] = []
    for top in result.top_candidates[:top_k]:
        candidate = result.archive.get(top.program_id)
        lineage = result.archive.lineage_for(top.program_id)
        entries.append(
            {
                "benchmark_name": "bin_packing",
                "candidate_id": top.program_id,
                "code_hash": code_hash(candidate.code),
                "generation": top.generation,
                "parent_id": candidate.parent_id,
                "parent_ids": [record.program_id for record in lineage[:-1]],
                "score": top.test_score,
                "validation_score": top.validation_score,
                "train_score": top.train_score,
                "failure_reason": candidate.failure_reason,
                "runtime": candidate.runtime,
                "python_version": platform.python_version(),
                "package_version": PACKAGE_VERSION,
                "random_seeds": {
                    "evolution": random_seed,
                    "train_validation_test_suites": "default",
                    "item_count": item_count,
                },
                "code": candidate.code,
            }
        )
    return {
        "schema_version": 1,
        "benchmark": "bin_packing",
        "split": "held_out_test",
        "item_count": item_count,
        "random_seed": random_seed,
        "entries": entries,
    }


def rerun_manifest_entries(manifest: Mapping[str, object]) -> Dict[str, object]:
    if manifest.get("benchmark") != "bin_packing":
        raise ValueError("only bin_packing manifests are supported")
    item_count = int(manifest["item_count"])
    _, _, test = default_train_validation_test_suites(item_count=item_count)
    evaluator = BinPackingEvaluator()
    results = []
    for entry in manifest["entries"]:
        code = str(entry["code"])
        result = evaluator.evaluate_program(
            code,
            test,
            program_id=str(entry["candidate_id"]),
        )
        results.append(
            {
                "candidate_id": entry["candidate_id"],
                "ok": result.ok,
                "score": result.score,
                "expected_score": entry["score"],
                "failure_reason": result.failure_reason,
                "runtime": result.runtime,
                "code_hash": code_hash(code),
                "code_hash_matches": code_hash(code) == entry["code_hash"],
            }
        )
    return {
        "schema_version": manifest["schema_version"],
        "benchmark": manifest["benchmark"],
        "results": results,
    }


def code_hash(code: str) -> str:
    return "sha256:" + hashlib.sha256(code.encode("utf-8")).hexdigest()
