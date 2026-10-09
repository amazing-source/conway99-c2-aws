"""Pilot 1b.  Question: is there a closed rule for the flipped far adjacency of BvLS in the coordinates F_3^5 ?
Vertices are base-3 vectors, T = <e0>, quotient F_3^4 carries the elliptic quadric (20 singular vectors = near cosets)."""
import numpy as np, itertools, collections
R = "C:/home/researcher/Desktop/Nouveau/conway99-c1/data/srg243/"


def load(p, n=243):
    M = np.zeros((n, n), dtype=np.int64)
    for l in open(p):
        if l.strip():
            i, j = map(int, l.split()); M[i, j] = M[j, i] = 1
    return M


def vec(i): return tuple((i // 3 ** k) % 3 for k in range(5))
def idx(v): return sum((v[k] % 3) * 3 ** k for k in range(5))
def add(u, v): return tuple((a + b) % 3 for a, b in zip(u, v))
def sub(u, v): return tuple((a - b) % 3 for a, b in zip(u, v))


A = load(R + "bvls243.edges"); B = load(R + "twin243_switched.edges"); D = B - A
S = [vec(j) for j in range(243) if A[0, j]]
# Cayley check
assert all(A[i, idx(add(vec(i), s))] for i in range(243) for s in S)
Sbar = sorted(set(s[1:] for s in S if any(s[1:])))
print("projected connection set:", len(Sbar))
# quadratic form on F_3^4 vanishing on Sbar: monomials x_i x_j, i<=j
mons = [(i, j) for i in range(4) for j in range(i, 4)]
rows = [[(v[i] * v[j]) % 3 for (i, j) in mons] for v in Sbar]
# brute force over 3^10 coefficient vectors is fine
sols = []
for cf in itertools.product(range(3), repeat=10):
    if any(cf) and all(sum(c * r for c, r in zip(cf, row)) % 3 == 0 for row in rows):
        sols.append(cf)
print("quadratic forms vanishing on the 20 points:", len(sols))
cf = sols[0]
def Q(v): return sum(c * v[i] * v[j] for c, (i, j) in zip(cf, mons)) % 3
def Bf(u, v): return (Q(add(u, v)) - Q(u) - Q(v)) % 3
zeros = [v for v in itertools.product(range(3), repeat=4) if any(v) and Q(v) == 0]
print("singular nonzero vectors:", len(zeros), " = projected set:", sorted(zeros) == Sbar)
# fibre coordinate of the connection set: s = (gamma(sbar), sbar)
gam = {s[1:]: s[0] for s in S if any(s[1:])}
far = [i for i in range(243) if Q(vec(i)[1:]) != 0]
assert all((D[i] != 0).sum() == 16 for i in far) and all((D[i] != 0).sum() == 0 for i in range(243) if i not in far)
# removed edges: x ~ x+s ; classify by (Q(xbar), Q(xbar+sbar), B(xbar,sbar), ...)
st = collections.Counter()
for i in far:
    x = vec(i)
    for s in S:
        if not any(s[1:]): continue
        y = add(x, s); j = idx(y)
        if Q(y[1:]) == 0: continue                       # near neighbour
        st[(Q(x[1:]), Q(y[1:]), Bf(x[1:], s[1:]), int(D[i, j]))] += 1
print("far-far edges of BvLS by (Q(x),Q(y),B(x,s)) -> D:")
for k in sorted(st): print("  ", k, st[k])
# added edges: difference classes
st2 = collections.Counter()
for i in far:
    x = vec(i)
    for j in far:
        if D[i, j] == 1:
            d = sub(vec(j), x)
            st2[(Q(x[1:]), Q(vec(j)[1:]), Q(d[1:]), Bf(x[1:], d[1:]), "dbar=0" if not any(d[1:]) else "")] += 1
print("added edges by (Q(x),Q(y),Q(d),B(x,d)):")
for k in sorted(st2): print("  ", k, st2[k])

# fibre shift of the new edges compared with the old one over the same projected pair
st3 = collections.Counter()
for i in far:
    x = vec(i)
    for j in far:
        if D[i, j] == 1:
            d = sub(vec(j), x); g = gam[d[1:]]
            st3[(Q(x[1:]), g, (d[0] - g) % 3, x[0])] += 1
print("added edge: (Q(x), old shift gamma(dbar), new shift - old shift, x0):")
for k in sorted(st3): print("  ", k, st3[k])
# is the new shift a function of (xbar, dbar)?  and is it  -gamma  or gamma + c*Q(x) ...
fn = {}
ok = True
for i in far:
    x = vec(i)
    for j in far:
        if D[i, j] == 1:
            d = sub(vec(j), x); key = (x[1:], d[1:])
            if fn.setdefault(key, d[0]) != d[0]: ok = False
print("new shift depends only on (xbar, dbar):", ok, " pairs:", len(fn))
c2 = collections.Counter(((v - gam[k[1]]) % 3, Q(k[0])) for k, v in fn.items())
print("(new - old shift, Q(xbar)) over projected same-class pairs:", sorted(c2.items()))
c3 = collections.Counter(((v + gam[k[1]]) % 3) for k, v in fn.items())
print("new + old shift:", sorted(c3.items()))
