"""Builds fastrD.c from fastr.c: pivot block of size <= 5 and candidates balanced for NT extra vectors."""
BS = chr(92)
s = open("fastr.c").read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)


rep("/* Rank-mode exhaustive star search at rank 37 for a disconnected, triangle-free, torsion-free ball.",
    "/* fastrD.c = fastr.c generalised: pivot block of any size D <= 5, and candidate shadows restricted to those balanced\n"
    "   for NT extra vectors (balanced torsion taken as true relations; Gm must then be (M0 + sum z z^T)^(-1) over the\n"
    "   component relations AND these vectors).  Used for the sub-cases whose residue has rank 3, 4 or 5.\n"
    "   Input: u D ncomp NT limit maxnodes / quota / lay / comp / adj / K / Gm / NT vectors of length 36.\n"
    "   Original header of fastr.c:\n"
    "   Rank-mode exhaustive star search at rank 37 for a disconnected, triangle-free, torsion-free ball.")
rep("static int U, D, NCOMP, LIMIT; static long long MAXNODES;",
    "static int U, D, NCOMP, NT, LIMIT; static long long MAXNODES;\nstatic int TV[4][36];")
rep("static int rho[12], piv[12][2], Binv[12][2][2];", "static int rho[12], piv[12][5], Binv[12][5][5];")
rep("    int r = rho[d], c[2] = {0, 0}, k, i;", "    int r = rho[d], c[5] = {0, 0, 0, 0, 0}, k, i;")
a = s.index("            rho[d + 1] = rho[d] + inc; memcpy(piv[d + 1], piv[d], sizeof piv[d]); memcpy(Binv[d + 1], Binv[d], sizeof Binv[d]);")
b = s.index("            /* filter the alive candidates */")
block = (
    "            rho[d + 1] = rho[d] + inc; memcpy(piv[d + 1], piv[d], sizeof piv[d]); memcpy(Binv[d + 1], Binv[d], sizeof Binv[d]);\n"
    "            if (inc) {\n"
    "                /* new principal block: old pivots, plus d (inc = 1) or istar and d (inc = 2); it is invertible */\n"
    "                int r0 = rho[d], r1 = rho[d + 1], M[5][10], aa, bb, ee;\n"
    "                if (inc == 2) piv[d + 1][r0] = istar;\n"
    "                piv[d + 1][r1 - 1] = d;\n"
    "                for (aa = 0; aa < r1; aa++) for (bb = 0; bb < r1; bb++) { M[aa][bb] = Y[piv[d + 1][aa]][piv[d + 1][bb]]; M[aa][r1 + bb] = (aa == bb); }\n"
    "                for (aa = 0; aa < r1; aa++) {\n"
    "                    int p = -1; for (bb = aa; bb < r1; bb++) if (M[bb][aa]) { p = bb; break; }\n"
    "                    if (p < 0) { fprintf(stderr, \"singular pivot block" + BS + "n\"); exit(6); }\n"
    "                    if (p != aa) for (bb = 0; bb < 2 * r1; bb++) { int tt = M[aa][bb]; M[aa][bb] = M[p][bb]; M[p][bb] = tt; }\n"
    "                    int iv = inv7[M[aa][aa]]; for (bb = 0; bb < 2 * r1; bb++) M[aa][bb] = md(M[aa][bb] * iv);\n"
    "                    for (ee = 0; ee < r1; ee++) if (ee != aa && M[ee][aa]) { int fct = M[ee][aa]; for (bb = 0; bb < 2 * r1; bb++) M[ee][bb] = md(M[ee][bb] - fct * M[aa][bb]); }\n"
    "                }\n"
    "                for (aa = 0; aa < r1; aa++) for (bb = 0; bb < r1; bb++) Binv[d + 1][aa][bb] = M[aa][r1 + bb];\n"
    "            }\n")
s = s[:a] + block + s[b:]
rep("    for (k = 0; k < 6; k++) for (z = k + 1; z < 6; z++) if (K[n[k]][n[z]] == 0) return;\n    if (NC >= MAXC)",
    "    for (k = 0; k < 6; k++) for (z = k + 1; z < 6; z++) if (K[n[k]][n[z]] == 0) return;\n"
    "    for (k = 0; k < NT; k++) { int sv = 0; for (z = 0; z < 6; z++) sv += TV[k][n[z]]; if (sv % 7) return; }\n    if (NC >= MAXC)")
rep("    if (fscanf(f, \"%d %d %d %d %lld\", &U, &D, &NCOMP, &LIMIT, &MAXNODES) != 5) return 3;\n"
    "    if (D > 2) { fprintf(stderr, \"D <= 2 only" + BS + "n\"); return 4; }",
    "    if (fscanf(f, \"%d %d %d %d %d %lld\", &U, &D, &NCOMP, &NT, &LIMIT, &MAXNODES) != 6) return 3;\n"
    "    if (D > 5 || NT > 4) { fprintf(stderr, \"D <= 5 and NT <= 4 only" + BS + "n\"); return 4; }")
rep("    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, \"%d\", &Gm[i][j]);\n    fclose(f);",
    "    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, \"%d\", &Gm[i][j]);\n"
    "    for (k = 0; k < NT; k++) for (i = 0; i < 36; i++) if (fscanf(f, \"%d\", &TV[k][i]) != 1) return 7;\n    fclose(f);")
# the old 2 x 2 updates are gone with the replaced block; check nothing of them is left
assert "piv[d + 1][1] = d; Binv[d + 1][0][0] = md(c * id)" not in s
open("fastrD.c", "w", newline="\n").write(s)
print("fastrD.c written,", len(s), "characters")
