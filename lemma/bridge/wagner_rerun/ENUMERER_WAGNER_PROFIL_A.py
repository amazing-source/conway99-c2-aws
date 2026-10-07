"""Independent coverage and neighborhood audit for Wagner, global profile A.
Direct combinations for incidence matrices; bitset four-cliques for neighbors.
One process, 180 seconds cap, planned memory under 128 MiB.
No code from the previous DFS or its result files is loaded.
"""
from pathlib import Path
import itertools as it,json,time,collections
T0=time.monotonic()
def deadline():
    if time.monotonic()-T0>180:raise TimeoutError('180s cap')
def sw(m):return sum(1<<(i^1) for i in range(8) if m>>i&1)
def sigma_vertex(i):
    if i<16:return i+8 if i<8 else i-8
    if i<34:return 16+((i-16)^1)
    return i
def matchings(items):
    if not items:yield ();return
    for j in range(1,len(items)):
        for rest in matchings(items[1:j]+items[j+1:]):yield ((items[0],items[j]),)+rest
B=[sum(1<<j for j in range(8) if j not in {i,(i-1)%8,(i+1)%8,(i+4)%8}) for i in range(8)]
deficiencies=[(1<<i)|(1<<j) for i,j in it.combinations(range(8),2) if (B[i]&B[j]).bit_count()==1]
coords=[(i,i) for i in range(8)]+list(it.combinations(range(8),2))
def vector(m):return tuple(int((m>>i&1) and (m>>j&1))+int((sw(m)>>i&1) and (sw(m)>>j&1)) for i,j in coords)
tag_vectors={}
for i,j in it.combinations(range(8),2):
    m=(1<<i)|(1<<j)
    if m>sw(m):continue
    tag_vectors[(0,)*8+vector(m)[8:]]=(m,sw(m))
G_orbits=[]
for i,j in it.combinations(range(5),2):
    for s in (0,1):G_orbits.append(((2*i,2*j+s),(2*i+1,2*j+(s^1))))
graphs=[]
for selected in it.combinations(G_orbits,3):
    G=[0]*10
    for es in selected:
        for i,j in es:G[i]|=1<<j;G[j]|=1<<i
    if [m.bit_count() for m in G]==[2,2]+[1]*8:graphs.append(G)
assert len(graphs)==48
def base_adjacency(rectangles,C,G):
    adj=[0]*35
    def put(i,j):adj[i]|=1<<j;adj[j]|=1<<i
    for i in range(8):
        for j in range(8):
            if B[i]>>j&1:put(i,8+j)
    for z in range(10):
        for w in range(z):
            if G[z]>>w&1:put(16+z,16+w)
        for s in range(8):
            if C[z]>>s&1:put(16+z,26+s)
    for s,(u,v) in enumerate(rectangles):
        for i in range(8):
            if u>>i&1:put(i,26+s)
            if v>>i&1:put(8+i,26+s)
    for i,j in ((26,27),(26,34),(27,34)):put(i,j)
    return adj
def all_common_bounds(adj):
    return all((adj[i]&adj[j]).bit_count()<=2-(adj[i]>>j&1) for i in range(len(adj)) for j in range(i))
old_pairs=list(it.combinations(range(35),2))
def old_coverage(n0,n1):
    result=collections.Counter()
    for mask in (n0,n1):
        vertices=[i for i in range(35) if mask>>i&1]
        result.update(it.combinations(vertices,2))
    return dict(result)
def candidates_for(base,F,LP,LQ):
    out=[]
    for z,w in it.combinations([i for i in range(10) if F[i]],2):
        for i in range(8):
            if not LP[i]:continue
            for j in range(8):
                if not LQ[j]:continue
                n0=sum(1<<v for v in (26,16+z,16+w,i,8+j))
                n1=sum(1<<sigma_vertex(v) for v in range(35) if n0>>v&1)
                aa=base[:]+[n0,n1]
                for v in range(35):
                    if n0>>v&1:aa[v]|=1<<35
                    if n1>>v&1:aa[v]|=1<<36
                if not all_common_bounds(aa):continue
                if (aa[26]&aa[35]).bit_count()!=1:continue
                out.append({'X0':[z,w],'cell':[i,j],'neighbors':[n0,n1],'coverage':old_coverage(n0,n1)})
    return out
def audit_four(base,F,LP,LQ):
    ca=candidates_for(base,F,LP,LQ)
    budgets={(i,j):2-(base[i]>>j&1)-(base[i]&base[j]).bit_count() for i,j in old_pairs}
    conn=[0]*len(ca)
    for a,b in it.combinations(range(len(ca)),2):
        x,y=ca[a],ca[b]
        if any((u&v).bit_count()>2 for u in x['neighbors'] for v in y['neighbors']):continue
        if any(z+y['coverage'].get(p,0)>budgets[p] for p,z in x['coverage'].items()):continue
        conn[a]|=1<<b;conn[b]|=1<<a
    four_cliques=0;demand_covers=0;whole_covers=0
    def visit(chosen,remaining):
        nonlocal four_cliques,demand_covers,whole_covers
        if len(chosen)==4:
            four_cliques+=1
            ff=[0]*10;pp=[0]*8;qq=[0]*8
            for k in chosen:
                z,w=ca[k]['X0'];i,j=ca[k]['cell'];ff[z]+=1;ff[w]+=1;pp[i]+=1;qq[j]+=1
            if (ff,pp,qq)!=(F,LP,LQ):return
            demand_covers+=1
            cover=collections.Counter()
            for k in chosen:cover.update(ca[k]['coverage'])
            if any(v>budgets[p] for p,v in cover.items()):return
            whole_covers+=1
            return
        while remaining:
            bit=remaining&-remaining;k=bit.bit_length()-1;remaining^=bit
            visit(chosen+[k],remaining&conn[k])
    visit([], (1<<len(ca))-1)
    assert four_cliques==0, 'A compatible set of four candidate orbits was found'
    return {'candidates':[{k:v for k,v in c.items() if k!='coverage'} for c in ca],'compatibility_rows':conn,'four_cliques':four_cliques,'demand_covers':demand_covers,'local_assemblies':whole_covers}
counts={'perfect_matchings':0,'admissible_matchings':0,'marked_inner_orbits':0,'incidence_matrices':0,'partial_graphs':0,'matching_obstruction':0,'neighborhood_checks':0}
records=[];e_f_census=collections.Counter()
for matching in matchings(tuple(deficiencies)):
    deadline();counts['perfect_matchings']+=1
    rr=[r for u,v in matching for r in ((u,v),(v,u))]
    if any((B[i]&v).bit_count()>1 for u,v in rr for i in range(8) if u>>i&1):continue
    if any((rr[i][0]&rr[j][0]).bit_count()+(rr[i][1]&rr[j][1]).bit_count()>2 for i in range(8) for j in range(i)):continue
    if any(sum(int((u>>i&1) and (v>>j&1)) for u,v in rr)>2-(B[i]>>j&1) for i in range(8) for j in range(8)):continue
    counts['admissible_matchings']+=1
    for special,(u,v) in enumerate(matching):
        if u&v:continue
        counts['marked_inner_orbits']+=1
        marked=(matching[special],)+matching[:special]+matching[special+1:]
        rectangles=[r for u,v in marked for r in ((u,v),(v,u))]
        sc=[[((u&uu).bit_count()+(v&vv).bit_count()) for uu,vv in rectangles] for u,v in rectangles]
        target=tuple(4 if i==j else (0 if (i,j)==(0,1) else 2-sc[i][j]) for i,j in coords)
        fam={}
        for degree in (3,4):
            ff=[]
            for js in it.combinations(range(8),degree):
                m=sum(1<<j for j in js);mm=sw(m)
                if m>mm or (m&mm).bit_count()>2:continue
                vv=vector(m)
                if any(x>t for x,t in zip(vv,target)):continue
                ff.append((m,mm,vv))
            fam[degree]=ff
        for high in fam[4]:
            for mids in it.combinations(fam[3],4):
                deadline()
                total=tuple(sum(row[2][k] for row in (high,)+mids) for k in range(36))
                rem=tuple(t-v for t,v in zip(target,total))
                if rem not in tag_vectors:continue
                C=[v for row in (high,)+mids for v in row[:2]]
                if any((C[i]&C[j]).bit_count()>2 for i in range(10) for j in range(i)):continue
                counts['incidence_matrices']+=1
                tags=tag_vectors[rem]
                # This also follows from the degree identity at x;
                # verify it on the classification without assuming it.
                assert not ((tags[0]|tags[1])&3)
                assert not (C[0]&3 or C[1]&3)
                for G in graphs:
                    base=base_adjacency(rectangles,C,G)
                    if not all_common_bounds(base):continue
                    counts['partial_graphs']+=1
                    U,V=rectangles[0]
                    e=sum((B[i]&V).bit_count() for i in range(8) if U>>i&1)
                    T=[i for i in range(10) if C[i]&1]
                    f=sum(G[i]>>j&1 for i,j in it.combinations(T,2))
                    e_f_census[e,f]+=1
                    if e+f<2:counts['matching_obstruction']+=1;continue
                    assert (e,f)==(1,1)
                    F=[2-(base[26]>>(16+i)&1)-(base[26]&base[16+i]).bit_count() for i in range(10)]
                    LP=[2-(base[26]>>i&1)-(base[26]&base[i]).bit_count() for i in range(8)]
                    LQ=[2-(base[26]>>(8+j)&1)-(base[26]&base[8+j]).bit_count() for j in range(8)]
                    assert sum(F)==8 and sum(LP)==sum(LQ)==4
                    checked=audit_four(base,F,LP,LQ)
                    counts['neighborhood_checks']+=1
                    records.append({'rectangles':rectangles,'X0_X2_rows':C,'X0_adjacency':G,'exception_tags':tags,'base_adjacency_rows':base,'demand_X0':F,'demand_P':LP,'demand_Q':LQ,**checked})
assert counts['perfect_matchings']==105
assert (counts['incidence_matrices'],counts['partial_graphs'],counts['neighborhood_checks'])==(48,640,240)
result={'status':'EXACT_FINITE_CLASSIFICATION_AND_LOCAL_NEIGHBORHOOD_OBSTRUCTION','scope':'Wagner, global profile A. Together with profile B audit, excludes Wagner in the eight exterior orbit equality case.','counts':counts,'edge_census':{str(k):v for k,v in e_f_census.items()},'four_clique_count':sum(r['four_cliques'] for r in records),'demand_cover_count':sum(r['demand_covers'] for r in records),'local_assembly_count':sum(r['local_assemblies'] for r in records),'records':records,'seconds':time.monotonic()-T0,'limits':{'processes':1,'time_cap_seconds':180,'planned_memory_MiB':128}}
json.dump(result,open(Path(__file__).resolve().parent/'WAGNER_PROFIL_A_CERTIFICATS.json','w',encoding='utf8'),indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='records'}))
