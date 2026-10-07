import sys, itertools, numpy as np
import r2c
from r2c import *
name = sys.argv[1]
m, H = r2c.load_structs()[name]
A0 = r2c.base_graph(m, H); r2c.check_base(A0, H); Hs = set(H)
NB = 27
AB = np.zeros((NB, NB), dtype=np.int64); AB[:21,:21] = A0
for e in range(3):
    a, b = 21+2*e, 22+2*e
    AB[a,b]=AB[b,a]=1; AB[PV,a]=AB[a,PV]=1; AB[PV,b]=AB[b,PV]=1
print("base S u N[p]: budgets", budgets_ok(AB), "exact PSD (M1),(M2):", psd_exact_report(AB))
print("base S u {p}: exact PSD", psd_exact_report(A0))
units = []
for i in range(N):
    for j in range(i+1, N):
        c = int((A0[i]*A0[j]).sum()); need = (1 if A0[i,j] else 2) - c
        units += [(i,j)]*need
print(len(units), units)
def add_orbit(A, U, V, N0):
    n = A.shape[0]; B = np.zeros((n+2,n+2), dtype=np.int64); B[:n,:n] = A; z, sz = n, n+1
    for i in U: B[z,i]=B[i,z]=1; B[sz,10+i]=B[10+i,sz]=1
    for i in V: B[z,10+i]=B[10+i,z]=1; B[sz,i]=B[i,sz]=1
    for u in N0:
        su = u+1 if (u-21)%2==0 else u-1
        B[z,u]=B[u,z]=1; B[sz,su]=B[su,sz]=1
    return B
up = sorted(set(units))
nrect = 0; nrect23 = 0
for a in range(len(up)):
    for b in range(a+1, len(up)):
        U, V = up[a], up[b]
        if set(U)&set(V)&Hs or len(set(U)&set(V))>1: continue
        B23 = add_orbit(A0, U, V, ())
        if not budgets_ok(B23): continue
        nrect += 1
        r23 = psd_reject(B23)
        r = sum(1 for i in U if i in Hs)+sum(1 for i in V if i in Hs)
        k = 2-r
        res = []
        if k==0: choices=[()]
        elif k==1: choices=[(21,)]
        else: choices=[(21,23),(21,24)]
        for N0 in choices:
            B = add_orbit(AB, U, V, N0)
            bo = budgets_ok(B)
            pr = psd_reject(B) if bo else None
            res.append((N0, bo, None if pr is None else (pr[0], pr[2])))
        if r23 is None: nrect23 += 1
        print("rect", U, V, "r=%d"%r, "PSD on 23:", "ok" if r23 is None else (r23[0], r23[2]), "| with X0:", res)
print("rectangles passing (L) on 23 vertices:", nrect, " and PSD on 23:", nrect23)
