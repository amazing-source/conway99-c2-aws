import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_p250.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


# make the H-independent W prefilter lazy: it is only needed when stage B leaves some H
old = ("        single_ok = {}\n"
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
new = ("        ts_box = [None]\n"
       "        def lazy_type_sols():\n"
       "            if ts_box[0] is None:\n"
       "                single_ok = {}\n"
       "                for (i, j) in sorted(set(pr for ts in type_sols for pr in ts)):\n"
       "                    rw = rows0[:]; wrows(rw, 0, i, j)\n"
       "                    single_ok[(i, j)] = graph_ok(rw, L0 + [37, 38])\n"
       "                ts_ok = []\n"
       "                for ts in type_sols:\n"
       "                    if not all(single_ok[pr] for pr in ts):\n"
       "                        continue\n"
       "                    rw = rows0[:]\n"
       "                    for c, (i, j) in enumerate(ts):\n"
       "                        wrows(rw, c, i, j)\n"
       "                    if graph_ok(rw, L0 + list(range(37, 47))):\n"
       "                        ts_ok.append(ts)\n"
       "                TOT[\"type_sols\"] += len(type_sols); TOT[\"type_sols_ok33\"] += len(ts_ok)\n"
       "                if ts_ok:\n"
       "                    TOT[\"F_W_ok\"] += 1\n"
       "                ts_box[0] = ts_ok\n"
       "            return ts_box[0]\n")
rep(old, new)
rep("            for ts in type_sols:\n                TOT[\"C_type_solutions\"] += 1\n",
    "            for ts in lazy_type_sols():\n                TOT[\"C_type_solutions\"] += 1\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("r3_p250 patched (b), syntax ok")
