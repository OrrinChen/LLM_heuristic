from __future__ import annotations

import signal
from dataclasses import dataclass
from time import perf_counter
from types import FrameType
from typing import Any, Dict, Optional

from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    validate_candidate_code,
)

SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "pow": pow,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


class SandboxTimeoutError(TimeoutError):
    pass


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    value: Optional[float]
    runtime: float
    failure_reason: Optional[FailureReason] = None


def execute_scoring_function(
    code: str,
    *args: Any,
    config: Optional[ValidationConfig] = None,
    timeout_seconds: float = 1.0,
    **kwargs: Any,
) -> ExecutionResult:
    config = config or ValidationConfig()
    started = perf_counter()
    validation = validate_candidate_code(code, config)
    if not validation.ok:
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=validation.failure_reason,
        )

    namespace: Dict[str, Any] = {"__builtins__": SAFE_BUILTINS}
    try:
        compiled = compile(code, "<candidate>", "exec")
        exec(compiled, namespace, namespace)
        scoring_function = namespace[config.allowed_function]
        with _timeout(timeout_seconds):
            value = scoring_function(*args, **kwargs)
    except SandboxTimeoutError:
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=FailureReason(
                code="timeout",
                message=f"candidate exceeded {timeout_seconds} seconds",
            ),
        )
    except Exception as exc:  # noqa: BLE001 - structured sandbox failure boundary.
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=FailureReason(
                code="runtime_error",
                message=f"{type(exc).__name__}: {exc}",
            ),
        )

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ExecutionResult(
            ok=False,
            value=None,
            runtime=perf_counter() - started,
            failure_reason=FailureReason(
                code="non_numeric_score",
                message="scoring function must return an int or float",
            ),
        )

    return ExecutionResult(
        ok=True,
        value=float(value),
        runtime=perf_counter() - started,
        failure_reason=None,
    )


class _timeout:
    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        self.previous_handler: Any = None
        self.previous_timer: Any = None

    def __enter__(self) -> None:
        if self.seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.previous_handler = signal.getsignal(signal.SIGALRM)
        self.previous_timer = signal.setitimer(signal.ITIMER_REAL, self.seconds)
        signal.signal(signal.SIGALRM, self._handle_timeout)

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        if self.previous_handler is not None:
            signal.signal(signal.SIGALRM, self.previous_handler)
        if self.previous_timer is not None and self.previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, self.previous_timer[0])

    def _handle_timeout(
        self,
        signum: int,
        frame: Optional[FrameType],  # noqa: ARG002
    ) -> None:
        raise SandboxTimeoutError("candidate timed out")
