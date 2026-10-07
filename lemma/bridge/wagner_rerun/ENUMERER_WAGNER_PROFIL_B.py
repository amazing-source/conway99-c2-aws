"""Independent finite audit of Wagner, global profile B.
Direct products of row-orbit combinations; direct partial adjacency counts.
One process, 180 seconds cap, planned memory under 128 MiB.
Does not use x0x2_probe or x1_incidence_probe.
"""
from pathlib import Path
import itertools as it, json, time
T0=time.monotonic()
def deadline():
    if time.monotonic()-T0>180:raise TimeoutError('180s cap')
def swapmask(m):return sum(1<<(i^1) for i in range(8) if m>>i&1)
def perfect_matchings(items):
    if not items:yield ();return
    for k in range(1,len(items)):
        for rest in perfect_matchings(items[1:k]+items[k+1:]):yield ((items[0],items[k]),)+rest
def sumvec(a,b):return tuple(x+y for x,y in zip(a,b))
coords=[(i,i) for i in range(8)]+list(it.combinations(range(8),2))
def rowvec(m):return tuple(int((m>>i&1) and (m>>j&1)) for i,j in coords)
def neighbor_pair_vec(m):return sumvec(rowvec(m),rowvec(swapmask(m)))
B=[sum(1<<j for j in range(8) if j not in {i,(i-1)%8,(i+1)%8,(i+4)%8}) for i in range(8)]
defedges=[(1<<i)|(1<<j) for i,j in it.combinations(range(8),2) if (B[i]&B[j]).bit_count()==1]
assert len(defedges)==8
edge_orbits=[]
for i,j in it.combinations(range(5),2):
    for orientation in (0,1):edge_orbits.append(((2*i,2*j+orientation),(2*i+1,2*j+(orientation^1))))
graphs=[]
for selected in it.combinations(edge_orbits,3):
    g=[0]*10
    for orbit in selected:
        for i,j in orbit:g[i]|=1<<j;g[j]|=1<<i
    if [m.bit_count() for m in g]==[2,2,2,2,1,1,1,1,0,0]:graphs.append(g)
assert len(graphs)==18
def partial_graph(rects,C,g):
    A=[0]*35
    def edge(i,j):A[i]|=1<<j;A[j]|=1<<i
    for i in range(8):
        for j in range(8):
            if B[i]>>j&1:edge(i,8+j)
    for z in range(10):
        for w in range(z):
            if g[z]>>w&1:edge(16+z,16+w)
        for s in range(8):
            if C[z]>>s&1:edge(16+z,26+s)
    for s,(u,v) in enumerate(rects):
        for i in range(8):
            if u>>i&1:edge(i,26+s)
            if v>>i&1:edge(8+i,26+s)
    edge(26,27);edge(34,26);edge(34,27)
    return A
def locally_valid(A):
    return all((A[i]&A[j]).bit_count()<=2-(A[i]>>j&1) for i in range(len(A)) for j in range(i))
def demands_and_allowed(A):
    # x=26, p=34, X0 vertices 16..25 plus p.
    X0=list(range(16,26))+[34]
    F=[2-(A[26]>>z&1)-(A[26]&A[z]).bit_count() for z in X0]
    assert sum(F)==8 and all(f in (0,1) for f in F)
    V=[i for i,f in enumerate(F) if f]
    allowed={i:set() for i in V}
    for i,j in it.combinations(V,2):
        augmented=A[:]+[0]
        for z in (26,X0[i],X0[j]):augmented[z]|=1<<35;augmented[35]|=1<<z
        if locally_valid(augmented):allowed[i].add(j);allowed[j].add(i)
    witnesses=[]
    for W in it.combinations(V,3):
        if any(j in allowed[i] for i,j in it.combinations(W,2)):continue
        N=set().union(*(allowed[i] for i in W))
        if len(N)<len(W):witnesses.append((list(W),sorted(N)))
    return F,allowed,witnesses
counts={'perfect_matchings':0,'matching_survivors':0,'marked_inner_orbits':0,'incidence_matrices':0,'partial_graphs':0}
records=[]
for matching in perfect_matchings(tuple(defedges)):
    deadline();counts['perfect_matchings']+=1
    rr=[r for u,v in matching for r in ((u,v),(v,u))]
    if any((B[i]&v).bit_count()>1 for u,v in rr for i in range(8) if u>>i&1):continue
    if any((rr[i][0]&rr[j][0]).bit_count()+(rr[i][1]&rr[j][1]).bit_count()>2 for i in range(8) for j in range(i)):continue
    if any(sum(int((u>>i&1) and (v>>j&1)) for u,v in rr)>2-(B[i]>>j&1) for i in range(8) for j in range(8)):continue
    counts['matching_survivors']+=1
    for special,(u,v) in enumerate(matching):
        if u&v:continue
        counts['marked_inner_orbits']+=1
        rotated=(matching[special],)+matching[:special]+matching[special+1:]
        rects=[r for u,v in rotated for r in ((u,v),(v,u))]
        sc=[[((u&uu).bit_count()+(v&vv).bit_count()) for uu,vv in rects] for u,v in rects]
        target=tuple(4 if i==j else (0 if (i,j)==(0,1) else 2-sc[i][j]) for i,j in coords)
        fam={}
        for a in (2,3,4):
            family=[]
            for js in it.combinations(range(8),a):
                m=sum(1<<i for i in js);ms=swapmask(m)
                if m>ms or (m&ms).bit_count()>2:continue
                vec=neighbor_pair_vec(m)
                if any(z>t for z,t in zip(vec,target)):continue
                family.append((m,ms,vec))
            fam[a]=family
        for high in it.combinations(fam[4],2):
            vh=sumvec(high[0][2],high[1][2])
            if any(z>t for z,t in zip(vh,target)):continue
            for middle in it.combinations(fam[3],2):
                deadline()
                vm=sumvec(vh,sumvec(middle[0][2],middle[1][2]))
                if any(z>t for z,t in zip(vm,target)):continue
                for low in fam[2]:
                    if sumvec(vm,low[2])!=target:continue
                    C=[m for row in (*high,*middle,low) for m in row[:2]]
                    if any((C[i]&C[j]).bit_count()>2 for i in range(10) for j in range(i)):continue
                    counts['incidence_matrices']+=1
                    for g in graphs:
                        A=partial_graph(rects,C,g)
                        if not locally_valid(A):continue
                        counts['partial_graphs']+=1
                        F,allowed,witnesses=demands_and_allowed(A)
                        assert witnesses, 'No three-against-two certificate for a retained graph'
                        W,N=witnesses[0]
                        records.append({'rectangles':rects,'X0_X2_rows':C,'X0_adjacency':g,'demand':F,'allowed_edges':[[i,j] for i in allowed for j in allowed[i] if i<j],'independent_demand_set':W,'possible_partners':N})
assert counts['perfect_matchings']==105
assert counts['incidence_matrices']==16 and counts['partial_graphs']==32
result={'status':'EXACT_FINITE_CLASSIFICATION_PLUS_HUMAN_MATCHING_OBSTRUCTION','scope':'Wagner, global profile B. The separate profile A audit is also supplied. No whole lattice exclusion.','counts':counts,'certificate_count':len(records),'records':records,'seconds':time.monotonic()-T0,'limits':{'processes':1,'time_cap_seconds':180,'planned_memory_MiB':128}}
json.dump(result,open(Path(__file__).resolve().parent/'WAGNER_PROFIL_B_CERTIFICATS.json','w',encoding='utf8'),indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='records'}))
