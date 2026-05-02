# candidate_id: seed-001-load_balancer
# benchmark: bin_packing
# source: phase2_seed_library
# objective_quality: 7.75
# runtime: 0.02368
# program_complexity: 32
# generalization_gap: 0.6500000000000004
# selected_tradeoff: quality_runtime_generalization_frontier


def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.01)
