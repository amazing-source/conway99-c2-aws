import ast, collections, sys
fn = sys.argv[1]
L = [l for l in open(fn) if l.startswith('   x = ')]
agg = collections.Counter(); per = collections.Counter(); fun = collections.Counter()
f1kinds = collections.Counter(); nF1 = 0
for l in L:
    d = ast.literal_eval(l.split('|', 1)[1].strip())
    rs = d.get('reasons', {})
    for k, v in rs.items():
        agg[k[:2]] += v
        if k.startswith('F1'):
            nF1 += v
            for kind in k.split(' on ')[1].split(','):
                f1kinds[kind] += v
    per[tuple(sorted(set(k[:2] for k in rs)))] += 1
    fun[(d['n_assign'], d['n_tint'], d['n_E'], d['n_full'])] += 1
print(len(L), 'stage-2 runs')
print('candidate counts by kill reason:', dict(agg))
print('reason classes present per run:'); [print('  ', v, k) for k, v in per.most_common()]
print('funnel (n_assign, n_tint, n_E, n_full) per run:'); [print('  ', v, k) for k, v in sorted(fun.items())]
print('F1 candidates:', nF1, '; fraction of F1 candidates violating each pair kind:')
for k, v in f1kinds.most_common(): print('   %-12s %d' % (k, v))
