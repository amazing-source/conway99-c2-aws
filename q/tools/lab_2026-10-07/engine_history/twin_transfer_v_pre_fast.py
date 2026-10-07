"""Twin-envelope transfer (Astra 29/09, sections 5, 5.2, 7): U+ = F(U)+J contains the same frame; its roots are
x + ((c-a) y1 + (d-b) y2)/7 for x in U of (norm, Y) in {(2,0),(2,5),(3,8),(3,9),(4,18)}, (c,d) = R(a,b) reduced mod 7 into [-3,3], R=[[2,2],[-2,2]].
If the twin's root system is that of an EXCLUDED envelope, the pair is dead (a frame would live in an excluded envelope)."""
import sys, os, re, json, collections, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def parse(s):
    c = collections.Counter()
    for t, n, e in re.findall(r"([ade])_\{?(\d+)\}?(?:\^\{?(\d+)\}?)?", s): c[(t.upper(), int(n))] += int(e or 1)
    return tuple(sorted(c.items()))
def classes():
    T = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "finishC", "finishC_tracker.json")))["lattices"]
    by = collections.defaultdict(set)
    for v in T: by[parse(v["roots"]) if v["nroots"] else ()].add(v["status"])
    return by
def rtype(Rt, G):
    P = np.rint(Rt @ G @ Rt.T).astype(np.int64); n = len(Rt); comp = -np.ones(n, int); k = 0
    for s in range(n):
        if comp[s] >= 0: continue
        st = [s]; comp[s] = k
        while st:
            a = st.pop()
            for b in np.flatnonzero(P[a] != 0):
                if comp[b] < 0: comp[b] = k; st.append(b)
        k += 1
    c = collections.Counter()
    for q in range(k):
        m = int((comp == q).sum()); r = int(np.linalg.matrix_rank(Rt[comp == q]))
        t = ("E", r) if (r, m) in ((6, 36), (7, 63), (8, 120)) else ("A", r) if m == r * (r + 1) // 2 else ("D", r)
        c[t] += 1
    return tuple(sorted(c.items()))
def twin_roots(L, y1, y2):
    G = L["G"]; out = []
    for X, n, Ys in ((L["R"], 2, (0, 5)), (L["X3"], 3, (8, 9)), (L["X4"], 4, (18,))):
        a = X @ G @ y1; b = X @ G @ y2; Y = a * a + b * b; m = np.isin(Y, Ys)
        a, b, Xm = a[m], b[m], X[m].astype(np.float64)
        c = (2 * a + 2 * b); d = (-2 * a + 2 * b); c = (c + 3) % 7 - 3; d = (d + 3) % 7 - 3
        out.append(Xm + (np.outer(c - a, y1) + np.outer(d - b, y2)) / 7.0)
    return np.vstack(out)
