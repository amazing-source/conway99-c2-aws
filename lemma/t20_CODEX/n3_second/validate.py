"""Cross-check optimized rules against direct definitions, on small cases.

These checks do not constitute the second search and do not prove T20.
"""
import json
import random
from pathlib import Path
import numpy as np
from model import (budget,conjugate,exact_psd,mate,projector_blocks,vertices,psd)
from search import add_orbit,Search


def adjacency(rows):
    return np.array([[(row>>j)&1 for j in range(len(rows))] for row in rows],dtype=np.int64)


def direct_add(rows,mask,inner):
    n=len(rows);other=conjugate(mask)
    out=list(rows)+[mask|(inner<<(n+1)),other|(inner<<n)]
    for i in vertices(mask):out[i]|=1<<n
    for i in vertices(other):out[i]|=1<<(n+1)
    return out


def main():
    rng=random.Random(20261007)
    bases=json.loads(Path(__file__).with_name('bases.json').read_text())['bases']
    checks=dict(block_congruences=0,psd_full_matrix=0,incremental_budgets=0,schur_comparisons=0)
    for record in bases[::31]:
        rows=record['rows'];n=len(rows);A=adjacency(rows)
        reps=list(range(10))+list(range(21,n,2));r=len(reps)
        O=np.zeros((n,r),dtype=np.int64);E=np.zeros((n,r+1),dtype=np.int64)
        for j,v in enumerate(reps):
            O[v,j]=1;O[mate(v),j]=-1
            E[v,j]=E[mate(v),j]=1
        E[20,r]=1
        full=(9*(3*np.eye(n,dtype=np.int64)-A)+np.ones((n,n),dtype=np.int64),
              11*(4*np.eye(n,dtype=np.int64)+A)-2*np.ones((n,n),dtype=np.int64))
        blocks=projector_blocks(rows)
        for M,odd,even,scale in ((full[0],blocks[0],blocks[1],18),(full[1],blocks[2],blocks[3],22)):
            assert np.array_equal(O.T@M@O,scale*np.array(odd))
            assert np.array_equal(E.T@M@E,np.array(even))
            assert not (O.T@M@E).any()
            checks['block_congruences']+=1
            assert exact_psd(M)==(exact_psd(odd) and exact_psd(even))
            checks['psd_full_matrix']+=1
        # Unrestricted candidate data intentionally exercises failing budgets.
        for _ in range(100):
            U=rng.sample(range(10),2);V=rng.sample(range(10),2)
            inner=rng.randrange(2)
            mask=sum(1<<i for i in U)+sum(1<<(10+i) for i in V)
            mask|=(inner<<20)|(rng.randrange(4)<<21)|(rng.randrange(64)<<23)
            brute=direct_add(rows,mask,inner)
            fast=add_orbit(rows,mask,inner)
            assert (fast is not None)==budget(brute)
            if fast is not None:assert fast==brute
            checks['incremental_budgets']+=1
    # Singular and indefinite matrices, including zero-diagonal/nonzero-row.
    for M,answer in (([[0,1],[1,0]],False),([[1,1],[1,1]],True),
                     ([[2,3],[3,2]],False),([[0,0],[0,1]],True)):
        assert exact_psd(M)==answer
    for record in bases[::201]:
        search=Search(record);search.catalog()
        for c in search.candidates[::max(1,len(search.candidates)//10)]:
            rows=direct_add(search.base,c.mask,c.inner)
            assert psd(rows)
            checks['schur_comparisons']+=1
        for _ in range(80):
            a,b=rng.choices(search.candidates,k=2)
            pattern=rng.randrange(4)
            rows=direct_add(search.base,a.mask,a.inner)
            mask=b.mask|((pattern&1)<<29)|(((pattern>>1)&1)<<30)
            extended=direct_add(rows,mask,b.inner)
            fast=add_orbit(rows,mask,b.inner)
            assert (fast is not None)==budget(extended)
            checks['incremental_budgets']+=1
            entries=search.reduction.entries(search.reduction.offsets(a.schur,b.schur),pattern)
            reduced=all(x[2]*y[2]>=e*e for x,y,e in zip(a.schur,b.schur,entries))
            assert reduced==psd(extended)
            checks['schur_comparisons']+=1
    print(json.dumps(checks),flush=True)


if __name__=='__main__':main()
