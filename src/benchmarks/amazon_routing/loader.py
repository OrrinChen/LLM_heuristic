from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence, Tuple, Union


@dataclass(frozen=True)
class PackageRecord:
    package_id: str
    weight: float = 0.0
    volume: float = 0.0


@dataclass(frozen=True)
class AmazonStop:
    stop_id: str
    zone_id: str
    x: float
    y: float
    service_time: float = 0.0
    ready_time: float = 0.0
    due_time: float = 1_000_000.0
    packages: Tuple[PackageRecord, ...] = ()


@dataclass(frozen=True)
class AmazonRoute:
    route_id: str
    station_code: str
    depot: AmazonStop
    stops: Tuple[AmazonStop, ...]
    travel_times: Mapping[str, Mapping[str, float]]
    actual_sequence: Tuple[str, ...]
    quality_label: str = ""

    @property
    def stop_ids(self) -> Tuple[str, ...]:
        return tuple(stop.stop_id for stop in self.stops)

    @property
    def all_location_ids(self) -> Tuple[str, ...]:
        return (self.depot.stop_id,) + self.stop_ids

    def stop_by_id(self, stop_id: str) -> AmazonStop:
        if stop_id == self.depot.stop_id:
            return self.depot
        for stop in self.stops:
            if stop.stop_id == stop_id:
                return stop
        raise KeyError(stop_id)

    def travel_time(self, from_stop_id: str, to_stop_id: str) -> float:
        return self.travel_times[from_stop_id][to_stop_id]


def load_route_record(record: Mapping[str, object]) -> AmazonRoute:
    route_id = str(record.get("route_id", ""))
    if not route_id:
        raise ValueError("missing_route_id")
    station_code = str(record.get("station_code", ""))
    depot = _parse_stop(record.get("depot"), default_stop_id="depot")
    stops = tuple(_parse_stop(stop) for stop in _sequence(record.get("stops")))
    stop_ids = [stop.stop_id for stop in stops]
    if len(set(stop_ids)) != len(stop_ids):
        raise ValueError("duplicate_stop_id")
    if depot.stop_id in set(stop_ids):
        raise ValueError("depot_stop_id_reused")

    actual_sequence = tuple(
        str(stop_id) for stop_id in record.get("actual_sequence", stop_ids)
    )
    if set(actual_sequence) != set(stop_ids) or len(actual_sequence) != len(stop_ids):
        raise ValueError("actual_sequence_must_match_stops")

    travel_times = _parse_travel_times(
        record.get("travel_times"), (depot.stop_id,) + tuple(stop_ids)
    )
    return AmazonRoute(
        route_id=route_id,
        station_code=station_code,
        depot=depot,
        stops=stops,
        travel_times=travel_times,
        actual_sequence=actual_sequence,
        quality_label=str(record.get("quality_label", "")),
    )


def load_route_records(records: object) -> Tuple[AmazonRoute, ...]:
    if isinstance(records, Mapping):
        records = records.get("routes", ())
    return tuple(load_route_record(record) for record in _sequence(records))


def load_route_records_from_json(path: Union[str, Path]) -> Tuple[AmazonRoute, ...]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return load_route_records(payload)


def _parse_stop(raw: object, default_stop_id: str = "") -> AmazonStop:
    if not isinstance(raw, Mapping):
        raise ValueError("stop_record_must_be_mapping")
    stop_id = str(raw.get("stop_id", default_stop_id))
    if not stop_id:
        raise ValueError("missing_stop_id")
    time_window = raw.get("time_window", (0.0, 1_000_000.0))
    ready_time, due_time = _parse_time_window(time_window)
    packages = tuple(
        _parse_package(package) for package in _sequence(raw.get("packages", ()))
    )
    return AmazonStop(
        stop_id=stop_id,
        zone_id=str(raw.get("zone_id", "")),
        x=float(raw.get("x", 0.0)),
        y=float(raw.get("y", 0.0)),
        service_time=float(
            raw.get("service_time", raw.get("planned_service_time", 0.0))
        ),
        ready_time=ready_time,
        due_time=due_time,
        packages=packages,
    )


def _parse_package(raw: object) -> PackageRecord:
    if not isinstance(raw, Mapping):
        raise ValueError("package_record_must_be_mapping")
    package_id = str(raw.get("package_id", ""))
    if not package_id:
        raise ValueError("missing_package_id")
    return PackageRecord(
        package_id=package_id,
        weight=float(raw.get("weight", 0.0)),
        volume=float(raw.get("volume", 0.0)),
    )


def _parse_time_window(raw: object) -> tuple[float, float]:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError("time_window_must_be_sequence")
    if len(raw) != 2:
        raise ValueError("time_window_must_have_two_values")
    ready_time = float(raw[0])
    due_time = float(raw[1])
    if ready_time > due_time:
        raise ValueError("invalid_time_window")
    return ready_time, due_time


def _parse_travel_times(
    raw: object,
    location_ids: Sequence[str],
) -> Mapping[str, Mapping[str, float]]:
    if not isinstance(raw, Mapping):
        raise ValueError("travel_times_must_be_mapping")
    expected = tuple(location_ids)
    parsed = {}
    for from_id in expected:
        row = raw.get(from_id)
        if not isinstance(row, Mapping):
            raise ValueError(f"missing_travel_time_row:{from_id}")
        parsed_row = {}
        for to_id in expected:
            if to_id not in row:
                raise ValueError(f"missing_travel_time_value:{from_id}->{to_id}")
            value = float(row[to_id])
            if value < 0:
                raise ValueError("negative_travel_time")
            parsed_row[to_id] = value
        parsed[from_id] = parsed_row
    return parsed


def _sequence(raw: object) -> Sequence[object]:
    if raw is None:
        return ()
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        return raw
    raise ValueError("expected_sequence")
