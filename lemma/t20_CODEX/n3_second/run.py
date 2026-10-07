"""One resumable JSON result per base, plus a coverage summary."""
import argparse
import hashlib
import json
import multiprocessing
import os
import time
from pathlib import Path
from search import Search


def atomic_json(path, value):
    tmp = path.with_suffix('.tmp.'+str(os.getpid()))
    tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)


def source_digest():
    h = hashlib.sha256()
    for name in ('model.py','schur.py','search.py','run.py'):
        h.update(name.encode()); h.update(Path(__file__).with_name(name).read_bytes())
    return h.hexdigest()


def job(args):
    record,out,seconds,digest = args
    path = Path(out)/(record['id']+'.json')
    if path.exists():
        prior = json.loads(path.read_text(encoding='utf-8'))
        if prior.get('status')=='complete' and prior.get('source_digest')==digest:
            return prior
    if record['hand_excluded']:
        result = dict(base_id=record['id'],status='complete',
                      hand_excluded=record['hand_excluded'],complete_configurations=0,
                      nodes_per_level=[0]*13,seconds=0)
    else:
        result = Search(record,seconds).run()
    result['source_digest'] = digest
    atomic_json(path,result)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,default=Path(__file__).with_name('bases.json'))
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--base-id')
    ap.add_argument('--pilot',type=int,default=0)
    ap.add_argument('--seconds',type=float,default=0,help='Per-base limit; timeout never proves exclusion')
    ap.add_argument('--workers',type=int,default=1)
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    all_records = manifest['bases']
    records = list(all_records)
    if args.base_id: records = [r for r in records if r['id']==args.base_id]
    if args.pilot:
        # Prefer different (case,profile) kinds, then graphs; deterministic.
        live = [r for r in records if not r['hand_excluded']]
        chosen,seen = [],set()
        for r in live:
            key = (r['case'],r['inner'] is not None)
            if key not in seen:
                chosen.append(r);seen.add(key)
        records = chosen[:args.pilot]
        if len(records)<args.pilot:
            records += [r for r in live if r not in records][:args.pilot-len(records)]
    if not records: raise SystemExit('No selected bases')
    assert len({r['id'] for r in records}) == len(records)
    args.output.mkdir(parents=True,exist_ok=True)
    digest = source_digest()
    work = [(r,str(args.output),args.seconds,digest) for r in records]
    start = time.monotonic()
    results = []
    def collect(iterator):
        for result in iterator:
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k not in ('configurations',)}),flush=True)
    if args.workers==1: collect(map(job,work))
    else:
        with multiprocessing.Pool(args.workers) as pool:
            collect(pool.imap_unordered(job,work))
    summary = dict(source_digest=digest,selected=len(records),manifest_bases=len(all_records),
                   covers_full_manifest=len(records)==len(all_records),
                   completed=sum(r['status']=='complete' for r in results),
                   timeouts=sum(r['status']=='timeout' for r in results),
                   complete_configurations=sum(r['complete_configurations'] for r in results),
                   seconds=time.monotonic()-start,base_ids=sorted(r['base_id'] for r in results))
    summary['exclusion_verified'] = (summary['covers_full_manifest'] and
        summary['completed']==len(all_records) and summary['timeouts']==0 and
        summary['complete_configurations']==0)
    atomic_json(args.output/'summary.json',summary)
    print(json.dumps(summary),flush=True)


if __name__=='__main__': main()
