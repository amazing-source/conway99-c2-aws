import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r4_verifyC2.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# 1. lazy evaluation of FS: a type solution dies as soon as one of its types has an empty FS (cached types first)
rep("            lists = [FS(i, j) for (i, j) in ts]\n"
    "            if any(not L for L in lists):\n"
    "                ST[\"ts_dead_empty_FS\"] += 1\n"
    "                continue\n",
    "            dead = False\n"
    "            for c in sorted(range(5), key=lambda c: ts[c] not in fs_cache):\n"
    "                if not FS(*ts[c]):\n"
    "                    dead = True; break\n"
    "            if dead:\n"
    "                ST[\"ts_dead_empty_FS\"] += 1\n"
    "                continue\n"
    "            lists = [FS(i, j) for (i, j) in ts]\n")
# 2. inside FS: budgets are monotone in N, so a partial N that already violates a budget on the 39 vertices is dropped
rep("                        elif len(N) < 2 + slack:\n"
    "                            rec_n(a + 1, N + [k if name == \"+\" else tk])\n",
    "                        elif len(N) < 2 + slack:\n"
    "                            N2 = N + [k if name == \"+\" else tk]\n"
    "                            A2 = A.copy()\n"
    "                            put_W(A2, 0, i, j)\n"
    "                            for q in N2:\n"
    "                                A2[37, 19 + q] = A2[19 + q, 37] = 1\n"
    "                                A2[38, 19 + tau[q]] = A2[19 + tau[q], 38] = 1\n"
    "                            sub = A2[:39, :39]\n"
    "                            Cn = sub @ sub\n"
    "                            np.fill_diagonal(Cn, 0)\n"
    "                            if (Cn > 2 - sub).any():\n"
    "                                ST[\"FS_partial_budget_cut\"] += 1\n"
    "                                continue\n"
    "                            rec_n(a + 1, N2)\n")
rep('"FS_candidates": 0,', '"FS_candidates": 0, "FS_partial_budget_cut": 0,')
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("r4_verifyC2 patched, syntax ok")
