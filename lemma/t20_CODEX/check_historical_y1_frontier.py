"""Exact Y1 certificate checks and historical-record frontier accounting.

Usage: python check_historical_y1_frontier.py <lab-root>
Standard library only. Replays metadata selection, not pair enumeration/search.
Certificate arithmetic is independent of q/check_cert_y1.py: an exact integral
basis change and integer-scaled ambient coordinates establish every witness.
"""
import collections
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time

from verify_003_fixed_y1 import determinant, matmul

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def inverse(matrix):
    n = len(matrix)
    a = [list(row)+[F(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for k in range(n):
        p = next(i for i in range(k, n) if a[i][k])
        a[k], a[p] = a[p], a[k]
        scale = a[k][k]
        a[k] = [x/scale for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                c = a[i][k]
                a[i] = [x-c*y for x, y in zip(a[i], a[k])]
    return [row[n:] for row in a]


def int_vector(v):
    assert len(v) == 24 and all(type(x) is int for x in v)
    return v


def check_certificate(cert, plan, lattice, plan_bytes):
    assert cert['id'] == plan['id'] == lattice['id']
    assert sha(plan_bytes) == cert['plan_sha256']
    assert sha(json.dumps(cert['basis']).encode())[:16] == plan['basis_sha'] == cert['plan_basis_sha']
    basis = [[F(x) for x in row] for row in cert['basis']]
    gens = [[F(str(x)) for x in row] for row in lattice['gens']]
    assert len(basis) == len(gens) == 24
    assert all(len(row) == 24 for mat in (basis, gens) for row in mat)
    change = matmul(basis, inverse(gens))
    assert all(x.denominator == 1 for row in change for x in row)
    assert abs(determinant(change)) == 1 and matmul(change, gens) == basis
    gram = matmul(basis, list(map(list, zip(*basis))))
    assert all(x.denominator == 1 for row in gram for x in row)
    assert determinant(gram) == 1
    denominator = math.lcm(*(x.denominator for row in basis for x in row))
    scaled = [[int(x*denominator) for x in row] for row in basis]
    def ambient(c):
        c = int_vector(c)
        return [sum(c[k]*scaled[k][j] for k in range(24)) for j in range(24)]
    nr = len(plan['y1_reps'])
    keys = sorted(int(k) for k in cert['reps'])
    assert len(set(keys)) == len(keys) and all(str(i) in cert['reps'] and 0 <= i < nr for i in keys)
    assert keys == cert['covered'] and cert['y1_reps_in_plan'] == nr
    for i in keys:
        w = cert['reps'][str(i)]
        c = int_vector(plan['y1_reps'][i])
        assert w['chunk'] == [i, nr] and c == w['y1_coordinates']
        y, r = ambient(c), ambient(w['r_coordinates'])
        assert len(w['y1']) == len(w['r']) == 24
        assert y == [F(x)*denominator for x in w['y1']]
        assert r == [F(x)*denominator for x in w['r']]
        assert sum(x*x for x in y) == 7*denominator**2
        assert sum(x*x for x in r) == 2*denominator**2
        assert abs(sum(x*z for x, z in zip(y, r))) == 2*denominator**2
    return set(keys)


def wrapper_shas(lab, path):
    prefix = ['git', '-c', 'safe.directory='+str(lab/'aws_repo'), '-C', str(lab/'aws_repo')]
    revs = subprocess.check_output(prefix+['log', '--all', '--format=%H', '--', path], text=True).split()
    hashes = set()
    for rev in revs:
        b = subprocess.check_output(prefix+['show', rev+':'+path])
        hashes.update([sha(b)[:16], sha(b.replace(b'\r\n', b'\n'))[:16]])
    return hashes


def main():
    started = time.monotonic()
    lab = Path(sys.argv[1]).resolve()
    history = REPO/'q/tools/lab_2026-10-07/engine_history'
    history_hashes = {}
    for record in read(history/'MANIFEST.json')['files']:
        b = (history/record['file']).read_bytes()
        lf = b.replace(b'\r\n', b'\n')
        crlf = lf.replace(b'\n', b'\r\n')
        assert sha(lf)[:16] == record['sha256_LF']
        assert sha(crlf)[:16] == record['sha256_CRLF']
        assert record['sha256_as_on_lab_disk'] in {sha(lf)[:16], sha(crlf)[:16]}
        history_hashes[record['file']] = {'LF': sha(lf), 'CRLF': sha(crlf)}
    recovered = dict(read(lab/'c2_cloud_run/MANIFEST.json')['engine_code_sha'])
    package_hashes = {}
    for name, prefix in recovered.items():
        package_hashes[name] = sha((lab/'c2_cloud_run/scripts'/name).read_bytes())
        assert package_hashes[name][:16] == prefix
    assert recovered['frame_dfs.py'] == history_hashes['frame_dfs_v_pre_n24.py']['CRLF'][:16]
    recovered['hstage_stream.py'] = history_hashes['hstage_stream_v_pre_telemetry.py']['CRLF'][:16]
    assert recovered['hstage_stream.py'] == '4e310e729b7df3d0'

    spec = importlib.util.spec_from_file_location('archived_import_sweep', REPO/'q/tools/lab_2026-10-07/import_sweep.py')
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    importer.LAB = str(lab)
    st, go = importer.engines()
    par, defer = wrapper_shas(lab, 'q/par_consumer.py'), wrapper_shas(lab, 'q/defer_consumer.py')
    report_path = REPO/'measures/STREAM_RECOUNT_2026-10-07.json'
    report = read(report_path)
    lids = sorted(lid for lid, v in report.items() if v['by_tier']['L']+v['by_tier']['N'])
    assert len(lids) == 55
    totals = collections.Counter()
    detail = {}
    negative_controls = []
    for lid in lids:
        base = lab/'data/finishC/stream'/lid
        plan_path, chunks_path = base/'plan.json', base/'chunks.jsonl'
        cert_path = REPO/'measures/cert_y1_rerun'/('cert_y1_'+lid+'.json')
        lattice_path = lab/'external_runs/structures_3eceb4d/U'/(lid+'.json')
        plan, cert, lattice = read(plan_path), read(cert_path), read(lattice_path)
        certified = check_certificate(cert, plan, lattice, plan_path.read_bytes())
        if not negative_controls:
            first = str(min(certified))
            for field in ('r_coordinates', 'y1_coordinates'):
                bad_cert = deepcopy(cert)
                bad_cert['reps'][first][field][0] += 1
                try:
                    check_certificate(bad_cert, plan, lattice, plan_path.read_bytes())
                except AssertionError:
                    negative_controls.append(field)
                else:
                    raise AssertionError('Corrupted certificate accepted: '+field)
        resolved_path = base/'incomplete_resolved.jsonl'
        resolved = {(tuple(r['y1']), tuple(r['y2'])): r['verdict'] for r in rows(resolved_path)} if resolved_path.exists() else {}
        candidates = []
        for r in rows(chunks_path):
            if not r.get('chunk_ok') or not r.get('verdicts'):
                continue
            k, n = r['chunk']
            bad = importer.check(r, lid, k, n, st, go, par, defer)
            assert all(x.startswith('engine not of a lab package') for x in bad), (lid, bad)
            tier = 'P' if not bad else 'L' if r.get('code_sha') else 'N'
            if tier == 'L':
                assert r['code_sha'] == recovered
                totals['L_records_before_selection'] += 1
            pending = r.get('not_excluded') or []
            done = r.get('chunk_done') or (pending and all(q.get('verdict') == 'INCOMPLETE' and
                resolved.get((tuple(q['y1']), tuple(q['y2'])), '').startswith('EXCLUDED') for q in pending))
            if done:
                candidates.append((tier, r))
        coverage = {}
        pairs, selected = collections.Counter(), collections.Counter()
        verdicts = collections.Counter()
        for tier, r in sorted(candidates, key=lambda tr: ('PLN'.index(tr[0]), tr[1]['chunk'][1], tr[1]['chunk'][0], str(tr[1].get('t', '')))):
            k, n = r['chunk']
            reps = set(range(k, len(plan['y1_reps']), n))
            if reps <= coverage.keys():
                continue
            assert not reps.intersection(coverage), (lid, 'overlap')
            coverage.update((i, tier) for i in reps)
            pairs[tier] += r['n_pairs']
            selected[tier] += 1
            if tier == 'L':
                assert r['code_sha'] == recovered, (lid, 'different L engine')
            for v, count in r['verdicts'].items():
                verdicts[importer.cls(v)] += count
        rr = report[lid]
        assert len(coverage) == rr['y1_reps'] == rr['covered']
        assert {t: pairs[t] for t in 'PLN'} == rr['pairs_by_tier']
        assert {t: sum(x == t for x in coverage.values()) for t in 'PLN'} == rr['by_tier']
        assert dict(selected) == rr['selected_records']
        assert all(verdicts[c] == rr[c] for c in importer.CLASSES)
        uncovered = {t: sorted(i for i, value in coverage.items() if value == t and i not in certified) for t in 'LN'}
        covered = {t: sum(value == t and i in certified for i, value in coverage.items()) for t in 'LN'}
        totals['certified_all_tiers'] += len(certified)
        for t in 'LN':
            totals[t+'_certified'] += covered[t]
            totals[t+'_uncertified'] += len(uncovered[t])
            totals[t+'_pairs'] += pairs[t]
            totals[t+'_records'] += selected[t]
        detail[lid] = {'certified_all_tiers': len(certified), 'certified_by_tier': covered,
                       'uncertified_by_tier': uncovered,
                       'sha256': {name: sha(p.read_bytes()) for name, p in
                                  [('plan', plan_path), ('lattice', lattice_path), ('certificate', cert_path), ('chunks', chunks_path)]}}
        print(lid, 'exact certificates', len(certified), 'remaining N', len(uncovered['N']), flush=True)
    out = {'totals': dict(totals), 'lattices_checked': len(lids),
           'remaining_N_lattices': [lid for lid in lids if detail[lid]['uncertified_by_tier']['N']],
           'history_hashes': history_hashes, 'recovered_L_engine_record': recovered,
           'package_v1_engine_files_sha256': package_hashes,
           'negative_controls_rejected': negative_controls,
           'recount_sha256': sha(report_path.read_bytes()),
           'certificates': detail, 'dependencies': ['R', 'T18', 'T20'],
           'historical_N_versions_attested': False, 'pair_enumeration_or_search_replayed': False,
           'other_32_early_lattices_audited': False, 'whole_proof_verified': False,
           'seconds': round(time.monotonic()-started, 2)}
    target = HERE/'historical_y1_frontier_check.json'
    target.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'totals': out['totals'], 'remaining_N_lattices': len(out['remaining_N_lattices']), 'seconds': out['seconds']}))


if __name__ == '__main__':
    main()
