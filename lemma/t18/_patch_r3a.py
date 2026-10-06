import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_p250.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


# 1. certificate cap
rep("LOG = CertLog(TAG)\n", "LOG = CertLog(TAG)\nCERTCAP = int(os.environ.get('R3_CERTCAP', '15000'))\n")
rep("            LOG.write({\"n\": n,", "            if LOG.n < CERTCAP:\n                LOG.write({\"n\": n,")
# 2. counters
rep('"C_type_solutions": 0,', '"type_sols": 0, "type_sols_ok33": 0, "F_W_ok": 0, "C_nb1_tests": 0, "C_nb2_tests": 0, "C_type_solutions": 0,')
# 3. W prefilters independent of H, before stage B
rep("        TOT[\"F_base_ok\"] += 1\n",
    "        TOT[\"F_base_ok\"] += 1\n"
    "        # ---- W prefilters that do not depend on H: single mate pairs (25 vertices), then S u N[p] (33 vertices)\n"
    "        def wrows(rw, c, i, j):\n"
    "            w, sw = 37 + 2 * c, 38 + 2 * c\n"
    "            add(rw, w, P_); add(rw, sw, P_); add(rw, w, sw)\n"
    "            add(rw, w, i); add(rw, w, 9 + j); add(rw, sw, j); add(rw, sw, 9 + i)\n"
    "        single_ok = {}\n"
    "        for (i, j) in sorted(set(pr for ts in type_sols for pr in ts)):\n"
    "            rw = rows0[:]; wrows(rw, 0, i, j)\n"
    "            single_ok[(i, j)] = graph_ok(rw, L0 + [37, 38])\n"
    "        ts_ok = []\n"
    "        for ts in type_sols:\n"
    "            if not all(single_ok[pr] for pr in ts):\n"
    "                continue\n"
    "            rw = rows0[:]\n"
    "            for c, (i, j) in enumerate(ts):\n"
    "                wrows(rw, c, i, j)\n"
    "            if graph_ok(rw, L0 + list(range(37, 47))):\n"
    "                ts_ok.append(ts)\n"
    "        TOT[\"type_sols\"] += len(type_sols); TOT[\"type_sols_ok33\"] += len(ts_ok)\n"
    "        if not ts_ok:\n"
    "            continue\n"
    "        TOT[\"F_W_ok\"] += 1\n"
    "        type_sols = ts_ok\n")
# 4. per-H neighbour prefilters
rep("            slack = 4 - fl // 2\n            Hgot = False\n",
    "            slack = 4 - fl // 2\n            Hgot = False\n"
    "            nb1_cache = {}; nb2_cache = {}\n"
    "            def nb1(i, j):\n"
    "                if (i, j) not in nb1_cache:\n"
    "                    good = []\n"
    "                    for k in range(18):\n"
    "                        if req[k] > 0 and req[tau[k]] > 0:\n"
    "                            TOT[\"C_nb1_tests\"] += 1\n"
    "                            rw = rows[:]; wrows(rw, 0, i, j)\n"
    "                            add(rw, 37, X2(k)); add(rw, 38, X2(tau[k]))\n"
    "                            if graph_ok(rw, L0 + [X2(k), X2(tau[k]), 37, 38]):\n"
    "                                good.append(k)\n"
    "                    nb1_cache[(i, j)] = good\n"
    "                return nb1_cache[(i, j)]\n"
    "            def nb2(i, j, k, k2):\n"
    "                key = (i, j, min(k, k2), max(k, k2))\n"
    "                if key not in nb2_cache:\n"
    "                    TOT[\"C_nb2_tests\"] += 1\n"
    "                    rw = rows[:]; wrows(rw, 0, i, j)\n"
    "                    add(rw, 37, X2(k)); add(rw, 38, X2(tau[k])); add(rw, 37, X2(k2)); add(rw, 38, X2(tau[k2]))\n"
    "                    nb2_cache[key] = graph_ok(rw, L0 + [X2(k), X2(tau[k]), X2(k2), X2(tau[k2]), 37, 38])\n"
    "                return nb2_cache[key]\n")
rep("                rw = rows[:]\n                ok = True\n                for c, (i, j) in enumerate(ts):\n"
    "                    w, sw = 37 + 2 * c, 38 + 2 * c\n"
    "                    add(rw, w, P_); add(rw, sw, P_); add(rw, w, sw)\n"
    "                    add(rw, w, i); add(rw, w, 9 + j); add(rw, sw, j); add(rw, sw, 9 + i)\n",
    "                rw = rows[:]\n                for c, (i, j) in enumerate(ts):\n                    wrows(rw, c, i, j)\n"
    "                if any(len(nb1(i, j)) < 2 for (i, j) in ts):\n                    continue\n")
rep("                    cands = [k for k in range(18) if rq[k] > 0 and rq[tau[k]] > 0]\n",
    "                    ti_, tj_ = ts[c]\n"
    "                    cands = [k for k in nb1(ti_, tj_) if rq[k] > 0 and rq[tau[k]] > 0]\n")
rep("                            if rq2[k] <= 0 or rq2[tau[k]] <= 0 or tau[k] in chosen or k in chosen:\n                                continue\n",
    "                            if rq2[k] <= 0 or rq2[tau[k]] <= 0 or tau[k] in chosen or k in chosen:\n                                continue\n"
    "                            if not all(nb2(ti_, tj_, k, k0) for k0 in chosen):\n                                continue\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("r3_p250 patched (a), syntax ok")
