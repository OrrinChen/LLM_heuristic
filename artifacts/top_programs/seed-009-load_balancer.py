# candidate_id: seed-009-load_balancer
# benchmark: bin_packing
# code_hash: sha256:b11008e8b8bbd5155ea56688c83b875452479007147c9971a9b88f63a6825ef4
# score: 7.75


def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return abs(projected - 0.09)
