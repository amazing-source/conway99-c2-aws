"""Read-only: how much of the AWS Route-C batch is already saved on the GitHub run branches.
Slice rule (run_jobs.py line 49): slice i/m takes jobs[t] with t % m == i. Done job = a results/<job>.jsonl on the branch."""
import json, subprocess

JOBS = json.load(open(r'C:\Users\RESEARCHER\Desktop\c2_experimental\c2_cloud_run\jobs.json'))
jobs = JOBS['jobs'] if isinstance(JOBS, dict) and 'jobs' in JOBS else JOBS
M = 54
names = {i: n for n, i in [(e['name'], int(e['slice'].split('/')[0])) for e in json.load(open(
    r'C:\Users\RESEARCHER\Desktop\c2_experimental\aws_machines_54.json'))]} if False else None

machines = json.loads(subprocess.run(['gh', 'api', 'repos/amazing-source/conway99-c2-aws/contents/machines.json',
                                      '-H', 'Accept: application/vnd.github.raw'], capture_output=True, text=True).stdout)
branch_of = {int(e['slice'].split('/')[0]): e['name'] for e in machines}
for i in range(M):
    branch_of.setdefault(i, 'slice-%d' % i)

aliases = []
for i in range(M):
    aliases.append('s%d: object(expression: "run/%s:results") { ... on Tree { entries { name } } }' % (i, branch_of[i]))
q = 'query { repository(owner:"amazing-source", name:"conway99-c2-aws") { %s } }' % ' '.join(aliases)
out = json.loads(subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + q], capture_output=True, text=True).stdout)
repo = out['data']['repository']

tot_jobs = tot_done = 0
never = []
lines = []
for i in range(M):
    sl = [j for t, j in enumerate(jobs) if t % M == i]
    node = repo.get('s%d' % i)
    done = len([e for e in node['entries'] if e['name'].endswith('.jsonl')]) if node else 0
    if node is None:
        never.append(i)
    tot_jobs += len(sl)
    tot_done += min(done, len(sl))
    lines.append('%2d %-14s %3d/%3d' % (i, branch_of[i], done, len(sl)))
print('total jobs in package:', len(jobs))
print('saved finished jobs on GitHub: %d / %d' % (tot_done, tot_jobs))
print('slices with no branch (never started):', never)
print('per slice (done/total):')
for k in range(0, len(lines), 3):
    print('   ' + '   '.join(lines[k:k + 3]))

# --- weight by estimated hours (est_h per job), and per-lattice completion
done_keys = set()
for i in range(M):
    node = repo.get('s%d' % i)
    for e in (node['entries'] if node else []):
        if e['name'].endswith('.jsonl'):
            p = e['name'][:-6].split('_')
            done_keys.add((p[0], int(p[1]), int(p[2])))
H = sum(j['est_h'] for j in jobs)
Hd = sum(j['est_h'] for j in jobs if (j['lid'], j['k'], j['n']) in done_keys)
print('estimated core-hours: done %.0f of %.0f (%.0f%%), remaining %.0f' % (Hd, H, 100 * Hd / H, H - Hd))
from collections import defaultdict
per = defaultdict(lambda: [0, 0])
for j in jobs:
    per[j['lid']][1] += 1
    per[j['lid']][0] += (j['lid'], j['k'], j['n']) in done_keys
full = sorted(l for l, (d, t) in per.items() if d == t)
print('lattices in the batch: %d; fully finished on GitHub: %d %s' % (len(per), len(full), full))
