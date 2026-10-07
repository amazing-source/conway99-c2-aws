"""Small independent checks of the DATA PRINTED in T20_PROOF.md.

No imports of the first or second enumeration engines. This checks nine
displayed support representatives and arithmetic, not the exhaustive searches.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import re

PROOF = Path(__file__).resolve().parents[1] / 'T20_PROOF.md'


def automorphism_count(minus, plus, inner):
    assignment=[]
    def go(unused):
        i=len(assignment)
        if i==10:return 1
        total=0
        for j in sorted(unused):
            if (i in inner)!=(j in inner):continue
            if any((((minus[i]>>a)&1)!=((minus[j]>>b)&1) or
                    ((plus[i]>>a)&1)!=((plus[j]>>b)&1))
                   for a,b in enumerate(assignment)):continue
            assignment.append(j);total+=go(unused-{j});assignment.pop()
        return total
    return go(set(range(10)))


def main():
    raw=PROOF.read_bytes();text=raw.decode('utf-8')
    structures={};unit_tables={}
    for line in text.splitlines():
        if not re.match(r'^\| (I\.[0-5]|IIa\.0|III\.[01]) \|',line):continue
        parts=[p.strip() for p in line.strip('|').split('|')]
        label=parts[0]
        if len(parts)==5 and parts[1].isdigit():
            unit_tables[label]=(int(parts[1]),set(parts[2].split()),set(parts[3].split()))
        elif len(parts)==4 and parts[1].isdigit():
            unit_tables[label]=(int(parts[1]),set(parts[2].split()),set(parts[3].split()))
        elif re.fullmatch(r'\d\d(?: \d\d)+',parts[1]):
            structures[label]=(parts[1],int(parts[2] if label.startswith('I.') else parts[-1]))
    assert len(structures)==len(unit_tables)==9
    checked=[]
    for label,(edges,claimed_aut) in structures.items():
        inner=set() if label.startswith('I.') else ({0,1} if label=='IIa.0' else {0,1,2,3})
        minus=[0]*10;plus=[0]*10;rows=[0]*21
        def edge(a,b):rows[a]|=1<<b;rows[b]|=1<<a
        for word in edges.split():
            a,b=map(int,word)
            minus[a]|=1<<b;minus[b]|=1<<a
            edge(a,10+b);edge(b,10+a)
        for a in inner:edge(a,10+a);edge(a,20);edge(10+a,20)
        if label=='IIa.0':
            plus[2]|=1<<3;plus[3]|=1<<2;edge(2,3);edge(12,13)
        phi=[1]*10+[-1]*10+[0]
        for i in range(21):
            assert sum(phi[j] for j in range(21) if (rows[i]>>j)&1)==-4*phi[i]
            for j in range(i):
                assert (rows[i]&rows[j]).bit_count()<=2-((rows[i]>>j)&1)
        auto=automorphism_count(minus,plus,inner)
        assert auto==claimed_aut
        need={f'{i}{j}':2-((rows[i]>>j)&1)-(rows[i]&rows[j]).bit_count()
              for i,j in combinations(range(10),2)}
        total,double,single=unit_tables[label]
        assert sum(need.values())==total
        assert {pair for pair,value in need.items() if value==2}==double
        assert {pair for pair,value in need.items() if value==1}==single
        assert all(0<=v<=2 for v in need.values())
        checked.append(dict(label=label,automorphisms=auto,total_units=total))
    # Independent orbit-size arithmetic in section 4.9.
    assert 28800*sum((Fraction(1,a) for a in (16,4,10,4,4,20)),Fraction(0))==27720
    assert 17280*(Fraction(1,3)+Fraction(1,4))==10080
    stage1=[];stage2=[]
    for line in text.splitlines():
        if re.match(r'^> \| I\.[0-5] \| \d+ \| \d+ \| \([34],[24],[01]\)',line):
            p=[x.strip() for x in line[2:].strip('|').split('|')]
            stage1.append(tuple(int(x.replace(',','')) for x in p[4:7]))
        if re.match(r'^> \| I\.[0-5] \([34],[24],[01]\) \|',line):
            p=[x.strip() for x in line[2:].strip('|').split('|')]
            nodes=[int(x.strip()) for x in p[1].split(',')]
            total=int(p[2].replace(',',''))
            assert sum(nodes)==total and len(nodes)-1==int(p[3])
            stage2.append((total,int(p[4])))
    assert len(stage1)==len(stage2)==12
    assert tuple(map(sum,zip(*stage1)))==(17396042,3130401,615405)
    assert tuple(map(sum,zip(*stage2)))==(15762181,15)
    result=dict(proof_sha256=hashlib.sha256(raw).hexdigest(),support_checks=checked,
                stage1_totals=[17396042,3130401,615405],stage2_total_nodes=15762181,
                scope='printed representatives, units, automorphisms and table arithmetic; no exhaustive rerun')
    out=Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
