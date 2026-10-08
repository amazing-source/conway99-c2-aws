/* General exhaustive star search at rank 37 for a ball whose Gram has a radical (disconnected and/or 7-torsion).
   Each item = a shadow through u with scalars (nu1, nu2, alpha) and data s, csum3, cbeta, cv[36]:
     pair value v(i,j) = csum3_i + sum_{z in N_j} cv_i[z] - s_j cbeta_i + alpha_i s_j + alpha_j s_i
                         + C0 nu1_i nu1_j + C1 nu2_i nu2_j - 3   (mod 7)
     v = 0: non-adjacent (intersection <= 2);  v = 1: adjacent (intersection = {u}, no apex, one partner each).
   Final: sum nu1 = sum nu2 = 0, sum alpha = ALSUM (mod 7), every non-apex member has a partner, sum of shadows = dem.
   Input: nitems u C0 C1 ALSUM limit maxnodes / dem[36] / per item: 6 members, nu1 nu2 alpha s apex csum3 cbeta, cv[36]. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXI 400000
static int NI, U, C0, C1, ALSUM, LIMIT; static long long MAXNODES;
static int dem[36];
static int (*mem)[6]; static signed char *nu1, *nu2, *al, *ss, *apex, *cs3, *cb; static signed char (*cv)[36];
static unsigned long long *mask;
static int *alive[12], *tie[12]; static int nalive[12];
static int chosen[10], partner[10]; static long long nodes = 0; static int nsol = 0, timeout = 0;

static inline int rel(int i, int j) {
    int s = cs3[i], k; for (k = 0; k < 6; k++) s += cv[i][mem[j][k]];
    s += -ss[j] * cb[i] + al[i] * ss[j] + al[j] * ss[i] + C0 * nu1[i] * nu1[j] + C1 * nu2[i] * nu2[j] - 3;
    int v = ((s % 7) + 7) % 7;
    int inter = __builtin_popcountll(mask[i] & mask[j]);
    if (v == 0) return inter <= 2 ? 0 : -1;
    if (v == 1) return (inter == 1 && !apex[i] && !apex[j]) ? 1 : -1;
    return -1;
}

static void dfs(int depth, int signfixed) {
    if (timeout || (LIMIT && nsol >= LIMIT)) return;
    if (++nodes > MAXNODES) { timeout = 1; return; }
    int *a_ = alive[depth], *ti = tie[depth], n = nalive[depth], w, k, t;
    if (depth == 10) {
        for (w = 0; w < 36; w++) if (dem[w]) return;
        int s1 = 0, s2 = 0, sa = 0;
        for (k = 0; k < 10; k++) { s1 += nu1[chosen[k]]; s2 += nu2[chosen[k]]; sa += al[chosen[k]]; if (!apex[chosen[k]] && partner[k] < 0) return; }
        if (s1 % 7 || s2 % 7 || ((sa - ALSUM) % 7 + 7) % 7) return;
        nsol++;
        if (nsol <= 2) { printf("SOLUTION:"); for (k = 0; k < 10; k++) { printf(" ["); for (t = 0; t < 6; t++) printf("%d ", mem[chosen[k]][t]); printf("| %d %d %d]", nu1[chosen[k]], nu2[chosen[k]], al[chosen[k]]); } printf("\n"); }
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

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int i, k, t, x[7];
    if (!f) return 2;
    if (fscanf(f, "%d %d %d %d %d %d %lld", &NI, &U, &C0, &C1, &ALSUM, &LIMIT, &MAXNODES) != 7) return 3;
    if (NI > MAXI) return 4;
    mem = malloc(sizeof(int[6]) * (NI + 1)); cv = malloc(sizeof(signed char[36]) * (NI + 1)); mask = malloc(8 * (NI + 1));
    nu1 = malloc(NI + 1); nu2 = malloc(NI + 1); al = malloc(NI + 1); ss = malloc(NI + 1); apex = malloc(NI + 1); cs3 = malloc(NI + 1); cb = malloc(NI + 1);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &dem[k]);
    for (i = 0; i < NI; i++) {
        mask[i] = 0;
        for (k = 0; k < 6; k++) { fscanf(f, "%d", &mem[i][k]); mask[i] |= 1ULL << mem[i][k]; }
        for (k = 0; k < 7; k++) fscanf(f, "%d", &x[k]);
        nu1[i] = x[0]; nu2[i] = x[1]; al[i] = x[2]; ss[i] = x[3]; apex[i] = x[4]; cs3[i] = x[5]; cb[i] = x[6];
        for (k = 0; k < 36; k++) { fscanf(f, "%d", &t); cv[i][k] = (signed char)t; }
    }
    fclose(f);
    for (k = 0; k < 12; k++) { alive[k] = malloc(sizeof(int) * (NI + 1)); tie[k] = malloc(sizeof(int) * (NI + 1)); }
    for (i = 0; i < NI; i++) { alive[0][i] = i; tie[0][i] = -1; }
    nalive[0] = NI;
    dfs(0, 0);
    printf("items %d nodes %lld solutions %d timeout %d\n", NI, nodes, nsol, timeout);
    return 0;
}
