"""Read-only audit of pinned rerun records, coverage and exact cached bases.

Usage: <lab-python> referee_rerun_713.py <lab-root>
No producer enumeration, frame search or cloud access is performed.
"""
import ast
import collections
from fractions import Fraction as F
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile

from check_historical_y1_frontier import inverse, check_certificate, wrapper_shas
from verify_003_fixed_y1 import determinant, matmul

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PINS = {
    'origin/run/q-i-0c0a95abbac3d8463': '970a3f74e923862725576a3ecea4e64750135c55',
    'origin/run/q-i-024b07e5fa9d980a5': 'f6d42bbadbe5780066d7585e0d5b21d0377fbaf6',
    'origin/run/q-i-0058b87765fd902ac': 'a6195cf8b6149f522186bfbfea9ddfda1ac10724',
    'origin/run/q-i-011cdbf73eb1c5524': 'b08203c1a305bb18865a90be53ab59280d93348c',
}


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    lab = Path(sys.argv[1]).resolve()
    pkg = lab/'c2_cloud_run_v10'
    git = ['git', '-c', 'safe.directory='+str(REPO), '-C', str(REPO)]
    manifest_path = REPO/'measures/RERUN_713_MANIFEST_LAB_2026-10-07.json'
    jobs = read(manifest_path)['jobs']
    frontier = read(HERE/'historical_y1_frontier_check.json')
    published = read(REPO/'measures/RERUN_713_CHECK_2026-10-07.json')
    wanted = {'results/%s_%d_%d.jsonl' % (m['lid'], m['k'], m['n']): m for m in jobs}
    assert len(wanted) == len(jobs) == 386
    lids = {m['lid'] for m in jobs}
    assert lids == set(frontier['remaining_N_lattices']) == set(published)
    records = collections.defaultdict(dict)
    for branch, pin in PINS.items():
        archive = subprocess.check_output(git+['archive', pin, 'results'])
        with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
            for member in tf:
                if member.name not in wanted:
                    continue
                blob = tf.extractfile(member).read()
                rs = [json.loads(s) for s in blob.splitlines() if s.strip()]
                rs = [r for r in rs if 'verdicts' in r]
                assert len(rs) == 1, (branch, member.name, 'ambiguous records')
                records[member.name][branch] = rs[0]
    assert set(records) == set(wanted)
    importer = load('rerun_importer', REPO/'q/tools/lab_2026-10-07/import_sweep.py')
    importer.LAB = str(lab)
    st, go = importer.engines()
    par, defer = wrapper_shas(lab, 'q/par_consumer.py'), wrapper_shas(lab, 'q/defer_consumer.py')
    engine = read(pkg/'MANIFEST.json')['engine_code_sha']
    engine_files = {}
    for name, prefix in engine.items():
        engine_files[name] = sha((pkg/'scripts'/name).read_bytes())
        assert engine_files[name][:16] == prefix
    packaged_tracker = pkg/'data/finishC/finishC_tracker.json'
    packaged_lattices = read(packaged_tracker)['lattices']
    classes = collections.defaultdict(set)
    for v in read(lab/'data/finishC/finishC_tracker.json')['lattices']:
        counts = collections.Counter()
        for t, n, e in re.findall(r'([ade])_\{?(\d+)\}?(?:\^\{?(\d+)\}?)?', v['roots']):
            counts[(t.upper(), int(n))] += int(e or 1)
        classes[tuple(sorted(counts.items())) if v['nroots'] else ()].add(v['status'])
    envelope = load('rerun_envelope', pkg/'c1/code/envelope_trap.py')
    packaged_cache = read(pkg/'c1/code/lll_cache.json')
    extra = read(REPO/'measures/rerun_713/lll_lab.json')
    basis_info = {}
    per = {lid: {'jobs': 0, 'pairs': 0, 'reps': set(), 'verdicts': collections.Counter(),
                 'raw_verdicts': collections.Counter()} for lid in lids}
    pair_records = []
    for name, m in wanted.items():
        lid = m['lid']
        def resolve(path):
            return REPO/path[5:] if path.startswith('repo:') else pkg/path
        plan_path, gamma_path = resolve(m['plan']), resolve(m['gamma'])
        plan = read(plan_path)
        if lid not in basis_info:
            old_plan = read(lab/'data/finishC/stream'/lid/'plan.json')
            assert plan['basis_sha'] == old_plan['basis_sha']
            assert plan['y1_reps'] == old_plan['y1_reps']
            assert sha(gamma_path.read_bytes())[:16] == plan['gamma_sha']
            lattice = read(pkg/'external_runs/structures_3eceb4d/U'/(lid+'.json'))
            gens = [[F(str(x)) for x in row] for row in lattice['gens']]
            hnf = envelope.to_int_basis(gens)
            key = sha(json.dumps([[str(F(x)) for x in row] for row in hnf]).encode())
            cache = dict(packaged_cache)
            if m.get('lll'):
                assert resolve(m['lll']) == REPO/'measures/rerun_713/lll_lab.json'
                assert key in extra
                assert key not in cache or cache[key] == extra[key]
                cache.update(extra)
            assert key in cache, (lid, 'would fall back to floating LLL')
            basis = [[F(x) for x in row] for row in cache[key]]
            assert len(basis) == 24 and all(len(row) == 24 for row in basis)
            change = matmul(basis, inverse(gens))
            assert all(x.denominator == 1 for row in change for x in row)
            assert abs(determinant(change)) == 1 and matmul(change, gens) == basis
            assert sha(json.dumps([[str(x) for x in row] for row in basis]).encode())[:16] == plan['basis_sha']
            basis_info[lid] = {'plan_sha256': sha(plan_path.read_bytes()), 'gamma_sha256': sha(gamma_path.read_bytes()),
                               'basis_key': key, 'basis_sha': plan['basis_sha'],
                               'exact_same_lattice': True, 'same_ordered_y1_as_old_plan': True,
                               'old_gamma_order': old_plan['plan']['gamma'], 'new_gamma_order': plan['plan']['gamma']}
        got = records[name]
        assert len(got) == 2, (name, 'not exactly two machines')
        assert len({r['sha256'] for r in got.values()}) == 1
        assert len({r['n_pairs'] for r in got.values()}) == 1
        assert len({json.dumps(r['verdicts'], sort_keys=True) for r in got.values()}) == 1
        for branch, r in got.items():
            assert not importer.check(r, lid, m['k'], m['n'], st, go, par, defer)
            assert importer.open_state(r) == 'done'
            assert r['code_sha'] == engine, (name, branch, 'not v10')
            assert r['producer']['id'] == int(lid) and r['producer']['chunk'] == [m['k'], m['n']]
            assert not r.get('not_excluded')
            assert len(r['sha256']) == 64
            assert any(info == plan['plan'] for info in r['producer_info'])
            for target in (r.get('twin_deferred') or {}):
                assert classes[ast.literal_eval(target)] == {'excluded'}
        r = next(iter(got.values()))
        o = per[lid]
        indices = set(range(m['k'], len(plan['y1_reps']), m['n']))
        assert not indices & o['reps']
        o['reps'].update(indices)
        o['jobs'] += 1
        o['pairs'] += r['n_pairs']
        for v, count in r['verdicts'].items():
            o['verdicts'][importer.cls(v)] += count
            o['raw_verdicts'][v] += count
        pair_records.append({'file': name, 'branches': sorted(got), 'stream_sha256': r['sha256'], 'pairs': r['n_pairs']})
    for lid, o in per.items():
        need = frontier['certificates'][lid]['uncertified_by_tier']['N']
        assert set(need) <= o['reps']
        expected = published[lid]
        assert expected['ok'] and not expected['problems'] and expected['to_rerun'] == need
        assert (o['jobs'], o['pairs'], sorted(o['reps']), dict(o['verdicts'])) == (
            expected['accepted'], expected['pairs'], expected['reps_covered'], expected['verdict_classes'])
        o['reps'] = sorted(o['reps'])
    hand_dir = REPO/'measures/hand_28'
    hand = {}
    for path in sorted(hand_dir.glob('[0-9][0-9][0-9].json')):
        lid = path.stem
        r = read(path)
        plan_path = REPO/'measures/rerun_28'/('plan_'+lid+'.json')
        cert_path = hand_dir/'cert_y1'/('cert_y1_'+lid+'.json')
        plan, cert = read(plan_path), read(cert_path)
        lattice = read(pkg/'external_runs/structures_3eceb4d/U'/(lid+'.json'))
        covered = check_certificate(cert, plan, lattice, plan_path.read_bytes())
        assert r['y1_with_root_of_product_2'] == len(covered)
        assert len(plan['y1_reps']) == r['y1'] == r['y1_with_root_of_product_2']+r['y1_left']
        assert sorted(set(range(r['y1']))-covered) == cert['not_covered']
        assert sum(r['by_min_E'].values()) == r['pairs']
        assert r['by_min_E'].get('>=11', 0) == r['survivors']
        assert not r['pairs'] or r['stream_complete'] is True
        if r['y1_left']:
            assert r['y1_left_indices'] == cert['not_covered']
            assert len(read(hand_dir/(lid+'_survivors.json'))) == r['survivors']
        hand[lid] = {k: r[k] for k in ('y1', 'y1_with_root_of_product_2', 'y1_left', 'pairs', 'survivors')}
        hand[lid]['stored_witness_samples'] = len(r.get('first_witnesses', []))
    out = {'scope': 'Pinned metadata and exact basis/Y1 checks, no search replay.',
           'pins': PINS, 'manifest_sha256': sha(manifest_path.read_bytes()),
           'engine_files_sha256': engine_files, 'basis_checks': basis_info,
           'lattices': len(per), 'jobs': len(jobs), 'records_checked': sum(len(v) for v in records.values()),
           'pairs': sum(o['pairs'] for o in per.values()), 'per_lattice': per, 'job_streams': pair_records,
           'hand_28': hand, 'hand_28_Y1_certificates_checked': sum(r['y1_with_root_of_product_2'] for r in hand.values()),
           'hand_28_pair_witnesses_independently_checked': False,
           'producer_completeness_proved': False, 'whole_proof_verified': False}
    out['twin_status_dependency'] = {
        'package_tracker_sha256': sha(packaged_tracker.read_bytes()),
        'package_tracker_excluded_lattices': sum(v['status'] == 'excluded' for v in packaged_lattices),
        'status_transfer_pairs_counted_once': sum(o['raw_verdicts']['EXCLUDED (twin transfer)'] for o in per.values()),
        'status_targets_retained_per_pair': False,
        'target_exclusions_independently_verified': False,
        'dependency_acyclicity_verified': False,
        'note': 'The consumer reads the packaged tracker. Current lab tracker statuses checked above for named deferred types do not prove the packaged status shortcuts. No claim that all old proof dependencies are superseded.'}
    target = HERE/'referee_rerun_713.json'
    target.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({k: out[k] for k in ('lattices', 'jobs', 'records_checked', 'pairs', 'hand_28_Y1_certificates_checked')}))


if __name__ == '__main__':
    main()
