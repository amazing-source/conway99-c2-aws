"""Audit the archived recount's arithmetic and its 161 resolution links.

Usage: python check_stream_provenance_report.py <lab-root>
No enumeration, producer replay, tracker change or proof verification.
"""
import collections
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CLASSES = ('excl_at_once', 'excl_search', 'twin', 'swap',
           'defer_T18', 'defer_T20', 'incomplete', 'other')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines()
            if s.strip()]


def pair(row):
    return tuple(row['y1']), tuple(row['y2'])


def main():
    lab = Path(sys.argv[1]).resolve()
    source = REPO / 'measures/STREAM_RECOUNT_2026-10-07.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    assert len(data) == 91 and '003' not in data
    totals = collections.Counter()
    tier_pairs = collections.Counter()
    tier_reps = collections.Counter()
    resolutions = {}
    final_verdicts = collections.Counter()
    for lid, row in data.items():
        assert row['ok'] is True
        assert row['covered'] == row['y1_reps'] == sum(row['by_tier'].values())
        assert row['covered_twice'] == row['twin_classes_pending'] == 0
        assert not row['other_faults']
        assert row['defer_T18'] == row['defer_T20'] == row['other'] == 0
        assert row['pairs'] == sum(row['pairs_by_tier'].values())
        assert row['pairs'] == sum(row[c] for c in CLASSES)
        assert row['incomplete'] == row['incomplete_resolved_pairs']
        for c in (*CLASSES, 'pairs', 'incomplete_resolved_pairs'):
            totals[c] += row[c]
        tier_pairs.update(row['pairs_by_tier'])
        tier_reps.update(row['by_tier'])
        if not row['incomplete']:
            continue
        base = lab / 'data/finishC/stream' / lid
        resolved_path = base / 'incomplete_resolved.jsonl'
        chunks_path = base / 'chunks.jsonl'
        resolved_rows = rows(resolved_path)
        resolved = {}
        for r in resolved_rows:
            key = pair(r)
            assert key not in resolved or resolved[key] == r['verdict']
            resolved[key] = r['verdict']
        old = set()
        for r in rows(chunks_path):
            if r.get('chunk_ok') and r.get('verdicts'):
                old.update(pair(q) for q in r.get('not_excluded', [])
                           if q.get('verdict') == 'INCOMPLETE')
        assert old == set(resolved)
        assert len(resolved) == row['incomplete']
        # These actual verdicts are narrower than the recount's generic
        # startswith('EXCLUDED') acceptance. No search is replayed here.
        assert set(resolved.values()) <= {
            'EXCLUDED (stage 1 empty: no 7 h)',
            'EXCLUDED (no local star sums)',
        }
        final_verdicts.update(resolved.values())
        resolutions[lid] = {
            'unique_pairs': len(resolved),
            'resolution_records': len(resolved_rows),
            'duplicate_records_with_same_verdict': len(resolved_rows)-len(resolved),
            'exact_pair_sets_equal': True,
            'chunks_sha256': sha(chunks_path),
            'resolutions_sha256': sha(resolved_path),
        }
    some = {t: sorted(lid for lid, r in data.items() if r['by_tier'][t])
            for t in 'LN'}
    gaps = sorted(set(some['L']) | set(some['N']))
    out = {
        'scope': 'Arithmetic of archived 91-lattice recount; exact links for its 161 originally incomplete pairs.',
        'source': str(source.relative_to(REPO)),
        'source_sha256': sha(source),
        'lattices': len(data),
        'all_P_lattices': sorted(set(data)-set(gaps)),
        'some_L_lattices': some['L'], 'some_N_lattices': some['N'],
        'L_or_N_lattices': gaps,
        'pairs_by_tier': dict(tier_pairs), 'reps_by_tier': dict(tier_reps),
        'totals': dict(totals),
        'resolved_final_verdicts': dict(final_verdicts),
        'resolution_checks': resolutions,
        'case_003_in_this_recount': False,
        'original_recount_selection_replayed': False,
        'enumerations_or_exclusion_searches_replayed': False,
        'historical_engine_provenance_restored': False,
        'whole_proof_verified': False,
    }
    target = HERE / 'stream_provenance_report_check.json'
    target.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'report': str(target), 'lattices': len(data),
                      'pairs': totals['pairs'], 'L_or_N_lattices': len(gaps),
                      'L_or_N_pairs': tier_pairs['L']+tier_pairs['N'],
                      'exact_resolution_links': sum(r['unique_pairs'] for r in resolutions.values())}))


if __name__ == '__main__':
    main()
