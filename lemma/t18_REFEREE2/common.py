# Referee 2: common helpers, written from the text of T18_PROOF.md only.
import itertools

DOC_B = {
    0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
    1: "01 02 03 04 14 17 18 23 26 28 35 36 45 47 56 57 68 78",
    2: "01 02 03 04 14 17 18 23 25 26 34 36 48 56 57 58 67 78",
}
DOC_DEF = {
    0: "01 02 03 04 14 17 18 23 26 28 35 37 45 46 56 57 68 78",
    1: "01 02 03 04 13 16 18 24 27 28 35 37 45 46 56 57 68 78",
    2: "01 02 05 07 12 16 17 25 28 34 36 37 38 45 46 48 58 67",
}

def Bgraph(s):
    adj = [set() for _ in range(9)]
    for e in DOC_B[s].split():
        i, j = int(e[0]), int(e[1])
        adj[i].add(j)
        adj[j].add(i)
    return adj

def codeg(adj, i, j):
    return len(adj[i] & adj[j])

def deficient_pairs(adj):
    return [(i, j) for i in range(9) for j in range(i + 1, 9) if codeg(adj, i, j) == 1]

def automorphisms(adj):
    n = len(adj)
    res = []
    img = [-1] * n
    used = [False] * n

    def rec(i):
        if i == n:
            res.append(tuple(img))
            return
        for t in range(n):
            if used[t] or len(adj[t]) != len(adj[i]):
                continue
            ok = True
            for j in range(i):
                if (j in adj[i]) != (img[j] in adj[t]):
                    ok = False
                    break
            if ok:
                img[i] = t
                used[t] = True
                rec(i + 1)
                used[t] = False
                img[i] = -1

    rec(0)
    return res

def budget_ok(nbr):
    """nbr: list of sets (adjacency of a graph on range(n)). True iff no budget violation (Lemma 6.2)."""
    n = len(nbr)
    for u in range(n):
        nu = nbr[u]
        for v in range(u + 1, n):
            c = len(nu & nbr[v])
            if c > (1 if v in nu else 2):
                return False
    return True

def budget_violations(nbr):
    n = len(nbr)
    out = []
    for u in range(n):
        nu = nbr[u]
        for v in range(u + 1, n):
            c = len(nu & nbr[v])
            if c > (1 if v in nu else 2):
                out.append((u, v, c))
    return out
