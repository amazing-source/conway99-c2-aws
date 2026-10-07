"""Check the two Wagner certificate files with dense integer arithmetic.
This verifies each finite obstruction, not the coverage of the classification:
coverage is supplied by ENUMERER_WAGNER_PROFIL_A.py and ..._B.py.
One process, 180 seconds cap, planned memory under 128 MiB.
"""
from pathlib import Path
import json,itertools as it,time,os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np
T0=time.monotonic();root=Path(__file__).resolve().parent
def deadline():
    if time.monotonic()-T0>180:raise TimeoutError('180s verification cap')
def matrix(rows):
    n=len(rows)
    return np.array([[row>>j&1 for j in range(n)] for row in rows],dtype=np.int16)
def oldmask(mask):return np.array([mask>>j&1 for j in range(35)],dtype=np.int16)
def sigma(i):
    if i<16:return (i+8)%16
    if i<34:return 16+((i-16)^1)
    return i
def bound(A):
    C=A@A;cap=2-A
    np.fill_diagonal(cap,32767)
    return bool(np.all(C<=cap))
def candidate(A,N):
    X=np.column_stack((N,np.array([N[sigma(i)] for i in range(35)],dtype=np.int16)))
    augmented=np.zeros((37,37),dtype=np.int16)
    augmented[:35,:35]=A;augmented[:35,35:]=X;augmented[35:,:35]=X.T
    if not bound(augmented) or int(A[26]@N)!=1:return None
    return X
def K4free(rows):
    for i,row in enumerate(rows):
        for j in range(i):
            if not row>>j&1:continue
            common=row&rows[j]
            while common:
                bit=common&-common;k=bit.bit_length()-1;common^=bit
                if rows[k]&common:return False
    return True
def check_A(record):
    A=matrix(record['base_adjacency_rows']);assert bound(A)
    assert np.array_equal(A,reconstruct_B(record))
    assert np.array_equal(A,A.T) and not np.diag(A).any()
    A2=A@A;oldcap=2-A-A2;np.fill_diagonal(oldcap,32767)
    F=[int(2-A[26,16+i]-A2[26,16+i]) for i in range(10)]
    LP=[int(2-A[26,i]-A2[26,i]) for i in range(8)]
    LQ=[int(2-A[26,8+j]-A2[26,8+j]) for j in range(8)]
    assert (F,LP,LQ)==(record['demand_X0'],record['demand_P'],record['demand_Q'])
    assert sum(F)==8 and sum(LP)==sum(LQ)==4
    xs={}
    for z,w in it.combinations([i for i in range(10) if F[i]],2):
        for i in range(8):
            if not LP[i]:continue
            for j in range(8):
                if not LQ[j]:continue
                N=np.zeros(35,dtype=np.int16);N[[26,16+z,16+w,i,8+j]]=1
                X=candidate(A,N)
                if X is not None:
                    masks=tuple(sum(int(X[k,s])<<k for k in range(35)) for s in range(2))
                    xs[masks]=X
    listed=[tuple(c['neighbors']) for c in record['candidates']]
    assert len(set(listed))==len(listed) and set(listed)==set(xs)
    X=[xs[k] for k in listed];delta=[x@x.T for x in X]
    graph=[0]*len(X)
    for i,j in it.combinations(range(len(X)),2):
        if np.any(delta[i]+delta[j]>oldcap):continue
        if np.any(X[i].T@X[j]>2):continue
        graph[i]|=1<<j;graph[j]|=1<<i
    assert graph==record['compatibility_rows']
    assert K4free(graph)
    return len(X)
def reconstruct_B(r):
    A=np.zeros((35,35),dtype=np.int16)
    B=np.array([[int(j not in {i,(i-1)%8,(i+1)%8,(i+4)%8}) for j in range(8)] for i in range(8)],dtype=np.int16)
    A[:8,8:16]=B;A[8:16,:8]=B.T
    for z in range(10):
        for w in range(10):A[16+z,16+w]=r['X0_adjacency'][z]>>w&1
        for s in range(8):A[16+z,26+s]=A[26+s,16+z]=r['X0_X2_rows'][z]>>s&1
    for s,(u,v) in enumerate(r['rectangles']):
        for i in range(8):
            A[i,26+s]=A[26+s,i]=u>>i&1;A[8+i,26+s]=A[26+s,8+i]=v>>i&1
    for i,j in ((26,27),(26,34),(27,34)):A[i,j]=A[j,i]=1
    return A
def check_B(r):
    A=reconstruct_B(r);assert bound(A)
    X0=list(range(16,26))+[34];A2=A@A
    F=[int(2-A[26,z]-A2[26,z]) for z in X0]
    assert F==r['demand'] and sum(F)==8 and all(v in (0,1) for v in F)
    V=[i for i,v in enumerate(F) if v];edges=set()
    for i,j in it.combinations(V,2):
        aa=np.zeros((36,36),dtype=np.int16);aa[:35,:35]=A
        aa[35,[26,X0[i],X0[j]]]=1;aa[[26,X0[i],X0[j]],35]=1
        if bound(aa):edges.add((i,j))
    assert edges==set(map(tuple,r['allowed_edges']))
    W=set(r['independent_demand_set']);N=set()
    for i,j in edges:
        assert not (i in W and j in W)
        if i in W:N.add(j)
        if j in W:N.add(i)
    assert N==set(r['possible_partners']) and len(N)<len(W)
    return len(edges)
Adata=json.loads((root/'WAGNER_PROFIL_A_CERTIFICATS.json').read_text())
Bdata=json.loads((root/'WAGNER_PROFIL_B_CERTIFICATS.json').read_text())
assert len(Adata['records'])==240 and len(Bdata['records'])==32
candidate_count=0
for record in Adata['records']:deadline();candidate_count+=check_A(record)
for record in Bdata['records']:deadline();check_B(record)
assert candidate_count==6544
result={'verified_profile_A_obstructions':len(Adata['records']),'verified_profile_B_obstructions':len(Bdata['records']),'profile_A_candidate_orbits_recomputed':candidate_count,'arithmetic':'dense int16; maximal sum per matrix entry below 100, no overflow','coverage':'Requires the supplied enumeration sources, separately cross-checked against the first DFS.','seconds':time.monotonic()-T0}
(root/'WAGNER_VERIFICATION_INDEPENDANTE.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
