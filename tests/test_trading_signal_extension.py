from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from benchmarks.trading_signal import (
    ALLOWED_SIGNAL_FEATURES,
    TradingSignalEvaluator,
    build_default_trading_signal_splits,
    build_trading_signal_report,
    validate_trading_signal_code,
)
from reports.artifacts import export_report_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_trading_signal_static_validator_accepts_only_pit_features() -> None:
    code = """
def score_signal(features):
    raw = features["imbalance"] + 0.5 * features.get("ofi", 0.0)
    if features["spread"] > 0.05:
        raw *= 0.5
    return max(-1.0, min(1.0, raw))
"""

    result = validate_trading_signal_code(code)

    assert result.ok is True
    assert result.function_name == "score_signal"
    assert ALLOWED_SIGNAL_FEATURES == (
        "imbalance",
        "ofi",
        "trade_imbalance",
        "spread",
        "microprice",
        "realized_volatility",
    )


def test_trading_signal_static_validator_rejects_lookahead_features() -> None:
    for feature_name in (
        "future_return",
        "future return",
        "label",
        "future_midprice",
        "future midprice",
        "post_trade_pnl",
        "post-trade PnL",
    ):
        code = f"""
def score_signal(features):
    return features[{feature_name!r}]
"""

        result = validate_trading_signal_code(code)

        assert result.ok is False
        assert result.failure_reason is not None
        assert result.failure_reason.code == "lookahead_bias"


def test_trading_signal_static_validator_rejects_hallucinated_features() -> None:
    code = """
def score_signal(features):
    return features["magic_alpha"]
"""

    result = validate_trading_signal_code(code)

    assert result.ok is False
    assert result.failure_reason is not None
    assert result.failure_reason.code == "hallucinated_feature"


def test_trading_signal_evaluator_scores_valid_pit_strategy() -> None:
    splits = build_default_trading_signal_splits()
    evaluator = TradingSignalEvaluator(max_average_turnover=1.25)
    code = """
def score_signal(features):
    raw = features["imbalance"] + 0.25 * features["ofi"]
    if features["realized_volatility"] > 0.7:
        raw *= 0.5
    return max(-1.0, min(1.0, raw))
"""

    result = evaluator.evaluate_program(
        code,
        splits.validation,
        program_id="pit-valid",
    )

    assert result.ok is True
    assert result.failure_reason is None
    assert result.score is not None
    assert result.metrics["net_return"] > 0.0
    assert result.metrics["turnover"] >= 0.0
    assert result.metrics["max_drawdown"] >= 0.0
    assert result.metrics["program_complexity"] > 0


def test_trading_signal_evaluator_fails_invalid_position_output() -> None:
    evaluator = TradingSignalEvaluator()
    splits = build_default_trading_signal_splits()

    result = evaluator.evaluate_program(
        "def score_signal(features):\n    return 'long'\n",
        splits.validation,
        program_id="bad-output",
    )

    assert result.ok is False
    assert result.failure_reason == "invalid_position_output"


def test_trading_signal_evaluator_fails_leverage_violation() -> None:
    evaluator = TradingSignalEvaluator(max_abs_position=1.0)
    splits = build_default_trading_signal_splits()

    result = evaluator.evaluate_program(
        "def score_signal(features):\n    return 1.5\n",
        splits.validation,
        program_id="over-levered",
    )

    assert result.ok is False
    assert result.failure_reason == "leverage_violation"


def test_trading_signal_evaluator_fails_turnover_gate() -> None:
    evaluator = TradingSignalEvaluator(max_average_turnover=0.55)
    splits = build_default_trading_signal_splits()
    code = """
def score_signal(features):
    if features["imbalance"] >= 0:
        return 1.0
    return -1.0
"""

    result = evaluator.evaluate_program(
        code,
        splits.validation,
        program_id="churn",
    )

    assert result.ok is False
    assert result.failure_reason == "turnover_too_high"
    assert result.metrics["turnover"] > 0.55


def test_trading_signal_report_contains_pareto_evidence_and_claim_boundary() -> None:
    report = build_trading_signal_report(candidate_count=8)

    assert report["benchmark"] == "trading_signal"
    assert report["feature_schema"] == ALLOWED_SIGNAL_FEATURES
    assert report["requires_api_key"] is False
    assert report["requires_lob_artifacts"] is False
    assert report["pareto_axes"] == (
        "net_return",
        "turnover",
        "max_drawdown",
        "program_complexity",
    )
    assert len(report["candidate_rows"]) == 8
    assert len(report["pareto_rows"]) >= 1
    assert any(row["is_pareto_frontier"] for row in report["candidate_rows"])
    assert "does not claim tradable alpha" in report["claim_boundary"]


def test_cli_run_trading_signal_exports_summary(tmp_path: Path) -> None:
    result = _run_cli(
        "run",
        "--benchmark",
        "trading_signal",
        "--candidate-count",
        "8",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["benchmark"] == "trading_signal"
    assert payload["best_program_id"]
    assert payload["pareto_frontier_count"] >= 1

    summary = json.loads((tmp_path / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["benchmark"] == "trading_signal"
    assert summary["requires_api_key"] is False
    assert summary["requires_lob_artifacts"] is False


def test_report_export_includes_trading_signal_artifacts(tmp_path: Path) -> None:
    summary = export_report_artifacts(tmp_path, top_k=2)

    trading_summary = tmp_path / "reports" / "tables" / "trading_signal_summary.csv"
    trading_pareto = tmp_path / "reports" / "tables" / "trading_signal_pareto.csv"
    trading_plot = tmp_path / "reports" / "plots" / "trading_signal_frontier.json"

    assert trading_summary.is_file()
    assert trading_pareto.is_file()
    assert trading_plot.is_file()
    assert str(trading_summary) in summary["tables"]
    assert str(trading_pareto) in summary["tables"]
    assert str(trading_plot) in summary["extra_plot_series"]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "heuristic_discovery", *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
