"""Independent tiny search on S + X3 + X0, from NOTES H1/H2 only.
No full configuration search and no solver. Negative norms are PSD obstructions;
positive norms below 10 are small-dual-norm obstructions. Tests only stated
coefficient ranges, so survival never claims absence of all such obstructions.
"""
import itertools as it
import json
import time
from pathlib import Path
from dual_local import np,graph,budgets

TYPES=[['034/179'],['034/178','034/258','034/278','257/268','257/368','257/678','258/345','278/349','368/457'],
       ['034/189','034/589','345/389'],['034/156','034/159','159/168','159/368'],
       ['025/279','027/035','035/169','035/279','279/348'],['012/168','012/579','016/359']]

def base(B,U,V,case,inner,edges):
    A=np.zeros((29,29),dtype=np.int64)
    A[:10,10:20]=B;A[10:20,:10]=B
    def edge(a,b):A[a,b]=A[b,a]=1
    for i in U:edge(i,21);edge(10+i,22)
    for i in V:edge(i,22);edge(10+i,21)
    T={'i':[23,25,27],'ii':[23,24,25],'iii':[23,24,25,27]}[case]
    for w in T:edge(21,w);edge(22,w+1 if w%2 else w-1)
    if inner is not None:
        a=23+2*inner
        edge(a,a+1);edge(20,a);edge(20,a+1)
    for n,(i,j) in enumerate(it.combinations(range(3),2)):
        a,b=23+2*i,23+2*j
        if edges&(1<<(2*n)):edge(a,b);edge(a+1,b+1)
        if edges&(1<<(2*n+1)):edge(a,b+1);edge(a+1,b)
    return A

def run():
    started=time.monotonic()
    bits=np.array([[(mask>>i)&1 for i in range(10)] for mask in range(1024)],dtype=np.int64)
    sizes=bits.sum(axis=1)
    coeff=np.array(list(it.product(range(-2,3),repeat=3)),dtype=np.int64)
    rows=[]
    for gi in range(6):
        B=graph(gi);edge2=np.sum((bits@B)*bits,axis=1)
        support=np.array([10*k*k+7*((3-2*k)*sizes+edge2) for k in (1,2,3)])
        stats={'graph':gi,'labelled':0,'budget_degree':0,'negative_certificate':0,'small_positive_certificate':0,'remaining':0}
        witnesses=[]
        for typ in TYPES[gi]:
            U,V=[tuple(map(int,word)) for word in typ.split('/')]
            b=np.array([int(i in U)-int(i in V) for i in range(10)])
            s=bits@b
            for case in ['i','ii','iii']:
                if set(U)&set(V) and case!='i':continue
                for inner in [None,0,1,2]:
                    if case!='i' and inner==0:continue
                    for edges in range(64):
                        stats['labelled']+=1
                        A=base(B,U,V,case,inner,edges)
                        if not budgets(A):continue
                        X0=[20,23,24,25,26,27,28]
                        a0=A[np.ix_(range(23,29),X0)].sum(axis=1)
                        a3=A[23:29,21:23].sum(axis=1)
                        if any(8-2*d0+d3<0 for d0,d3 in zip(a0,a3)):continue
                        stats['budget_degree']+=1
                        reps=[21,23,25,27];mates=[22,24,26,28]
                        G=3*np.eye(4,dtype=np.int64)-A[np.ix_(reps,reps)]+A[np.ix_(reps,mates)]
                        q=np.sum((coeff@G[1:,1:])*coeff,axis=1)
                        minimum=None;certificate=None
                        for t in range(-3,4):
                            qc=q+2*t*(coeff@G[0,1:])
                            ci=int(np.argmin(qc)); shift=int(qc[ci])
                            N=support+7*(3*t*t-2*t*s+shift)
                            loc=np.unravel_index(int(np.argmin(N)),N.shape)
                            n=int(N[loc])
                            if minimum is None or n<minimum:
                                minimum=n
                                certificate={'type':typ,'case':case,'inner':inner,'edges':edges,'k':int(loc[0])+1,
                                             'I':[i for i in range(10) if bits[loc[1],i]],'outside_coeff':[t]+list(map(int,coeff[ci])),'N':n}
                        if minimum<0:stats['negative_certificate']+=1
                        elif minimum<10:
                            assert minimum>0
                            stats['small_positive_certificate']+=1;witnesses.append(certificate)
                        else:stats['remaining']+=1
        rows.append({'counts':stats,'small_positive_witnesses':witnesses})
        print(json.dumps(stats),flush=True)
    data={'elapsed_seconds':time.monotonic()-started,'coefficient_range':{'support':'0,1','z':'-3..3','X0_orbits':'-2..2'},'results':rows}
    Path(__file__).with_suffix('.json').write_text(json.dumps(data,indent=2)+'\n')
    print('elapsed_seconds',data['elapsed_seconds'])

if __name__=='__main__':run()
