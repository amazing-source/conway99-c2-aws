import numpy as np, time
rng = np.random.default_rng(1)
for n in (27, 39, 47):
    A = rng.integers(0, 2, (n, n)); A = np.triu(A, 1); A = A + A.T
    M = (27 * np.eye(n) - 9 * A + 1)
    t = time.time()
    for _ in range(300):
        w, V = np.linalg.eigh(M)
    print(n, "eigh ms:", (time.time() - t) / 300 * 1000)
