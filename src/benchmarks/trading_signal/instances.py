from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Union

ALLOWED_SIGNAL_FEATURES = (
    "imbalance",
    "ofi",
    "trade_imbalance",
    "spread",
    "microprice",
    "realized_volatility",
)

_FEATURE_COLUMN_ALIASES = {
    "imbalance": (
        "imbalance",
        "imbalance_l1",
        "imbalance_l2",
        "imbalance_l5",
        "imbalance_l10",
    ),
    "ofi": ("ofi", "OFI", "ofi_l1", "ofi_l2", "ofi_l5", "ofi_l10"),
    "trade_imbalance": (
        "trade_imbalance",
        "trade imbalance",
        "trade_flow_imbalance",
        "agg_trade_imbalance",
    ),
    "spread": ("spread", "spread_bps", "quoted_spread"),
    "microprice": ("microprice", "micro_price", "midprice", "mid_price"),
    "realized_volatility": (
        "realized_volatility",
        "realized volatility",
        "rv",
        "volatility",
    ),
}

_RETURN_COLUMN_ALIASES = (
    "next_return",
    "future_return",
    "future return",
    "label_return",
    "label",
    "target",
)


@dataclass(frozen=True)
class TradingSignalRow:
    timestamp: int
    features: Mapping[str, float]
    next_return: float
    source: str = "built_in_fixture"

    def candidate_features(self) -> Dict[str, float]:
        return {
            name: float(self.features.get(name, 0.0))
            for name in ALLOWED_SIGNAL_FEATURES
        }


@dataclass(frozen=True)
class TradingSignalSplits:
    train: Sequence[TradingSignalRow]
    validation: Sequence[TradingSignalRow]
    test: Sequence[TradingSignalRow]
    source: str = "built_in_small_deterministic"

    @property
    def all_rows(self) -> Sequence[TradingSignalRow]:
        return tuple(self.train) + tuple(self.validation) + tuple(self.test)


def build_default_trading_signal_splits() -> TradingSignalSplits:
    rows: List[TradingSignalRow] = []
    signs = (1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1, -1)
    for index in range(24):
        sign = signs[index % len(signs)]
        scale = 0.34 + 0.025 * (index % 5)
        spread = 0.012 + 0.004 * (index % 4)
        volatility = 0.22 + 0.08 * (index % 6)
        imbalance = sign * scale
        ofi = sign * (0.18 + 0.02 * (index % 3))
        trade_imbalance = sign * (0.10 + 0.015 * (index % 4))
        microprice = 100.0 + sign * (0.018 + 0.004 * (index % 5))
        next_return = sign * (0.0022 + 0.0002 * (index % 4))
        rows.append(
            TradingSignalRow(
                timestamp=index,
                features={
                    "imbalance": imbalance,
                    "ofi": ofi,
                    "trade_imbalance": trade_imbalance,
                    "spread": spread,
                    "microprice": microprice,
                    "realized_volatility": volatility,
                },
                next_return=next_return,
            )
        )
    return TradingSignalSplits(
        train=tuple(rows[:12]),
        validation=tuple(rows[12:18]),
        test=tuple(rows[18:24]),
    )


def load_lob_feature_artifacts(
    path: Union[str, Path],
    *,
    max_rows: int = 240,
) -> TradingSignalSplits:
    """Load optional local LOB feature artifacts without making them required.

    The default O2 reproduction path never calls this loader. It supports small
    CSV/JSON/JSONL files through the stdlib and attempts parquet only when a
    local pandas/pyarrow stack is already installed.
    """

    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"trading data path does not exist: {root}")
    rows: List[TradingSignalRow] = []
    for data_path in _candidate_data_paths(root):
        rows.extend(_load_rows_from_path(data_path, max_rows=max_rows - len(rows)))
        if len(rows) >= max_rows:
            break
    if not rows:
        raise ValueError(
            "no loadable trading signal rows found; provide CSV/JSON/JSONL/parquet "
            "features or a manifest referencing them"
        )
    return _split_rows(rows[:max_rows], source=f"local_lob_artifact:{root}")


def _split_rows(
    rows: Sequence[TradingSignalRow],
    *,
    source: str,
) -> TradingSignalSplits:
    if len(rows) < 3:
        raise ValueError("at least three rows are required for train/validation/test")
    train_end = max(1, int(len(rows) * 0.6))
    validation_end = max(train_end + 1, int(len(rows) * 0.8))
    validation_end = min(validation_end, len(rows) - 1)
    return TradingSignalSplits(
        train=tuple(rows[:train_end]),
        validation=tuple(rows[train_end:validation_end]),
        test=tuple(rows[validation_end:]),
        source=source,
    )


def _candidate_data_paths(root: Path) -> Sequence[Path]:
    if root.is_dir():
        paths = [
            path
            for path in sorted(root.rglob("*"))
            if path.suffix.lower() in {".csv", ".json", ".jsonl", ".parquet"}
        ]
        return tuple(paths)
    if root.suffix.lower() == ".json":
        referenced = _paths_from_manifest(root)
        if referenced:
            return referenced
    return (root,)


def _paths_from_manifest(path: Path) -> Sequence[Path]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ()
    paths: List[Path] = []
    for value in _walk_json_values(payload):
        if not isinstance(value, str):
            continue
        if not value.lower().endswith((".csv", ".json", ".jsonl", ".parquet")):
            continue
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = path.parent / candidate
        if candidate.exists():
            paths.append(candidate)
    return tuple(paths)


def _walk_json_values(value: object) -> Iterable[object]:
    if isinstance(value, Mapping):
        for item in value.values():
            yield from _walk_json_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_json_values(item)
    else:
        yield value


def _load_rows_from_path(path: Path, *, max_rows: int) -> Sequence[TradingSignalRow]:
    if max_rows <= 0:
        return ()
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            return _rows_from_dicts(
                csv.DictReader(handle),
                source=str(path),
                max_rows=max_rows,
            )
    if suffix == ".jsonl":
        records = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return _rows_from_dicts(records, source=str(path), max_rows=max_rows)
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return _rows_from_dicts(payload, source=str(path), max_rows=max_rows)
        if isinstance(payload, Mapping) and isinstance(payload.get("rows"), list):
            return _rows_from_dicts(
                payload["rows"],
                source=str(path),
                max_rows=max_rows,
            )
        referenced = _paths_from_manifest(path)
        rows: List[TradingSignalRow] = []
        for referenced_path in referenced:
            rows.extend(
                _load_rows_from_path(referenced_path, max_rows=max_rows - len(rows))
            )
            if len(rows) >= max_rows:
                break
        return tuple(rows)
    if suffix == ".parquet":
        return _load_parquet_rows(path, max_rows=max_rows)
    return ()


def _load_parquet_rows(path: Path, *, max_rows: int) -> Sequence[TradingSignalRow]:
    try:
        import pandas as pd  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001 - optional local adapter dependency.
        raise RuntimeError(
            "parquet trading artifacts require a local pandas/pyarrow installation"
        ) from exc
    frame = pd.read_parquet(path)
    if max_rows:
        frame = frame.head(max_rows)
    return _rows_from_dicts(
        frame.to_dict(orient="records"),
        source=str(path),
        max_rows=max_rows,
    )


def _rows_from_dicts(
    records: Iterable[Mapping[str, object]],
    *,
    source: str,
    max_rows: int,
) -> Sequence[TradingSignalRow]:
    rows: List[TradingSignalRow] = []
    for index, record in enumerate(records):
        if len(rows) >= max_rows:
            break
        features = {
            feature: _float_from_record(record, aliases, default=0.0)
            for feature, aliases in _FEATURE_COLUMN_ALIASES.items()
        }
        next_return = _float_from_record(record, _RETURN_COLUMN_ALIASES, default=0.0)
        timestamp = int(
            _float_from_record(
                record,
                ("timestamp", "ts", "event_index"),
                default=index,
            )
        )
        rows.append(
            TradingSignalRow(
                timestamp=timestamp,
                features=features,
                next_return=next_return,
                source=source,
            )
        )
    return tuple(rows)


def _float_from_record(
    record: Mapping[str, object],
    aliases: Sequence[str],
    *,
    default: float,
) -> float:
    for alias in aliases:
        if alias not in record:
            continue
        value = record[alias]
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default
