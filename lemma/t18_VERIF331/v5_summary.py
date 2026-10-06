"""Aggregate the outputs of v1/v2/v3 into one table per graph and per mode.  usage: python v5_summary.py"""
import json, glob

for g in (2, 1, 0):
    J1 = json.load(open('v1_tau_%d.json' % g))
    print('=== B%d: admissible rectangles %d (inside N(p): %d); matchings %d; orbits under Aut(B) %d'
          % (g, len(J1['rect_out']), len(J1['rect_in']), J1['n_matchings'], len(J1['reps'])))
    for mode in (2, 1):
        S = []
        cnt2 = {}
        for fn in sorted(glob.glob('v2_surv_%d_m%d_*of*.json' % (g, mode))):
            j = json.load(open(fn))
            S += j['survivors']
            for k, v in j['counts'].items():
                cnt2[k] = cnt2.get(k, 0) + v
            assert len(j['done']) == len(range(j['part'], j['n_reps'], j['nparts'])), 'stage 2 incomplete'
        if not S and not cnt2:
            continue
        S.sort(key=lambda s: (s['tau'], s['F'], s['sides'], s['H']))
        print('  mode %d (PSD matrices: %s)' % (mode, 'M1 and M2' if mode == 2 else 'M1 only'))
        print('    stage 2: (tau,F) passing budgets on S u {p} u A_p: %d ; survivors on 39 vertices: %d, in %d matchings, '
              '%d pairs (tau,F) ; budget rejections %d, PSD rejections %d'
              % (cnt2['tauF_budget25'], len(S), len({s['tau'] for s in S}), len({(s['tau'], tuple(s['F'])) for s in S}),
                 cnt2['bud_rej'], cnt2['psd_rej']))
        for variant in ('_norowpsd', ''):
            files = [f for f in sorted(glob.glob('v3_out_%d_m%d_*of*%s.json' % (g, mode, variant)))
                     if ('norowpsd' in f) == bool(variant)]
            if not files:
                continue
            c = {}
            done = 0
            Y = []; W = []; F = []
            for fn in files:
                j = json.load(open(fn))
                assert j['n_surv_input'] == len(S)
                done += j['done']
                for k, v in j['counts'].items():
                    c[k] = c.get(k, 0) + v
                Y += j['Y_tables']; W += j['W_tables']; F += j['final']
            print('    stages 3-4 (%s): configurations processed %d of %d%s'
                  % ('raw: no PSD on single rows of C' if variant else 'PSD also on single rows of C', done, len(S),
                     '' if done == len(S) else '   *** INCOMPLETE ***'))
            print('      rows %d (after row PSD %d); C with the right column sums %d; (C,G) %d; passing budgets on Y %d; '
                  'passing budgets + exact PSD on Y %d, in %d configurations, %d matchings'
                  % (c['rows'], c['rows_psd'], c['C_colsum'], c['CG'], c['CG_budget'], len(Y),
                     len({t['surv'] for t in Y}), len({S[t['surv']]['tau'] for t in Y})))
            print('      dual order: W-orbit candidates %d (ok %d); W triples %d; passing budgets on Y1 u W %d; '
                  'passing budgets + exact PSD %d, in %d configurations'
                  % (c['wcand'], c['wcand_ok'], c['wtriples'], c['w_budget'], len(W), len({t['surv'] for t in W})))
            print('      51 vertices: pairs (Y-table, W-table) %d; passing budgets %d; passing budgets + exact PSD %d'
                  % (c['final_pairs'], c['final_budget'], len(F)))
