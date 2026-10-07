"""Unit test of the inner-orbit path (zz = 1) of the engine routines used by eng5z: on the bases of one graph, for random inner
candidates (row adjacent to p, to one deficient pair on each side, to a random subset of X_0'), compare
  Node.budget_fail(row, 1)  with a from-scratch budget count on the child graph, and
  Node.psd_fail(row, 1)     with the eigenvalues of M1 and M2 of the child graph (float; cases within 1e-6 of zero are skipped).
Also zz = 0 rows, as a control. Usage: python check_inner.py <graph> <number of trials>"""
import sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, n3_cases as NC, eng5z
name, trials = sys.argv[1], int(sys.argv[2]); rng = random.Random(7)
recs, _ = NC.labelled_bases(name); reps = NC.quotient(recs, NC.bmat(name))
stats = eng5z.Counter(); agree = {"budget": 0, "psd": 0}; skipped = 0; seen = {(0, "b0"): 0, (0, "b1"): 0, (1, "b0"): 0, (1, "b1"): 0, (0, "p1"): 0, (1, "p1"): 0}
for _ in range(trials):
    rec = rng.choice(reps); prob = NC.CaseIN3(rec); node = eng5z.Node(prob.AB.copy(), prob.sig); node.prepare()
    units = sorted(prob.units); U = rng.choice(units); V = rng.choice(units); zz = rng.randint(0, 1)
    row = np.zeros(node.n, dtype=np.int64)
    for i in U: row[i] = 1
    for i in V: row[10 + i] = 1
    if zz: row[20] = 1
    for x in NC.X0V:
        if rng.random() < 0.3: row[x] = 1
    if rng.random() < 0.2: row[rng.choice((21, 22))] = 1
    ch = node.child(row, zz); A = ch.A; n = A.shape[0]
    assert A[n - 2, n - 1] == zz and (A == A.T).all()
    C = A @ A; viol = C + A > 2; np.fill_diagonal(viol, False); full_b = bool(viol.any())
    eb = bool(node.budget_fail(row, zz)); assert eb == full_b, ("budget mismatch", rec["type"], U, V, zz, row.tolist())
    agree["budget"] += 1; seen[(zz, "b1" if eb else "b0")] += 1
    if eb: continue
    I = np.eye(n); J = np.ones((n, n))
    w1 = np.linalg.eigvalsh(9 * (3 * I - A) + J)[0]; w2 = np.linalg.eigvalsh(11 * (4 * I + A) - 2 * J)[0]
    if min(abs(w1), abs(w2)) < 1e-6 and min(w1, w2) > -1e-6: skipped += 1; continue
    ep = node.psd_fail(row, zz, stats) is not None
    assert ep == (min(w1, w2) < -1e-6), ("psd mismatch", rec["type"], U, V, zz, w1, w2)
    agree["psd"] += 1; seen[(zz, "p1")] += int(ep)
print("%s: %d trials; budget agreements %d, psd agreements %d, skipped (eigenvalue ~ 0) %d; cases seen %s" % (name, trials, agree["budget"], agree["psd"], skipped, seen))
