/* fastrD.c = fastr.c generalised: pivot block of any size D <= 5, and candidate shadows restricted to those balanced
   for NT extra vectors (balanced torsion taken as true relations; Gm must then be (M0 + sum z z^T)^(-1) over the
   component relations AND these vectors).  Used for the sub-cases whose residue has rank 3, 4 or 5.
   Input: u D ncomp NT limit maxnodes / quota / lay / comp / adj / K / Gm / NT vectors of length 36.
   Original header of fastr.c:
   Rank-mode exhaustive star search at rank 37 for a disconnected, triangle-free, torsion-free ball.
   No scalar is enumerated.  With g(i,j) = (3 + n_i)^T Gm (3 + n_j), Gm = (M0 + Z Z^T)^(-1) mod 7, the matrix
        Y_ii = -g(i,i),     Y_ij = 3 + A_ij - g(i,j)    (i != j)
   of a star must be the Gram matrix of ten vectors of sum zero in a non-degenerate space of dimension D = (number of
   components) - 1.  Necessary conditions tested here: rank(Y) <= D over F_7 and Y 1 = 0.  Both classes of forms are
   covered at once.  The search chooses the ten shadows and, for each, its partner among the chosen ones (adjacent
   pairs: intersection {u}, no apex, one partner each); the rank is tracked with a pivot block of size <= D (D <= 2).
   Input: u D ncomp limit maxnodes / quota[ncomp] / lay[36] / comp[36] / adj[36][3] / K[36][36] / Gm[36][36]. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXC 60000
static int U, D, NCOMP, NT, LIMIT; static long long MAXNODES;
static int TV[4][36];
static int quota[6], lay[36], comp[36], adj[36][3], K[36][36], Gm[36][36];
static unsigned long long amask[36];
static int NC = 0;
static int (*mem)[6]; static signed char *apex, *hs, *gd; static signed char (*hv)[36]; static unsigned long long *mask;
static int dem[36];
static int *al[12]; static unsigned short *op[12]; static signed char (*gv[12])[10]; static int nal[12];
static int chosen[10], partner[10], Y[10][10];
static int rho[12], piv[12][5], Binv[12][5][5];
static long long nodes = 0; static int nsol = 0, timeout = 0;
static const int inv7[7] = {0, 1, 4, 5, 2, 3, 6};
static inline int md(int x) { x %= 7; return x < 0 ? x + 7 : x; }

/* rank increase (0, 1, 2) of the chosen set of size d (structure at index d) bordered by the row y[0..d-1], diagonal yjj;
   *istar receives a chosen index with non-zero residual when the increase is 2 */
static inline int border(int d, const int *y, int yjj, int *istar) {
    int r = rho[d], c[5] = {0, 0, 0, 0, 0}, k, i;
    for (k = 0; k < r; k++) { int s = 0; for (i = 0; i < r; i++) s += Binv[d][k][i] * y[piv[d][i]]; c[k] = md(s); }
    for (i = 0; i < d; i++) { int s = y[i]; for (k = 0; k < r; k++) s -= Y[i][piv[d][k]] * c[k]; if (md(s)) { *istar = i; return 2; } }
    int s = yjj; for (k = 0; k < r; k++) s -= y[piv[d][k]] * c[k];
    return md(s) ? 1 : 0;
}

static void dfs(int d) {
    if (timeout || (LIMIT && nsol >= LIMIT)) return;
    if (++nodes > MAXNODES) { timeout = 1; return; }
    int n = nal[d], w, k, t, i;
    if (d == 10) {
        for (w = 0; w < 36; w++) if (dem[w]) return;
        for (k = 0; k < 10; k++) { if (!apex[chosen[k]] && partner[k] < 0) return; int s = 0; for (i = 0; i < 10; i++) s += Y[k][i]; if (md(s)) return; }
        nsol++;
        if (nsol <= 2) { printf("SOLUTION:"); for (k = 0; k < 10; k++) { printf(" ["); for (t = 0; t < 6; t++) printf("%d ", mem[chosen[k]][t]); printf("| p%d]", partner[k]); } printf("\n"); }
        return;
    }
    int cnt[36]; memset(cnt, 0, sizeof cnt);
    unsigned short have = 0;
    for (t = 0; t < n; t++) { for (k = 0; k < 6; k++) cnt[mem[al[d][t]][k]]++; have |= op[d][t]; }
    int best = -1;
    for (w = 0; w < 36; w++) if (dem[w] > 0) { if (cnt[w] < dem[w]) return; if (best < 0 || cnt[w] < cnt[best]) best = w; }
    if (best < 0) return;
    int unp = 0;
    for (k = 0; k < d; k++) if (!apex[chosen[k]] && partner[k] < 0) { unp++; if (!((have >> (k + 1)) & 1)) return; }
    if (unp > 10 - d) return;
    for (t = 0; t < n; t++) {
        int j = al[d][t];
        if (!((mask[j] >> best) & 1ULL)) continue;
        for (int o = 0; o <= d; o++) {
            if (!((op[d][t] >> o) & 1)) continue;
            int pa = o - 1;                                 /* partner among the chosen, or -1 */
            if (pa >= 0 && partner[pa] >= 0) continue;
            int y[10], istar = -1;
            for (i = 0; i < d; i++) y[i] = md(3 + (i == pa) - gv[d][t][i]);
            int inc = border(d, y, gd[j], &istar);
            if (rho[d] + inc > D) continue;                 /* cannot happen: options are filtered, kept as a guard */
            /* choose (j, pa) */
            for (k = 0; k < 6; k++) if (mem[j][k] != U) dem[mem[j][k]]--;
            chosen[d] = j; partner[d] = pa; if (pa >= 0) partner[pa] = d;
            for (i = 0; i < d; i++) Y[d][i] = Y[i][d] = y[i];
            Y[d][d] = gd[j];
            rho[d + 1] = rho[d] + inc; memcpy(piv[d + 1], piv[d], sizeof piv[d]); memcpy(Binv[d + 1], Binv[d], sizeof Binv[d]);
            if (inc) {
                /* new principal block: old pivots, plus d (inc = 1) or istar and d (inc = 2); it is invertible */
                int r0 = rho[d], r1 = rho[d + 1], M[5][10], aa, bb, ee;
                if (inc == 2) piv[d + 1][r0] = istar;
                piv[d + 1][r1 - 1] = d;
                for (aa = 0; aa < r1; aa++) for (bb = 0; bb < r1; bb++) { M[aa][bb] = Y[piv[d + 1][aa]][piv[d + 1][bb]]; M[aa][r1 + bb] = (aa == bb); }
                for (aa = 0; aa < r1; aa++) {
                    int p = -1; for (bb = aa; bb < r1; bb++) if (M[bb][aa]) { p = bb; break; }
                    if (p < 0) { fprintf(stderr, "singular pivot block\n"); exit(6); }
                    if (p != aa) for (bb = 0; bb < 2 * r1; bb++) { int tt = M[aa][bb]; M[aa][bb] = M[p][bb]; M[p][bb] = tt; }
                    int iv = inv7[M[aa][aa]]; for (bb = 0; bb < 2 * r1; bb++) M[aa][bb] = md(M[aa][bb] * iv);
                    for (ee = 0; ee < r1; ee++) if (ee != aa && M[ee][aa]) { int fct = M[ee][aa]; for (bb = 0; bb < 2 * r1; bb++) M[ee][bb] = md(M[ee][bb] - fct * M[aa][bb]); }
                }
                for (aa = 0; aa < r1; aa++) for (bb = 0; bb < r1; bb++) Binv[d + 1][aa][bb] = M[aa][r1 + bb];
            }
            /* filter the alive candidates */
            int m = 0, s;
            for (s = 0; s < n; s++) {
                int q = al[d][s];
                if (q == j || mask[q] == mask[j]) continue;
                int okd = 1; for (k = 0; k < 6; k++) if (mem[q][k] != U && dem[mem[q][k]] <= 0) { okd = 0; break; }
                if (!okd) continue;
                int inter = __builtin_popcountll(mask[q] & mask[j]);
                int g = hs[q]; for (k = 0; k < 6; k++) g += hv[q][mem[j][k]];
                g = md(g);
                unsigned short oo = op[d][s], no = 0;
                int yy[11], is2;
                for (i = 0; i < d; i++) yy[i] = md(3 - gv[d][s][i]);
                /* old options (not adjacent to the new member): need intersection <= 2 */
                if (inter <= 2) {
                    yy[d] = md(3 - g);
                    for (int o2 = 0; o2 <= d; o2++) {
                        if (!((oo >> o2) & 1)) continue;
                        int p2 = o2 - 1;
                        if (p2 >= 0 && partner[p2] >= 0) continue;
                        if (p2 >= 0) yy[p2] = md(yy[p2] + 1);
                        int in2 = border(d + 1, yy, gd[q], &is2);
                        if (p2 >= 0) yy[p2] = md(yy[p2] - 1);
                        if (rho[d + 1] + in2 <= D) no |= (unsigned short)(1 << o2);
                    }
                }
                /* new option: adjacent to the new member */
                if ((oo & 1) && inter == 1 && !apex[q] && !apex[j] && pa < 0) {
                    yy[d] = md(4 - g);
                    int in2 = border(d + 1, yy, gd[q], &is2);
                    if (rho[d + 1] + in2 <= D) no |= (unsigned short)(1 << (d + 1));
                }
                if (!no) continue;
                al[d + 1][m] = q; op[d + 1][m] = no;
                memcpy(gv[d + 1][m], gv[d][s], 10); gv[d + 1][m][d] = (signed char)g;
                m++;
            }
            nal[d + 1] = m;
            dfs(d + 1);
            if (pa >= 0) partner[pa] = -1;
            for (k = 0; k < 6; k++) if (mem[j][k] != U) dem[mem[j][k]]++;
            if (timeout || (LIMIT && nsol >= LIMIT)) return;
        }
    }
}

static void add_candidate(const int *n) {
    int k, z, cnt[6] = {0, 0, 0, 0, 0, 0}; unsigned long long m = 0;
    for (k = 0; k < 6; k++) { cnt[comp[n[k]]]++; m |= 1ULL << n[k]; }
    for (k = 0; k < NCOMP; k++) if (cnt[k] != quota[k]) return;
    for (k = 0; k < 6; k++) if (__builtin_popcountll(amask[n[k]] & m) > 1) return;
    for (z = 0; z < 36; z++) if (!((m >> z) & 1ULL) && __builtin_popcountll(amask[z] & m) > 2) return;
    for (k = 0; k < 6; k++) for (z = k + 1; z < 6; z++) if (K[n[k]][n[z]] == 0) return;
    for (k = 0; k < NT; k++) { int sv = 0; for (z = 0; z < 6; z++) sv += TV[k][n[z]]; if (sv % 7) return; }
    if (NC >= MAXC) { fprintf(stderr, "too many candidates\n"); exit(5); }
    int hsum = 0, g;
    for (z = 0; z < 36; z++) { int s = 0; for (k = 0; k < 6; k++) s += Gm[n[k]][z]; for (k = 0; k < 36; k++) s += 3 * Gm[k][z]; hv[NC][z] = (signed char)(s % 7); hsum += s % 7; }
    hsum = (3 * hsum) % 7; g = hsum; for (k = 0; k < 6; k++) g += hv[NC][n[k]];
    for (k = 0; k < 6; k++) mem[NC][k] = n[k];
    mask[NC] = m; hs[NC] = (signed char)hsum; gd[NC] = (signed char)md(-g);
    int ap = 0; for (k = 0; k < 3; k++) if (lay[adj[U][k]] != lay[U] && ((m >> adj[U][k]) & 1ULL)) ap = 1;
    apex[NC] = (signed char)ap;
    NC++;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int i, j, k;
    if (!f) return 2;
    if (fscanf(f, "%d %d %d %d %d %lld", &U, &D, &NCOMP, &NT, &LIMIT, &MAXNODES) != 6) return 3;
    if (D > 5 || NT > 4) { fprintf(stderr, "D <= 5 and NT <= 4 only\n"); return 4; }
    for (k = 0; k < NCOMP; k++) fscanf(f, "%d", &quota[k]);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &lay[k]);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &comp[k]);
    for (i = 0; i < 36; i++) { amask[i] = 0; for (k = 0; k < 3; k++) { fscanf(f, "%d", &adj[i][k]); amask[i] |= 1ULL << adj[i][k]; } }
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &K[i][j]);
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &Gm[i][j]);
    for (k = 0; k < NT; k++) for (i = 0; i < 36; i++) if (fscanf(f, "%d", &TV[k][i]) != 1) return 7;
    fclose(f);
    mem = malloc(sizeof(int[6]) * MAXC); hv = malloc(sizeof(signed char[36]) * MAXC); mask = malloc(8 * MAXC);
    apex = malloc(MAXC); hs = malloc(MAXC); gd = malloc(MAXC);
    int L[3][12], nl[3] = {0, 0, 0}, mate[36];
    for (i = 0; i < 36; i++) { L[lay[i]][nl[lay[i]]++] = i; for (k = 0; k < 3; k++) if (lay[adj[i][k]] == lay[i]) mate[i] = adj[i][k]; }
    int lu = lay[U], o1 = (lu == 0) ? 1 : 0, o2 = (lu == 2) ? 1 : 2, n[6];
    for (int a = 0; a < 12; a++) {
        int va = L[lu][a]; if (va == U || K[U][va] == 0) continue;
        for (int b1 = 0; b1 < 12; b1++) for (int b2 = b1 + 1; b2 < 12; b2++) {
            int x1 = L[o1][b1], x2 = L[o1][b2]; if (mate[x1] == x2 || K[U][x1] == 0 || K[U][x2] == 0) continue;
            for (int c1 = 0; c1 < 12; c1++) for (int c2 = c1 + 1; c2 < 12; c2++) {
                int y1 = L[o2][c1], y2 = L[o2][c2]; if (mate[y1] == y2 || K[U][y1] == 0 || K[U][y2] == 0) continue;
                n[0] = U; n[1] = va; n[2] = x1; n[3] = x2; n[4] = y1; n[5] = y2;
                add_candidate(n);
            }
        }
    }
    for (k = 0; k < 36; k++) dem[k] = K[U][k]; dem[U] = 0;
    for (k = 0; k < 12; k++) { al[k] = malloc(sizeof(int) * (NC + 1)); op[k] = malloc(sizeof(unsigned short) * (NC + 1)); gv[k] = malloc(sizeof(signed char[10]) * (NC + 1)); }
    int m = 0;
    for (i = 0; i < NC; i++) {
        /* a single shadow: rank of the 1 x 1 matrix (gd) must be <= D: always true for D >= 1 */
        al[0][m] = i; op[0][m] = 1; m++;
    }
    nal[0] = m; rho[0] = 0;
    dfs(0);
    printf("cands %d nodes %lld solutions %d timeout %d\n", NC, nodes, nsol, timeout);
    return 0;
}
