"""How many free parameters does the nine-class theta vector keep, as the truncation grows?"""
import sys, time
import z9theta as Z
r = int(sys.argv[1])
for N in (24, 32, 40, 48):
    t0 = time.time(); Mo = Z.Model(r, N)
    ok0, piv0, free0, _ = Mo.solve()
    Mo.geometry(); ok, piv, free, R = Mo.solve()
    kinds = {}
    for j in free: kinds[Mo.names[j][0]] = kinds.get(Mo.names[j][0], 0) + 1
    print(f"rank {r} N {N}: unknowns {len(Mo.names)}, modularity alone free {len(free0)}; with zeros: consistent {ok}, free {len(free)} {kinds}  [{time.time()-t0:.0f}s]", flush=True)
