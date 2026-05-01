# candidate_id: seed-005-load_balancer
# benchmark: bin_packing
# code_hash: sha256:6747d8c8cf2d2caa8114e96cb40d192ffffc8bc0ba45ebdf632b5a6c1b74ce39
# score: 7.75


def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.05)
