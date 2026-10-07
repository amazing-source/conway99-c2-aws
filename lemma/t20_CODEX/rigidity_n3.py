"""Apply the hand theorem PROFILE_421 to the tiny n3=2 bases, exact PSD only."""
import itertools as it
import json
import time
from pathlib import Path
from dual_local import graph,np,budgets
from dual_n3 import TYPES,base
from verify_certificates import exact_psd

def run():
    started=time.monotonic();rows=[]
    for gi in range(6):
        B=graph(gi);stats={'graph':gi,'labelled':0,'budget_degree':0,'psd':0};kept=[]
        for typ in TYPES[gi]:
            U,V=[tuple(map(int,w)) for w in typ.split('/')]
            for case in ['i','ii','iii']:
                if set(U)&set(V) and case!='i':continue
                for inner in range(3):
                    if case!='i' and inner==0:continue
                    for edges in range(64):
                        if any(edges&(3<<(2*k)) for k,pair in enumerate(it.combinations(range(3),2)) if inner in pair):continue
                        stats['labelled']+=1
                        A=base(B,U,V,case,inner,edges)
                        if not budgets(A):continue
                        a0=A[np.ix_(range(23,29),[20,23,24,25,26,27,28])].sum(axis=1)
                        a3=A[23:29,21:23].sum(axis=1)
                        if any(8-2*b+g<0 for b,g in zip(a0,a3)):continue
                        stats['budget_degree']+=1
                        eye=np.eye(29,dtype=np.int64);one=np.ones((29,29),dtype=np.int64)
                        if not exact_psd(9*(3*eye-A)+one) or not exact_psd(11*(4*eye+A)-2*one):continue
                        stats['psd']+=1;kept.append({'type':typ,'case':case,'inner':inner,'edges':edges})
        rows.append({'counts':stats,'kept':kept});print(json.dumps(stats),flush=True)
    data={'scope':'n3=2, profile421, hand isolation theorem plus exact base budgets/PSD, no isomorphism quotient',
          'elapsed_seconds':time.monotonic()-started,'results':rows}
    Path(__file__).with_suffix('.json').write_text(json.dumps(data,indent=2)+'\n')
    print('elapsed_seconds',data['elapsed_seconds'])

if __name__=='__main__':run()
