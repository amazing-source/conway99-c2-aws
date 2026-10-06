import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r3_p250.py")
s = open(fn, encoding="utf-8").read()


def cut(start_marker, end_marker):
    a = s.index(start_marker); b = s.index(end_marker)
    assert a < b
    return a, b


# ---- faster exact tests (numpy integer arithmetic; no overflow: |x_i| <= 10^5, |M_ij| <= 44, n <= 55 => |x^T M x| < 2*10^15)
a, b = cut("def find_neg_vector(M):", "SURV = []")
new_block = '''def find_neg_vector(M):
    """integer vector x with x^T M x < 0, exact in int64 (|x_i| <= 10^5, |M_ij| <= 44, n <= 55: |x^T M x| < 2*10^15)"""
    w, V = np.linalg.eigh(M.astype(float))
    if w[0] > -1e-7:
        return None
    for col in range(min(3, len(w))):
        if w[col] > -1e-7:
            break
        for scale in (8, 30, 100, 1000, 10 ** 5):
            x = np.rint(scale * V[:, col]).astype(np.int64)
            if int(x @ (M @ x)) < 0:
                return [int(t) for t in x]
    TOT["psd_float_neg_no_cert"] += 1
    return None


def to_matrix(rows, L):
    n = len(L)
    buf = b"".join(rows[u].to_bytes(8, "little") for u in L)
    bits = np.unpackbits(np.frombuffer(buf, dtype=np.uint8).reshape(n, 8), axis=1, bitorder="little")
    return bits[:, L].astype(np.int64)


def graph_ok(rows, L):
    n = len(L)
    A = to_matrix(rows, L)
    C = A @ A
    np.fill_diagonal(C, 0)
    if (C > 2 - A).any():
        TOT["rej_budget"] += 1
        return False
    TOT["psd_tests"] += 1
    for mi, Mx in enumerate((27 * np.eye(n, dtype=np.int64) - 9 * A + 1, 44 * np.eye(n, dtype=np.int64) + 11 * A - 2)):
        x = find_neg_vector(Mx)
        if x is not None:
            TOT["rej_psd"] += 1
            if LOG.n < CERTCAP:
                LOG.write({"n": n, "rows": [int(sum(1 << q for q in range(n) if A[u, q])) for u in range(n)], "m": mi, "x": x})
            return False
    return True


def budgets_only(rows, L):
    A = to_matrix(rows, L)
    C = A @ A
    np.fill_diagonal(C, 0)
    return not (C > 2 - A).any()


'''
s = s[:a] + new_block + s[b:]


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# ---- cheap necessary condition per type solution: every X_2 vertex outside A_p must have enough admissible W-neighbours,
#      every vertex of W at least 2 admissible X_2-neighbours (admissible = the 27-vertex test nb1)
rep('"C_type_solutions": 0,', '"C_type_solutions": 0, "C_ts_dead_by_counts": 0,')
rep("                if any(len(nb1(i, j)) < 2 for (i, j) in ts):\n                    continue\n",
    "                if any(len(nb1(i, j)) < 2 for (i, j) in ts):\n                    TOT[\"C_ts_dead_by_counts\"] += 1\n                    continue\n"
    "                dead = False\n"
    "                for k in range(18):\n"
    "                    if req[k] > 0:\n"
    "                        # w_c may see k iff k in nb1(type c); sigma w_c may see k iff tau k in nb1(type c); not both\n"
    "                        avail = sum(1 for (i, j) in ts if (k in nb1(i, j)) or (tau[k] in nb1(i, j)))\n"
    "                        if avail < req[k]:\n"
    "                            dead = True; break\n"
    "                if dead:\n"
    "                    TOT[\"C_ts_dead_by_counts\"] += 1\n"
    "                    continue\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("patched (d), syntax ok")
