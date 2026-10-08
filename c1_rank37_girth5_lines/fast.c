/* Fast exhaustive star search at rank 37 for a disconnected, triangle-free, torsion-free ball (any number of
   components).  Everything heavy is done here: candidate shadows, scalars, search.
   Model (see NOTE.md of c1_rank37_girth5_lines): g(i,j) = (3 + n_i)^T Gm (3 + n_j) with Gm = (M0 + Z Z^T)^(-1) mod 7,
   far vertex = shadow + nu in N0 (dimension = components - 1, form C0 x^2 + C1 y^2):
       g(i,i) + q(nu_i) = 0,   g(i,j) + b(nu_i,nu_j) = 3 + A_ij,   sum of nu over the star = 0.
   Optional real filter (valid at every rank): e_i = n_i^T H^+ n_i <= 37/12 and
       (1/12 - A_ij - n_i^T H^+ n_j)^2 <= (37/12 - e_i)(37/12 - e_j).
   Input: u C0 C1 ncomp use_real limit maxnodes / quota[ncomp] / lay[36] / comp[36] / adj[36][3] / K[36][36] /
          Gm[36][36] / Hr[36][36] (doubles). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXI 600000
static int U, C0, C1, NCOMP, USE_REAL, LIMIT; static long long MAXNODES;
static int quota[6], lay[36], comp[36], adj[36][3], K[36][36], Gm[36][36]; static double Hr[36][36];
static unsigned long long amask[36];
static int NI = 0, NCAND = 0;
static int (*mem)[6]; static signed char *nu1, *nu2, *apex, *hs; static signed char (*hv)[36];
static double *en; static float (*hvr)[36]; static unsigned long long *mask;
static int dem[36], *alive[12], *tie[12], nalive[12], chosen[10], partner[10];
static long long nodes = 0; static int nsol = 0, timeout = 0;
static const double B = 37.0 / 12.0, TOL = 1e-6;

static inline int rel(int i, int j) {
    int s = hs[i], k; for (k = 0; k < 6; k++) s += hv[i][mem[j][k]];
    s += C0 * nu1[i] * nu1[j] + C1 * nu2[i] * nu2[j] - 3;
    int v = ((s % 7) + 7) % 7, a;
    int inter = __builtin_popcountll(mask[i] & mask[j]);
    if (v == 0) { if (inter > 2) return -1; a = 0; }
    else if (v == 1) { if (inter != 1 || apex[i] || apex[j]) return -1; a = 1; }
    else return -1;
    if (USE_REAL) {
        double eps = 0; for (k = 0; k < 6; k++) eps += hvr[i][mem[j][k]];
        double lhs = 1.0 / 12.0 - a - eps;
        if (lhs * lhs > (B - en[i]) * (B - en[j]) + TOL) return -1;
    }
    return a;
}

static void dfs(int depth, int signfixed) {
    if (timeout || (LIMIT && nsol >= LIMIT)) return;
    if (++nodes > MAXNODES) { timeout = 1; return; }
    int *a_ = alive[depth], *ti = tie[depth], n = nalive[depth], w, k, t;
    if (depth == 10) {
        for (w = 0; w < 36; w++) if (dem[w]) return;
        int s1 = 0, s2 = 0;
        for (k = 0; k < 10; k++) { s1 += nu1[chosen[k]]; s2 += nu2[chosen[k]]; if (!apex[chosen[k]] && partner[k] < 0) return; }
        if (s1 % 7 || s2 % 7) return;
        nsol++;
        if (nsol <= 2) { printf("SOLUTION:"); for (k = 0; k < 10; k++) { printf(" ["); for (t = 0; t < 6; t++) printf("%d ", mem[chosen[k]][t]); printf("| %d %d]", nu1[chosen[k]], nu2[chosen[k]]); } printf("\n"); }
        return;
    }
    int cnt[36]; memset(cnt, 0, sizeof cnt);
    for (t = 0; t < n; t++) for (k = 0; k < 6; k++) cnt[mem[a_[t]][k]]++;
    int best = -1;
    for (w = 0; w < 36; w++) if (dem[w] > 0) { if (cnt[w] < dem[w]) return; if (best < 0 || cnt[w] < cnt[best]) best = w; }
    if (best < 0) return;
    int unp = 0; char has[10]; memset(has, 0, sizeof has);
    for (t = 0; t < n; t++) if (ti[t] >= 0) has[ti[t]] = 1;
    for (k = 0; k < depth; k++) if (!apex[chosen[k]] && partner[k] < 0) { unp++; if (!has[k]) return; }
    if (unp > 10 - depth) return;
    int *nal = alive[depth + 1], *nti = tie[depth + 1];
    for (t = 0; t < n; t++) {
        int i = a_[t], a = ti[t];
        if (!((mask[i] >> best) & 1ULL)) continue;
        if (!signfixed && nu1[i] > 3) continue;
        if (a >= 0 && partner[a] >= 0) continue;
        for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]--;
        chosen[depth] = i; partner[depth] = a; if (a >= 0) partner[a] = depth;
        int m = 0, s;
        for (s = 0; s < n; s++) {
            int j = a_[s], b = ti[s];
            if (j == i || mask[j] == mask[i]) continue;
            int okd = 1; for (k = 0; k < 6; k++) if (mem[j][k] != U && dem[mem[j][k]] <= 0) { okd = 0; break; }
            if (!okd) continue;
            int r = rel(j, i);
            if (r < 0) continue;
            int nb;
            if (r == 1) { if (b >= 0 || a >= 0) continue; nb = depth; }
            else { if (b >= 0 && b == a) continue; nb = b; }
            nal[m] = j; nti[m] = nb; m++;
        }
        nalive[depth + 1] = m;
        dfs(depth + 1, signfixed || nu1[i] != 0);
        if (a >= 0) partner[a] = -1;
        for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]++;
        if (timeout || (LIMIT && nsol >= LIMIT)) return;
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
    int h[36], hsum = 0, g = 0; double hr[36], e = 0;
    for (z = 0; z < 36; z++) { int s = 0; double r = 0; for (k = 0; k < 6; k++) { s += Gm[n[k]][z]; r += Hr[n[k]][z]; } for (k = 0; k < 36; k++) s += 3 * Gm[k][z]; h[z] = s % 7; hsum += h[z]; hr[z] = r; }
    hsum = (3 * hsum) % 7;
    g = hsum; for (k = 0; k < 6; k++) { g += h[n[k]]; e += hr[n[k]]; }
    g %= 7;
    if (USE_REAL && e > B + TOL) return;
    int ap = 0; for (k = 0; k < 3; k++) if (lay[adj[U][k]] != lay[U] && ((m >> adj[U][k]) & 1ULL)) ap = 1;
    for (int a = 0; a < 7; a++) for (int b = 0; b < (C1 ? 7 : 1); b++) {
        if ((g + C0 * a * a + C1 * b * b) % 7) continue;
        if (NI >= MAXI) { fprintf(stderr, "too many items\n"); exit(5); }
        for (k = 0; k < 6; k++) mem[NI][k] = n[k];
        mask[NI] = m; nu1[NI] = a; nu2[NI] = b; apex[NI] = ap; hs[NI] = hsum; en[NI] = e;
        for (z = 0; z < 36; z++) { hv[NI][z] = h[z]; hvr[NI][z] = (float)hr[z]; }
        NI++;
    }
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int i, j, k;
    if (!f) return 2;
    if (fscanf(f, "%d %d %d %d %d %d %lld", &U, &C0, &C1, &NCOMP, &USE_REAL, &LIMIT, &MAXNODES) != 7) return 3;
    for (k = 0; k < NCOMP; k++) fscanf(f, "%d", &quota[k]);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &lay[k]);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &comp[k]);
    for (i = 0; i < 36; i++) { amask[i] = 0; for (k = 0; k < 3; k++) { fscanf(f, "%d", &adj[i][k]); amask[i] |= 1ULL << adj[i][k]; } }
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &K[i][j]);
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &Gm[i][j]);
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%lf", &Hr[i][j]);
    fclose(f);
    mem = malloc(sizeof(int[6]) * MAXI); hv = malloc(sizeof(signed char[36]) * MAXI); hvr = malloc(sizeof(float[36]) * MAXI);
    mask = malloc(8 * MAXI); nu1 = malloc(MAXI); nu2 = malloc(MAXI); apex = malloc(MAXI); hs = malloc(MAXI); en = malloc(8 * MAXI);
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
    for (k = 0; k < 12; k++) { alive[k] = malloc(sizeof(int) * (NI + 1)); tie[k] = malloc(sizeof(int) * (NI + 1)); }
    for (i = 0; i < NI; i++) { alive[0][i] = i; tie[0][i] = -1; }
    nalive[0] = NI;
    dfs(0, 0);
    printf("cands %d items %d nodes %lld solutions %d timeout %d\n", NCAND, NI, nodes, nsol, timeout);
    return 0;
}
