# numba kernel of enumerator 1: iterative DFS over the 45 orbit pairs, incremental check of (L) on the 21 vertices.
import numpy as np
from numba import njit

NP_ = 45


@njit(cache=True)
def popc(x):
    c = 0
    while x:
        x &= x - 1
        c += 1
    return c


@njit(cache=True)
def touch_ok(adj, us):
    for t in range(4):
        u = us[t]
        au = adj[u]
        for v in range(21):
            if v == u:
                continue
            c = popc(au & adj[v])
            if c > 2:
                return False
            if c > 1 and ((au >> v) & 1):
                return False
    return True


@njit(cache=True)
def toggle(adj, i, j, s):
    # toggles the edges of state s on the orbit pair (i, j); used both to add and to remove
    if s & 1:
        adj[i] ^= (1 << (10 + j)); adj[10 + j] ^= (1 << i)
        adj[j] ^= (1 << (10 + i)); adj[10 + i] ^= (1 << j)
    if s & 2:
        adj[i] ^= (1 << j); adj[j] ^= (1 << i)
        adj[10 + i] ^= (1 << (10 + j)); adj[10 + j] ^= (1 << (10 + i))


@njit(cache=True)
def search(pi, pj, opt, nopt, target, adj0, out, maxnodes):
    adj = adj0.copy()
    mdeg = np.zeros(10, np.int64)
    left = np.full(10, 9, np.int64)
    c = np.zeros(NP_ + 1, np.int64)
    applied = np.full(NP_ + 1, -1, np.int64)
    us = np.zeros(4, np.int64)
    nout = 0
    nodes = 0
    k = 0
    while True:
        if k == NP_:
            if nout < out.shape[0]:
                for t in range(NP_):
                    out[nout, t] = applied[t]
            nout += 1
            k -= 1
            s = applied[k]; i = pi[k]; j = pj[k]
            toggle(adj, i, j, s)
            mdeg[i] -= s & 1; mdeg[j] -= s & 1; left[i] += 1; left[j] += 1
            applied[k] = -1
            continue
        nodes += 1
        if nodes > maxnodes:
            return nout, nodes, False
        i = pi[k]; j = pj[k]
        found = False
        while c[k] < nopt[k]:
            s = opt[k, c[k]]
            c[k] += 1
            m = s & 1
            if mdeg[i] + m > target[i] or mdeg[j] + m > target[j]:
                continue
            if mdeg[i] + m + left[i] - 1 < target[i] or mdeg[j] + m + left[j] - 1 < target[j]:
                continue
            ok = True
            if s:
                toggle(adj, i, j, s)
                us[0] = i; us[1] = j; us[2] = 10 + i; us[3] = 10 + j
                ok = touch_ok(adj, us)
                if not ok:
                    toggle(adj, i, j, s)
            if ok:
                mdeg[i] += m; mdeg[j] += m; left[i] -= 1; left[j] -= 1
                applied[k] = s
                found = True
                break
        if found:
            k += 1
            c[k] = 0
            continue
        c[k] = 0
        k -= 1
        if k < 0:
            break
        s = applied[k]; i = pi[k]; j = pj[k]
        toggle(adj, i, j, s)
        mdeg[i] -= s & 1; mdeg[j] -= s & 1; left[i] += 1; left[j] += 1
        applied[k] = -1
    return nout, nodes, True
