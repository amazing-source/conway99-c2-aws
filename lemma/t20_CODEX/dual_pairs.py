"""Exact two-word consequences of the independent-triple / one-edge-four-set lemma.
Scans only pairs touched by those hand lemmas. This does NOT prove T20.
"""
import json
import itertools as it
import math
import time
from pathlib import Path
from dual_local import np, graph, schur_setup, budgets

def scaled_inverse(M):
    den=math.lcm(*(x.denominator for row in M for x in row))
    nums=[[int(x*den) for x in row] for row in M]
    return den,np.array(nums,dtype=object)

def two_orbits(B,t1,t2,state):
    A=np.zeros((25,25),dtype=np.int64)
    A[:10,10:20]=B
    A[10:20,:10]=B
    for (U,V),w,wp in [(t1,21,22),(t2,23,24)]:
        for i in U: A[i,w]=A[w,i]=A[10+i,wp]=A[wp,10+i]=1
        for i in V: A[i,wp]=A[wp,i]=A[10+i,w]=A[w,10+i]=1
    if state&1:
        for i,j in [(21,23),(22,24)]: A[i,j]=A[j,i]=1
    if state&2:
        for i,j in [(21,24),(22,23)]: A[i,j]=A[j,i]=1
    return A

def run():
    started=time.monotonic()
    local=json.loads(Path(__file__).with_name('dual_local.json').read_text())
    result=[]
    for index in range(6):
        B=graph(index)
        types=[(tuple(t['U']),tuple(t['V'])) for row in local['graphs'][index]
               if row['counts']['d']==2 and row['counts']['inner']==0 for t in row['survivors']]
        families=[]
        for size,e,k in [(3,0,2),(4,1,3)]:
            for I in it.combinations(range(10),size):
                if sum(int(B[a,b]) for a,b in it.combinations(I,2))==e:
                    families.append((I,k))
        sig=[]
        vectors=[[],[],[],[]]
        for U,V in types:
            u=np.array([int(i in U) for i in range(10)],dtype=np.int64)
            v=np.array([int(i in V) for i in range(10)],dtype=np.int64)
            sig.append(tuple(sum(int(u[i]-v[i]) for i in I) for I,k in families))
            vectors[0].append(v-u)
            vectors[1].append(v-u)
            vectors[2].append(list(4-18*(u+v))+[2])
            vectors[3].append(list(22*(u+v)-8)+[-4])
        projections=[]
        residuals=[]
        denominators=[]
        for inv,V,diag in zip(schur_setup(B),vectors,[3,4,58,80]):
            den,M=scaled_inverse(inv)
            V=np.array(V,dtype=object)
            Q=V@M@V.T
            projections.append(Q)
            residuals.append([diag*den-int(Q[i,i]) for i in range(len(types))])
            denominators.append(den)
        counts={'graph':index,'types':len(types),'families':len(families),'affected_pairs':0,
                'budget_patterns':0,'psd_patterns':0,'dual_excluded_patterns':0,
                'new_incompatible_pairs':0,'strengthened_pairs':0}
        certificates=[]
        for i,j in it.combinations(range(len(types)),2):
            requirements={}
            for f,(a,b) in enumerate(zip(sig[i],sig[j])):
                if abs(a)==2 and abs(b)==2: requirements.setdefault(a*b//4,f)
            if not requirements: continue
            counts['affected_pairs']+=1
            before=[]; after=[]
            for state in range(4):
                if not budgets(two_orbits(B,types[i],types[j],state)): continue
                counts['budget_patterns']+=1
                direct=state&1; cross=(state>>1)&1
                g=cross-direct
                betas=[g,-g,4-18*(direct+cross),-8+22*(direct+cross)]
                if any(residuals[t][i]*residuals[t][j] <
                       (betas[t]*denominators[t]-int(projections[t][i,j]))**2 for t in range(4)): continue
                counts['psd_patterns']+=1
                before.append(state)
                bad=next(((sign,f) for sign,f in requirements.items() if g!=sign),None)
                if bad is None: after.append(state)
                else:
                    sign,f=bad; I,k=families[f]
                    norm=(5 if k==2 else 6)+14*sign*g
                    assert norm in [5,6], ('PSD should reject negative norm',norm)
                    counts['dual_excluded_patterns']+=1
                    if len(certificates)<20:
                        certificates.append({'type1':types[i],'type2':types[j],'edge_state':state,
                            'I':I,'k':k,'oriented_signs':[sig[i][f]//2,sig[j][f]//2],'N':norm})
            if before and not after: counts['new_incompatible_pairs']+=1
            if before and len(after)<len(before): counts['strengthened_pairs']+=1
        result.append({'counts':counts,'example_certificates':certificates})
        print(json.dumps(counts),flush=True)
    data={'scope':'pairs of distinct word X2 types touched by the two proved hand rules',
          'elapsed_seconds':time.monotonic()-started,'results':result}
    Path(__file__).with_suffix('.json').write_text(json.dumps(data,indent=2)+'\n')
    print('elapsed_seconds',data['elapsed_seconds'])

if __name__=='__main__':run()
