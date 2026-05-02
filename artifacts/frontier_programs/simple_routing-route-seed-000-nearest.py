# candidate_id: route-seed-000-nearest
# benchmark: simple_routing
# source: phase4_seed_library_plus_2opt
# objective_quality: 17.103554625000005
# runtime: 0.002244
# program_complexity: 11
# generalization_gap: 9.551715458333339
# selected_tradeoff: quality_runtime_generalization_frontier


def score_next_stop(state, candidate_stop):
    return candidate_stop["travel_time"]
