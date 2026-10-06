"""Does the second projector 11(4I+A)-2J (= 77 E_3) reject some of my 39-vertex survivors?  exact (charpoly).
usage: python v2_second_matrix.py <graph>"""
import sys, json, glob
import numpy as np
sys.argv_backup = sys.argv[:]
g = int(sys.argv[1])
sys.argv = ['v3', str(g), '0', '1']
from vcommon import *
B = support_graph(g)
J1 = json.load(open('v1_tau_%d.json' % g))
D = [tuple(u) for u in J1['D']]
REPS = [[tuple(r) for r in tau] for tau in J1['reps']]
SA = support_adj(B)
S = []
for fn in sorted(glob.glob('v2_surv_%d_m1_*of*.json' % g)):
    if 'nopsd' in fn: continue
    S += json.load(open(fn))['survivors']
def srow(U, V):
    r = np.zeros(18, dtype=np.int64)
    for u in U: r[u] = 1
    for v in V: r[9 + v] = 1
    return r
def build39(s):
    tau = REPS[s['tau']]
    A = np.zeros((39, 39), dtype=np.int64)
    A[:18, :18] = SA
    A[18, 19] = A[18, 20] = A[19, 20] = 1
    for k, f in enumerate(s['F']):
        a, c = tau[f]; i, j = 21 + 2 * k, 22 + 2 * k
        A[i, :18] = srow(D[a], D[c]); A[j, :18] = srow(D[c], D[a]); A[i, j] = 1; A[18, i] = A[18, j] = 1
    for k, f in enumerate(s['rest']):
        a, c = tau[f]; i, j = 27 + 2 * k, 28 + 2 * k
        A[i, :18] = srow(D[a], D[c]); A[j, :18] = srow(D[c], D[a])
        side = s['sides'][k]; A[19 + side, i] = 1; A[20 - side, j] = 1
    pos = {f: k for k, f in enumerate(s['rest'])}
    for (fa, fb, opt) in s['H']:
        ia, ib = 27 + 2 * pos[fa], 27 + 2 * pos[fb]
        if opt & 1: A[ia, ib] = 1; A[ia + 1, ib + 1] = 1
        if opt & 2: A[ia, ib + 1] = 1; A[ia + 1, ib] = 1
    return np.maximum(A, A.T)
n1 = n2 = both = 0
keep = []
for s in S:
    A = build39(s)
    n = len(A)
    M1 = 27 * np.eye(n, dtype=np.int64) - 9 * A + 1
    M2 = 44 * np.eye(n, dtype=np.int64) + 11 * A - 2
    p1 = exact_psd_charpoly(M1); p2 = exact_psd_charpoly(M2)
    n1 += p1; n2 += p2; both += (p1 and p2)
    if p1 and p2: keep.append(s)
print('graph B%d: %d survivors; exactly PSD for 9(3I-A)+J: %d; for 11(4I+A)-2J: %d; for both: %d' % (g, len(S), n1, n2, both))
print('  both: in %d matchings, %d pairs (tau,F)' % (len({s['tau'] for s in keep}), len({(s['tau'], tuple(s['F'])) for s in keep})))
