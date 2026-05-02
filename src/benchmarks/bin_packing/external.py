from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from benchmarks.bin_packing.baselines import BASELINE_PACKERS, PackingResult
from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    ProgramEvaluation,
    SeedCandidateProgram,
    build_seed_candidate_programs,
    evaluate_candidate_suite,
)
from benchmarks.bin_packing.instances import (
    BinPackingInstance,
    InstanceDistribution,
    default_train_validation_test_suites,
    generate_instance,
)

ExternalSuites = Tuple[
    List[BinPackingInstance],
    List[BinPackingInstance],
    List[BinPackingInstance],
]

PHASE9_CLAIM_BOUNDARY = (
    "external benchmark-style evidence only; no SOTA or universal dominance claim"
)

_DEFAULT_EXTERNAL_OR_LIBRARY_TEXT = """
6
orlib_train_a 8 10 4
2 8 4 6 5 5 3 7
orlib_train_b 7 10 4
6 4 6 4 5 5 2
orlib_validation_a 8 10 4
7 3 6 4 5 5 2 8
orlib_validation_b 9 10 5
6 4 4 6 3 7 5 5 2
orlib_test_a 10 10 5
8 2 7 3 6 4 5 5 4 6
orlib_test_b 9 10 5
9 1 8 2 7 3 5 5 4
"""


@dataclass(frozen=True)
class ExternalKnownOptimumSummary:
    average_known_optimum: Optional[float]
    average_bins_used: Optional[float]
    average_gap: Optional[float]

    def as_dict(self) -> Mapping[str, Optional[float]]:
        return {
            "average_known_optimum": self.average_known_optimum,
            "average_bins_used": self.average_bins_used,
            "average_gap": self.average_gap,
        }


def parse_or_library_bin_packing(
    text: str,
    *,
    source: str = "or_library",
) -> List[BinPackingInstance]:
    lines = _meaningful_lines(text)
    if not lines:
        raise ValueError("external benchmark text is empty")
    try:
        instance_count = int(lines[0].split()[0])
    except ValueError as exc:
        raise ValueError(
            "first OR-Library-style line must be an instance count"
        ) from exc

    instances: List[BinPackingInstance] = []
    line_index = 1
    for instance_index in range(instance_count):
        if line_index >= len(lines):
            raise ValueError("missing OR-Library-style instance header")
        header = lines[line_index].split()
        line_index += 1
        if _is_number(header[0]):
            instance_id = f"{source}-{instance_index:03d}"
            numeric_header = header
        else:
            instance_id = header[0]
            numeric_header = header[1:]
        if len(numeric_header) < 2:
            raise ValueError("instance header must include item count and capacity")

        item_count = int(float(numeric_header[0]))
        capacity = float(numeric_header[1])
        known_optimum = (
            int(float(numeric_header[2])) if len(numeric_header) >= 3 else None
        )
        weights: List[float] = [float(token) for token in numeric_header[3:]]
        while len(weights) < item_count and line_index < len(lines):
            weights.extend(float(token) for token in lines[line_index].split())
            line_index += 1
        if len(weights) != item_count:
            raise ValueError(
                f"{instance_id} expected {item_count} weights, got {len(weights)}"
            )
        instances.append(
            _external_instance(
                instance_id=instance_id,
                source=source,
                capacity=capacity,
                items=weights,
                known_optimum=known_optimum,
            )
        )
    return instances


def parse_bpplib_bin_packing(
    text: str,
    *,
    source: str = "bpplib",
) -> List[BinPackingInstance]:
    instances = []
    current: Dict[str, object] = {}
    reading_weights = False
    for line in _meaningful_lines(text):
        upper = line.upper()
        if upper == "EOF":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().upper()
            value = value.strip()
            if key == "NAME" and current.get("weights"):
                instances.append(_instance_from_bpplib_block(current, source))
                current = {}
            if key == "WEIGHTS":
                reading_weights = True
                if value:
                    current.setdefault("weights", []).extend(
                        float(token) for token in value.split()
                    )
                continue
            reading_weights = False
            if key == "NAME":
                current["name"] = value
            elif key == "CAPACITY":
                current["capacity"] = float(value)
            elif key in {"ITEMS", "ITEM_COUNT", "N"}:
                current["item_count"] = int(float(value))
            elif key in {"OPTIMUM", "OPTIMAL", "BEST_KNOWN"}:
                current["known_optimum"] = int(float(value))
            continue
        if reading_weights:
            current.setdefault("weights", []).extend(
                float(token) for token in line.split()
            )
    if current:
        instances.append(_instance_from_bpplib_block(current, source))
    if not instances:
        raise ValueError("no BPPLIB-style instances found")
    return instances


def load_external_bin_packing_instances(
    path: Union[str, Path],
    *,
    parser: str = "auto",
    source: Optional[str] = None,
) -> List[BinPackingInstance]:
    data_path = Path(path)
    text = data_path.read_text(encoding="utf-8")
    resolved_source = source or data_path.name
    if parser == "auto":
        parser = "bpplib" if _looks_like_bpplib(text) else "or_library"
    if parser == "bpplib":
        return parse_bpplib_bin_packing(text, source=resolved_source)
    if parser == "or_library":
        return parse_or_library_bin_packing(text, source=resolved_source)
    raise ValueError(f"unknown external bin packing parser: {parser}")


def split_external_instances(
    instances: Sequence[BinPackingInstance],
) -> ExternalSuites:
    if len(instances) < 3:
        raise ValueError("at least three external instances are required for splits")
    ordered = list(instances)
    train_end = max(1, len(ordered) // 3)
    validation_end = max(train_end + 1, (len(ordered) * 2) // 3)
    validation_end = min(validation_end, len(ordered) - 1)
    return (
        ordered[:train_end],
        ordered[train_end:validation_end],
        ordered[validation_end:],
    )


def default_external_train_validation_test_suites() -> ExternalSuites:
    return split_external_instances(
        parse_or_library_bin_packing(
            _DEFAULT_EXTERNAL_OR_LIBRARY_TEXT,
            source="or_library_style_fixture",
        )
    )


def build_phase9_report(
    *,
    candidate_count: int = 120,
    synthetic_item_count: int = 25,
    external_instances: Optional[Sequence[BinPackingInstance]] = None,
) -> Dict[str, object]:
    if candidate_count < 1:
        raise ValueError("candidate_count must be positive")
    synthetic_train, synthetic_validation, synthetic_test = (
        default_train_validation_test_suites(item_count=synthetic_item_count)
    )
    if external_instances is None:
        external_train, external_validation, external_test = (
            default_external_train_validation_test_suites()
        )
    else:
        external_train, external_validation, external_test = split_external_instances(
            external_instances
        )

    candidates = build_seed_candidate_programs(candidate_count)
    synthetic_summary = evaluate_candidate_suite(
        candidates=candidates,
        train_instances=synthetic_train,
        validation_instances=synthetic_validation,
        test_instances=synthetic_test,
    )
    external_summary = evaluate_candidate_suite(
        candidates=candidates,
        train_instances=external_train,
        validation_instances=external_validation,
        test_instances=external_test,
    )
    evaluator = BinPackingEvaluator()
    synthetic_top = _candidate_for(candidates, synthetic_summary.best_program_id)
    external_top = _candidate_for(candidates, external_summary.best_program_id)
    synthetic_top_external = evaluator.evaluate_program(
        synthetic_top.code,
        external_test,
        program_id=synthetic_top.program_id,
    )
    external_top_test = evaluator.evaluate_program(
        external_top.code,
        external_test,
        program_id=external_top.program_id,
    )
    external_top_validation = evaluator.evaluate_program(
        external_top.code,
        external_validation,
        program_id=external_top.program_id,
    )
    return {
        "phase": 9,
        "benchmark": "bin_packing_external",
        "source": "BPPLIB / OR-Library-style parser with small local fixtures",
        "candidate_count": candidate_count,
        "external_split": {
            "train_count": len(external_train),
            "validation_count": len(external_validation),
            "test_count": len(external_test),
            "train_ids": _instance_ids(external_train),
            "validation_ids": _instance_ids(external_validation),
            "test_ids": _instance_ids(external_test),
        },
        "synthetic_top_program_id": synthetic_top.program_id,
        "synthetic_top_validation_score": synthetic_summary.best_validation_score,
        "synthetic_top_external_test_score": synthetic_top_external.score,
        "best_external_program_id": external_top.program_id,
        "best_external_validation_score": external_top_validation.score,
        "best_external_test_score": external_top_test.score,
        "synthetic_to_external_gap": _gap(
            synthetic_summary.best_validation_score,
            synthetic_top_external.score,
        ),
        "external_generalization_gap": _gap(
            external_top_validation.score,
            external_top_test.score,
        ),
        "external_validation_baseline_scores": _baseline_scores(external_validation),
        "external_test_baseline_scores": _baseline_scores(external_test),
        "known_optimum": {
            "synthetic_top_external": _known_optimum_summary(
                synthetic_top_external,
                external_test,
            ).as_dict(),
            "external_top_test": _known_optimum_summary(
                external_top_test,
                external_test,
            ).as_dict(),
        },
        "top_programs": external_summary.top_programs,
        "claim_boundary": PHASE9_CLAIM_BOUNDARY,
    }


def _instance_from_bpplib_block(
    block: Mapping[str, object],
    source: str,
) -> BinPackingInstance:
    if "capacity" not in block or "weights" not in block:
        raise ValueError("BPPLIB-style instance requires capacity and weights")
    instance_id = str(block.get("name") or f"{source}-{_stable_seed(str(block))}")
    weights = [float(value) for value in block["weights"]]  # type: ignore[index]
    item_count = block.get("item_count")
    if item_count is not None and int(item_count) != len(weights):
        raise ValueError(
            f"{instance_id} expected {item_count} weights, got {len(weights)}"
        )
    known_optimum = block.get("known_optimum")
    return _external_instance(
        instance_id=instance_id,
        source=source,
        capacity=float(block["capacity"]),
        items=weights,
        known_optimum=int(known_optimum) if known_optimum is not None else None,
    )


def _external_instance(
    *,
    instance_id: str,
    source: str,
    capacity: float,
    items: Sequence[float],
    known_optimum: Optional[int],
) -> BinPackingInstance:
    return generate_instance(
        InstanceDistribution.EXTERNAL,
        seed=_stable_seed(f"{source}:{instance_id}"),
        item_count=0,
        capacity=capacity,
        items=items,
        instance_id=instance_id,
        source=source,
        known_optimum=known_optimum,
    )


def _baseline_scores(instances: Sequence[BinPackingInstance]) -> Dict[str, float]:
    return {
        name: _mean(float(result.bins_used) for result in _pack_all(packer, instances))
        for name, packer in BASELINE_PACKERS.items()
    }


def _pack_all(
    packer: object,
    instances: Sequence[BinPackingInstance],
) -> List[PackingResult]:
    return [packer(instance) for instance in instances]  # type: ignore[operator]


def _known_optimum_summary(
    result: ProgramEvaluation,
    instances: Sequence[BinPackingInstance],
) -> ExternalKnownOptimumSummary:
    known = [
        float(instance.known_optimum)
        for instance in instances
        if instance.known_optimum is not None
    ]
    if not known or result.score is None:
        return ExternalKnownOptimumSummary(None, result.score, None)
    average_known = _mean(known)
    return ExternalKnownOptimumSummary(
        average_known_optimum=average_known,
        average_bins_used=result.score,
        average_gap=result.score - average_known,
    )


def _candidate_for(
    candidates: Sequence[SeedCandidateProgram],
    program_id: str,
) -> SeedCandidateProgram:
    for candidate in candidates:
        if candidate.program_id == program_id:
            return candidate
    raise KeyError(program_id)


def _gap(left: Optional[float], right: Optional[float]) -> Optional[float]:
    if left is None or right is None:
        return None
    return abs(right - left)


def _instance_ids(instances: Iterable[BinPackingInstance]) -> Tuple[str, ...]:
    return tuple(instance.instance_id for instance in instances)


def _meaningful_lines(text: str) -> List[str]:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].split("//", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def _looks_like_bpplib(text: str) -> bool:
    upper = text.upper()
    return "CAPACITY:" in upper or "WEIGHTS:" in upper or "NAME:" in upper


def _is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def _stable_seed(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
