"""Random CONNECTED balls without triangle and without type-I 4-cycle (six lines per layer), 7 not dividing tau:
star test at u = 0 with no free vector (D = 0): g(f,f) = 0, g(f,f') = 3 + A_ff'.  Exploration only (a sample).
usage: conn_sample.py n seed"""
import sys, random, re, time
import fastlib

def rand_key(rnd):
    n = 12; iota = tuple(i ^ 1 for i in range(n))
    while True:
        def matching():
            p = list(range(n)); rnd.shuffle(p); m = [0] * n
            for a, b in zip(p[0::2], p[1::2]): m[a] = b; m[b] = a
            return tuple(m)
        t1, t2 = matching(), matching(); pi = list(range(n)); rnd.shuffle(pi); pi = tuple(pi)
        if any(pi[i] == i for i in range(n)): continue
        if any(t1[i] == iota[i] or t2[i] == iota[i] or t2[pi[i]] == pi[t1[i]] for i in range(n)): continue
        adj = fastlib.build((iota, t1, t2, pi))
        seen = {0}; st = [0]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        if len(seen) != 36: continue
        if any(len(adj[a] & adj[b]) > 2 for a in range(36) for b in range(a + 1, 36) if b not in adj[a]): continue
        return (iota, t1, t2, pi)

if __name__ == "__main__":
    n = int(sys.argv[1]); rnd = random.Random(int(sys.argv[2])); stats = {"torsion": 0, "dead": 0, "star": 0, "other": 0}; nodes = []
    t0 = time.time()
    for k in range(n):
        key = rand_key(rnd)
        res = fastlib.run([key], [(0, 1, 2)], 0, 0, 0, tag=f"cs{sys.argv[2]}")
        if res == "TORSION": stats["torsion"] += 1; continue
        m = re.search(r"nodes (\d+) solutions (\d+) timeout (\d+)", res)
        if not m: stats["other"] += 1; print("?", res[:200], flush=True); continue
        nodes.append(int(m.group(1)))
        if m.group(2) == "0" and m.group(3) == "0": stats["dead"] += 1
        else: stats["star"] += 1; print("STAR or timeout:", key, res[:200], flush=True)
        if k < 3: print(res[:200], flush=True)
    nodes.sort()
    print(f"sample {n}: {stats}; nodes median {nodes[len(nodes)//2] if nodes else 0} max {nodes[-1] if nodes else 0}; {time.time()-t0:.0f}s", flush=True)
