# candidate_id: g01-m001-seed-001-load_balancer
# benchmark: bin_packing
# code_hash: sha256:7efc35935f1eae4aaec18bdaef2a284f85b022b71b635faeba3f36fb933240ef
# score: 7.75


def score_bin(item_size, bin_remaining_capacity, bin_features):
    projected = bin_remaining_capacity - item_size
    if projected < 0:
        return 1000000
    return projected - 0.0925 * bin_features["items_in_bin"]
