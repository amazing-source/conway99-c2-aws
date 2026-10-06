import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_p250.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# 1. the test of the first mate pair of W depends only on (H, its type, its set of X_2-neighbours): cache it per H
rep("            nb1_cache = {}; nb2_cache = {}\n", "            nb1_cache = {}; nb2_cache = {}; first_cache = {}\n")
rep("                                TOT[\"C_nodes\"] += 1\n"
    "                                if graph_ok(r3, Lc):\n"
    "                                    recW(c + 1, r3, Lc, rq2, sl - (size - 2))\n",
    "                                if c == 0:\n"
    "                                    ck = (ts[0], tuple(sorted(chosen)))\n"
    "                                    if ck not in first_cache:\n"
    "                                        TOT[\"C_nodes\"] += 1\n"
    "                                        first_cache[ck] = graph_ok(r3, Lc)\n"
    "                                    okc = first_cache[ck]\n"
    "                                else:\n"
    "                                    TOT[\"C_nodes\"] += 1\n"
    "                                    okc = graph_ok(r3, Lc)\n"
    "                                if okc:\n"
    "                                    recW(c + 1, r3, Lc, rq2, sl - (size - 2))\n")
# 2. always record the stage-B set (tau, F, H) for the comparison with the independent verifier
rep("SURV = []          # survivors of the last stage run\n",
    "SURV = []          # survivors of the last stage run\nHLIST = []         # stage B: all (tau, F, H) passing the counting conditions\n")
rep("            TOT[\"H_after_counts\"] += 1\n",
    "            TOT[\"H_after_counts\"] += 1\n"
    "            HLIST.append({\"tau\": ti, \"F\": list(Forb), \"H\": [(rows[X2(k)] >> 19) & ((1 << 18) - 1) for k in range(18)]})\n")
rep("\"timed_out\": timed_out, \"tau_alive\": tau_alive, \"survivors\": SURV[:200000], \"n_cert\": LOG.n},",
    "\"timed_out\": timed_out, \"tau_alive\": tau_alive, \"survivors\": SURV[:200000], \"n_cert\": LOG.n,\n"
    "           \"H_stageB\": HLIST},")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)

fn2 = os.path.join(here, "r3_verify.py")
v = open(fn2, encoding="utf-8").read()
old = "        for e in d[\"survivors\"]:\n            theirs.add((e[\"tau\"], tuple(sorted(e[\"F\"])), tuple(e[\"H\"])))\n"
assert v.count(old) == 1
v = v.replace(old, "        for e in d[\"H_stageB\"]:\n            theirs.add((e[\"tau\"], tuple(sorted(e[\"F\"])), tuple(e[\"H\"])))\n")
open(fn2, "w", encoding="utf-8", newline="\n").write(v)
ast.parse(v)
print("patched (c), both files syntax ok")
