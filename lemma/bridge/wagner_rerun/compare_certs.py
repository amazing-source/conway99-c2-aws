import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
print("keys only in rerun:", sorted(set(a) - set(b)), "| only in dossier:", sorted(set(b) - set(a)))
for k in sorted(set(b) - set(a)): print("  dossier-only", k, "=", str(b[k])[:300])
same = all(a[k] == b[k] for k in set(a) & set(b) if k != "seconds")
print("all common keys except 'seconds' identical:", same, "| common keys:", sorted(set(a) & set(b)))
print("number of certificates:", len(a.get("certificates", [])), len(b.get("certificates", [])))
