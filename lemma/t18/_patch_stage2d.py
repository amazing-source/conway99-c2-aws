import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_stage2.py")
s = open(fn, encoding="utf-8-sig").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


# 1. survivors of r2_hfirst.py (profile (3,3,1)): restrict (tau, F, A_z0, H) to them
rep("pc = lambda x: bin(x).count(\"1\")\nt0 = time.time()\n",
    "pc = lambda x: bin(x).count(\"1\")\nt0 = time.time()\n"
    "# optional restriction to the survivors of r2_hfirst.py: env R2_SURV = comma separated json files.\n"
    "# SURV[tau][F][canonical A_z0] = set of admissible H (tuples of 18 bitmasks)\n"
    "SURV = None\n"
    "if os.environ.get('R2_SURV'):\n"
    "    SURV = {}\n"
    "    M18 = (1 << 18) - 1\n"
    "    for f_ in os.environ['R2_SURV'].split(','):\n"
    "        for s_ in json.load(open(os.path.join(here, f_)))['survivors']:\n"
    "            rows_ = s_['rows']\n"
    "            H_ = tuple((rows_[19 + k] >> 19) & M18 for k in range(18))\n"
    "            A0_ = (rows_[37] >> 19) & M18; A1_ = (rows_[38] >> 19) & M18\n"
    "            SURV.setdefault(tuple(s_['tau']), {}).setdefault(tuple(s_['F']), {}).setdefault(min(A0_, A1_), set()).add(H_)\n"
    "curH = [None]\n")
rep("            mem = [k for o in Forb for k in (o, tau[o])]\n            if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):\n                continue\n",
    "            if SURV is not None and tuple(Forb) not in SURV.get(tuple(tau), {}):\n                continue\n"
    "            mem = [k for o in Forb for k in (o, tau[o])]\n            if any(R[a][b] > 1 for a in mem for b in mem if a != b and b != tau[a]):\n                continue\n")
rep("                    pool = [(A, 1) for A in cands_in if A <= tmask(A)]\n",
    "                    pool = [(A, 1) for A in cands_in if A <= tmask(A)]\n"
    "                    if SURV is not None:\n"
    "                        pool = [(A, 1) for A, _ in pool if A in SURV[tuple(tau)][tuple(Forb)]]\n")
rep("                    if pair_ok(A) and pair_ok(tA):\n                        chosen.append((A, isin))\n"
    "                        orbit_rec(n_in + isin, budget - cost)\n                        chosen.pop()\n",
    "                    if pair_ok(A) and pair_ok(tA):\n                        chosen.append((A, isin))\n"
    "                        if SURV is not None and isin:\n"
    "                            oldc, oldr = cap[:], req[:]\n"
    "                            curH[0] = SURV[tuple(tau)][tuple(Forb)][A]\n"
    "                            for k in range(18):\n"
    "                                ds = [pc(h_[k]) for h_ in curH[0]]\n"
    "                                cap[k] = max(ds) + 2; req[k] = min(ds) + 2\n"
    "                        orbit_rec(n_in + isin, budget - cost)\n"
    "                        if SURV is not None and isin:\n"
    "                            cap[:] = oldc; req[:] = oldr\n"
    "                        chosen.pop()\n")
rep("                Hset = set(tuple(h) for h in Hs)\n",
    "                Hset = set(tuple(h) for h in Hs)\n"
    "                if SURV is not None:\n                    Hset &= curH[0]\n")
rep("my = [r for q, r in enumerate(reps) if q % nparts == part]\n",
    "if SURV is not None:\n    reps = [r for r in reps if tuple(r) in SURV]\n"
    "my = [r for q, r in enumerate(reps) if q % nparts == part]\n")
rep('f"r2_stage2_{si}_{part}of{nparts}.json"', 'f"r2_stage2_{si}_{part}of{nparts}{\'_surv\' if SURV is not None else \'\'}.json"')
open(fn, "w", encoding="utf-8", newline="\n").write(s)
import ast
ast.parse(s)
print("patched d, syntax ok")
