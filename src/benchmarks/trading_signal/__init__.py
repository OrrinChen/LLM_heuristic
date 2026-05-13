"""PIT-constrained trading-signal benchmark for program search."""

from benchmarks.trading_signal.evaluator import (
    SignalEvaluation,
    TradingSignalEvaluator,
)
from benchmarks.trading_signal.instances import (
    ALLOWED_SIGNAL_FEATURES,
    TradingSignalRow,
    TradingSignalSplits,
    build_default_trading_signal_splits,
    load_lob_feature_artifacts,
)
from benchmarks.trading_signal.report import (
    TRADING_SIGNAL_CLAIM_BOUNDARY,
    build_seed_signal_programs,
    build_trading_signal_report,
)
from benchmarks.trading_signal.validation import validate_trading_signal_code

__all__ = [
    "ALLOWED_SIGNAL_FEATURES",
    "SignalEvaluation",
    "TRADING_SIGNAL_CLAIM_BOUNDARY",
    "TradingSignalEvaluator",
    "TradingSignalRow",
    "TradingSignalSplits",
    "build_default_trading_signal_splits",
    "build_seed_signal_programs",
    "build_trading_signal_report",
    "load_lob_feature_artifacts",
    "validate_trading_signal_code",
]
