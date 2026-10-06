import os
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r2_stage2.py")
s = open(fn, encoding="utf-8").read()
BS = chr(92)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)


rep("    for h2 in (2, 3, 4):\n", "    for h2 in CASES:\n")
rep("tlimit = float(sys.argv[4]) if len(sys.argv) > 4 else 540.0\n",
    "tlimit = float(sys.argv[4]) if len(sys.argv) > 4 else 540.0\n"
    "# cases h_2 = number of sigma-orbits of X_2 inside N(p): 3 = profile (3,3,1), 2 = profile (2,5,0); h_2 = 4 is excluded (A9)\n"
    "CASES = [int(c) for c in (sys.argv[5] if len(sys.argv) > 5 else '3')]\n")
rep("                if okp and pc(A & tA) <= 2:\n                    cands_out.append(A)\n"
    "                if size >= 6 and inter_p == 0 and (A & tA) == 0:\n                    cands_in.append(A)\n",
    "                # profile (3,3,1) (A10): every z outside N[p] sees exactly 2 vertices of A_p, the z in N(p) has a = 6\n"
    "                if okp and pc(A & tA) <= 2 and (h2 != 3 or pc(inter_p) == 2):\n                    cands_out.append(A)\n"
    "                if size >= 6 and inter_p == 0 and (A & tA) == 0 and (h2 != 3 or size == 6):\n                    cands_in.append(A)\n"
    "            TOT['cands_out'] = TOT.get('cands_out', 0) + len(cands_out)\n"
    "            TOT['cands_in'] = TOT.get('cands_in', 0) + len(cands_in)\n"
    "            req = [3 if (h2 == 3 and (Ap >> k) & 1) else 2 for k in range(18)]\n"
    "            cap = [3 if (h2 == 3 and (Ap >> k) & 1) else 6 for k in range(18)]\n")
rep("                return all(cov[k] <= 6 for k in ks)\n", "                return all(cov[k] <= cap[k] for k in ks)\n")
rep("                    if n_in != h0 or any(c < 2 for c in cov):\n",
    "                    if n_in != h0 or any(cov[k] < req[k] for k in range(18)):\n")
rep("                deficit = sum(max(0, 2 - c) for c in cov)\n",
    "                deficit = sum(max(0, req[k] - cov[k]) for k in range(18))\n")
rep("                low = [k for k in range(18) if cov[k] < 2]\n                if low:\n",
    "                low = [k for k in range(18) if cov[k] < req[k]]\n"
    "                if n_in < h0:\n"
    "                    pool = [(A, 1) for A in cands_in if A <= tmask(A)]\n"
    "                elif low:\n")
rep("                    pool = [(A, 0) for A in cands_out if (A >> k0) & 1] + " + BS + "\n"
    "                           ([(A, 1) for A in cands_in if (A >> k0) & 1] if n_in < h0 else [])\n",
    "                    pool = [(A, 0) for A in cands_out if (A >> k0) & 1]\n")
rep("                    pool = [(A, 0) for A in cands_out if A <= tmask(A)] + " + BS + "\n"
    "                           ([(A, 1) for A in cands_in if A <= tmask(A)] if n_in < h0 else [])\n",
    "                    pool = [(A, 0) for A in cands_out if A <= tmask(A)]\n")
open(fn, "w", encoding="utf-8").write(s)
print("patched")
