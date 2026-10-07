# exploration (case I, N(p) in the base): eng5 on a few configurations of N(p) from i_bases_<name>.json
# usage: python run_in.py I.0 "(4, 2, 1)" <indices comma separated> <tlim per base>
import sys, json, time, os
import eng5, cases
name, prof = sys.argv[1], sys.argv[2]
idx = [int(t) for t in sys.argv[3].split(",")]
tl = float(sys.argv[4])
bases = json.load(open("i_bases_%s.json" % name.replace(".", "_")))[prof]
h0 = 1 if prof.startswith("(4") else 0
os.makedirs("in_test", exist_ok=True)
for bi in idx:
    b = bases[bi]
    pairs = []
    for t in b:
        if isinstance(t[0], list):
            pairs.append(("2", tuple(t[0]), tuple(t[1])))
        else:
            pairs.append(("1", t[0], t[1]))
    pairs += [("0",)] * h0
    prob = cases.CaseIN(name, pairs)
    t0 = time.process_time()
    out = eng5.run(prob, 0, 1, tl, 99, "in_test/%s_%d" % (name.replace(".", "_"), bi))
    print("BASE %d of %d (%s %s): timeout %s cpu %.1f s visited %s complete %d" % (
        bi, len(bases), name, prof, out["timeout"], time.process_time() - t0, out["visited"], len(out["survivors"])))
    sys.stdout.flush()
