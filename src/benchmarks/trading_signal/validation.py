from __future__ import annotations

import ast
import re
from typing import Optional

from benchmarks.trading_signal.instances import ALLOWED_SIGNAL_FEATURES
from sandbox.static_checks import (
    FailureReason,
    ValidationConfig,
    ValidationResult,
    validate_candidate_code,
)

TRADING_SIGNAL_VALIDATION_CONFIG = ValidationConfig(allowed_function="score_signal")


def _normalize_feature_name(value: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", value.lower().replace("-", "_").replace(" ", "_"))


_ALLOWED_NORMALIZED_FEATURES = {
    _normalize_feature_name(feature) for feature in ALLOWED_SIGNAL_FEATURES
}
_ALLOWED_NORMALIZED_FEATURES.update(
    {
        "ofi",
        "tradeimbalance",
        "trade_imbalance",
        "realizedvolatility",
        "realized_volatility",
    }
)

_LOOKAHEAD_FEATURES = {
    "future_return",
    "futurereturn",
    "label",
    "future_midprice",
    "futuremidprice",
    "post_trade_pnl",
    "posttradepnl",
    "post_trade_profit_and_loss",
}


def validate_trading_signal_code(code: str) -> ValidationResult:
    base = validate_candidate_code(code, TRADING_SIGNAL_VALIDATION_CONFIG)
    if not base.ok:
        return base
    try:
        module = ast.parse(code)
    except SyntaxError as exc:
        return _fail("syntax_error", exc.msg, exc.lineno, exc.offset)
    function = module.body[0]
    if not isinstance(function, ast.FunctionDef):
        return _fail("missing_allowed_function", "candidate must define score_signal")
    feature_failure = _find_disallowed_feature_access(function)
    if feature_failure is not None:
        return feature_failure
    return base


def _find_disallowed_feature_access(
    function: ast.FunctionDef,
) -> Optional[ValidationResult]:
    for node in ast.walk(function):
        key_node: Optional[ast.AST] = None
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "features"
        ):
            key_node = node.slice
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "features"
            and node.func.attr == "get"
        ):
            if not node.args:
                return _fail(
                    "hallucinated_feature",
                    "features.get must name an allowed PIT feature",
                    node.lineno,
                    node.col_offset,
                )
            key_node = node.args[0]
        if key_node is None:
            continue
        feature_name = _literal_string(key_node)
        if feature_name is None:
            return _fail(
                "hallucinated_feature",
                "dynamic feature keys are blocked for trading signals",
                getattr(key_node, "lineno", None),
                getattr(key_node, "col_offset", None),
            )
        normalized = _normalize_feature_name(feature_name)
        if normalized in _LOOKAHEAD_FEATURES:
            return _fail(
                "lookahead_bias",
                f"feature {feature_name!r} would expose labels or future data",
                getattr(key_node, "lineno", None),
                getattr(key_node, "col_offset", None),
            )
        if normalized not in _ALLOWED_NORMALIZED_FEATURES:
            return _fail(
                "hallucinated_feature",
                f"feature {feature_name!r} is outside the PIT feature schema",
                getattr(key_node, "lineno", None),
                getattr(key_node, "col_offset", None),
            )
    return None


def _literal_string(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):  # pragma: no cover - Python <3.8 compatibility.
        return node.s
    return None


def _fail(
    code: str,
    message: str,
    line: Optional[int] = None,
    column: Optional[int] = None,
) -> ValidationResult:
    return ValidationResult(
        ok=False,
        failure_reason=FailureReason(
            code=code,
            message=message,
            line=line,
            column=column,
        ),
    )
