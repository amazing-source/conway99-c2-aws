# identification of some case-I survivors with named graphs (exact isomorphism test of t20_common)
import json
from t20_common import *
ref = json.load(open("structures_I.json"))["I"]
def circ(conn):
    m = [[0]*N for _ in range(N)]
    for i in range(N):
        for s in conn:
            m[i][(i+s) % N] = 1; m[(i+s) % N][i] = 1
    return m
cands = {"C10(1,2)": circ((1,2)), "C10(1,3)": circ((1,3)), "C10(1,4)": circ((1,4)), "C10(2,3)": circ((2,3)),
         "C10(2,4)": circ((2,4)), "C10(3,4)": circ((3,4))}
# K5 x K2 minus ...: prism-like graphs
def from_edges(es):
    m = [[0]*N for _ in range(N)]
    for a, b in es:
        m[a][b] = m[b][a] = 1
    return m
# C5 [x] K2 (cartesian product of C5 and K2 has degree 3); C5 x K2 with both "ladders": lexicographic-like graphs
c5k2 = [(i, (i+1) % 5) for i in range(5)] + [(5+i, 5+(i+1) % 5) for i in range(5)] + [(i, 5+i) for i in range(5)]
cands["C5 box K2 + matching i~(i+2)'"] = from_edges(c5k2 + [(i, 5 + (i+2) % 5) for i in range(5)])
cands["C5 box K2 + matching i~(i+1)'"] = from_edges(c5k2 + [(i, 5 + (i+1) % 5) for i in range(5)])
for idx, rec in enumerate(ref):
    hits = [nm for nm, mm in cands.items() if iso_count(rec["m"], [], mm, [])]
    print("I.%d (|Aut| %d): isomorphic to %s" % (idx, rec["aut"], hits if hits else "none of the tested graphs"))
