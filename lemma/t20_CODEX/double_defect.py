"""Small exploration: can both outside common neighbours of a deficient pair be words?"""
import itertools as it
import json
from pathlib import Path
from dual_local import np, graph, schur_setup, budgets
from dual_pairs import scaled_inverse, two_orbits

def run():
    local=json.loads(Path(__file__).with_name('dual_local.json').read_text())
    data=[]
    for index in range(6):
        B=graph(index); codeg=B@B
        types=[(tuple(t['U']),tuple(t['V'])) for row in local['graphs'][index]
               if row['counts']['d']==2 and row['counts']['inner']==0 for t in row['survivors']]
        families=[I for size,e in [(3,0),(4,1)] for I in it.combinations(range(10),size)
                  if sum(int(B[a,b]) for a,b in it.combinations(I,2))==e]
        inv=schur_setup(B)
        for U in it.combinations(range(10),2):
            if codeg[U]!=0: continue
            ts=[(U,t[1] if t[0]==U else t[0]) for t in types if U in t]
            vectors=[[],[],[],[]]; sig=[]
            for _,V in ts:
                u=np.array([int(i in U) for i in range(10)])
                v=np.array([int(i in V) for i in range(10)])
                sig.append(tuple(sum(int(u[i]-v[i]) for i in I) for I in families))
                for arr,row in zip(vectors,[v-u,v-u,list(4-18*(u+v))+[2],list(22*(u+v)-8)+[-4]]): arr.append(row)
            qs=[];rs=[];ds=[]
            for M,V,diag in zip(inv,vectors,[3,4,58,80]):
                den,nums=scaled_inverse(M); V=np.array(V,dtype=object)
                Q=V@nums@V.T
                qs.append(Q); ds.append(den); rs.append([diag*den-int(Q[i,i]) for i in range(len(ts))])
            before=[];after=[]
            for i,j in it.combinations(range(len(ts)),2):
                for state in range(4):
                    if not budgets(two_orbits(B,ts[i],ts[j],state)):continue
                    a=state&1;b=(state>>1)&1;g=b-a
                    betas=[g,-g,4-18*(a+b),-8+22*(a+b)]
                    if any(rs[t][i]*rs[t][j]<(betas[t]*ds[t]-int(qs[t][i,j]))**2 for t in range(4)):continue
                    record=[ts[i][1],ts[j][1],state]
                    before.append(record)
                    if all(abs(s)!=2 or abs(t)!=2 or g==s*t//4 for s,t in zip(sig[i],sig[j])):after.append(record)
            row={'graph':index,'U':U,'word_types':len(ts),'before':len(before),'after':len(after),'survivors':after}
            data.append(row)
            print(json.dumps({k:v for k,v in row.items() if k!='survivors'}),flush=True)
    Path(__file__).with_suffix('.json').write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':run()
