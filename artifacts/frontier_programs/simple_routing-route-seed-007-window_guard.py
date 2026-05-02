# candidate_id: route-seed-007-window_guard
# benchmark: simple_routing
# source: phase4_seed_library_plus_2opt
# objective_quality: 15.617200124999993
# runtime: 0.009996
# program_complexity: 49
# generalization_gap: 6.413389124999993
# selected_tradeoff: quality_runtime_generalization_frontier


def score_next_stop(state, candidate_stop):
    projected = state["elapsed_time"] + candidate_stop["travel_time"]
    lateness = max(0, projected - candidate_stop["due_time"])
    return candidate_stop["travel_time"] + 5.26 * lateness
