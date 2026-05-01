from __future__ import annotations

import multiprocessing
import os
import queue
from time import perf_counter
from typing import Any, Mapping, Optional

from sandbox.restricted_exec import SAFE_BUILTINS, ExecutionResult
from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    validate_candidate_code,
)


def execute_scoring_function_subprocess(
    code: str,
    *args: Any,
    config: Optional[ValidationConfig] = None,
    timeout_seconds: float = 1.0,
    memory_limit_mb: Optional[int] = None,
    **kwargs: Any,
) -> ExecutionResult:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if memory_limit_mb is not None and memory_limit_mb <= 0:
        raise ValueError("memory_limit_mb must be positive")

    config = config or ValidationConfig()
    started = perf_counter()
    validation = validate_candidate_code(code, config)
    if not validation.ok:
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=validation.failure_reason,
            metadata={"is_subprocess": False},
        )

    context = _multiprocessing_context()
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_child_main,
        args=(code, args, kwargs, config, memory_limit_mb, result_queue),
    )
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join(0.2)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(0.2)
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=FailureReason(
                code="timeout",
                message=f"candidate exceeded {timeout_seconds} seconds",
            ),
            metadata={
                "is_subprocess": True,
                "child_pid": process.pid,
                "memory_limit_mb": memory_limit_mb,
            },
        )

    try:
        payload = result_queue.get_nowait()
    except queue.Empty:
        failure_code = "process_error"
        if memory_limit_mb is not None and process.exitcode not in (0, None):
            failure_code = "memory_limit_exceeded"
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=FailureReason(
                code=failure_code,
                message=f"candidate subprocess exited with code {process.exitcode}",
            ),
            metadata={
                "is_subprocess": True,
                "child_pid": process.pid,
                "exitcode": process.exitcode,
                "memory_limit_mb": memory_limit_mb,
            },
        )

    failure = payload.get("failure_reason")
    failure_reason = None
    if isinstance(failure, Mapping):
        failure_reason = FailureReason(
            code=str(failure["code"]),
            message=str(failure["message"]),
            line=failure.get("line"),  # type: ignore[arg-type]
            column=failure.get("column"),  # type: ignore[arg-type]
        )
    return ExecutionResult(
        ok=bool(payload["ok"]),
        value=payload.get("value"),  # type: ignore[arg-type]
        runtime=perf_counter() - started,
        failure_reason=failure_reason,
        metadata={
            "is_subprocess": True,
            "child_pid": payload.get("child_pid", process.pid),
            "exitcode": process.exitcode,
            "memory_limit_mb": memory_limit_mb,
            "memory_limit_supported": payload.get("memory_limit_supported"),
        },
    )


def _child_main(
    code: str,
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    config: ValidationConfig,
    memory_limit_mb: Optional[int],
    result_queue: Any,
) -> None:
    memory_limit_supported = _apply_memory_limit(memory_limit_mb)
    if memory_limit_mb is not None and memory_limit_supported is False:
        _put_result(
            result_queue,
            ok=False,
            value=None,
            failure_reason=FailureReason(
                code="memory_limit_unsupported",
                message="subprocess memory limits are not supported on this platform",
            ),
            memory_limit_supported=memory_limit_supported,
        )
        return
    try:
        namespace = {"__builtins__": SAFE_BUILTINS}
        compiled = compile(code, "<candidate>", "exec")
        exec(compiled, namespace, namespace)
        value = namespace[config.allowed_function](*args, **dict(kwargs))
    except MemoryError:
        _put_result(
            result_queue,
            ok=False,
            value=None,
            failure_reason=FailureReason(
                code="memory_limit_exceeded",
                message="candidate exceeded subprocess memory limit",
            ),
            memory_limit_supported=memory_limit_supported,
        )
        return
    except Exception as exc:  # noqa: BLE001 - structured sandbox boundary.
        _put_result(
            result_queue,
            ok=False,
            value=None,
            failure_reason=FailureReason(
                code="runtime_error",
                message=f"{type(exc).__name__}: {exc}",
            ),
            memory_limit_supported=memory_limit_supported,
        )
        return

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _put_result(
            result_queue,
            ok=False,
            value=None,
            failure_reason=FailureReason(
                code="non_numeric_score",
                message="scoring function must return an int or float",
            ),
            memory_limit_supported=memory_limit_supported,
        )
        return

    _put_result(
        result_queue,
        ok=True,
        value=float(value),
        failure_reason=None,
        memory_limit_supported=memory_limit_supported,
    )


def _put_result(
    result_queue: Any,
    *,
    ok: bool,
    value: Optional[float],
    failure_reason: Optional[FailureReason],
    memory_limit_supported: Optional[bool],
) -> None:
    payload = {
        "ok": ok,
        "value": value,
        "child_pid": os.getpid(),
        "memory_limit_supported": memory_limit_supported,
        "failure_reason": None,
    }
    if failure_reason is not None:
        payload["failure_reason"] = {
            "code": failure_reason.code,
            "message": failure_reason.message,
            "line": failure_reason.line,
            "column": failure_reason.column,
        }
    result_queue.put(payload)


def _apply_memory_limit(memory_limit_mb: Optional[int]) -> Optional[bool]:
    if memory_limit_mb is None:
        return None
    if memory_limit_mb <= 0:
        raise ValueError("memory_limit_mb must be positive")
    try:
        import resource
    except ImportError:
        return False

    limit_bytes = int(memory_limit_mb) * 1024 * 1024
    applied = False
    for name in ("RLIMIT_AS", "RLIMIT_DATA"):
        resource_name = getattr(resource, name, None)
        if resource_name is None:
            continue
        soft, hard = resource.getrlimit(resource_name)
        target_hard = hard
        if hard in (-1, resource.RLIM_INFINITY):
            target_hard = limit_bytes
        else:
            target_hard = min(hard, limit_bytes)
        if soft in (-1, resource.RLIM_INFINITY):
            target_soft = limit_bytes
        else:
            target_soft = min(soft, limit_bytes)
        try:
            resource.setrlimit(resource_name, (target_soft, target_hard))
            applied = True
        except (OSError, ValueError):
            continue
    return applied


def _multiprocessing_context() -> multiprocessing.context.BaseContext:
    if os.name == "posix":
        return multiprocessing.get_context("fork")
    return multiprocessing.get_context("spawn")
