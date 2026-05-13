from __future__ import annotations

import math
from dataclasses import dataclass
from time import perf_counter
from typing import Mapping, Optional, Sequence

from benchmarks.trading_signal.instances import TradingSignalRow
from benchmarks.trading_signal.validation import (
    TRADING_SIGNAL_VALIDATION_CONFIG,
    validate_trading_signal_code,
)
from program_search.scoring import compute_program_complexity
from sandbox.subprocess_exec import execute_scoring_function_subprocess


@dataclass(frozen=True)
class SignalEvaluation:
    program_id: str
    ok: bool
    score: Optional[float]
    metrics: Mapping[str, float]
    runtime: float
    failure_reason: Optional[str] = None


class TradingSignalEvaluator:
    def __init__(
        self,
        *,
        timeout_seconds: float = 0.2,
        max_abs_position: float = 1.0,
        max_average_turnover: float = 1.25,
        fee_bps: float = 1.0,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_abs_position = max_abs_position
        self.max_average_turnover = max_average_turnover
        self.fee_bps = fee_bps

    def evaluate_program(
        self,
        code: str,
        rows: Sequence[TradingSignalRow],
        *,
        program_id: str,
    ) -> SignalEvaluation:
        started = perf_counter()
        if not rows:
            return SignalEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={"failure_rate": 1.0},
                runtime=perf_counter() - started,
                failure_reason="no_rows",
            )
        validation = validate_trading_signal_code(code)
        if not validation.ok:
            return SignalEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics={
                    "net_return": 0.0,
                    "turnover": 0.0,
                    "max_drawdown": 0.0,
                    "program_complexity": float(compute_program_complexity(code)),
                    "failure_rate": 1.0,
                    "row_count": float(len(rows)),
                },
                runtime=perf_counter() - started,
                failure_reason=validation.failure_reason.code
                if validation.failure_reason
                else "static_validation_failed",
            )

        positions = []
        returns = []
        turnovers = []
        previous_position = 0.0
        for row in rows:
            result = execute_scoring_function_subprocess(
                code,
                row.candidate_features(),
                config=TRADING_SIGNAL_VALIDATION_CONFIG,
                timeout_seconds=self.timeout_seconds,
            )
            if not result.ok:
                reason = "invalid_position_output"
                if result.failure_reason is not None:
                    reason = _map_sandbox_failure(result.failure_reason.code)
                return SignalEvaluation(
                    program_id=program_id,
                    ok=False,
                    score=None,
                    metrics={
                        "net_return": 0.0,
                        "turnover": _mean(turnovers),
                        "max_drawdown": 0.0,
                        "program_complexity": float(compute_program_complexity(code)),
                        "failure_rate": 1.0,
                        "row_count": float(len(rows)),
                    },
                    runtime=perf_counter() - started,
                    failure_reason=reason,
                )
            position = float(result.value)
            if not math.isfinite(position):
                return self._failed_position(
                    code,
                    rows,
                    turnovers,
                    started,
                    program_id,
                    "invalid_position_output",
                )
            if abs(position) > self.max_abs_position + 1e-12:
                return self._failed_position(
                    code,
                    rows,
                    turnovers,
                    started,
                    program_id,
                    "leverage_violation",
                )
            turnover = abs(position - previous_position)
            net_return = position * row.next_return - turnover * self.fee_bps * 0.0001
            positions.append(position)
            turnovers.append(turnover)
            returns.append(net_return)
            previous_position = position

        average_turnover = _mean(turnovers)
        cumulative = 0.0
        peak = 0.0
        max_drawdown = 0.0
        for value in returns:
            cumulative += value
            peak = max(peak, cumulative)
            max_drawdown = max(max_drawdown, peak - cumulative)
        net_return = sum(returns)
        metrics = {
            "net_return": net_return,
            "gross_return": sum(
                position * row.next_return for position, row in zip(positions, rows)
            ),
            "turnover": average_turnover,
            "total_turnover": sum(turnovers),
            "max_drawdown": max_drawdown,
            "program_complexity": float(compute_program_complexity(code)),
            "failure_rate": 0.0,
            "row_count": float(len(rows)),
        }
        if average_turnover > self.max_average_turnover:
            return SignalEvaluation(
                program_id=program_id,
                ok=False,
                score=None,
                metrics=metrics,
                runtime=perf_counter() - started,
                failure_reason="turnover_too_high",
            )
        return SignalEvaluation(
            program_id=program_id,
            ok=True,
            score=-net_return,
            metrics=metrics,
            runtime=perf_counter() - started,
            failure_reason=None,
        )

    def _failed_position(
        self,
        code: str,
        rows: Sequence[TradingSignalRow],
        turnovers: Sequence[float],
        started: float,
        program_id: str,
        reason: str,
    ) -> SignalEvaluation:
        return SignalEvaluation(
            program_id=program_id,
            ok=False,
            score=None,
            metrics={
                "net_return": 0.0,
                "turnover": _mean(turnovers),
                "max_drawdown": 0.0,
                "program_complexity": float(compute_program_complexity(code)),
                "failure_rate": 1.0,
                "row_count": float(len(rows)),
            },
            runtime=perf_counter() - started,
            failure_reason=reason,
        )


def _map_sandbox_failure(code: str) -> str:
    if code in {"non_numeric_score", "runtime_error"}:
        return "invalid_position_output"
    return code


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0
