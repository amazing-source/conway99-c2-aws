"""Independent T20 n3=2 model, from SPEC_N3.md; no first-engine imports.

Vertex order: x0..x9, y0..y9, p, z,z', three X0 pairs, then X2 pairs.
All graph and degree decisions use Python integers. Exact PSD uses integral
Schur complements; floating point is not used anywhere in base generation.
"""
from itertools import combinations, permutations, product
from math import gcd

EDGE_TEXT = (
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79',
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78',
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89',
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79',
 '01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79',
 '01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89')
PAIRS = tuple(combinations(range(10), 2))
PAIR_MASKS = tuple((1 << a) | (1 << b) for a, b in PAIRS)
PAIR_ID = {m: i for i, m in enumerate(PAIR_MASKS)}
X0 = (1 << 20) | (63 << 23)
X3 = 3 << 21
BASE_N = 29


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mate(i):
    if i < 10: return i + 10
    if i < 20: return i - 10
    if i == 20: return 20
    return i + 1 if i & 1 else i - 1


def conjugate(mask):
    return sum(1 << mate(i) for i in vertices(mask))


def edge(rows, a, b):
    rows[a] |= 1 << b
    rows[b] |= 1 << a


def support(gi):
    rows = [0] * 21
    for word in EDGE_TEXT[gi].split():
        a, b = map(int, word)
        edge(rows, a, b + 10)
        edge(rows, b, a + 10)
    return rows


def budget(rows):
    for i, row in enumerate(rows):
        if row.bit_count() > 14: return False
        for j in range(i):
            if (row & rows[j]).bit_count() > 2 - ((row >> j) & 1):
                return False
    return True


def exact_psd(matrix):
    """Integer Schur elimination, including the zero-pivot range condition.

    Positive scaling and division by a positive gcd preserve inertia.
    This is exact even when the matrix is singular.
    """
    a = [list(map(int, row)) for row in matrix]
    while a:
        p = a[0][0]
        if p < 0: return False
        if p == 0:
            if any(a[0][1:]): return False
            a = [row[1:] for row in a[1:]]
            continue
        n = len(a)
        b = [[0] * (n - 1) for _ in range(n - 1)]
        divisor = 0
        for i in range(1, n):
            for j in range(i, n):
                value = p * a[i][j] - a[i][0] * a[0][j]
                if i == j and value < 0: return False
                b[i-1][j-1] = b[j-1][i-1] = value
                divisor = gcd(divisor, value)
        if divisor > 1:
            b = [[x // divisor for x in row] for row in b]
        a = b
    return True


def projector_blocks(rows):
    """Congruence blocks of 9(3I-A)+J and 11(4I+A)-2J.

    Odd blocks are divided by positive factors 18 and 22. Even bases
    are e_i+e_sigma(i), with e_p as last vector; all entries are integers.
    """
    reps = list(range(10)) + list(range(21, len(rows), 2))
    n = len(reps)
    o1 = [[0] * n for _ in reps]
    o2 = [[0] * n for _ in reps]
    e1 = [[0] * (n+1) for _ in range(n+1)]
    e2 = [[0] * (n+1) for _ in range(n+1)]
    for i, v in enumerate(reps):
        for j, w in enumerate(reps):
            direct = (rows[v] >> w) & 1
            cross = (rows[v] >> mate(w)) & 1
            o1[i][j] = 3*(i == j) - direct + cross
            o2[i][j] = 4*(i == j) + direct - cross
            e1[i][j] = 18*(3*(i == j)-direct-cross)+4
            e2[i][j] = 22*(4*(i == j)+direct+cross)-8
        adjacent = (rows[v] >> 20) & 1
        e1[i][n] = e1[n][i] = 2 - 18*adjacent
        e2[i][n] = e2[n][i] = -4 + 22*adjacent
    e1[n][n] = 28
    e2[n][n] = 42
    return o1, e1, o2, e2


def psd(rows):
    return all(exact_psd(m) for m in projector_blocks(rows))


def automorphisms(gi):
    """All permutations preserving the ten-vertex B, by direct backtracking."""
    B = [row >> 10 for row in support(gi)[:10]]
    result, assigned = [], []
    def visit(unused):
        i = len(assigned)
        if i == 10:
            result.append(tuple(assigned))
            return
        for target in vertices(unused):
            if any(((B[i] >> j) & 1) != ((B[target] >> t) & 1)
                   for j, t in enumerate(assigned)):
                continue
            assigned.append(target)
            visit(unused ^ (1 << target))
            assigned.pop()
    visit(1023)
    return result


def permute(mask, perm):
    return sum(1 << perm[i] for i in vertices(mask))


def make_base(gi, U, V, case, inner, pattern):
    rows = support(gi) + [0] * 8
    for i in vertices(U): edge(rows, 21, i); edge(rows, 22, i+10)
    for i in vertices(V): edge(rows, 22, i); edge(rows, 21, i+10)
    T = {'i': (23,25,27), 'ii': (23,24,25), 'iii': (23,24,25,27)}[case]
    for i in T: edge(rows, 21, i); edge(rows, 22, mate(i))
    if inner is not None:
        i = 23 + 2*inner
        edge(rows, 20, i); edge(rows, 20, i+1); edge(rows, i, i+1)
    for k, (i, j) in enumerate(combinations(range(3), 2)):
        a, b = 23+2*i, 23+2*j
        if (pattern >> (2*k)) & 1: edge(rows, a, b); edge(rows, a+1, b+1)
        if (pattern >> (2*k+1)) & 1: edge(rows, a, b+1); edge(rows, a+1, b)
    return rows


def types(gi, autos):
    """Enumerate all triples; quotient only by explicit graph automorphisms.

    H2's budget and odd M1 test define the type list. Other PSD tests
    are applied later to the complete base, to keep counts comparable.
    """
    triples = [sum(1 << i for i in t) for t in combinations(range(10), 3)]
    seen, result = set(), []
    for U, V in combinations(triples, 2):
        key = tuple(sorted((U, V)))
        if key in seen or (U & V).bit_count() > 1: continue
        rows = make_base(gi, U, V, 'i', None, 0)
        # The type uses only S,p,z,z', not the artificial X0 transversal.
        rows = [r & ((1 << 23)-1) for r in rows[:23]]
        if not budget(rows) or not exact_psd(projector_blocks(rows)[0]): continue
        orbit = {tuple(sorted((permute(U, p), permute(V, p)))) for p in autos}
        seen.update(orbit)
        a, b = min(orbit)
        result.append((a, b))
    return sorted(result)


def base_key(rows, allow_z_swap):
    """Canonicalize the induced nine-vertex graph off S, fixing p.

    X0 pairs may permute and flip. z may flip exactly when an automorphism
    of B exchanges U,V. These are all relabellings fixing a chosen type.
    """
    best = None
    for perm in permutations(range(3)):
        for flips in product(range(2), repeat=3):
            for swap in range(1 + int(allow_z_swap)):
                labels = [20,21+swap,22-swap]
                for i in range(3):
                    v = 23 + 2*perm[i] + flips[i]
                    labels.extend((v, mate(v)))
                key = 0
                for j, v in enumerate(labels):
                    for w in labels[:j]: key = 2*key + ((rows[v] >> w) & 1)
                if best is None or key < best: best = key
    return best


def generate(gi):
    autos = automorphisms(gi)
    type_list = types(gi, autos)
    counts = dict(graph=gi, automorphisms=len(autos), types=len(type_list),
                  labelled=0, budget_degree=0, psd=0, classes=0,
                  hand_excluded_classes=0, search_classes=0)
    records, seen = [], set()
    for U, V in type_list:
        swap = any(permute(U, p) == V and permute(V, p) == U for p in autos)
        for case in ('i', 'ii', 'iii'):
            if U & V and case != 'i': continue
            for inner in (None,0,1,2):
                if case != 'i' and inner == 0: continue
                for pattern in range(64):
                    counts['labelled'] += 1
                    rows = make_base(gi,U,V,case,inner,pattern)
                    if not budget(rows): continue
                    if any(8-2*(rows[v]&X0).bit_count()+(rows[v]&X3).bit_count() < 0
                           for v in range(23,29)): continue
                    counts['budget_degree'] += 1
                    if not psd(rows): continue
                    counts['psd'] += 1
                    key = (U,V,base_key(rows,swap))
                    if key in seen: continue
                    seen.add(key); counts['classes'] += 1
                    hand = None
                    if inner is not None:
                        v = 23+2*inner
                        if rows[v] & (X0 ^ (1<<20) ^ (3<<v)):
                            hand = 'inner-X0 isolation'
                        elif (rows[v]&X3).bit_count() != 1:
                            hand = 'X3 triangle attachment'
                    record = dict(graph=gi,U=U,V=V,case=case,inner=inner,
                                  pattern=pattern,key=list(key),hand_excluded=hand,
                                  rows=rows)
                    records.append(record)
                    counts['hand_excluded_classes' if hand else 'search_classes'] += 1
    return counts, records


def needs(rows, U, V):
    values = [2-((rows[a]>>10)&(rows[b]>>10)&1023).bit_count()
              -int((U&m)==m)-int((V&m)==m) for (a,b),m in zip(PAIRS,PAIR_MASKS)]
    assert min(values) >= 0 and sum(values) == 24
    return values
