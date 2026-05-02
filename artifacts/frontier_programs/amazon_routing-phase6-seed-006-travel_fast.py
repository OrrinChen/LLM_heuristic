# candidate_id: phase6-seed-006-travel_fast
# benchmark: amazon_routing
# source: phase6_amazon_discovery
# objective_quality: 10.833333333333332
# runtime: 2.2e-05
# program_complexity: 11
# generalization_gap: 0.0
# selected_tradeoff: quality_runtime_driver_likeness_frontier


def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"]
