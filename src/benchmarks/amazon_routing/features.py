from __future__ import annotations

import math
from typing import Mapping, Sequence

from benchmarks.amazon_routing.loader import AmazonRoute

AMAZON_CANDIDATE_FEATURES = (
    "travel_time",
    "same_zone",
    "zone_transition_cost",
    "time_window_slack",
    "package_count",
    "package_weight",
    "service_time",
    "wait_time",
    "lateness",
    "zone_density",
    "distance_to_depot",
    "distance_from_depot_xy",
    "depot_angle",
    "cluster_compactness",
    "remaining_count",
    "remaining_same_zone_count",
    "remaining_zone_count",
)


def extract_route_features(route: AmazonRoute) -> Mapping[str, object]:
    packages = [package for stop in route.stops for package in stop.packages]
    zones = {stop.zone_id for stop in route.stops}
    return {
        "route_id": route.route_id,
        "station_code": route.station_code,
        "quality_label": route.quality_label,
        "stop_count": len(route.stops),
        "package_count": len(packages),
        "package_weight": sum(package.weight for package in packages),
        "zone_count": len(zones),
        "average_service_time": _mean([stop.service_time for stop in route.stops]),
        "historical_sequence": route.actual_sequence,
    }


def extract_stop_features(
    route: AmazonRoute,
    *,
    candidate_stop_id: str,
    current_stop_id: str,
    elapsed_time: float,
    visited: Sequence[str] = (),
) -> Mapping[str, object]:
    candidate = route.stop_by_id(candidate_stop_id)
    current = route.stop_by_id(current_stop_id)
    travel_time = route.travel_time(current_stop_id, candidate_stop_id)
    projected_arrival = elapsed_time + travel_time
    same_zone = (
        current_stop_id != route.depot.stop_id and current.zone_id == candidate.zone_id
    )
    visited_set = set(visited)
    remaining_stops = [stop for stop in route.stops if stop.stop_id not in visited_set]
    remaining_same_zone = [
        stop for stop in remaining_stops if stop.zone_id == candidate.zone_id
    ]
    remaining_zones = {stop.zone_id for stop in remaining_stops}
    zone_size = sum(stop.zone_id == candidate.zone_id for stop in route.stops)
    depot_angle = math.atan2(candidate.y - route.depot.y, candidate.x - route.depot.x)
    return {
        "stop_id": candidate.stop_id,
        "zone_id": candidate.zone_id,
        "x": candidate.x,
        "y": candidate.y,
        "travel_time": travel_time,
        "same_zone": 1.0 if same_zone else 0.0,
        "zone_transition_cost": 0.0 if same_zone else 1.0,
        "package_count": len(candidate.packages),
        "package_weight": sum(package.weight for package in candidate.packages),
        "service_time": candidate.service_time,
        "ready_time": candidate.ready_time,
        "due_time": candidate.due_time,
        "wait_time": max(0.0, candidate.ready_time - projected_arrival),
        "time_window_slack": candidate.due_time - projected_arrival,
        "lateness": max(0.0, projected_arrival - candidate.due_time),
        "distance_to_depot": route.travel_time(candidate_stop_id, route.depot.stop_id),
        "historical_position": route.actual_sequence.index(candidate_stop_id),
        "remaining_count": len(route.stops) - len(tuple(visited)),
        "remaining_same_zone_count": len(remaining_same_zone),
        "remaining_zone_count": len(remaining_zones),
        "zone_density": zone_size / len(route.stops),
        "distance_from_depot_xy": math.dist(
            (route.depot.x, route.depot.y), (candidate.x, candidate.y)
        ),
        "depot_angle": depot_angle,
        "cluster_compactness": len(remaining_same_zone) / max(1, len(remaining_stops)),
    }


def _mean(values: Sequence[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
