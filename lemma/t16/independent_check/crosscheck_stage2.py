#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Second, differently-coded implementation of stage 2 (used as a cross-check of
wagner_check.stage2).  Reuses only the stage-1 configurations (35x35 matrices) and
the vertex layout.  Differences from stage2():
  * single-t "profiles" are generated generically: t ~ x, one P, one Q, a_t X2-neighbours
    (x plus a_t-1 others, y allowed), a_t+1 X0-neighbours (p allowed), filtered by
    vectorised <= checks against Y and |N(t) n N_Y(x)| <= 1;
  * multisets of 4 profiles are found by a DFS that always covers the smallest P-index
    still demanded, with the exact count vector r (no separate Q/X0 bookkeeping);
  * T-internal graphs (64) are tested by generic exact/<= checks on a matmul, and all
    64 T-sigma(T) edge sets are tested in one batched matmul (no hand-derived filters).
Usage: python crosscheck_stage2.py A|B [time_limit_s]
"""
import sys
import time
from itertools import combinations

import numpy as np

import wagner_check as W

T0 = time.time()
profile = sys.argv[1]
TLIM = float(sys.argv[2]) if len(sys.argv) > 2 else 270.0
DIAG = len(sys.argv) > 3 and sys.argv[3] == "diag"
store = W.run_profile(profile, do_stage2=False)
maxa = W.PROFILES[profile]["X1max_a"]
NY, NT = 35, 43
SIG43 = np.array(W.SIG + [39, 40, 41, 42, 35, 36, 37, 38])
TP = list(combinations(range(4), 2))


def profiles_for(A, x):
    Nx = A[x].copy()
    rows, meta = [], []
    others = [z for z in W.X2 if z != x]
    for a in range(1, maxa + 1):
        for rest in combinations(others, a - 1):
            for S0 in combinations(W.X0, a + 1):
                base = np.zeros(NY, np.int64)
                base[x] = 1
                for z in rest:
                    base[z] = 1
                for w in S0:
                    base[w] = 1
                for i in range(8):
                    for j in range(8):
                        v = base.copy()
                        v[W.P(i)] = 1
                        v[W.Q(j)] = 1
                        rows.append(v)
                        meta.append((i, j, a))
    R = np.array(rows)
    meta = np.array(meta)
    keep = (R @ Nx) <= 1                      # lambda(x,t)=1: Y-part of N(x) n N(t) <= 1
    C = R @ A                                  # |N(t) n N_Y(v)| for v in Y
    keep &= (C <= 2 - R).all(axis=1)           # <= bound with every v in Y
    return R[keep], meta[keep], len(rows)


def multisets(R, meta, r):
    byP = {i: np.where(meta[:, 0] == i)[0] for i in range(8)}
    found = set()

    def rec(rem, chosen):
        if len(chosen) == 4:
            if not rem.any():
                found.add(tuple(sorted(chosen)))
            return
        dem = [i for i in range(8) if rem[W.P(i)] > 0]
        if not dem:
            return
        idx = byP[dem[0]]
        ok = idx[(R[idx] <= rem).all(axis=1)]
        for c in ok:
            rec(rem - R[c], chosen + [int(c)])

    rec(r.copy(), [])
    return sorted(found)


def check_multiset(A, x, R, ms):
    y = int(SIG43[x])
    M = np.zeros((NT, NT), np.int64)
    M[:NY, :NY] = A
    for k, c in enumerate(ms):
        for v in np.where(R[c])[0]:
            M[35 + k, v] = M[v, 35 + k] = 1
            M[39 + k, SIG43[v]] = M[SIG43[v], 39 + k] = 1
    n_t = n_e = 0
    surv = []
    for tm in range(64):
        M1 = M.copy()
        for b, (i, j) in enumerate(TP):
            if tm >> b & 1:
                M1[35 + i, 35 + j] = M1[35 + j, 35 + i] = 1
                M1[39 + i, 39 + j] = M1[39 + j, 39 + i] = 1
        C = M1 @ M1
        np.fill_diagonal(C, 0)
        # exact counts with x for v in Y u T (independent of T-sigma(T) edges)
        tgt = 2 - M1[x, :39]
        tgt[x] = 0
        if not (C[x, :39] == tgt).all():
            continue
        sub = C[:39, :39]
        badm = np.triu(sub > (2 - M1[:39, :39]), 1)
        if badm.any():
            if DIAG and tm == 0:
                print("     multiset %s, no T-edges: <= violated on %s" % (
                    [tuple(int(v) for v in np.where(R[c])[0]) for c in ms],
                    [(int(u), int(v), int(sub[u, v]), "adj" if M1[u, v] else "non")
                     for u, v in np.argwhere(badm)]))
            continue
        n_t += 1
        Mb = np.repeat(M1[None, :, :], 64, axis=0).astype(np.float32)
        for em in range(64):
            for b, (i, j) in enumerate(TP):
                if em >> b & 1:
                    Mb[em, 35 + i, 39 + j] = Mb[em, 39 + j, 35 + i] = 1
                    Mb[em, 35 + j, 39 + i] = Mb[em, 39 + i, 35 + j] = 1
        Cb = np.matmul(Mb, Mb)
        idx = np.arange(NT)
        Cb[:, idx, idx] = 0
        le = (Cb <= 2 - Mb).all(axis=(1, 2))
        ex = np.ones(64, bool)
        for c in (x, y):
            t = 2 - Mb[:, c, :]
            t[:, c] = 0
            ex &= (Cb[:, c, :] == t).all(axis=1)
        good = le & ex
        n_e += int(good.sum())
        for em in np.where(good)[0]:
            assert (Mb[em][np.ix_(SIG43, SIG43)] == Mb[em]).all()
            surv.append(Mb[em].astype(np.int64))
    return n_t, n_e, surv


total_surv = 0
nruns = 0
for n, (key, (A, M, mxy, masks, comb)) in enumerate(sorted(store.items())):
    for side in (0, 1):
        if time.time() - T0 > TLIM:
            print("TIME LIMIT reached; stopped before config #%d side %d" % (n, side), flush=True)
            sys.exit(2)
        x = W.Z(mxy, side)
        R, meta, nraw = profiles_for(A, x)
        known = A[:, A[x].astype(bool)].sum(axis=1)
        r = (2 - A[x]) - known
        r[x] = 4
        if (r < 0).any():
            print("config #%d side %d: negative r" % (n, side))
            continue
        mss = multisets(R, meta, r)
        if maxa >= 2:
            mss = [ms for ms in mss if sum(1 for c in ms if meta[c, 2] == 2) <= 1]
        nt = ne = 0
        surv = []
        for ms in mss:
            a, b, s = check_multiset(A, x, R, ms)
            nt += a
            ne += b
            surv += s
        nruns += 1
        total_surv += len(surv)
        print("config #%d x-side %d: profiles %d/%d, multisets %d, T-internal ok %d, full ok %d" % (
            n, side, len(R), nraw, len(mss), nt, ne), flush=True)
        for S in surv:
            print("SURVIVOR adjacency rows of T and sigma(T):")
            for v in range(35, 43):
                print("  ", v, list(np.where(S[v])[0]))
print("profile %s: %d runs, total full survivors %d, time %.1fs" % (profile, nruns, total_surv, time.time() - T0))
