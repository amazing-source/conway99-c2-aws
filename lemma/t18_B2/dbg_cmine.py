# debug: first K that passes the incremental budget test of c_mine.py but fails the numpy recount; prints the violating pairs
import sys, os, json
sys.argv = ["c_mine.py", "2", "0", "1", "0"]          # time limit 0: nothing is run at import
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "c_mine.py"), encoding="utf-8").read()
ns = {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "c_mine.py"), "__name__": "dbg"}
exec(compile(src.split("\nitems = []")[0], "c_mine.py", "exec"), ns)
np = ns["np"]
orig_good = ns["good"]
count = [0]
def good_dbg(rows, L):
    r = orig_good(rows, L)
    if not r and ns["LAST"][0] == 1 and len(L) == 39 and count[0] < 3:
        count[0] += 1
        A = ns["to_np"](rows, L); C = A @ A; np.fill_diagonal(C, 0)
        bad = np.argwhere(C > 2 - A)
        print("violations:", [(L[a], L[b], int(C[a, b]), int(A[a, b])) for a, b in bad if a < b])
        for v in (37, 38):
            print("  N(%d) =" % v, [u for u in range(47) if (rows[v] >> u) & 1])
        for a, b in bad[:2]:
            print("  N(%d) =" % L[a], [u for u in range(47) if (rows[L[a]] >> u) & 1])
    return r
ns["good"] = good_dbg
d = json.load(open("r3_p250_2_1of2_BC.json"))
for e in d["H_stageB"][:3]:
    ns["do_triple"](e["tau"], tuple(sorted(e["F"])), tuple(e["H"]))
print(ns["ST"])
