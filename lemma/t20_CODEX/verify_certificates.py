"""Direct full-matrix rational recheck of the small certificates.
This avoids the Schur formula used in the exploration; it is not an independently
authored second implementation of an exhaustive T20 search.
"""
import json
import time
from fractions import Fraction
from pathlib import Path
from dual_local import graph, np
from dual_pairs import two_orbits
from dual_n3 import base

def exact_psd(M):
    a=[[Fraction(int(x)) for x in row] for row in M]
    for k in range(len(a)):
        if a[k][k]<0:return False
        if a[k][k]==0:
            if any(a[k][j] for j in range(k+1,len(a))):return False
            continue
        for i in range(k+1,len(a)):
            if not a[i][k]:continue
            q=a[i][k]/a[k][k]
            for j in range(i,len(a)):
                a[i][j]-=q*a[k][j]
                a[j][i]=a[i][j]
    return True

def inspect(A,certificate,reps,mates,outside):
    n=len(A)
    for i in range(n):
        for j in range(i):
            assert sum(int(A[i,h])*int(A[j,h]) for h in range(n))<=2-int(A[i,j])
    G=3*np.eye(len(reps),dtype=np.int64)-A[np.ix_(reps,reps)]+A[np.ix_(reps,mates)]
    m=[int(i in certificate['I']) for i in range(10)]+outside
    k=certificate['k']
    N=10*k*k+7*(sum(m[i]*int(G[i,j])*m[j] for i in range(len(m)) for j in range(len(m)))-2*k*sum(m[:10]))
    assert N==certificate['N'] and 0<N<10
    eye=np.eye(n,dtype=np.int64)
    return exact_psd(9*(3*eye-A)+np.ones((n,n),dtype=np.int64)) and exact_psd(11*(4*eye+A)-2*np.ones((n,n),dtype=np.int64))

def run():
    start=time.monotonic();root=Path(__file__).parent
    pairs=json.loads((root/'dual_pairs.json').read_text())
    checked=0
    for row in pairs['results']:
        B=graph(row['counts']['graph'])
        for c in row['example_certificates']:
            A=two_orbits(B,c['type1'],c['type2'],c['edge_state'])
            assert inspect(A,c,list(range(10))+[21,23],list(range(10,20))+[22,24],c['oriented_signs'])
            checked+=1
    print('pair certificates checked by full matrices:',checked,flush=True)
    n3=json.loads((root/'dual_n3.json').read_text());result=[]
    for row in n3['results']:
        gi=row['counts']['graph'];B=graph(gi);kept=[]
        for c in row['small_positive_witnesses']:
            U,V=[tuple(map(int,word)) for word in c['type'].split('/')]
            A=base(B,U,V,c['case'],c['inner'],c['edges'])
            if inspect(A,c,list(range(10))+[21,23,25,27],list(range(10,20))+[22,24,26,28],c['outside_coeff']):kept.append(c)
        result.append({'graph':gi,'new_after_psd':len(kept),'certificates':kept})
        print('n3 graph',gi,'positive certificates',len(row['small_positive_witnesses']),'new after full PSD',len(kept),flush=True)
    data={'pair_certificates_checked':checked,'n3':result,'elapsed_seconds':time.monotonic()-start}
    (root/'verified_certificates.json').write_text(json.dumps(data,indent=2)+'\n')
    print('elapsed_seconds',data['elapsed_seconds'])

if __name__=='__main__':run()
