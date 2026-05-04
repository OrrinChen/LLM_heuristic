from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Mapping, Optional, Sequence, Union

from benchmarks.bin_packing.evaluator import (
    BinPackingEvaluator,
    SeedCandidateProgram,
    build_seed_candidate_programs,
)
from benchmarks.bin_packing.instances import (
    BinPackingInstance,
    default_train_validation_test_suites,
)

PHASE17_CLAIM_BOUNDARY = (
    "local parallel and checkpoint evidence only; no paid cloud execution, "
    "cloud-provider binding, or scale-performance superiority claim"
)


@dataclass(frozen=True)
class ParallelEvaluationConfig:
    mode: str = "sequential"
    max_workers: int = 2
    candidate_budget: Optional[int] = None
    cost_budget: Optional[float] = None
    cost_per_candidate: float = 1.0
    checkpoint_path: Optional[Union[str, Path]] = None
    resume: bool = False
    timeout_seconds: float = 0.25


@dataclass(frozen=True)
class CandidateEvaluationRecord:
    candidate_id: str
    ok: bool
    train_score: Optional[float]
    validation_score: Optional[float]
    test_score: Optional[float]
    failure_reason: str
    runtime: float

    def as_dict(self) -> Mapping[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "ok": self.ok,
            "train_score": self.train_score,
            "validation_score": self.validation_score,
            "test_score": self.test_score,
            "failure_reason": self.failure_reason,
            "runtime": self.runtime,
        }


@dataclass(frozen=True)
class ParallelRunResult:
    records: List[CandidateEvaluationRecord]
    top_program_ids: List[str]
    stop_reason: str
    parallelism: str
    worker_count: int
    estimated_cost: float
    checkpoint_path: Optional[str]

    @property
    def evaluated_count(self) -> int:
        return len(self.records)

    @property
    def successful_count(self) -> int:
        return sum(1 for record in self.records if record.ok)

    @property
    def record_by_id(self) -> Mapping[str, CandidateEvaluationRecord]:
        return {record.candidate_id: record for record in self.records}

    @property
    def result_signature(self) -> Sequence[Mapping[str, object]]:
        return tuple(
            {
                "candidate_id": record.candidate_id,
                "ok": record.ok,
                "train_score": _stable_score(record.train_score),
                "validation_score": _stable_score(record.validation_score),
                "test_score": _stable_score(record.test_score),
                "failure_reason": record.failure_reason,
            }
            for record in self.records
        )

    def as_dict(self) -> Mapping[str, object]:
        return {
            "records": [record.as_dict() for record in self.records],
            "top_program_ids": self.top_program_ids,
            "stop_reason": self.stop_reason,
            "parallelism": self.parallelism,
            "worker_count": self.worker_count,
            "evaluated_count": self.evaluated_count,
            "successful_count": self.successful_count,
            "estimated_cost": self.estimated_cost,
            "checkpoint_path": self.checkpoint_path,
            "result_signature": list(self.result_signature),
        }


def run_candidate_evaluation_batch(
    candidates: Sequence[SeedCandidateProgram],
    train_instances: Sequence[BinPackingInstance],
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
    *,
    config: Optional[ParallelEvaluationConfig] = None,
) -> ParallelRunResult:
    resolved = config or ParallelEvaluationConfig()
    if resolved.mode not in {"sequential", "parallel"}:
        raise ValueError("mode must be sequential or parallel")
    if resolved.max_workers < 1:
        raise ValueError("max_workers must be positive")
    if resolved.cost_per_candidate <= 0:
        raise ValueError("cost_per_candidate must be positive")

    candidate_by_id = {candidate.program_id: candidate for candidate in candidates}
    order = {candidate.program_id: index for index, candidate in enumerate(candidates)}
    checkpoint_path = (
        Path(resolved.checkpoint_path) if resolved.checkpoint_path is not None else None
    )
    loaded = (
        _load_checkpoint_records(checkpoint_path, candidate_by_id)
        if checkpoint_path is not None and resolved.resume
        else {}
    )

    selected: List[SeedCandidateProgram] = []
    stop_reason = "complete"
    planned_total = len(loaded)
    planned_cost = planned_total * resolved.cost_per_candidate
    for candidate in candidates:
        if candidate.program_id in loaded:
            continue
        if (
            resolved.candidate_budget is not None
            and planned_total >= resolved.candidate_budget
        ):
            stop_reason = "candidate_budget_exhausted"
            break
        if (
            resolved.cost_budget is not None
            and planned_cost + resolved.cost_per_candidate > resolved.cost_budget
        ):
            stop_reason = "cost_budget_exhausted"
            break
        selected.append(candidate)
        planned_total += 1
        planned_cost += resolved.cost_per_candidate

    process_pool_available = resolved.mode == "parallel" and _can_spawn_process_pool()
    if process_pool_available and selected:
        new_records = _run_parallel(
            selected,
            train_instances,
            validation_instances,
            test_instances,
            max_workers=resolved.max_workers,
            timeout_seconds=resolved.timeout_seconds,
        )
    else:
        new_records = [
            _evaluate_candidate_record(
                candidate,
                train_instances,
                validation_instances,
                test_instances,
                timeout_seconds=resolved.timeout_seconds,
            )
            for candidate in selected
        ]
    records_by_id = {
        **loaded,
        **{record.candidate_id: record for record in new_records},
    }
    records = sorted(
        records_by_id.values(), key=lambda record: order[record.candidate_id]
    )
    result = _build_result(
        records,
        stop_reason=stop_reason,
        parallelism=(
            "process"
            if process_pool_available
            else "sequential_fallback"
            if resolved.mode == "parallel"
            else "sequential"
        ),
        worker_count=resolved.max_workers if process_pool_available else 1,
        estimated_cost=len(records) * resolved.cost_per_candidate,
        checkpoint_path=str(checkpoint_path) if checkpoint_path is not None else None,
    )
    if checkpoint_path is not None:
        _write_checkpoint(checkpoint_path, result)
    return result


def build_phase17_report(
    *,
    candidate_count: int = 12,
    item_count: int = 14,
    max_workers: int = 2,
) -> Dict[str, object]:
    train, validation, test = default_train_validation_test_suites(
        item_count=item_count
    )
    candidates = build_seed_candidate_programs(candidate_count)
    sequential = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="sequential"),
    )
    parallel = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="parallel", max_workers=max_workers),
    )
    failure_candidates = [
        SeedCandidateProgram(
            program_id="phase17-worker-crash",
            code=None,  # type: ignore[arg-type]
            explanation="forces unexpected worker exception",
        ),
        *candidates[: min(6, len(candidates))],
    ]
    failure_run = run_candidate_evaluation_batch(
        failure_candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(mode="parallel", max_workers=max_workers),
    )
    budget_run = run_candidate_evaluation_batch(
        candidates,
        train,
        validation,
        test,
        config=ParallelEvaluationConfig(
            mode="parallel",
            max_workers=max_workers,
            cost_budget=3.0,
            cost_per_candidate=1.0,
        ),
    )
    with TemporaryDirectory() as directory:
        checkpoint_path = Path(directory) / "phase17_checkpoint.json"
        run_candidate_evaluation_batch(
            candidates,
            train,
            validation,
            test,
            config=ParallelEvaluationConfig(
                mode="sequential",
                candidate_budget=max(1, candidate_count // 2),
                checkpoint_path=checkpoint_path,
            ),
        )
        resumed = run_candidate_evaluation_batch(
            candidates,
            train,
            validation,
            test,
            config=ParallelEvaluationConfig(
                mode="parallel",
                max_workers=max_workers,
                checkpoint_path=checkpoint_path,
                resume=True,
            ),
        )

    failed_record = failure_run.record_by_id["phase17-worker-crash"]
    return {
        "phase": 17,
        "benchmark": "parallel_runner",
        "candidate_count": candidate_count,
        "worker_count": max_workers,
        "parallel_matches_sequential": (
            parallel.result_signature == sequential.result_signature
        ),
        "sequential_top_program_ids": tuple(sequential.top_program_ids),
        "parallel_top_program_ids": tuple(parallel.top_program_ids),
        "checkpoint_resume_matches_full": (
            resumed.result_signature == sequential.result_signature
        ),
        "failed_worker_recorded": failed_record.failure_reason.startswith(
            "worker_exception"
        ),
        "successful_after_failure": failure_run.successful_count,
        "cost_budget_stop_reason": budget_run.stop_reason,
        "cost_budget_evaluated_candidates": budget_run.evaluated_count,
        "estimated_cost": budget_run.estimated_cost,
        "cloud_adapter_status": "dry_run_only",
        "cloud_adapter_reason": (
            "Cloud execution remains adapter-only to avoid paid services and "
            "provider-specific binding."
        ),
        "claim_boundary": PHASE17_CLAIM_BOUNDARY,
        "checkpoint_artifact": {
            "schema_version": 1,
            "phase": 17,
            "benchmark": "parallel_runner",
            "stop_reason": resumed.stop_reason,
            "parallelism": resumed.parallelism,
            "worker_count": resumed.worker_count,
            "results": [
                _checkpoint_artifact_record(record) for record in resumed.records
            ],
        },
    }


def _run_parallel(
    candidates: Sequence[SeedCandidateProgram],
    train_instances: Sequence[BinPackingInstance],
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
    *,
    max_workers: int,
    timeout_seconds: float,
) -> Sequence[CandidateEvaluationRecord]:
    worker_count = min(max_workers, len(candidates))
    payloads = [
        (
            candidate,
            train_instances,
            validation_instances,
            test_instances,
            timeout_seconds,
        )
        for candidate in candidates
    ]
    records: List[CandidateEvaluationRecord] = []
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(_evaluate_candidate_worker, payload): payload[0].program_id
            for payload in payloads
        }
        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as exc:  # noqa: BLE001 - worker boundary.
                records.append(
                    CandidateEvaluationRecord(
                        candidate_id=futures[future],
                        ok=False,
                        train_score=None,
                        validation_score=None,
                        test_score=None,
                        failure_reason=(
                            f"worker_exception: {type(exc).__name__}: {exc}"
                        ),
                        runtime=0.0,
                    )
                )
    return records


def _can_spawn_process_pool() -> bool:
    main_module = sys.modules.get("__main__")
    main_file = getattr(main_module, "__file__", "")
    return bool(
        main_file and not str(main_file).startswith("<") and Path(main_file).exists()
    )


def _evaluate_candidate_worker(payload: object) -> CandidateEvaluationRecord:
    candidate, train, validation, test, timeout_seconds = payload
    return _evaluate_candidate_record(
        candidate,
        train,
        validation,
        test,
        timeout_seconds=timeout_seconds,
    )


def _evaluate_candidate_record(
    candidate: SeedCandidateProgram,
    train_instances: Sequence[BinPackingInstance],
    validation_instances: Sequence[BinPackingInstance],
    test_instances: Sequence[BinPackingInstance],
    *,
    timeout_seconds: float,
) -> CandidateEvaluationRecord:
    try:
        evaluator = BinPackingEvaluator(timeout_seconds=timeout_seconds)
        train = evaluator.evaluate_program(
            candidate.code,
            train_instances,
            program_id=candidate.program_id,
        )
        validation = evaluator.evaluate_program(
            candidate.code,
            validation_instances,
            program_id=candidate.program_id,
        )
        test = evaluator.evaluate_program(
            candidate.code,
            test_instances,
            program_id=candidate.program_id,
        )
        failure_reason = (
            validation.failure_reason
            or train.failure_reason
            or test.failure_reason
            or ""
        )
        return CandidateEvaluationRecord(
            candidate_id=candidate.program_id,
            ok=validation.ok and train.ok and test.ok,
            train_score=train.score,
            validation_score=validation.score,
            test_score=test.score,
            failure_reason=failure_reason,
            runtime=train.runtime + validation.runtime + test.runtime,
        )
    except Exception as exc:  # noqa: BLE001 - preserve batch health.
        return CandidateEvaluationRecord(
            candidate_id=candidate.program_id,
            ok=False,
            train_score=None,
            validation_score=None,
            test_score=None,
            failure_reason=f"worker_exception: {type(exc).__name__}: {exc}",
            runtime=0.0,
        )


def _build_result(
    records: Sequence[CandidateEvaluationRecord],
    *,
    stop_reason: str,
    parallelism: str,
    worker_count: int,
    estimated_cost: float,
    checkpoint_path: Optional[str],
) -> ParallelRunResult:
    successful = [
        record
        for record in records
        if record.validation_score is not None and record.failure_reason == ""
    ]
    top = sorted(
        successful,
        key=lambda record: (
            float(record.validation_score)
            if record.validation_score is not None
            else float("inf"),
            record.candidate_id,
        ),
    )[:5]
    return ParallelRunResult(
        records=list(records),
        top_program_ids=[record.candidate_id for record in top],
        stop_reason=stop_reason,
        parallelism=parallelism,
        worker_count=worker_count,
        estimated_cost=estimated_cost,
        checkpoint_path=checkpoint_path,
    )


def _write_checkpoint(path: Path, result: ParallelRunResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "phase": 17,
        "benchmark": "parallel_runner",
        "stop_reason": result.stop_reason,
        "parallelism": result.parallelism,
        "worker_count": result.worker_count,
        "estimated_cost": result.estimated_cost,
        "results": [record.as_dict() for record in result.records],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _load_checkpoint_records(
    path: Optional[Path],
    candidate_by_id: Mapping[str, SeedCandidateProgram],
) -> Mapping[str, CandidateEvaluationRecord]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = {}
    for row in payload.get("results", []):
        candidate_id = str(row["candidate_id"])
        if candidate_id not in candidate_by_id:
            continue
        records[candidate_id] = CandidateEvaluationRecord(
            candidate_id=candidate_id,
            ok=bool(row["ok"]),
            train_score=_optional_float(row.get("train_score")),
            validation_score=_optional_float(row.get("validation_score")),
            test_score=_optional_float(row.get("test_score")),
            failure_reason=str(row.get("failure_reason") or ""),
            runtime=float(row.get("runtime") or 0.0),
        )
    return records


def _checkpoint_artifact_record(
    record: CandidateEvaluationRecord,
) -> Mapping[str, object]:
    payload = dict(record.as_dict())
    payload.pop("runtime", None)
    return payload


def _optional_float(value: object) -> Optional[float]:
    if value is None:
        return None
    return float(value)


def _stable_score(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 6)
