"""(6,6) components: cubic graphs on 18 vertices = 3 layers of 6 (3 mate pairs per layer, one neighbour in each other
layer), connected, girth >= 5.  Normal form: layers Z^0, Z^1, Z^2 indexed by 0..5 so that the cross matchings 0-1 and
0-2 are the identity; data = (iota, tau1, tau2, pi): mates in each layer and the cross matching 1-2 (i^1 ~ pi(i)^2).
Enumerates all, classifies up to isomorphism (layers unordered), prints tau, tau mod 7 and the 7-nullity of the
Laplacian.  Writes comp66_types.json.   No new fact used: this regenerates the lab's list (288 labelled, 15 types)."""
import itertools, json, sys
from fractions import Fraction as Fr


def matchings(elts):
    elts = list(elts)
    if not elts:
        yield ()
        return
    a = elts[0]
    for b in elts[1:]:
        rest = [x for x in elts if x not in (a, b)]
        for m in matchings(rest):
            yield ((a, b),) + m


def involution(m):
    inv = [0] * 6
    for a, b in m:
        inv[a] = b; inv[b] = a
    return tuple(inv)


def build(iota, t1, t2, pi):
    adj = [set() for _ in range(18)]
    def e(x, y):
        adj[x].add(y); adj[y].add(x)
    for i in range(6):
        e(i, iota[i]); e(6 + i, 6 + t1[i]); e(12 + i, 12 + t2[i])
        e(i, 6 + i); e(i, 12 + i); e(6 + i, 12 + pi[i])
    return adj


def ok(adj):
    if any(len(s) != 3 for s in adj): return False
    for u in range(18):
        for v in range(u + 1, 18):
            c = len(adj[u] & adj[v])
            if v in adj[u]:
                if c: return False
            elif c > 1: return False
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    return len(seen) == 18


def canon(adj):
    """minimal (iota, t1, t2, pi) over the 6 orders of the layers and the 720 labellings of the first layer"""
    best = None
    lay = lambda v: v // 6
    for order in itertools.permutations(range(3)):
        L0 = [v for v in range(18) if lay(v) == order[0]]
        for perm in itertools.permutations(range(6)):
            lab = {}
            for idx, v in zip(perm, L0):
                lab[v] = (0, idx)
                for w in adj[v]:
                    if lay(w) == order[1]: lab[w] = (1, idx)
                    elif lay(w) == order[2]: lab[w] = (2, idx)
            inv = {val: key for key, val in lab.items()}
            def mate(l, i):
                v = inv[(l, i)]
                return lab[next(w for w in adj[v] if lay(w) == lay(v))][1]
            iota = tuple(mate(0, i) for i in range(6))
            if best is not None and iota > best[0]: continue
            t1 = tuple(mate(1, i) for i in range(6)); t2 = tuple(mate(2, i) for i in range(6))
            pi = tuple(lab[next(w for w in adj[inv[(1, i)]] if lay(w) == order[2])][1] for i in range(6))
            key = (iota, t1, t2, pi)
            if best is None or key < best: best = key
    return best


def det_fr(M):
    M = [[Fr(x) for x in r] for r in M]; n = len(M); d = Fr(1)
    for c in range(n):
        p = next((i for i in range(c, n) if M[i][c] != 0), None)
        if p is None: return Fr(0)
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for i in range(c + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / M[c][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return d


def rank7(M):
    M = [[x % 7 for x in r] for r in M]; r = 0; n = len(M)
    for c in range(len(M[0])):
        p = next((i for i in range(r, n) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        iv = pow(M[r][c], -1, 7)
        M[r] = [(x * iv) % 7 for x in M[r]]
        for i in range(n):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(x - f * y) % 7 for x, y in zip(M[i], M[r])]
        r += 1
    return r


def main():
    iota = involution(((0, 1), (2, 3), (4, 5)))
    ms = [involution(m) for m in matchings(range(6))]
    found = []
    for t1 in ms:
        for t2 in ms:
            for pi in itertools.permutations(range(6)):
                adj = build(iota, t1, t2, pi)
                if ok(adj): found.append((iota, t1, t2, pi))
    print("normal forms with iota fixed, connected, girth >= 5:", len(found), flush=True)
    types = {}
    for key in found:
        c = canon(build(*key))
        types.setdefault(c, 0)
        types[c] += 1
    print("isomorphism types (layers unordered):", len(types))
    out = []
    for c, mult in sorted(types.items()):
        adj = build(*c)
        H = [[(3 if i == j else 0) - (1 if j in adj[i] else 0) for j in range(18)] for i in range(18)]
        tau = int(det_fr([r[:17] for r in H[:17]]))
        nul = 18 - rank7(H)
        out.append({"key": [list(x) for x in c], "mult": mult, "tau": tau, "tau_mod7": tau % 7, "torsion": nul - 1})
        print(f"  mult {mult:5d}  tau = {tau:6d}  tau mod 7 = {tau % 7}  7-torsion rank = {nul - 1}  key = {c}")
    json.dump(out, open("comp66_types.json", "w"))


if __name__ == "__main__":
    main()
