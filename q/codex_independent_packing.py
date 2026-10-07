"""Independent exact packing computation from the 24 rational generators.

No imports from envelope_pack, envelope_trap, their enumerators or caches.
Sympy supplies exact LLL and matrix algebra; sphere enumeration is below.
All pruning bounds are rational, with integer square roots. Numpy is used
only for bounded integer pairings after explicit overflow checks.
"""
import argparse
import collections
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

import numpy as np
from sympy import Matrix, Rational, __version__ as sympy_version
from sympy.matrices.normalforms import hermite_normal_form

IDS = [94,117,128,129,133,134,136,142,144,145,146,147,148,150,151,152,154,155]


def gram(basis):
    return [[sum(a*b for a,b in zip(u,v)) for v in basis] for u in basis]


def exact_reduced_basis(basis):
    denominator = math.lcm(*(x.denominator for row in basis for x in row))
    integral = Matrix([[int(x*denominator) for x in row] for row in basis])
    reduced, transform = integral.lll_transform(delta=Rational(99,100))
    assert transform*integral == reduced and abs(transform.det()) == 1
    return [[F(int(x), denominator) for x in row] for row in reduced.tolist()]


def ldl(g):
    n = len(g)
    lower = [[F(i == j) for j in range(n)] for i in range(n)]
    diagonal = []
    for i in range(n):
        for j in range(i):
            lower[i][j] = (F(g[i][j])-sum(lower[i][k]*diagonal[k]*lower[j][k] for k in range(j)))/diagonal[j]
        diagonal.append(F(g[i][i])-sum(lower[i][k]**2*diagonal[k] for k in range(i)))
        assert diagonal[-1] > 0
    assert all(sum(lower[i][k]*diagonal[k]*lower[j][k] for k in range(n)) == g[i][j]
               for i in range(n) for j in range(n))
    return lower, diagonal


def sphere(g, bound, parity=None, strict=False):
    """All nonzero integer vectors up to sign, optionally in a parity coset.

Q(x)=sum_i d_i (x_i + sum_{j>i} L[j,i]x_j)^2. At each node
|b*x_i+a| <= isqrt(floor((remaining/d_i)*b^2)), where a/b is
the suffix shift. This is an exact interval; no floating endpoint enters.
The highest nonzero coordinate is positive. Parity cosets are sign-stable.
"""
    bound = F(bound)
    lower, diagonal = ldl(g)
    n = len(g)
    x = [0]*n
    found = []
    nodes = 0
    columns = [[(j, lower[j][i]) for j in range(i+1,n) if lower[j][i]] for i in range(n)]
    def visit(i, remaining, nonzero):
        nonlocal nodes
        nodes += 1
        if i < 0:
            q = bound-remaining
            if nonzero and (not strict or q < bound):
                found.append((tuple(x),q))
            return
        shift = sum((a*x[j] for j,a in columns[i]), F(0))
        a,b = shift.numerator,shift.denominator
        square = remaining/diagonal[i]
        radius = math.isqrt((square.numerator*b*b)//square.denominator)
        lo = -((radius+a)//b)
        hi = (radius-a)//b
        if not nonzero:
            lo = max(lo,0)
        step = 1
        if parity is not None:
            step = 2
            lo += (parity[i]-lo)%2
        for v in range(lo,hi+1,step):
            x[i] = v
            cost = diagonal[i]*(F(v)+shift)**2
            assert cost <= remaining
            visit(i-1,remaining-cost,nonzero or v != 0)
        x[i] = 0
    visit(n-1,bound,False)
    return found, {'nodes':nodes,'complete':True,'up_to_sign':True,'bound':str(bound),'strict':strict}


def strings(matrix):
    return [[str(x) for x in row] for row in matrix]


def trap_components(coordinates, basis, g):
    """Graph components, their integral span lattices and complete short duals."""
    maximum = max(abs(x) for row in coordinates for x in row)
    bound = maximum**2*sum(abs(x) for row in g for x in row)
    assert bound < 2**63
    a = np.array(coordinates,dtype=np.int64)
    products = a @ np.array(g,dtype=np.int64) @ a.T
    adjacent = np.abs(products) == 1
    unseen = set(range(len(a)))
    components = []
    while unseen:
        first = min(unseen)
        unseen.remove(first)
        stack = [first]
        component = []
        while stack:
            i = stack.pop()
            component.append(i)
            fresh = set(map(int,np.flatnonzero(adjacent[i]))) & unseen
            unseen.difference_update(fresh)
            stack.extend(sorted(fresh))
        components.append(sorted(component))
    del products,adjacent
    output = []
    for indices in components:
        if len(indices) < 42:
            output.append({'classes':len(indices),'excluded_by_size':True})
            continue
        generators = Matrix([coordinates[i] for i in indices])
        module_basis = hermite_normal_form(generators.T).T
        rank = module_basis.rows
        real_basis = module_basis*Matrix([[Rational(x.numerator,x.denominator) for x in row] for row in basis])
        q = real_basis*real_basis.T
        qinv = q.inv()
        # Exact membership of every component vector in the returned Z-module.
        coeff = generators*Matrix(g)*module_basis.T*qinv
        assert all(x.q == 1 for x in coeff) and coeff*module_basis == generators
        dual = qinv*real_basis
        reduced_dual = exact_reduced_basis([[F(x) for x in row] for row in dual.tolist()])
        gd = gram(reduced_dual)
        short, enumeration = sphere(gd,F(8,7),strict=True)
        assert all(0 < sum(F(v[i])*gd[i][j]*v[j] for i in range(rank) for j in range(rank)) == norm < F(8,7)
                   for v,norm in short)
        short_coords = [list(v) for v,norm in short]
        dual_rank = Matrix(short_coords).rank() if short_coords else 0
        output.append({
            'classes':len(indices),'admissible_indices':indices,'span_rank':rank,
            'orthogonal_dimension':24-rank,'module_basis_coordinates':module_basis.tolist(),
            'module_gram':[[str(x) for x in row] for row in q.tolist()],
            'dual_reduced_basis_ambient':strings(reduced_dual),
            'short_dual_sign_classes':len(short),'short_dual_span_dimension':dual_rank,
            'short_dual_coordinates':short_coords,'short_dual_norm_histogram':dict(collections.Counter(str(norm) for _,norm in short)),
            'enumeration':enumeration,'test_2_excludes':dual_rank+24-rank > 2,
        })
    return {'graph_pairing_int64_bound':bound,'components':output,
            'all_components_excluded':all(r.get('excluded_by_size') or r['test_2_excludes'] for r in output)}


def compute(lattice_path):
    start = time.monotonic()
    rec = json.loads(lattice_path.read_text())
    basis = exact_reduced_basis([[F(x) for x in row] for row in rec['gens']])
    gq = gram(basis)
    assert all(x.denominator == 1 for row in gq for x in row)
    g = [[int(x) for x in row] for row in gq]
    assert Matrix(g).det() == 1
    diag = [g[i][i] for i in range(24)]
    assert any(x%2 for x in diag)
    chi = [int(x)%2 for x in Matrix(g).inv()*Matrix(diag)]
    assert all(sum(g[i][j]*chi[j] for j in range(24))%2 == diag[i]%2 for i in range(24))
    assert sum(chi[i]*g[i][j]*chi[j] for i in range(24) for j in range(24))%8 == 0
    vectors, enum = sphere(g,3)
    short = collections.defaultdict(list)
    for v,q in vectors:
        assert q.denominator == 1
        assert sum(v[i]*g[i][j]*v[j] for i in range(24) for j in range(24)) == q
        short[int(q)].append(v)
    assert not short[1]
    roots = short[2]
    x3 = short[3]
    shadow, enum_shadow = sphere(g,8,parity=chi)
    new = [[],[]]
    for w,q in shadow:
        assert q == 8, ('unexpected shorter shadow vector',q)
        z = [(w[i]-chi[i])//2 for i in range(24)]
        coset = sum(z[i]*diag[i] for i in range(24))%2
        new[coset].append(w)
    mx = max(abs(a) for v in x3 for a in v)
    mw = max(abs(a) for coset in new for v in coset for a in v)
    pairing_bound = mx*mw*sum(abs(a) for row in g for a in row)
    assert pairing_bound < 2**63
    xx = np.array(x3,dtype=np.int64)
    gg = np.array(g,dtype=np.int64)
    hits = []
    for coset in new:
        ww = np.array(coset,dtype=np.int64).reshape(-1,24)
        products = ww @ gg @ xx.T
        assert np.all(products%2 != 0)
        hits.append((2*np.count_nonzero(np.abs(products)==3,axis=0)).tolist())
    assert hits[0] == hits[1], 'different packing counts in the two shadow cosets'
    counts = [2*len(v) for v in new]
    assert sum(counts) == 2*len(roots)+48
    sorted_hits = sorted(hits[0])
    least42 = sum(sorted_hits[:42])
    assert len(sorted_hits) >= 42
    cap = min(counts)
    result = {
        'id':rec['id'],'roots':rec['roots'],'input_sha256':hashlib.sha256(lattice_path.read_bytes()).hexdigest(),
        'basis':strings(basis),'gram':g,'characteristic_coefficients_mod2':chi,
        'norm2_vectors':2*len(roots),'norm3_sign_classes':len(x3),
        'new_shadow_roots_by_coset':counts,
        'm_histograms_sign_classes':[dict(sorted(collections.Counter(h).items())) for h in hits],
        'm_equal_for_every_class':True,'sum_42_smallest':[least42,least42],
        'new_root_capacity':cap,'test_1_excludes':least42>cap,
        'sphere_norm_le_3':enum,'sphere_shadow':enum_shadow,
        'pairing_int64_bound':pairing_bound,
    }
    if least42 <= cap:
        smallest41 = sum(sorted_hits[:41])
        admissible = [i for i,m in enumerate(hits[0])
                      if m+(smallest41-m+sorted_hits[41] if m <= sorted_hits[40] else smallest41) <= cap]
        result['admissible_indices'] = admissible
        result['admissible_coordinates'] = [list(x3[i]) for i in admissible]
        result['dual_trap'] = trap_components(result['admissible_coordinates'],basis,g)
        result['dual_trap_complete'] = True
    result['seconds'] = round(time.monotonic()-start,3)
    return result


def enumeration_controls():
    cases = [([[1]],F(3),None,False), ([[2,1],[1,2]],F(3),None,False),
             ([[1,0],[0,1]],F(2),[1,1],False),
             ([[1,0,0],[0,1,0],[0,0,1]],F(8,7),None,True),
             ([[1,0],[0,1]],F(1),None,True),
             ([[F(1,2),F(1,4)],[F(1,4),F(1,2)]],F(8,7),None,True),
             ([[F(8,7)]],F(8,7),None,True)]
    for g,bound,parity,strict in cases:
        expected = set()
        for x in itertools.product(range(-4,5),repeat=len(g)):
            if not any(x) or next(v for v in reversed(x) if v) < 0:
                continue
            if parity is not None and any((a-b)%2 for a,b in zip(x,parity)):
                continue
            q = sum(x[i]*g[i][j]*x[j] for i in range(len(g)) for j in range(len(g)))
            if q < bound or (q == bound and not strict):
                expected.add((x,F(q)))
        actual,_ = sphere(g,bound,parity,strict)
        assert set(actual) == expected
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lattices',type=Path)
    parser.add_argument('--ids',default=','.join(map(str,IDS)))
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'measures/codex_independent_packing')
    args = parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    controls = enumeration_controls()
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    expected_packing = {94:(84,80),128:(84,64),129:(84,64),133:(168,128),142:(168,128),136:(84,48),
                        144:(168,104),147:(84,32),148:(168,64),150:(168,64),151:(336,128),152:(672,256),154:(252,48),155:(672,128)}
    expected_dual = {117:8,134:9,145:8,146:24}
    summary = {'implementation_sha256':code_hash,'sympy_version':sympy_version,'numpy_version':np.__version__,
               'brute_force_enumeration_controls':controls,'records':{},'differences_from_announced_numbers':[]}
    for lid in map(int,args.ids.split(',')):
        result = compute(args.lattices/(f'{lid:03d}.json'))
        result['implementation_sha256'] = code_hash
        (args.output/(f'{lid:03d}.json')).write_text(json.dumps(result,indent=2,default=int)+'\n')
        print(json.dumps({k:result.get(k) for k in ('id','norm2_vectors','norm3_sign_classes','new_shadow_roots_by_coset','sum_42_smallest','test_1_excludes','seconds')}),flush=True)
        row = {k:result[k] for k in ('roots','norm2_vectors','norm3_sign_classes','new_shadow_roots_by_coset','m_histograms_sign_classes',
                                     'sum_42_smallest','new_root_capacity','test_1_excludes','seconds')}
        if lid in expected_packing:
            observed = (result['sum_42_smallest'][0],result['new_root_capacity'])
            if observed != expected_packing[lid]:
                summary['differences_from_announced_numbers'].append({'id':lid,'observed':observed,'expected':expected_packing[lid]})
        if 'dual_trap' in result:
            row['admissible_sign_classes'] = len(result['admissible_indices'])
            row['components'] = [{k:c[k] for k in ('classes','span_rank','orthogonal_dimension','short_dual_sign_classes','short_dual_span_dimension','short_dual_norm_histogram','test_2_excludes')}
                                 for c in result['dual_trap']['components'] if not c.get('excluded_by_size')]
            dims = [c['short_dual_span_dimension'] for c in row['components']]
            if lid in expected_dual and dims != [expected_dual[lid]]:
                summary['differences_from_announced_numbers'].append({'id':lid,'observed_dual_dimensions':dims,'expected':expected_dual[lid]})
        row['excluded'] = result['test_1_excludes'] or result.get('dual_trap',{}).get('all_components_excluded',False)
        summary['records'][f'{lid:03d}'] = row
    summary['all_computed_lattices_excluded'] = all(r['excluded'] for r in summary['records'].values())
    (args.output/'SUMMARY.json').write_text(json.dumps(summary,indent=2,default=int)+'\n')


if __name__ == '__main__':
    main()
