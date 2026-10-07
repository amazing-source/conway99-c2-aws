"""Verify every hand_28 witness and bind its pair arrays to the stream hash.

Run with the lab Python (numpy is needed to read NPZ files). No enumeration,
search or cloud access. The witness checker uses Python integer arithmetic;
only stream reconstruction uses int64, after explicit overflow bounds.
"""
import collections
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np

from check_historical_y1_frontier import check_certificate

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASELINE = '13514d769'
CHECKER = 'q/tools/lab_2026-10-07/check_hand_witness.py'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def checker_args(lab, lid, summary, pairs, script=None):
    return [sys.executable, str(script or REPO/CHECKER),
            str(lab/'c2_cloud_run_v10/external_runs/structures_3eceb4d/U'/(lid+'.json')),
            str(REPO/'measures/rerun_28'/('plan_'+lid+'.json')),
            str(REPO/'measures/hand_28/cert_y1'/('cert_y1_'+lid+'.json')),
            str(summary), str(pairs)]


def reconstruct_stream(summary, pairs):
    with np.load(pairs, allow_pickle=False) as z:
        assert all(z[k].dtype.kind in 'iu' for k in z.files)
        basis = [[F(x) for x in row] for row in summary['basis']]
        den = math.lcm(*(x.denominator for row in basis for x in row))
        bd = [[int(x*den) for x in row] for row in basis]
        assert len(bd) == 24 and all(len(row) == 24 for row in bd)
        max_basis = max(abs(x) for row in bd for x in row)
        max_coord = max(int(np.abs(z[k].astype(object)).max(initial=0)) for k in ('y1', 'y2'))
        # Bounds on every multiplication, partial sum and final entry.
        bound = max_coord*max(sum(abs(row[j]) for row in bd) for j in range(24))
        assert max_basis < 2**63 and max_coord < 2**63 and bound < 2**63
        matrix = np.array(bd, dtype=np.int64)
        a1 = z['y1'].astype(np.int64) @ matrix
        a2 = z['y2'].astype(np.int64) @ matrix
        strings = {int(n): str(F(int(n), den)) for n in np.unique(np.concatenate((a1.ravel(), a2.ravel())))}
        first = {int(o): [strings[int(n)] for n in row] for o, row in zip(z['y1_o'], a1)}
        h = hashlib.sha256()
        for o, row in zip(z['o'], a2):
            record = {'o': int(o), 'y1': first[int(o)], 'y2': [strings[int(n)] for n in row]}
            h.update((json.dumps(record)+'\n').encode())
        assert h.hexdigest() == summary['stream_sha256'], 'pair arrays do not reconstruct the reported producer stream'
        return {'stream_sha256': h.hexdigest(), 'int64_ambient_bound': bound,
                'basis_denominator': den, 'pairs_reconstructed': len(z['o'])}


def negative_controls(lab):
    lid = '141'
    base = REPO/'measures/hand_28'
    with np.load(base/(lid+'_pairs.npz'), allow_pickle=False) as z:
        original = {k: z[k].copy() for k in z.files}
    summary = read(base/(lid+'.json'))
    git = ['git', '-c', 'safe.directory='+str(REPO), '-C', str(REPO)]
    old = subprocess.check_output(git+['show', BASELINE+':'+CHECKER])
    results = {}
    with tempfile.TemporaryDirectory(prefix='witness-negative-', dir=HERE) as td:
        temp = Path(td).resolve()
        assert temp.parent == HERE.resolve()  # Bound the eventual recursive cleanup.
        old_script = temp/'old_checker.py'
        old_script.write_bytes(old)
        for label in ('nonintegral_witness', 'wrong_integer_witness', 'bad_shape', 'bad_index'):
            arrays = {k: v.copy() for k, v in original.items()}
            if label == 'nonintegral_witness':
                # Reflection w -> w - (e_2-e_5)/2, for pair row 1:
                # preserves norm 3 and E=8 but leaves the lattice.
                arrays['w'] = arrays['w'].astype(np.float64)
                arrays['w'][1, 1] -= 0.5
                arrays['w'][1, 4] += 0.5
            elif label == 'wrong_integer_witness':
                arrays['w'][1, 0] += 1
            elif label == 'bad_shape':
                arrays['y2'] = np.pad(arrays['y2'], ((0, 0), (0, 1)))
            else:
                arrays['o'][1] = 999
            pairs = temp/(label+'.npz')
            np.savez_compressed(pairs, **arrays)
            metadata = dict(summary, pairs_file_sha256=sha(pairs.read_bytes()))
            meta_path = temp/(label+'.json')
            meta_path.write_text(json.dumps(metadata), encoding='utf-8')
            if label == 'nonintegral_witness':
                before = subprocess.run(checker_args(lab, lid, meta_path, pairs, old_script), capture_output=True, text=True)
                assert before.returncode == 0 and before.stdout.rstrip().endswith('ok'), before.stderr
                results['baseline_accepted_nonlattice_witness'] = {'commit': BASELINE, 'checker_sha256': sha(old),
                                                                  'output': before.stdout.strip()}
            after = subprocess.run(checker_args(lab, lid, meta_path, pairs), capture_output=True, text=True)
            assert after.returncode != 0, 'corruption accepted: '+label
            if label == 'nonintegral_witness':
                assert 'all certificate arrays must have integer dtype' in after.stderr
            results[label] = 'rejected'
    return results


def main():
    started = time.monotonic()
    lab = Path(sys.argv[1]).resolve()
    base = REPO/'measures/hand_28'
    results = {}
    totals = collections.Counter()
    for summary_path in sorted(base.glob('[0-9][0-9][0-9].json')):
        lid = summary_path.stem
        summary = read(summary_path)
        plan_path = REPO/'measures/rerun_28'/('plan_'+lid+'.json')
        cert_path = base/'cert_y1'/('cert_y1_'+lid+'.json')
        lattice_path = lab/'c2_cloud_run_v10/external_runs/structures_3eceb4d/U'/(lid+'.json')
        plan, cert, lattice = read(plan_path), read(cert_path), read(lattice_path)
        covered = check_certificate(cert, plan, lattice, plan_path.read_bytes())
        assert len(covered) == summary['y1_with_root_of_product_2']
        left = sorted(set(range(len(plan['y1_reps'])))-covered)
        assert left == cert['not_covered']
        totals['y1_certificates'] += len(covered)
        result = {'Y1_checked': len(covered), 'y1_left': len(left),
                  'summary_sha256': sha(summary_path.read_bytes()),
                  'plan_sha256': sha(plan_path.read_bytes()), 'Y1_certificate_sha256': sha(cert_path.read_bytes()),
                  'lattice_sha256': sha(lattice_path.read_bytes())}
        if left:
            pairs = base/(lid+'_pairs.npz')
            result['npz_sha256'] = sha(pairs.read_bytes())
            run = subprocess.run(checker_args(lab, lid, summary_path, pairs), capture_output=True, text=True)
            assert run.returncode == 0 and run.stdout.rstrip().endswith('ok'), (lid, run.stdout, run.stderr)
            result['checker_output'] = run.stdout.strip()
            result.update(reconstruct_stream(summary, pairs))
            totals['pair_files'] += 1
            totals['pairs'] += summary['pairs']
            totals['valid_witnesses'] += summary['pairs']-summary['survivors']
            totals['survivors'] += summary['survivors']
        else:
            assert summary['pairs'] == summary['survivors'] == 0
        results[lid] = result
        print(lid, 'verified', summary['pairs'], 'pairs', flush=True)
    out = {'totals': dict(totals), 'lattices': results,
           'checker_sha256': sha((REPO/CHECKER).read_bytes()),
           'negative_controls': negative_controls(lab),
           'dependencies': ['R', 'T16', 'T18', 'T20', 'completeness of the producer and its plans'],
           'pair_stream_hashes_reconstructed': True, 'producer_completeness_proved': False,
           'survivors_short_shell_minimum_rechecked': False, 'whole_proof_verified': False,
           'seconds': round(time.monotonic()-started, 2)}
    target = HERE/'referee_hand_witness.json'
    target.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'totals': out['totals'], 'seconds': out['seconds'], 'negative_controls': out['negative_controls']}))


if __name__ == '__main__':
    main()
