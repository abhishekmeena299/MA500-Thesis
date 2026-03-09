import itertools
from functools import lru_cache

def all_edges(n):
    return tuple(tuple(sorted((i, j))) for i in range(n) for j in range(i + 1, n))

def all_triangles(n):
    return tuple(tuple(sorted(tri)) for tri in itertools.combinations(range(n), 3))

@lru_cache(maxsize=None)
def has_maker_triangle(n, maker_edges_bits):
    triangles = all_triangles(n)
    for tri in triangles:
        mask = 0
        for e in itertools.combinations(tri, 2):
            idx = EDGE_INDEX[e]
            mask |= (1 << idx)
        if (maker_edges_bits & mask) == mask:
            return True
    return False

@lru_cache(maxsize=None)
def maker_can_win(n, rem_edges_bits, maker_edges_bits, breaker_edges_bits, breaker_bias, maker_turn):
    if has_maker_triangle(n, maker_edges_bits):
        return True
    if rem_edges_bits == 0:
        return False
    # Encode available edge indices for fast ops
    edge_indices = [i for i in range(EDGE_COUNT) if (rem_edges_bits & (1 << i))]
    if maker_turn:
        for e in edge_indices:
            next_rem = rem_edges_bits & ~(1 << e)
            next_maker = maker_edges_bits | (1 << e)
            if maker_can_win(n, next_rem, next_maker, breaker_edges_bits, breaker_bias, False):
                return True
        return False
    else:
        b = min(breaker_bias, len(edge_indices))
        for breaker_choice in itertools.combinations(edge_indices, b):
            next_rem = rem_edges_bits
            next_breaker = breaker_edges_bits
            for e in breaker_choice:
                next_rem &= ~(1 << e)
                next_breaker |= (1 << e)
            if not maker_can_win(n, next_rem, maker_edges_bits, next_breaker, breaker_bias, True):
                return False
        return True

def threshold_for_n(n):
    global EDGE_INDEX, EDGE_COUNT
    edges = all_edges(n)
    EDGE_INDEX = {e: i for i, e in enumerate(edges)}
    EDGE_COUNT = len(edges)
    full_mask = (1 << EDGE_COUNT) - 1
    for bias in range(1, EDGE_COUNT+1):
        maker_can_win.cache_clear()
        has_maker_triangle.cache_clear()
        if not maker_can_win(n, full_mask, 0, 0, bias, True):
            return bias+1
    return EDGE_COUNT

print("n   threshold")
for n in range(3, 10):
    t = threshold_for_n(n)
    print(f"{n:<3} {t}")
