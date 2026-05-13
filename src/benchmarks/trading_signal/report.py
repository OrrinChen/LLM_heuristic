from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence

from benchmarks.trading_signal.evaluator import SignalEvaluation, TradingSignalEvaluator
from benchmarks.trading_signal.instances import (
    ALLOWED_SIGNAL_FEATURES,
    TradingSignalSplits,
    build_default_trading_signal_splits,
)
from program_search.scoring import compute_program_complexity

TRADING_SIGNAL_CLAIM_BOUNDARY = (
    "sandboxed PIT trading-rule search evidence only; does not claim tradable "
    "alpha, investment advice, live execution readiness, SOTA, or production "
    "risk control"
)

TRADING_SIGNAL_PARETO_AXES = (
    "net_return",
    "turnover",
    "max_drawdown",
    "program_complexity",
)


@dataclass(frozen=True)
class SeedSignalProgram:
    program_id: str
    code: str
    explanation: str
    parent_id: Optional[str] = None
    generation: int = 0


def build_trading_signal_report(
    *,
    candidate_count: int = 8,
    splits: Optional[TradingSignalSplits] = None,
    max_average_turnover: float = 1.25,
) -> Dict[str, object]:
    dataset = splits or build_default_trading_signal_splits()
    evaluator = TradingSignalEvaluator(max_average_turnover=max_average_turnover)
    candidates = build_seed_signal_programs(candidate_count)
    rows = []
    for candidate in candidates:
        train = evaluator.evaluate_program(
            candidate.code,
            dataset.train,
            program_id=candidate.program_id,
        )
        validation = evaluator.evaluate_program(
            candidate.code,
            dataset.validation,
            program_id=candidate.program_id,
        )
        test = evaluator.evaluate_program(
            candidate.code,
            dataset.test,
            program_id=candidate.program_id,
        )
        rows.append(_candidate_row(candidate, train, validation, test))

    candidate_rows = _annotate_pareto(rows)
    pareto_rows = [row for row in candidate_rows if bool(row["is_pareto_frontier"])]
    eligible = [
        row
        for row in candidate_rows
        if row["validation_ok"] and row["validation_net_return"] is not None
    ]
    best = max(
        eligible,
        key=lambda row: (
            float(row["validation_net_return"]),
            -float(row["turnover"]),
            -float(row["program_complexity"]),
            str(row["program_id"]),
        ),
    )
    return {
        "phase": "trading_signal_extension",
        "benchmark": "trading_signal",
        "source": dataset.source,
        "feature_schema": ALLOWED_SIGNAL_FEATURES,
        "forbidden_inputs": (
            "future_return",
            "label",
            "future_midprice",
            "post_trade_pnl",
        ),
        "interface": "def score_signal(features): return position_score",
        "position_bounds": (-1.0, 1.0),
        "requires_api_key": False,
        "requires_lob_artifacts": not dataset.source.startswith("built_in"),
        "live_llm_required": False,
        "train_count": len(dataset.train),
        "validation_count": len(dataset.validation),
        "test_count": len(dataset.test),
        "candidate_count": len(candidate_rows),
        "candidate_rows": candidate_rows,
        "pareto_axes": TRADING_SIGNAL_PARETO_AXES,
        "pareto_rows": pareto_rows,
        "pareto_frontier_count": len(pareto_rows),
        "best_program_id": best["program_id"],
        "best_validation_net_return": best["validation_net_return"],
        "best_test_net_return": best["test_net_return"],
        "best_turnover": best["turnover"],
        "best_max_drawdown": best["max_drawdown"],
        "claim_boundary": TRADING_SIGNAL_CLAIM_BOUNDARY,
        "summary": (
            "Trading signal evidence evaluates compact `score_signal(features)` "
            "programs on point-in-time market features only. Labels and future "
            "returns stay inside the evaluator, while static checks, subprocess "
            "execution, leverage gates, turnover gates, and Pareto trade-offs "
            "bound the generated-code behavior."
        ),
    }


def build_seed_signal_programs(candidate_count: int = 8) -> Sequence[SeedSignalProgram]:
    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    templates = (
        (
            "signal-seed-000-flat",
            """
def score_signal(features):
    return 0.0
""",
            "flat no-position rule",
        ),
        (
            "signal-seed-001-imbalance",
            """
def score_signal(features):
    raw = features["imbalance"]
    return max(-1.0, min(1.0, raw))
""",
            "signed depth imbalance with hard position bounds",
        ),
        (
            "signal-seed-002-ofi",
            """
def score_signal(features):
    raw = 0.7 * features["ofi"]
    return max(-1.0, min(1.0, raw))
""",
            "order-flow imbalance proxy with hard position bounds",
        ),
        (
            "signal-seed-003-spread_guard",
            """
def score_signal(features):
    raw = features["imbalance"] + 0.25 * features["ofi"]
    if features["spread"] > 0.02:
        raw *= 0.45
    return max(-1.0, min(1.0, raw))
""",
            "depth signal scaled down when the spread is wider",
        ),
        (
            "signal-seed-004-vol_scaled",
            """
def score_signal(features):
    raw = features["imbalance"] + features["trade_imbalance"]
    scale = 1.0 + features["realized_volatility"]
    return max(-1.0, min(1.0, raw / scale))
""",
            "depth and trade imbalance damped by realized volatility",
        ),
        (
            "signal-seed-005-microprice_tilt",
            """
def score_signal(features):
    raw = (features["microprice"] - 100.0) * 8.0
    raw += 0.25 * features["imbalance"]
    return max(-1.0, min(1.0, raw))
""",
            "microprice tilt plus shallow depth imbalance",
        ),
        (
            "signal-seed-006-flow_blend",
            """
def score_signal(features):
    raw = 0.5 * features["imbalance"]
    raw += 0.3 * features["ofi"]
    raw += 0.2 * features["trade_imbalance"]
    return max(-1.0, min(1.0, raw))
""",
            "blend of PIT depth and flow features",
        ),
        (
            "signal-seed-007-turnover_stress",
            """
def score_signal(features):
    if features["imbalance"] >= 0:
        return 1.0
    return -1.0
""",
            "stress candidate for turnover gate evidence",
        ),
    )
    programs: List[SeedSignalProgram] = []
    for index in range(candidate_count):
        base_id, code, explanation = templates[index % len(templates)]
        if index < len(templates):
            programs.append(SeedSignalProgram(base_id, code.strip(), explanation))
            continue
        scale = 0.2 + 0.05 * (index % 7)
        program_id = f"signal-mut-{index:03d}-scaled_blend"
        variant = f"""
def score_signal(features):
    raw = {scale:.2f} * features["imbalance"]
    raw += {scale / 2.0:.2f} * features["ofi"]
    if features["spread"] > 0.024:
        raw *= 0.6
    return max(-1.0, min(1.0, raw))
"""
        programs.append(
            SeedSignalProgram(
                program_id=program_id,
                code=variant.strip(),
                explanation="deterministic scaled blend mutation",
                parent_id=base_id,
                generation=1,
            )
        )
    return tuple(programs)


def _candidate_row(
    candidate: SeedSignalProgram,
    train: SignalEvaluation,
    validation: SignalEvaluation,
    test: SignalEvaluation,
) -> Dict[str, object]:
    validation_metrics = validation.metrics
    return {
        "program_id": candidate.program_id,
        "parent_id": candidate.parent_id or "",
        "generation": candidate.generation,
        "source": "deterministic_seed_or_template_mutation",
        "train_ok": train.ok,
        "validation_ok": validation.ok,
        "test_ok": test.ok,
        "train_net_return": train.metrics.get("net_return"),
        "validation_net_return": validation.metrics.get("net_return"),
        "test_net_return": test.metrics.get("net_return"),
        "net_return": validation_metrics.get("net_return", 0.0),
        "turnover": validation_metrics.get("turnover", 0.0),
        "max_drawdown": validation_metrics.get("max_drawdown", 0.0),
        "program_complexity": compute_program_complexity(candidate.code),
        "runtime": validation.runtime,
        "failure_reason": validation.failure_reason or "",
        "claim": TRADING_SIGNAL_CLAIM_BOUNDARY,
        "code": candidate.code,
        "explanation": candidate.explanation,
    }


def _annotate_pareto(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    annotated: List[Dict[str, object]] = []
    for row in rows:
        peers = [peer for peer in rows if peer["validation_ok"]]
        dominated_by = [
            peer
            for peer in peers
            if peer["program_id"] != row["program_id"] and _dominates(peer, row)
        ]
        dominates_count = sum(
            1
            for peer in peers
            if peer["program_id"] != row["program_id"] and _dominates(row, peer)
        )
        enriched = dict(row)
        enriched["is_pareto_frontier"] = bool(row["validation_ok"]) and not dominated_by
        enriched["dominance_count"] = dominates_count
        enriched["selected_tradeoff"] = (
            "net_return_turnover_drawdown_complexity_frontier"
            if enriched["is_pareto_frontier"]
            else "dominated_or_failed_candidate"
        )
        annotated.append(enriched)
    return sorted(
        annotated,
        key=lambda row: (
            not bool(row["is_pareto_frontier"]),
            -float(row["net_return"]),
            float(row["turnover"]),
            str(row["program_id"]),
        ),
    )


def _dominates(
    challenger: Mapping[str, object],
    candidate: Mapping[str, object],
) -> bool:
    if not challenger["validation_ok"]:
        return False
    if not candidate["validation_ok"]:
        return True
    challenger_values = _axis_values(challenger)
    candidate_values = _axis_values(candidate)
    return all(
        left <= right for left, right in zip(challenger_values, candidate_values)
    ) and any(left < right for left, right in zip(challenger_values, candidate_values))


def _axis_values(row: Mapping[str, object]) -> Sequence[float]:
    return (
        -float(row["net_return"]),
        float(row["turnover"]),
        float(row["max_drawdown"]),
        float(row["program_complexity"]),
    )
