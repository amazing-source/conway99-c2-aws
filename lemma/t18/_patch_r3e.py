import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_p250.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# "forced orbits": for a W vertex w of type (i;j) and an orbit {k, tau k} of X_2 outside A_p, the set
# S u {p} u A_p u {w, sigma w} u {k, tau k} with NO edge between {w, sigma w} and {k, tau k} is completely determined.
# If it fails, every admissible N(w) n X_2 must meet {k, tau k}.
rep('"C_ts_dead_by_counts": 0,', '"C_ts_dead_by_counts": 0, "C_forced_tests": 0,')
rep("            def nb2(i, j, k, k2):\n",
    "            forced_cache = {}\n"
    "            def forced(i, j):\n"
    "                if (i, j) not in forced_cache:\n"
    "                    fo = []\n"
    "                    for k in range(18):\n"
    "                        if k < tau[k] and k not in mem:\n"
    "                            TOT[\"C_forced_tests\"] += 1\n"
    "                            rw = rows[:]; wrows(rw, 0, i, j)\n"
    "                            if not graph_ok(rw, L0 + [X2(k), X2(tau[k]), 37, 38]):\n"
    "                                fo.append(k)\n"
    "                    forced_cache[(i, j)] = fo\n"
    "                return forced_cache[(i, j)]\n"
    "            def nb2(i, j, k, k2):\n")
# a type with too many forced orbits, or a forced orbit that it cannot see, kills the type solution
rep("                dead = False\n                for k in range(18):\n                    if req[k] > 0:\n",
    "                dead = False\n"
    "                for (i, j) in ts:\n"
    "                    fo = forced(i, j)\n"
    "                    if len(fo) > 2 + slack or any((k not in nb1(i, j)) and (tau[k] not in nb1(i, j)) for k in fo):\n"
    "                        dead = True; break\n"
    "                for k in range(18):\n                    if dead:\n                        break\n                    if req[k] > 0:\n")
# a complete set N_c must meet every forced orbit of its type
rep("                        if size >= 2:\n",
    "                        if size >= 2 and all((k in chosen) or (tau[k] in chosen) for k in forced(ti_, tj_)):\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("patched (e), syntax ok")
