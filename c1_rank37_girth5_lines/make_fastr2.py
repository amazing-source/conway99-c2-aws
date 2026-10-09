"""Builds fastr2.c from fastrD.c: rank test on TWO stars at once, at a near point u and at its mate u2.
The far neighbours of u and of u2 are disjoint; a far neighbour f of u has exactly 1 - |n_f cap {transversal neighbours
of u2}| neighbours among those of u2 (f and u2 are not adjacent, their two common neighbours are u and one more vertex,
which is a transversal neighbour of u2 lying in the shadow of f or a far neighbour of u2), and symmetrically.
The 20 x 20 matrix Y (Y_ii = -g(i,i), Y_ij = 3 + A_ij - g(i,j)) must have rank <= D, and each of its rows must have
zero sum over the first star and zero sum over the second star."""
BS = chr(92)
NLC = BS + "n"
s = open("fastrD.c").read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)


rep("/* fastrD.c = fastr.c generalised:",
    "/* fastr2.c = fastrD.c with a SECOND star: after a star at u (rank <= D, zero row sums) is complete, a star at the\n"
    "   mate u2 of u is searched; the cross adjacency is a partial matching (each far neighbour f of u has\n"
    "   1 - |n_f cap {transversal neighbours of u2}| neighbours in the second star, and symmetrically); the 20 x 20\n"
    "   matrix must have rank <= D and every row must have zero sum over each star.  A 'solution' is a pair of stars.\n"
    "   Input: u u2 D ncomp NT limit maxnodes / quota / lay / comp / adj / K / Gm / NT vectors.\n"
    "   Header of fastrD.c:\n"
    "   fastrD.c = fastr.c generalised:")
rep("static int U, D, NCOMP, NT, LIMIT; static long long MAXNODES;",
    "static int U, U2, CEN, D, NCOMP, NT, LIMIT; static long long MAXNODES;\n"
    "static int NA = 0; static signed char *xo; static int dem2[36], matched[10], *al2[24], nal2[24]; static long long nstar1 = 0, nodes2 = 0;")
rep("static int chosen[10], partner[10], Y[10][10];", "static int chosen[20], partner[20], Y[20][20];")
rep("static int rho[12], piv[12][5], Binv[12][5][5];", "static int rho[24], piv[24][5], Binv[24][5][5];")

# the pivot-block update becomes a function
a = s.index("            rho[d + 1] = rho[d] + inc; memcpy(piv[d + 1], piv[d], sizeof piv[d]); memcpy(Binv[d + 1], Binv[d], sizeof Binv[d]);")
b = s.index("            /* filter the alive candidates */")
block = s[a:b]
s = s[:a] + "            newblock(d, inc, istar);\n" + s[b:]
func = ("/* pivot block after the member d has been written into Y */\n"
        "static void newblock(int d, int inc, int istar) {\n" + block.replace("            ", "    ", 1).replace("\n            ", "\n    ") + "}\n\n")
func = func.replace("    }\n}\n\n", "    }\n}\n\n") if func.rstrip().endswith("}") else func
# second stage
stage2 = r'''
static inline int gval(int q, int j) { int g = hs[q], k; for (k = 0; k < 6; k++) g += hv[q][mem[j][k]]; return md(g); }

static void dfs2(int d) {
    if (timeout || (LIMIT && nsol >= LIMIT)) return;
    if (++nodes > MAXNODES) { timeout = 1; return; }
    nodes2++;
    int n = nal2[d], w, k, t, i;
    if (d == 20) {
        for (w = 0; w < 36; w++) if (dem2[w]) return;
        for (k = 10; k < 20; k++) if (!apex[chosen[k]] && partner[k] < 0) return;
        for (k = 0; k < 10; k++) if (!xo[chosen[k]] && matched[k] < 0) return;
        for (k = 0; k < 20; k++) { int s1 = 0, s2 = 0; for (i = 0; i < 10; i++) s1 += Y[k][i]; for (i = 10; i < 20; i++) s2 += Y[k][i]; if (md(s1) || md(s2)) return; }
        nsol++;
        if (nsol <= 2) { printf("PAIR OF STARS:"); for (k = 0; k < 20; k++) { printf(" ["); for (t = 0; t < 6; t++) printf("%d ", mem[chosen[k]][t]); printf("| p%d]", partner[k]); } printf(" rank %d@@", rho[20]); }
        return;
    }
    int cnt[36]; memset(cnt, 0, sizeof cnt);
    for (t = 0; t < n; t++) for (k = 0; k < 6; k++) cnt[mem[al2[d][t]][k]]++;
    int best = -1;
    for (w = 0; w < 36; w++) if (dem2[w] > 0) { if (cnt[w] < dem2[w]) return; if (best < 0 || cnt[w] < cnt[best]) best = w; }
    if (best < 0) return;
    int unp = 0; for (k = 10; k < d; k++) if (!apex[chosen[k]] && partner[k] < 0) unp++;
    if (unp > 20 - d) return;
    for (t = 0; t < n; t++) {
        int j = al2[d][t];
        if (!((mask[j] >> best) & 1ULL)) continue;
        int g[20], inter[20];
        for (i = 0; i < d; i++) { g[i] = gval(j, chosen[i]); inter[i] = __builtin_popcountll(mask[j] & mask[chosen[i]]); }
        for (int pa = 9; pa < d; pa++) {                    /* pa = 9 stands for "no partner among the chosen" */
            if (pa >= 10 && (apex[j] || apex[chosen[pa]] || partner[pa] >= 0 || inter[pa] != 1)) continue;
            for (int ms = -1; ms < 10; ms++) {
                if (xo[j]) { if (ms >= 0) break; }            /* no neighbour in the first star */
                else { if (ms < 0) continue; if (xo[chosen[ms]] || matched[ms] >= 0 || inter[ms] > 1) continue; }
                int y[20], istar = -1;
                for (i = 0; i < d; i++) y[i] = md(3 + ((i == ms) || (pa >= 10 && i == pa)) - g[i]);
                int inc = border(d, y, gd[j], &istar);
                if (rho[d] + inc > D) continue;
                /* zero sum over the first star for the new row */
                int s1 = 0; for (i = 0; i < 10; i++) s1 += y[i];
                if (md(s1)) continue;
                for (k = 0; k < 6; k++) if (mem[j][k] != U2) dem2[mem[j][k]]--;
                chosen[d] = j; partner[d] = (pa >= 10) ? pa : -1; if (pa >= 10) partner[pa] = d;
                if (ms >= 0) matched[ms] = d;
                for (i = 0; i < d; i++) Y[d][i] = Y[i][d] = y[i];
                Y[d][d] = gd[j];
                newblock(d, inc, istar);
                int m = 0, q2;
                for (q2 = 0; q2 < n; q2++) {
                    int q = al2[d][q2];
                    if (q == j || mask[q] == mask[j]) continue;
                    int okd = 1; for (k = 0; k < 6; k++) if (mem[q][k] != U2 && dem2[mem[q][k]] <= 0) { okd = 0; break; }
                    if (!okd) continue;
                    if (__builtin_popcountll(mask[q] & mask[j]) > 2) continue;
                    al2[d + 1][m++] = q;
                }
                nal2[d + 1] = m;
                dfs2(d + 1);
                if (pa >= 10) partner[pa] = -1;
                partner[d] = -1;
                if (ms >= 0) matched[ms] = -1;
                for (k = 0; k < 6; k++) if (mem[j][k] != U2) dem2[mem[j][k]]++;
                if (timeout || (LIMIT && nsol >= LIMIT)) return;
            }
        }
    }
}

static void stage2(void) {
    int k, i, m = 0;
    nstar1++;
    for (k = 0; k < 36; k++) dem2[k] = K[U2][k];
    dem2[U2] = 0;
    for (k = 0; k < 10; k++) matched[k] = -1;
    for (k = 10; k < 20; k++) partner[k] = -1;
    for (i = NA; i < NC; i++) {
        int ok = 1;
        for (k = 0; k < 10 && ok; k++) if (__builtin_popcountll(mask[i] & mask[chosen[k]]) > 2) ok = 0;
        if (ok) al2[10][m++] = i;
    }
    nal2[10] = m;
    dfs2(10);
}

'''.replace("@@", NLC)
c = s.index("static void dfs(int d) {")
s = s[:c] + func + stage2 + s[c:]
# at the end of the first star: go to the second one instead of counting
rep("        nsol++;\n        if (nsol <= 2) { printf(\"SOLUTION:\"); for (k = 0; k < 10; k++) { printf(\" [\"); for (t = 0; t < 6; t++) printf(\"%d \", mem[chosen[k]][t]); printf(\"| p%d]\", partner[k]); } printf(\"" + NLC + "\"); }\n        return;",
    "        stage2();\n        return;")
# candidates: centre-dependent apex flag, and number of transversal neighbours of the other centre in the shadow
rep("    int ap = 0; for (k = 0; k < 3; k++) if (lay[adj[U][k]] != lay[U] && ((m >> adj[U][k]) & 1ULL)) ap = 1;\n    apex[NC] = (signed char)ap;",
    "    int ap = 0, other = (CEN == U) ? U2 : U, xx = 0;\n"
    "    for (k = 0; k < 3; k++) if (lay[adj[CEN][k]] != lay[CEN] && ((m >> adj[CEN][k]) & 1ULL)) ap = 1;\n"
    "    for (k = 0; k < 3; k++) if (lay[adj[other][k]] != lay[other] && ((m >> adj[other][k]) & 1ULL)) xx++;\n"
    "    if (xx > 1) return;\n"
    "    apex[NC] = (signed char)ap; xo[NC] = (signed char)xx;")
rep("    if (fscanf(f, \"%d %d %d %d %d %lld\", &U, &D, &NCOMP, &NT, &LIMIT, &MAXNODES) != 6) return 3;",
    "    if (fscanf(f, \"%d %d %d %d %d %d %lld\", &U, &U2, &D, &NCOMP, &NT, &LIMIT, &MAXNODES) != 7) return 3;")
rep("    apex = malloc(MAXC); hs = malloc(MAXC); gd = malloc(MAXC);", "    apex = malloc(MAXC); hs = malloc(MAXC); gd = malloc(MAXC); xo = malloc(MAXC);")
# candidate generation for both centres
a = s.index("    int lu = lay[U], o1 = (lu == 0) ? 1 : 0, o2 = (lu == 2) ? 1 : 2, n[6];")
b = s.index("    for (k = 0; k < 36; k++) dem[k] = K[U][k]; dem[U] = 0;")
gen = s[a:b]
gen2 = ("    int n[6], pass;\n"
        "    if (lay[U2] != lay[U] || mate[U] != U2) { fprintf(stderr, \"u2 must be the mate of u" + NLC + "\"); return 8; }\n"
        "    for (pass = 0; pass < 2; pass++) {\n"
        "    CEN = pass ? U2 : U;\n"
        "    int lu = lay[CEN], o1 = (lu == 0) ? 1 : 0, o2 = (lu == 2) ? 1 : 2;\n"
        + gen.split("\n", 1)[1].replace("L[lu][a]; if (va == U ||", "L[lu][a]; if (va == CEN ||")
              .replace("K[U][va] == 0", "K[CEN][va] == 0").replace("K[U][x1] == 0 || K[U][x2] == 0", "K[CEN][x1] == 0 || K[CEN][x2] == 0")
              .replace("K[U][y1] == 0 || K[U][y2] == 0", "K[CEN][y1] == 0 || K[CEN][y2] == 0").replace("n[0] = U;", "n[0] = CEN;")
        + "    if (pass == 0) NA = NC;\n    }\n")
assert "CEN ||" in gen2 and "n[0] = CEN;" in gen2 and gen2.count("K[CEN]") == 5, gen2
s = s[:a] + gen2 + s[b:]
rep("    for (i = 0; i < NC; i++) {\n        /* a single shadow", "    for (k = 0; k < 24; k++) al2[k] = malloc(sizeof(int) * (NC + 1));\n    for (i = 0; i < NA; i++) {\n        /* a single shadow")
rep("    printf(\"cands %d nodes %lld solutions %d timeout %d" + NLC + "\", NC, nodes, nsol, timeout);",
    "    printf(\"cands %d + %d first stars %lld nodes %lld (second stage %lld) pairs %d timeout %d" + NLC + "\", NA, NC - NA, nstar1, nodes, nodes2, nsol, timeout);")
assert "mem[j][k] != U) dem" in s      # first stage still uses U for its own demands
open("fastr2.c", "w", newline="\n").write(s)
print("fastr2.c written,", len(s), "characters")
