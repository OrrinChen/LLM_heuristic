from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import median
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    build_seed_candidate_programs,
)
from benchmarks.bin_packing.instances import default_train_validation_test_suites
from sandbox.restricted_exec import SAFE_BUILTINS, SandboxTimeoutError, _timeout
from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    validate_candidate_code,
)

NOVELTY_DIMENSIONS = (
    "code_novelty",
    "behavior_novelty",
    "feature_novelty",
    "performance_novelty",
)

PHASE13_CLAIM_BOUNDARY = (
    "semantic novelty reports probe-based behavior evidence and equivalence "
    "clusters; it does not prove human-level semantic understanding or "
    "universal performance improvement"
)


@dataclass(frozen=True)
class NoveltyCandidate:
    program_id: str
    source: str
    code: str
    validation_score: Optional[float] = None
    test_score: Optional[float] = None
    generation: int = 0


@dataclass(frozen=True)
class BehaviorProbe:
    probe_id: str
    item_size: float
    bin_options: Tuple[Mapping[str, float], ...]

    def as_dict(self) -> Mapping[str, object]:
        return {
            "probe_id": self.probe_id,
            "item_size": self.item_size,
            "bin_options": tuple(dict(option) for option in self.bin_options),
        }


@dataclass(frozen=True)
class FingerprintResult:
    rankings: Tuple[Tuple[int, ...], ...]
    score_vectors: Tuple[Tuple[float, ...], ...]
    behavior_hash: str
    failure_reason: Optional[str] = None


def build_phase13_report(
    *,
    candidate_count: int = 24,
    candidates: Optional[Sequence[NoveltyCandidate]] = None,
    probes: Optional[Sequence[BehaviorProbe]] = None,
) -> Dict[str, object]:
    if candidate_count < 1:
        raise ValueError("candidate_count must be positive")
    resolved_candidates = tuple(candidates or _default_candidates(candidate_count))
    resolved_probes = tuple(probes or default_behavior_probes())
    if not resolved_candidates:
        raise ValueError("at least one candidate is required")
    if not resolved_probes:
        raise ValueError("at least one behavior probe is required")

    enriched_candidates = _fill_missing_scores(resolved_candidates)
    preliminary_rows = []
    for candidate in enriched_candidates:
        fingerprint = fingerprint_score_bin(candidate.code, resolved_probes)
        features = _feature_usage(candidate.code)
        complexity = _complexity_decomposition(candidate.code)
        preliminary_rows.append(
            {
                "candidate": candidate,
                "fingerprint": fingerprint,
                "features": features,
                "complexity": complexity,
                "code_hash": _hash_text(_normalize_code(candidate.code)),
                "feature_hash": _hash_json(tuple(sorted(features))),
                "performance_value": _performance_value(candidate),
            }
        )

    code_counts = Counter(row["code_hash"] for row in preliminary_rows)
    behavior_counts = Counter(
        row["fingerprint"].behavior_hash for row in preliminary_rows
    )
    feature_counts = Counter(row["feature_hash"] for row in preliminary_rows)
    performance_values = [float(row["performance_value"]) for row in preliminary_rows]
    performance_median = median(performance_values)
    performance_span = max(performance_values) - min(performance_values)

    novelty_rows = []
    behavior_fingerprints = []
    for row in preliminary_rows:
        candidate = row["candidate"]
        fingerprint = row["fingerprint"]
        code_novelty = 1.0 / code_counts[row["code_hash"]]
        behavior_novelty = 1.0 / behavior_counts[fingerprint.behavior_hash]
        feature_novelty = 1.0 / feature_counts[row["feature_hash"]]
        performance_novelty = _performance_novelty(
            float(row["performance_value"]),
            performance_median,
            performance_span,
        )
        semantic_novelty = (
            code_novelty + behavior_novelty + feature_novelty + performance_novelty
        ) / 4.0
        feature_usage = tuple(sorted(row["features"]))
        novelty_rows.append(
            {
                "program_id": candidate.program_id,
                "source": candidate.source,
                "generation": candidate.generation,
                "code_hash": row["code_hash"],
                "behavior_hash": fingerprint.behavior_hash,
                "code_novelty": round(code_novelty, 6),
                "behavior_novelty": round(behavior_novelty, 6),
                "feature_novelty": round(feature_novelty, 6),
                "performance_novelty": round(performance_novelty, 6),
                "semantic_novelty_score": round(semantic_novelty, 6),
                "feature_usage": feature_usage,
                "complexity_nodes": row["complexity"]["nodes"],
                "complexity_branches": row["complexity"]["branches"],
                "complexity_operations": row["complexity"]["operations"],
                "complexity_literals": row["complexity"]["literals"],
                "validation_score": candidate.validation_score,
                "test_score": candidate.test_score,
                "failure_reason": fingerprint.failure_reason,
            }
        )
        behavior_fingerprints.append(
            {
                "program_id": candidate.program_id,
                "behavior_hash": fingerprint.behavior_hash,
                "rankings": fingerprint.rankings,
                "score_vectors": fingerprint.score_vectors,
                "failure_reason": fingerprint.failure_reason,
            }
        )

    duplicate_clusters = _behavior_clusters(novelty_rows, behavior_fingerprints)
    novelty_rows = sorted(
        novelty_rows,
        key=lambda item: (
            -float(item["semantic_novelty_score"]),
            str(item["program_id"]),
        ),
    )
    return {
        "phase": 13,
        "benchmark": "bin_packing_semantic_novelty",
        "candidate_count": len(enriched_candidates),
        "probe_count": len(resolved_probes),
        "probe_schema": tuple(probe.as_dict() for probe in resolved_probes),
        "novelty_dimensions": NOVELTY_DIMENSIONS,
        "novelty_rows": novelty_rows,
        "behavior_fingerprints": tuple(behavior_fingerprints),
        "duplicate_behavior_clusters": tuple(duplicate_clusters),
        "behavior_cluster_count": len({row["behavior_hash"] for row in novelty_rows}),
        "equivalent_program_count": sum(
            int(cluster["cluster_size"]) for cluster in duplicate_clusters
        ),
        "claim_boundary": PHASE13_CLAIM_BOUNDARY,
        "recommended_next_phase": "Phase 14: Failure Taxonomy v2",
    }


def default_behavior_probes() -> Tuple[BehaviorProbe, ...]:
    return (
        BehaviorProbe(
            probe_id="mixed-tight-fit",
            item_size=0.24,
            bin_options=(
                _bin_option(0, 0.31, 0.69, 2),
                _bin_option(1, 0.47, 0.53, 1),
                _bin_option(2, 0.77, 0.23, 4),
            ),
        ),
        BehaviorProbe(
            probe_id="large-placement",
            item_size=0.52,
            bin_options=(
                _bin_option(0, 0.58, 0.42, 1),
                _bin_option(1, 0.72, 0.28, 3),
                _bin_option(2, 0.49, 0.51, 2),
            ),
        ),
        BehaviorProbe(
            probe_id="many-used-bins",
            item_size=0.18,
            bin_options=(
                _bin_option(0, 0.42, 0.58, 8),
                _bin_option(1, 0.41, 0.59, 1),
                _bin_option(2, 0.35, 0.65, 3),
            ),
        ),
        BehaviorProbe(
            probe_id="near-infeasible",
            item_size=0.34,
            bin_options=(
                _bin_option(0, 0.33, 0.67, 4),
                _bin_option(1, 0.36, 0.64, 2),
                _bin_option(2, 0.61, 0.39, 1),
            ),
        ),
        BehaviorProbe(
            probe_id="balanced-residual",
            item_size=0.27,
            bin_options=(
                _bin_option(0, 0.52, 0.48, 2),
                _bin_option(1, 0.38, 0.62, 4),
                _bin_option(2, 0.74, 0.26, 1),
            ),
        ),
    )


def fingerprint_score_bin(
    code: str,
    probes: Sequence[BehaviorProbe],
    *,
    timeout_seconds: float = 0.05,
) -> FingerprintResult:
    scoring_function, failure = _compile_score_bin(code)
    if failure is not None:
        failure_text = str(failure)
        return FingerprintResult(
            rankings=(),
            score_vectors=(),
            behavior_hash=_hash_json(("invalid", failure_text)),
            failure_reason=failure_text,
        )

    rankings = []
    score_vectors = []
    for probe in probes:
        try:
            with _timeout(timeout_seconds):
                scores = tuple(
                    _score_option(scoring_function, probe.item_size, option)
                    for option in probe.bin_options
                )
        except SandboxTimeoutError:
            failure_text = f"timeout: candidate exceeded {timeout_seconds} seconds"
            return FingerprintResult(
                rankings=(),
                score_vectors=(),
                behavior_hash=_hash_json(("invalid", failure_text)),
                failure_reason=failure_text,
            )
        except Exception as exc:  # noqa: BLE001 - candidate behavior boundary.
            failure_text = f"runtime_error: {type(exc).__name__}: {exc}"
            return FingerprintResult(
                rankings=(),
                score_vectors=(),
                behavior_hash=_hash_json(("invalid", failure_text)),
                failure_reason=failure_text,
            )
        rankings.append(
            tuple(
                index
                for _, index in sorted((score, i) for i, score in enumerate(scores))
            )
        )
        score_vectors.append(tuple(round(score, 6) for score in scores))

    ranking_tuple = tuple(rankings)
    return FingerprintResult(
        rankings=ranking_tuple,
        score_vectors=tuple(score_vectors),
        behavior_hash=_hash_json(ranking_tuple),
        failure_reason=None,
    )


def _default_candidates(candidate_count: int) -> Tuple[NoveltyCandidate, ...]:
    train, validation, test = default_train_validation_test_suites(item_count=20)
    evaluator = BinPackingEvaluator()
    candidates = []
    for seed in build_seed_candidate_programs(candidate_count):
        validation_result = evaluator.evaluate_program(
            seed.code,
            validation,
            program_id=seed.program_id,
        )
        test_result = evaluator.evaluate_program(
            seed.code,
            test,
            program_id=seed.program_id,
        )
        candidates.append(
            NoveltyCandidate(
                program_id=seed.program_id,
                source="seed_library",
                code=seed.code,
                validation_score=validation_result.score,
                test_score=test_result.score,
                generation=0,
            )
        )
    return tuple(candidates)


def _fill_missing_scores(
    candidates: Sequence[NoveltyCandidate],
) -> Tuple[NoveltyCandidate, ...]:
    if all(
        candidate.validation_score is not None and candidate.test_score is not None
        for candidate in candidates
    ):
        return tuple(candidates)
    _train, validation, test = default_train_validation_test_suites(item_count=20)
    evaluator = BinPackingEvaluator()
    enriched = []
    for candidate in candidates:
        validation_score = candidate.validation_score
        test_score = candidate.test_score
        if validation_score is None:
            validation_score = evaluator.evaluate_program(
                candidate.code,
                validation,
                program_id=candidate.program_id,
            ).score
        if test_score is None:
            test_score = evaluator.evaluate_program(
                candidate.code,
                test,
                program_id=candidate.program_id,
            ).score
        enriched.append(
            NoveltyCandidate(
                program_id=candidate.program_id,
                source=candidate.source,
                code=candidate.code,
                validation_score=validation_score,
                test_score=test_score,
                generation=candidate.generation,
            )
        )
    return tuple(enriched)


def _compile_score_bin(
    code: str,
) -> Tuple[
    Optional[Callable[[float, float, Mapping[str, float]], object]],
    Optional[FailureReason],
]:
    config = ValidationConfig(allowed_function="score_bin")
    validation = validate_candidate_code(code, config)
    if not validation.ok:
        return None, validation.failure_reason
    namespace = {"__builtins__": SAFE_BUILTINS}
    try:
        compiled = compile(code, "<semantic-novelty-candidate>", "exec")
        exec(compiled, namespace, namespace)
    except Exception as exc:  # noqa: BLE001 - structured candidate boundary.
        return None, FailureReason(
            code="runtime_error",
            message=f"{type(exc).__name__}: {exc}",
        )
    return namespace[config.allowed_function], None


def _score_option(
    scoring_function: Callable[[float, float, Mapping[str, float]], object],
    item_size: float,
    option: Mapping[str, float],
) -> float:
    remaining = float(option["remaining_capacity"])
    value = scoring_function(item_size, remaining, option)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("score_bin must return a numeric score")
    return float(value)


def _feature_usage(code: str) -> Tuple[str, ...]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ()
    features = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {
            "item_size",
            "bin_remaining_capacity",
        }:
            features.add(node.id)
        if isinstance(node, ast.Subscript) and _name(node.value) == "bin_features":
            key = _literal_subscript_key(node.slice)
            if key:
                features.add(f"bin_features.{key}")
    return tuple(sorted(features))


def _complexity_decomposition(code: str) -> Mapping[str, int]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "nodes": len(code.splitlines()) + 100,
            "branches": 0,
            "operations": 0,
            "literals": 0,
        }
    nodes = list(ast.walk(tree))
    return {
        "nodes": len(nodes),
        "branches": sum(
            isinstance(node, (ast.If, ast.IfExp, ast.For, ast.While)) for node in nodes
        ),
        "operations": sum(
            isinstance(node, (ast.BinOp, ast.BoolOp, ast.Compare, ast.UnaryOp))
            for node in nodes
        ),
        "literals": sum(isinstance(node, ast.Constant) for node in nodes),
    }


def _behavior_clusters(
    novelty_rows: Sequence[Mapping[str, object]],
    fingerprints: Sequence[Mapping[str, object]],
) -> List[Mapping[str, object]]:
    fingerprint_by_program = {str(row["program_id"]): row for row in fingerprints}
    rows_by_hash: Dict[str, List[Mapping[str, object]]] = defaultdict(list)
    for row in novelty_rows:
        rows_by_hash[str(row["behavior_hash"])].append(row)

    clusters = []
    for behavior_hash, rows in rows_by_hash.items():
        if len(rows) < 2:
            continue
        program_ids = tuple(str(row["program_id"]) for row in rows)
        representative = program_ids[0]
        representative_fingerprint = fingerprint_by_program[representative]
        clusters.append(
            {
                "behavior_hash": behavior_hash,
                "cluster_size": len(rows),
                "program_ids": program_ids,
                "representative_program_id": representative,
                "shared_ranking": representative_fingerprint["rankings"],
                "explanation": (
                    "Programs in this cluster produced identical ranking "
                    "vectors on the fixed bin-packing behavior probes."
                ),
            }
        )
    return sorted(
        clusters,
        key=lambda cluster: (
            -int(cluster["cluster_size"]),
            str(cluster["representative_program_id"]),
        ),
    )


def _bin_option(
    bin_index: int,
    remaining_capacity: float,
    current_load: float,
    items_in_bin: int,
) -> Mapping[str, float]:
    return {
        "bin_index": float(bin_index),
        "remaining_capacity": remaining_capacity,
        "current_load": current_load,
        "items_in_bin": float(items_in_bin),
        "capacity": 1.0,
    }


def _performance_value(candidate: NoveltyCandidate) -> float:
    if candidate.test_score is not None:
        return float(candidate.test_score)
    if candidate.validation_score is not None:
        return float(candidate.validation_score)
    return 1000.0


def _performance_novelty(value: float, center: float, span: float) -> float:
    if span <= 0:
        return 0.0
    return min(1.0, abs(value - center) / span)


def _normalize_code(code: str) -> str:
    return "\n".join(line.rstrip() for line in code.strip().splitlines()) + "\n"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hash_json(value: object) -> str:
    return _hash_text(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _literal_subscript_key(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    # Python 3.9 may wrap legacy index nodes when parsing older source.
    if isinstance(node, ast.Index):  # type: ignore[attr-defined]
        return _literal_subscript_key(node.value)  # type: ignore[attr-defined]
    return ""
