/* Star search with the REAL conditions only (they hold at every rank, no hypothesis mod 7).
   For a line T (connected or not, c components) and far vertices f, f':
        X_ff' = 7 Pi_ff' = 3 [f = f'] - A_ff' + 1/12 - n_f^T H^+ n_f',
   where Pi is the orthogonal projector on the (-4)-eigenvectors vanishing on the ball (rank 7 + c).  So for the ten far
   neighbours of a near point u the 10 x 10 matrix X must satisfy 0 <= X <= 7 I (its row sums are 0 automatically).
   Combinatorics of a star as in fast.c: ten admissible 6-sets through u with sum K e_u, pairwise intersections <= 2,
   two apexes (isolated), eight others in four adjacent pairs meeting only in u.
   Here the adjacency of two members is not given by a congruence, so the search branches on the partner.
   Input: same file as fast.exe (Gm, C0, C1 are read and ignored).  Output: number of stars found (LIMIT stops early).
   usage: realstar inst [tol]   (tol: slack on the eigenvalue tests, default 1e-7) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define MAXI 200000
static int U, C0, C1, NCOMP, USE_REAL, LIMIT; static long long MAXNODES;
static int quota[6], lay[36], comp[36], adj[36][3], K[36][36], Gm[36][36]; static double Hr[36][36];
static unsigned long long amask[36];
static int NI = 0, NCAND = 0, NREJ = 0;
static int (*mem)[6]; static signed char *apex; static double *en; static float (*hvr)[36]; static unsigned long long *mask;
static int dem[36], *alive[12], nalive[12], chosen[10], partner[10];
static long long nodes = 0; static int nsol = 0, timeout = 0;
static const double B = 37.0 / 12.0; static double TOL = 1e-7;
static double X[10][10], L1[10][10], L2[10][10];

static inline double eps(int i, int j) { double e = 0; int k; for (k = 0; k < 6; k++) e += hvr[i][mem[j][k]]; return e; }
/* can the pair (i, j) coexist: bit 0 = as non-adjacent, bit 1 = as adjacent (2 x 2 minors only) */
static inline int pairok(int i, int j) {
    int inter = __builtin_popcountll(mask[i] & mask[j]), r = 0;
    if (inter > 2) return 0;
    double e = eps(i, j), lim = (B - en[i]) * (B - en[j]) + TOL, x0 = 1.0 / 12.0 - e, x1 = x0 - 1.0;
    if (x0 * x0 <= lim) r |= 1;
    if (inter == 1 && !apex[i] && !apex[j] && x1 * x1 <= lim) r |= 2;
    return r;
}
/* incremental Cholesky of X and of 7I - X: returns 0 if a pivot is negative */
static int chol_add(int d) {
    int j, k;
    for (int which = 0; which < 2; which++) {
        double (*L)[10] = which ? L2 : L1;
        for (j = 0; j <= d; j++) {
            double s = which ? ((j == d ? 7.0 : 0.0) - X[d][j]) : X[d][j];
            for (k = 0; k < j; k++) s -= L[d][k] * L[j][k];
            if (j < d) { L[d][j] = (L[j][j] > 1e-9) ? s / L[j][j] : 0.0; if (L[j][j] <= 1e-9 && fabs(s) > 1e-5) return 0; }
            else { if (s < -TOL) return 0; L[d][d] = s > 0 ? sqrt(s) : 0.0; }
        }
    }
    return 1;
}

static void dfs(int depth) {
    if (timeout || (LIMIT && nsol >= LIMIT)) return;
    if (++nodes > MAXNODES) { timeout = 1; return; }
    int *a_ = alive[depth], n = nalive[depth], w, k, t;
    if (depth == 10) {
        for (w = 0; w < 36; w++) if (dem[w]) return;
        for (k = 0; k < 10; k++) if (!apex[chosen[k]] && partner[k] < 0) return;
        nsol++;
        if (nsol <= 2) {
            printf("STAR:"); for (k = 0; k < 10; k++) { printf(" ["); for (t = 0; t < 6; t++) printf("%d ", mem[chosen[k]][t]); printf("| p%d]", partner[k]); } printf("\n");
            printf("  diagonal of X:"); for (k = 0; k < 10; k++) printf(" %.4f", X[k][k]); printf("\n");
        }
        return;
    }
    int cnt[36]; memset(cnt, 0, sizeof cnt);
    for (t = 0; t < n; t++) for (k = 0; k < 6; k++) cnt[mem[a_[t]][k]]++;
    int best = -1;
    for (w = 0; w < 36; w++) if (dem[w] > 0) { if (cnt[w] < dem[w]) return; if (best < 0 || cnt[w] < cnt[best]) best = w; }
    if (best < 0) return;
    int unp = 0; for (k = 0; k < depth; k++) if (!apex[chosen[k]] && partner[k] < 0) unp++;
    if (unp > 10 - depth) return;
    int *nal = alive[depth + 1];
    for (t = 0; t < n; t++) {
        int i = a_[t];
        if (!((mask[i] >> best) & 1ULL)) continue;
        int po[10], opt;
        for (k = 0; k < depth; k++) po[k] = pairok(i, chosen[k]);
        /* opt = -1: no partner among the earlier members; opt = k: partner of member k */
        for (opt = -1; opt < depth; opt++) {
            if (opt >= 0 && (apex[i] || apex[chosen[opt]] || partner[opt] >= 0 || !(po[opt] & 2))) continue;
            int ok = 1;
            for (k = 0; k < depth && ok; k++) if (k != opt && !(po[k] & 1)) ok = 0;
            if (!ok) continue;
            if (opt < 0 && !apex[i] && unp + 1 > 10 - depth - 1) continue;
            for (k = 0; k < depth; k++) { double x = 1.0 / 12.0 - (k == opt ? 1.0 : 0.0) - eps(i, chosen[k]); X[depth][k] = X[k][depth] = x; }
            X[depth][depth] = B - en[i];
            if (!chol_add(depth)) continue;
            for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]--;
            chosen[depth] = i; partner[depth] = opt; if (opt >= 0) partner[opt] = depth;
            int m = 0, s;
            for (s = 0; s < n; s++) {
                int j = a_[s];
                if (j == i || mask[j] == mask[i]) continue;
                int okd = 1; for (k = 0; k < 6; k++) if (mem[j][k] != U && dem[mem[j][k]] <= 0) { okd = 0; break; }
                if (!okd) continue;
                if (!pairok(j, i)) continue;
                nal[m++] = j;
            }
            nalive[depth + 1] = m;
            dfs(depth + 1);
            if (opt >= 0) partner[opt] = -1;
            partner[depth] = -1;
            for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]++;
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
    NCAND++;
    double hr[36], e = 0;
    for (z = 0; z < 36; z++) { double r = 0; for (k = 0; k < 6; k++) r += Hr[n[k]][z]; hr[z] = r; }
    for (k = 0; k < 6; k++) e += hr[n[k]];
    if (e > B + TOL) { NREJ++; return; }
    int ap = 0; for (k = 0; k < 3; k++) if (lay[adj[U][k]] != lay[U] && ((m >> adj[U][k]) & 1ULL)) ap = 1;
    if (NI >= MAXI) { fprintf(stderr, "too many items\n"); exit(5); }
    for (k = 0; k < 6; k++) mem[NI][k] = n[k];
    mask[NI] = m; apex[NI] = ap; en[NI] = e;
    for (z = 0; z < 36; z++) hvr[NI][z] = (float)hr[z];
    NI++;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int i, j, k;
    if (!f) return 2;
    if (argc > 2) TOL = atof(argv[2]);
    if (fscanf(f, "%d %d %d %d %d %d %lld", &U, &C0, &C1, &NCOMP, &USE_REAL, &LIMIT, &MAXNODES) != 7) return 3;
    for (k = 0; k < NCOMP; k++) fscanf(f, "%d", &quota[k]);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &lay[k]);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &comp[k]);
    for (i = 0; i < 36; i++) { amask[i] = 0; for (k = 0; k < 3; k++) { fscanf(f, "%d", &adj[i][k]); amask[i] |= 1ULL << adj[i][k]; } }
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &K[i][j]);
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &Gm[i][j]);
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%lf", &Hr[i][j]);
    fclose(f);
    mem = malloc(sizeof(int[6]) * MAXI); hvr = malloc(sizeof(float[36]) * MAXI);
    mask = malloc(8 * MAXI); apex = malloc(MAXI); en = malloc(8 * MAXI);
    int Lr[3][12], nl[3] = {0, 0, 0}, mate[36];
    for (i = 0; i < 36; i++) { Lr[lay[i]][nl[lay[i]]++] = i; for (k = 0; k < 3; k++) if (lay[adj[i][k]] == lay[i]) mate[i] = adj[i][k]; }
    int lu = lay[U], o1 = (lu == 0) ? 1 : 0, o2 = (lu == 2) ? 1 : 2, n[6];
    for (int a = 0; a < 12; a++) {
        int va = Lr[lu][a]; if (va == U || K[U][va] == 0) continue;
        for (int b1 = 0; b1 < 12; b1++) for (int b2 = b1 + 1; b2 < 12; b2++) {
            int x1 = Lr[o1][b1], x2 = Lr[o1][b2]; if (mate[x1] == x2 || K[U][x1] == 0 || K[U][x2] == 0) continue;
            for (int c1 = 0; c1 < 12; c1++) for (int c2 = c1 + 1; c2 < 12; c2++) {
                int y1 = Lr[o2][c1], y2 = Lr[o2][c2]; if (mate[y1] == y2 || K[U][y1] == 0 || K[U][y2] == 0) continue;
                n[0] = U; n[1] = va; n[2] = x1; n[3] = x2; n[4] = y1; n[5] = y2;
                add_candidate(n);
            }
        }
    }
    for (k = 0; k < 36; k++) dem[k] = K[U][k]; dem[U] = 0;
    for (k = 0; k < 12; k++) alive[k] = malloc(sizeof(int) * (NI + 1));
    for (i = 0; i < NI; i++) alive[0][i] = i;
    for (k = 0; k < 10; k++) partner[k] = -1;
    nalive[0] = NI;
    double emin = 1e9, emax = -1e9; for (i = 0; i < NI; i++) { if (en[i] < emin) emin = en[i]; if (en[i] > emax) emax = en[i]; }
    dfs(0);
    printf("cands %d over-the-bound %d items %d energy %.4f..%.4f nodes %lld stars %d timeout %d\n", NCAND, NREJ, NI, emin, emax, nodes, nsol, timeout);
    return 0;
}
