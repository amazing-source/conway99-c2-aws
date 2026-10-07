"""T20, branch n_3 = 2: canonical keys of the base classes, to match the bases of another program with those of n3_cases.py.
Usage: python n3_keys.py            -> writes n3_class_keys.json (one record per class: graph, index, key, type, case, inner, bits, size)
       canon_key(A, name)           -> key of any 29 x 29 base matrix in the vertex order of n3_cases.py (x_i = i, y_i = 10 + i,
                                       p = 20, z = 21, z' = 22, the three orbits of X_0' = 23..28)
The key is the sha1 of the smallest relabelled matrix under Aut(B) x (z <-> z') x (permutations and flips of the orbits of X_0').
Two bases have the same key iff they are in the same class."""
import hashlib, json, os, sys
import numpy as np
import n3_cases as NC

_REL = {}


def canon_key(A, name):
    if name not in _REL: _REL[name] = NC.relabellings(NC.bmat(name))
    A = np.asarray(A, dtype=np.int64)
    return hashlib.sha1(min(A[np.ix_(inv, inv)].tobytes() for inv in _REL[name])).hexdigest()


if __name__ == "__main__":
    out = {}
    for name in NC.E:
        recs, counts = NC.labelled_bases(name); reps = NC.quotient(recs, NC.bmat(name))
        rows = [{"index": i, "key": canon_key(r["A"], name), "type": r["type"], "case": r["case"], "inner": r["inner"], "bits": r["bits"],
                 "class_size": r["class_size"]} for i, r in enumerate(reps)]
        assert len({r["key"] for r in rows}) == len(rows)
        lab = {canon_key(r["A"], name) for r in recs}
        assert lab == {r["key"] for r in rows}
        out[name] = rows; print(name, len(rows), "classes,", len(recs), "labelled", flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "n3_class_keys.json"), "w"), indent=0)
