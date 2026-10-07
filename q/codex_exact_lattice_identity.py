"""Exact input-lattice identification, using the independent rational enumerator.

Checks all 156 inputs without assuming minimum >= 2 or a theta-series count.
The classification theorem itself is cited, not reproved here.
"""
import argparse
import collections
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np
from sympy import Matrix

from codex_independent_packing import exact_reduced_basis, gram, sphere, strings


def label_counts(label):
    if label in ('', '(none)', None):
        return {}
    counts = collections.Counter()
    pattern = r'([ade])_\{?(\d+)\}?(?:\^\{?(\d+)\}?)?'
    for t, n, e in re.findall(pattern, label.lower()):
        counts[t+n] += int(e or 1)
    assert re.sub(pattern, '', label.lower()).strip() == '', label
    return dict(sorted(counts.items()))


def exact_rank(rows):
    echelon = []
    for row in rows:
        v = list(map(F, row))
        for pivot, basis in echelon:
            a = v[pivot]
            if a:
                v = [x-a*y for x,y in zip(v,basis)]
        pivot = next((j for j,x in enumerate(v) if x), None)
        if pivot is not None:
            a = v[pivot]
            echelon.append((pivot,[x/a for x in v]))
    return len(echelon)


def root_type(rows, g):
    if not rows:
        return {}, [], 0
    maximum = max(abs(x) for row in rows for x in row)
    bound = maximum**2*sum(abs(x) for row in g for x in row)
    assert bound < 2**63
    a = np.array(rows,dtype=np.int64)
    products = a @ np.array(g,dtype=np.int64) @ a.T
    remaining = set(range(len(rows)))
    parts = []
    counts = collections.Counter()
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        stack, indices = [seed], []
        while stack:
            i = stack.pop()
            indices.append(i)
            fresh = set(map(int,np.flatnonzero(products[i]))) & remaining
            remaining.difference_update(fresh)
            stack.extend(fresh)
        rank = exact_rank([rows[i] for i in indices])
        number = 2*len(indices)
        choices = []
        if number == rank*(rank+1):
            choices.append('a'+str(rank))
        if rank >= 4 and number == 2*rank*(rank-1):
            choices.append('d'+str(rank))
        if (rank,number) in ((6,72),(7,126),(8,240)):
            choices.append('e'+str(rank))
        assert len(choices) == 1, (rank,number,choices)
        counts[choices[0]] += 1
        parts.append({'rank':rank,'signed_roots':number,'type':choices[0]})
    return dict(sorted(counts.items())), parts, bound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lattices',type=Path)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'measures/codex_exact_lattice_identity.json')
    args = parser.parse_args()
    start = time.monotonic()
    records = []
    expected_duplicates = [(16,17),(23,27),(56,58),(77,79),(82,85),(120,121),(145,146)]
    duplicates_ids = {i for pair in expected_duplicates for i in pair}
    for lid in range(156):
        path = args.lattices/(f'{lid:03d}.json')
        rec = json.loads(path.read_text())
        assert rec['id'] == lid
        basis = exact_reduced_basis([[F(x) for x in row] for row in rec['gens']])
        gq = gram(basis)
        assert all(x.denominator == 1 for row in gq for x in row)
        g = [[int(x) for x in row] for row in gq]
        assert len(g) == 24 and Matrix(g).det() == 1
        diag = [g[i][i] for i in range(24)]
        assert any(x%2 for x in diag)
        short, enumeration = sphere(g,2)
        assert all(q == 2 for v,q in short), 'norm-one vector found'
        roots = [v for v,q in short]
        assert len(set(roots)) == len(roots)
        assert all(sum(v[i]*g[i][j]*v[j] for i in range(24) for j in range(24)) == 2 for v in roots)
        types, components, bound = root_type(roots,g)
        assert types == label_counts(rec['roots'])
        assert 2*len(roots) == rec['nroots']
        row = {'id':lid,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
               'basis':strings(basis),'gram':g,'determinant':1,'odd':True,'norm1_count':0,
               'root_type':types,'root_components':components,'root_sign_coordinates':roots,
               'sphere_norm_le_2':enumeration,'root_pairing_int64_bound':bound}
        if lid in duplicates_ids:
            chi = [int(x)%2 for x in Matrix(g).inv()*Matrix(diag)]
            assert any(chi)
            assert all(sum(g[i][j]*chi[j] for j in range(24))%2 == diag[i]%2 for i in range(24))
            shadow, shadow_enum = sphere(g,8,parity=chi)
            new = [[],[]]
            for w,q in shadow:
                assert q == 8
                assert all((w[i]-chi[i])%2 == 0 for i in range(24))
                coset = sum(((w[i]-chi[i])//2)*diag[i] for i in range(24))%2
                new[coset].append(w)
            neighbours = []
            for coset in new:
                doubled = [tuple(2*x for x in v) for v in roots]+coset
                assert len(set(doubled)) == len(doubled)
                assert all(sum(v[i]*g[i][j]*v[j] for i in range(24) for j in range(24)) == 8 for v in doubled)
                nt, nc, nb = root_type(doubled,g)
                neighbours.append({'root_type':nt,'components':nc,'pairing_int64_bound':nb})
            expected = sorted(json.dumps(label_counts(rec[k]),sort_keys=True) for k in ('nb1','nb2'))
            actual = sorted(json.dumps(n['root_type'],sort_keys=True) for n in neighbours)
            assert actual == expected, (lid,actual,expected)
            row.update({'characteristic_mod2':chi,'shadow_enumeration':shadow_enum,
                        'new_shadow_root_sign_coordinates':new,'neighbours':neighbours})
        records.append(row)
        if lid%20 == 0 or lid == 155:
            print(f'{lid:03d}: exact determinant, minimum, root type OK; {time.monotonic()-start:.1f}s',flush=True)
    groups = collections.defaultdict(list)
    for row in records:
        groups[json.dumps(row['root_type'],sort_keys=True)].append(row['id'])
    actual_duplicates = sorted(tuple(ids) for ids in groups.values() if len(ids)>1)
    assert actual_duplicates == expected_duplicates
    separations = []
    for a,b in expected_duplicates:
        signatures = [sorted(json.dumps(n['root_type'],sort_keys=True) for n in records[i]['neighbours']) for i in (a,b)]
        assert signatures[0] != signatures[1]
        separations.append({'ids':[a,b],'neighbour_signatures':signatures,'separated':True})
    packing_source = Path(__file__).with_name('codex_independent_packing.py')
    out = {'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'enumerator_sha256':hashlib.sha256(packing_source.read_bytes()).hexdigest(),
           'all_156_exact_input_checks_passed':True,'pairwise_nonisometric':True,
           'duplicate_root_type_pairs':separations,'records':records,
           'seconds':round(time.monotonic()-start,3)}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('records','duplicate_root_type_pairs')}),flush=True)


if __name__ == '__main__':
    main()
