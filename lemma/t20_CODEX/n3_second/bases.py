"""Generate and record the independent base manifest (one CPU process)."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from model import generate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=Path(__file__).with_name('bases.json'))
    ap.add_argument('--graph', type=int, choices=range(6))
    args = ap.parse_args()
    start = time.monotonic()
    stats, bases = [], []
    for gi in range(6) if args.graph is None else [args.graph]:
        count, records = generate(gi)
        for record in records:
            raw = json.dumps([record['graph'],record['key']],separators=(',',':')).encode()
            record['id'] = hashlib.sha256(raw).hexdigest()[:20]
        stats.append(count); bases.extend(records)
        print(json.dumps(count), flush=True)
    data = dict(schema=1, model='SPEC_N3.md; independent reconstruction',
                seconds=time.monotonic()-start, counts=stats, bases=bases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n', encoding='utf-8')
    print('seconds', data['seconds'], flush=True)


if __name__ == '__main__': main()
