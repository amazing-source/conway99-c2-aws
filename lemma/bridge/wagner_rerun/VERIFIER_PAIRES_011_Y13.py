"""Exact verification of the 363 Y=13 witnesses and their lattice membership.
Python standard library only. One process, 180s cap, planned memory <64 MiB.
The graph-theoretic exclusion theorem is supplied in the accompanying note.
"""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib, time

root=Path(__file__).resolve().parent
start=time.monotonic()
def deadline():
    if time.monotonic()-start>180:raise TimeoutError('180s cap')
def inverse(A):
    n=len(A);M=[list(map(F,r))+[F(i==j) for j in range(n)] for i,r in enumerate(A)]
    for j in range(n):
        k=next(i for i in range(j,n) if M[i][j]);M[k],M[j]=M[j],M[k]
        pivot=M[j][j];M[j]=[q/pivot for q in M[j]]
        for i in range(n):
            if i!=j and M[i][j]:
                q=M[i][j];M[i]=[a-q*b for a,b in zip(M[i],M[j])]
    return [r[n:] for r in M]
def transition(A,Binverse):
    n=len(A)
    return [[sum(A[i][k]*Binverse[k][j] for k in range(n)) for j in range(n)] for i in range(len(A))]
def determinant_integer(A):
    M=[r[:] for r in A];n=len(M);last=1;sign=1
    for k in range(n-1):
        p=next(i for i in range(k,n) if M[i][k])
        if p!=k:M[k],M[p]=M[p],M[k];sign=-sign
        pivot=M[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                q=M[i][j]*pivot-M[i][k]*M[k][j]
                assert q%last==0;M[i][j]=q//last
        for i in range(k+1,n):M[i][k]=0
        last=pivot
    return sign*M[-1][-1]
def dot(v,w,G):return sum(v[i]*sum(G[i][j]*w[j] for j in range(len(w))) for i in range(len(v)))
def ambient(c,B):return [sum(c[i]*B[i][j] for i in range(len(c))) for j in range(len(B))]

data=json.loads((root/'PAIRES_011_TEMOINS_Y13.json').read_text(encoding='utf8'))
for source in data['source_files']:
    assert hashlib.sha256((root/source['copy']).read_bytes()).hexdigest()==source['sha256']
U=json.loads((root/'SOURCE_U_011.json').read_text(encoding='utf8'))
pairs=json.loads((root/'SOURCE_011_SAMPLE_PAIRS.json').read_text(encoding='utf8'))
B=[list(map(F,r)) for r in data['basis_ambient_coordinates']]
gens=[list(map(F,r)) for r in U['gens']];G=data['gram'];n=len(B)
assert n==24 and len(gens)==24
assert [[sum(B[i][k]*B[j][k] for k in range(n)) for j in range(n)] for i in range(n)]==G
for change in (transition(B,inverse(gens)),transition(gens,inverse(B))):
    assert all(q.denominator==1 for r in change for q in r)
assert determinant_integer(G)==1

seen=set();selected_nodes=0
for cert in data['certificates']:
    deadline();idx=cert['pair_index'];assert idx not in seen;seen.add(idx)
    pair=pairs[idx];y1=cert['y1_coefficients'];y2=cert['y2_coefficients'];x=cert['x_coefficients']
    assert all(isinstance(t,int) for v in (y1,y2,x) for t in v)
    assert ambient(y1,B)==list(map(F,pair['y1'])) and ambient(y2,B)==list(map(F,pair['y2']))
    assert dot(y1,y1,G)==dot(y2,y2,G)==7 and dot(y1,y2,G)==0
    a=dot(x,y1,G);b=dot(x,y2,G)
    assert dot(x,x,G)==3 and [a,b]==cert['products'] and a*a+b*b==13
    q=[7*t-a*s-b*r for t,s,r in zip(x,y1,y2)]
    assert dot(q,q,G)==56 and dot(q,y1,G)==dot(q,y2,G)==0
    assert pair['K']==cert['K'] and sum(pair['nodes'])==cert['historical_nodes']
    selected_nodes+=sum(pair['nodes'])
assert len(pairs)==data['pairs_examined']==400
assert len(seen)==data['pairs_with_exact_Y13_witness']==363
assert sorted(set(range(len(pairs)))-seen)==data['pairs_without_found_witness']
assert selected_nodes==data['historical_nodes_on_witness_pairs']
assert sum(sum(p['nodes']) for p in pairs)==data['historical_nodes']
assert not any(p['K']==0 for p in pairs)
result={'verified_witnesses':len(seen),'basis_equals_catalog_lattice':'integer transition matrices in both directions','gram_determinant_exact':1,'arithmetic':'Python integers and exact fractions only','sample_has_K0_pairs':False,'historical_nodes_on_witness_pairs':selected_nodes,'historical_nodes_total':data['historical_nodes'],'seconds':time.monotonic()-start}
(root/'PAIRES_011_VERIFICATION_INDEPENDANTE.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
