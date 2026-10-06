import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r4_verifyD.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# (K) turned out to be the trivial kernel vector 4 e_p + 1_{N(p)} (see report A19), so the real independent check is:
# for every admissible Z (own generator), build the 49 vertices Y47 u {z, sigma z} and look for an exact PSD violation.
rep("seen = set()\ntotal_K = 0\n",
    "def violation(G):\n"
    "    \"\"\"True iff an integer vector x with x^T M x < 0 is found for M = 9(3I-A)+J or 11(4I+A)-2J (exact, Python ints)\"\"\"\n"
    "    n = G.shape[0]\n"
    "    I = np.eye(n, dtype=np.int64)\n"
    "    for M in (27 * I - 9 * G + 1, 44 * I + 11 * G - 2):\n"
    "        w, V = np.linalg.eigh(M.astype(np.float64))\n"
    "        if w[0] < -1e-7:\n"
    "            Ml = M.tolist()\n"
    "            for sc in (10, 60, 500, 10 ** 4, 10 ** 6):\n"
    "                x = [int(round(sc * float(c))) for c in V[:, 0]]\n"
    "                if sum(x[a] * sum(Ml[a][b] * x[b] for b in range(n)) for a in range(n)) < 0:\n"
    "                    return True\n"
    "            AMB[0] += 1\n"
    "    return False\n"
    "\n\n"
    "AMB = [0]\n"
    "seen = set()\ntotal_K = 0\ntotal_pass49 = 0\n")
rep("        cnt = {\"sets\": 0, \"sets_mate_ok\": 0, \"K\": 0}\n",
    "        cnt = {\"sets\": 0, \"sets_mate_ok\": 0, \"K\": 0, \"pass48\": 0, \"budget49\": 0, \"pass49\": 0}\n")
rep("                    cnt[\"sets_mate_ok\"] += 1\n",
    "                    cnt[\"sets_mate_ok\"] += 1\n"
    "                    G = np.zeros((49, 49), dtype=np.int64)\n"
    "                    G[:47, :47] = A\n"
    "                    for q in Z:\n"
    "                        G[47, 19 + q] = G[19 + q, 47] = 1\n"
    "                    for q in sZ:\n"
    "                        G[48, 19 + q] = G[19 + q, 48] = 1\n"
    "                    if not violation(G[:48, :48]):\n"
    "                        cnt[\"pass48\"] += 1\n"
    "                    C49 = G @ G\n"
    "                    np.fill_diagonal(C49, 0)\n"
    "                    if not (C49 > 2 - G).any():\n"
    "                        cnt[\"budget49\"] += 1\n"
    "                        if not violation(G):\n"
    "                            cnt[\"pass49\"] += 1\n")
rep("        total_K += cnt[\"K\"]\n", "        total_K += cnt[\"K\"]\n        total_pass49 += cnt[\"pass49\"]\n")
rep("              f\"with an admissible mate: {cnt['sets_mate_ok']}; satisfying the kernel condition (K): {cnt['K']}\")\n",
    "              f\"with an admissible mate: {cnt['sets_mate_ok']}; satisfying the kernel condition (K): {cnt['K']}\")\n"
    "        print(f\"   of these {cnt['sets_mate_ok']}: no PSD violation found on Y47 u {{z}} (48 vertices): {cnt['pass48']}; \"\n"
    "              f\"budgets hold on Y47 u {{z, sigma z}}: {cnt['budget49']}; no PSD violation on these 49 vertices: {cnt['pass49']}\")\n")
rep("        for Z in Ksets[:10]:\n            print(\"      Z =\", Z)\n", "")
rep("print(f\"survivors examined: {len(seen)}; sets Z satisfying (K) in total: {total_K}\")\n",
    "print(f\"survivors examined: {len(seen)}; sets Z satisfying (K) in total: {total_K}; \"\n"
    "      f\"candidates (z, sigma z) with no violation on 49 vertices: {total_pass49}; ambiguous float cases: {AMB[0]}\")\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("r4_verifyD patched, syntax ok")
