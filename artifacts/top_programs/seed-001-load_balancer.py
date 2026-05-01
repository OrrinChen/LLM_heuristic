# candidate_id: seed-001-load_balancer
# benchmark: bin_packing
# code_hash: sha256:2f37218cbccf340db303b5d9fc542beb1a72a95375014d5c9c96e2eacb706662
# score: 7.75


def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.01)
