"""Exact root-type and twin-row helpers; no historical-stream acceptance claim.

root_type assumes a COMPLETE root system modulo signs (possibly conditional
on existence of a frame). The integer consistency checks are not a substitute
for that hypothesis. All products use int64 only after Python-integer bounds.
"""
import collections
import hashlib
import json
from pathlib import Path

import numpy as np


def integral_array(rows):
    a = np.asarray(rows)
    assert a.dtype.kind in 'iu', 'integer coordinates required'
    assert all(abs(int(x)) < 2**63 for x in a.flat)
    return a.astype(np.int64)


def bounded_product(a, b):
    assert a.ndim == b.ndim == 2 and a.shape[1] == b.shape[0]
    ma = max((abs(int(x)) for x in a.flat), default=0)
    mb = max((abs(int(x)) for x in b.flat), default=0)
    assert ma * mb * a.shape[1] < 2**63, 'int64 product overflow bound'
    return a @ b


def twin_rows(shell, g, y1, y2, energies):
    """Return integer rows 7*r for the selected original shell.

    Original shell membership/completeness and the root-transfer theorem
    remain caller obligations. Pair validity is checked here exactly.
    """
    x, g = integral_array(shell), integral_array(g)
    y = integral_array([y1, y2])
    assert np.array_equal(bounded_product(bounded_product(y, g), y.T), 7*np.eye(2, dtype=np.int64))
    ab = bounded_product(bounded_product(x, g), y.T)
    rows = []
    for row, (a0,b0) in zip(x.tolist(), ab.tolist()):
        a,b = int(a0),int(b0)
        if a*a+b*b not in energies:
            continue
        c,d = (2*a+2*b+3)%7-3, (-2*a+2*b+3)%7-3
        rows.append([7*int(v)+(c-a)*int(p)+(d-b)*int(q) for v,p,q in zip(row,y1,y2)])
    return integral_array(rows) if rows else np.empty((0, g.shape[0]),dtype=np.int64)


def exact_pairings(rows, g, normals, denominator=7):
    q,g,y = integral_array(rows),integral_array(g),integral_array(normals)
    p = bounded_product(bounded_product(q,g),y.T)
    assert np.all(p % denominator == 0), 'nonintegral normal pairing'
    return p//denominator


def root_type(rows, g, denominator=7):
    """Input rows are denominator times one representative of each root line."""
    if len(rows) == 0:
        return {}, []
    q,g = integral_array(rows),integral_array(g)
    assert isinstance(denominator,int) and denominator > 0
    p = bounded_product(bounded_product(q,g),q.T)
    dd = denominator**2
    assert np.all(p % dd == 0), 'nonintegral root Gram matrix'
    p = p//dd
    assert np.all(np.diag(p) == 2), 'not norm-two roots'
    off = p.copy(); np.fill_diagonal(off,0)
    assert np.all(np.abs(off) <= 1), 'duplicate signs or invalid root inner product'
    remaining = set(range(len(q))); types = collections.Counter(); parts = []
    while remaining:
        seed = min(remaining); remaining.remove(seed); stack=[seed]; ids=[]
        while stack:
            a = stack.pop(); ids.append(a)
            fresh = remaining.intersection(map(int,np.flatnonzero(p[a])))
            remaining.difference_update(fresh); stack.extend(sorted(fresh))
        m = len(ids)
        neighbours = [int(np.count_nonzero(np.abs(p[a,ids]) == 1)) for a in ids]
        assert len(set(neighbours)) == 1, 'incomplete/nonuniform root component'
        twice_h = neighbours[0]+4
        assert twice_h % 2 == 0 and 4*m % twice_h == 0
        rank = 4*m//twice_h
        choices=[]
        if m == rank*(rank+1)//2: choices.append('a'+str(rank))
        if rank >= 4 and m == rank*(rank-1): choices.append('d'+str(rank))
        if (rank,m) in ((6,36),(7,63),(8,120)): choices.append('e'+str(rank))
        assert len(choices) == 1, (rank,m,choices)
        types[choices[0]] += 1
        parts.append({'type':choices[0], 'rank':rank, 'root_lines':m, 'neighbours':neighbours[0]})
    return dict(sorted(types.items())),parts


def main():
    repo=Path(__file__).resolve().parents[1]
    source=repo/'measures/codex_exact_lattice_identity.json'
    data=json.loads(source.read_text()); records=[]
    for r in data['records']:
        rows=[[7*x for x in v] for v in r['root_sign_coordinates']]
        ty,parts=root_type(rows,r['gram'])
        assert ty == r['root_type'], r['id']
        records.append({'id':r['id'],'type':ty,'components':parts})
    controls={}
    bads={
        'duplicate_signs':([[7,0],[-7,0]],[[2,0],[0,2]]),
        'wrong_norm':([[7,0]],[[3,0],[0,2]]),
        'fractional_dtype':([[7.0,0.0]],[[2,0],[0,2]]),
        'nonintegral_gram':([[1,0]],[[2,0],[0,2]]),
        'incomplete_A2':([[7,0],[0,7]],[[2,-1],[-1,2]]),
        'overflow_bound':([[2**62,0]],[[2,0],[0,2]])}
    for name,(q,g) in bads.items():
        try: root_type(q,g)
        except AssertionError: controls[name]=True
        else: raise AssertionError('accepted bad control '+name)
    # Exact construction control: A1 orthogonal to two norm-seven normals.
    g=np.diag([2,7,7]).astype(np.int64)
    q=twin_rows([[1,0,0]],g,[0,1,0],[0,0,1],{0,5})
    assert q.tolist()==[[7,0,0]] and exact_pairings(q,g,[[0,1,0],[0,0,1]]).tolist()==[[0,0]]
    out={'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'all_156_match_independent_rational_rank':True,'negative_controls':controls,
         'construction_control':True,'historical_twin_streams_checked':False,'records':records}
    path=repo/'lemma/t20_CODEX/exact_twin_type_controls.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k != 'records'}))


if __name__ == '__main__': main()
