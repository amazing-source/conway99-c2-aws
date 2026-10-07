"""Small exact local study, independent of the project's enumeration engines.

Enumerate one outside orbit, not a full T20 configuration. All rejections use
integer neighbour counts or exact rational Schur complements/dual norms.
Input: the six edge lists in T20_WORK.md. No solver and no floating-point tests.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import itertools as it
import json
import time
from fractions import Fraction as F
from pathlib import Path
import numpy as np

EDGES = [
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 58 59 67 68 79',
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 68 69 78',
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 57 59 67 68 89',
 '01 02 03 04 17 18 19 25 26 29 34 36 38 45 47 56 59 68 78 79',
 '01 02 03 04 17 18 19 24 26 29 34 35 38 46 56 57 58 69 78 79',
 '01 02 03 04 14 18 19 23 26 27 34 37 49 56 57 58 59 67 68 89',
]

def graph(index):
    B = np.zeros((10, 10), dtype=np.int64)
    for edge in EDGES[index].split():
        i, j = map(int, edge)
        B[i, j] = B[j, i] = 1
    assert (B.sum(axis=0) == 4).all()
    return B

def inverse(M):
    n = len(M)
    a = [[F(int(x)) for x in row] + [F(i == j) for j in range(n)] for i, row in enumerate(M)]
    for k in range(n):
        pivot = next(i for i in range(k, n) if a[i][k])
        a[k], a[pivot] = a[pivot], a[k]
        v = a[k][k]
        a[k] = [x/v for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                q = a[i][k]
                a[i] = [x-q*y for x, y in zip(a[i], a[k])]
    return [row[n:] for row in a]

def quadratic(M, b):
    nonzero = [(i, int(v)) for i, v in enumerate(b) if v]
    return sum((M[i][j]*u*v for i,u in nonzero for j,v in nonzero), F(0))

def support_adjacency(B, U, V, inner):
    A = np.zeros((23,23), dtype=np.int64)
    A[:10,10:20] = B
    A[10:20,:10] = B
    for i in U:
        A[i,21] = A[21,i] = A[10+i,22] = A[22,10+i] = 1
    for i in V:
        A[i,22] = A[22,i] = A[10+i,21] = A[21,10+i] = 1
    if inner:
        for i,j in [(20,21),(20,22),(21,22)]: A[i,j] = A[j,i] = 1
    return A

def budgets(A):
    excess = A@A + A - 2
    np.fill_diagonal(excess, 0)
    return not (excess > 0).any()

def schur_setup(B):
    eye = np.eye(10, dtype=np.int64)
    one = np.ones((10,10), dtype=np.int64)
    even1 = np.zeros((11,11), dtype=np.int64)
    even1[:10,:10] = 18*(3*eye-B)+4*one
    even1[:10,10] = even1[10,:10] = 2
    even1[10,10] = 28
    even2 = np.zeros((11,11), dtype=np.int64)
    even2[:10,:10] = 22*(4*eye+B)-8*one
    even2[:10,10] = even2[10,:10] = -4
    even2[10,10] = 42
    return [inverse(M) for M in [3*eye+B,4*eye-B+one,even1,even2]]

def schur_residuals(inv, U, V, inner):
    u = np.array([int(i in U) for i in range(10)], dtype=np.int64)
    v = np.array([int(i in V) for i in range(10)], dtype=np.int64)
    b = v-u
    return [
        F(3+inner)-quadratic(inv[0],b),
        F(4-inner)-quadratic(inv[1],b),
        F(58-18*inner)-quadratic(inv[2],list(4-18*(u+v))+[2-18*inner]),
        F(80+22*inner)-quadratic(inv[3],list(22*(u+v)-8)+[-4+22*inner]),
    ]

def run():
    start = time.monotonic()
    report = []
    bits = np.array([[(mask>>i)&1 for i in range(10)] for mask in range(1024)],dtype=np.int64)
    sizes = bits.sum(axis=1)
    for index in range(6):
        B = graph(index)
        inv = schur_setup(B)
        edge2 = np.sum((bits@B)*bits,axis=1)
        base = np.array([10*k*k+7*((3-2*k)*sizes+edge2) for k in (1,2,3)])
        rows=[]
        for d in (0,1,2,3):
            for inner in (0,1):
                count = {'graph':index,'d':d,'inner':inner,'budgets':0,'psd':0,'dual_rejected':0,'kept':0}
                survivors=[]
                certificates=[]
                pairs=list(it.combinations(range(10),d))
                for U,V in it.combinations_with_replacement(pairs,2):
                    if not budgets(support_adjacency(B,U,V,inner)): continue
                    count['budgets']+=1
                    residuals=schur_residuals(inv,U,V,inner)
                    if min(residuals)<0: continue
                    count['psd']+=1
                    b=np.array([int(i in U)-int(i in V) for i in range(10)],dtype=np.int64)
                    s=bits@b
                    norms=np.concatenate([base+7*(3+inner-2*s),base+7*(3+inner+2*s)])
                    bad=np.argwhere((norms>0)&(norms<10))
                    assert not (norms<0).any(), 'PSD implies nonnegative dual norms'
                    if len(bad):
                        count['dual_rejected']+=1
                        ki,mask=map(int,bad[0])
                        certificates.append({'U':U,'V':V,'k':ki%3+1,'outside_coefficient':1 if ki<3 else -1,'I':[i for i in range(10) if bits[mask,i]],'N':int(norms[ki,mask])})
                    else:
                        count['kept']+=1
                        survivors.append({'U':U,'V':V})
                rows.append({'counts':count,'survivors':survivors,'dual_certificates':certificates})
                print(json.dumps(count),flush=True)
        report.append(rows)
    result={'method':'one-orbit exact budgets, four exact Schur complements, then support-subset dual norm','elapsed_seconds':time.monotonic()-start,'graphs':report}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('elapsed_seconds',result['elapsed_seconds'],flush=True)

if __name__=='__main__': run()
