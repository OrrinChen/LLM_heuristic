# candidate_id: g01-m002-seed-005-load_balancer
# benchmark: bin_packing
# code_hash: sha256:f4eaa6e2a370f7445a2c855688c14613f41c71bc8b477d993bc9ab0902a5d6dc
# score: 7.75


def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected + 0.0446 * bin_features["current_load"]
