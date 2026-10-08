/* Exhaustive search for a complete star in a (6,6) ball at rank 37 (rank-one residue), see star66.py for the statement.
   Input (text): nitems u c0 use_real limit maxnodes / dem[36] / per item: 6 members, xi, apex, 36 hv mod 7, e, 36 real hv.
   Conditions: sum of the ten shadows = dem (+10 at u); pairs: v = g'(i,j) - 3 - c0 xi_i xi_j mod 7 must be 0 (non-adjacent,
   intersection <= 2) or 6 (adjacent: intersection = {u}, no apex, at most one partner each); every non-apex member has
   exactly one partner; sum of xi = 0 mod 7; optional real pair inequality |1/12 - a - eps| <= sqrt((B-e_i)(B-e_j)). */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define MAXI 40000
static int NI, U, C0, USE_REAL, LIMIT; static long long MAXNODES;
static int dem[36];
static int mem[MAXI][6], xi[MAXI], apex[MAXI]; static signed char hv[MAXI][36];
static double en[MAXI], hvr[MAXI][36]; static unsigned long long mask[MAXI];
static int *alive[12], *tie[12]; static int nalive[12];
static int chosen[10], partner[10]; static long long nodes = 0; static int nsol = 0, timeout = 0;
static const double B = 37.0 / 12.0;

static int rel(int i, int j) { /* -1 incompatible, 0 non-adjacent, 1 adjacent */
    int s = 0, k; for (k = 0; k < 6; k++) s += hv[i][mem[j][k]];
    int v = ((s - 3 - C0 * xi[i] * xi[j]) % 7 + 7) % 7;
    int inter = __builtin_popcountll(mask[i] & mask[j]);
    int a;
    if (v == 0) { if (inter > 2) return -1; a = 0; }
    else if (v == 6) { if (inter != 1 || apex[i] || apex[j]) return -1; a = 1; }
    else return -1;
    if (USE_REAL) {
        double eps = 0; for (k = 0; k < 6; k++) eps += hvr[i][mem[j][k]];
        double lhs = 1.0 / 12.0 - a - eps, rhs2 = (B - en[i]) * (B - en[j]);
        if (lhs * lhs > rhs2 + 1e-9) return -1;
    }
    return a;
}

static void dfs(int depth, int signfixed) {
    if (timeout || (LIMIT && nsol >= LIMIT)) return;
    if (++nodes > MAXNODES) { timeout = 1; return; }
    int *al = alive[depth], *ti = tie[depth], n = nalive[depth], w, k, t;
    if (depth == 10) {
        for (w = 0; w < 36; w++) if (dem[w]) return;
        int s = 0; for (k = 0; k < 10; k++) { s += xi[chosen[k]]; if (!apex[chosen[k]] && partner[k] < 0) return; }
        if (s % 7) return;
        nsol++;
        if (nsol <= 3) { printf("SOLUTION:"); for (k = 0; k < 10; k++) { printf(" ["); for (t = 0; t < 6; t++) printf("%d ", mem[chosen[k]][t]); printf("| xi %d]", xi[chosen[k]]); } printf("\n"); }
        return;
    }
    int cnt[36]; memset(cnt, 0, sizeof cnt);
    for (t = 0; t < n; t++) for (k = 0; k < 6; k++) cnt[mem[al[t]][k]]++;
    int best = -1;
    for (w = 0; w < 36; w++) if (dem[w] > 0) { if (cnt[w] < dem[w]) return; if (best < 0 || cnt[w] < cnt[best]) best = w; }
    if (best < 0) return;
    /* unpartnered chosen non-apex members need distinct future partners that are still alive */
    int unp = 0; char has[10]; memset(has, 0, sizeof has);
    for (t = 0; t < n; t++) if (ti[t] >= 0) has[ti[t]] = 1;
    for (k = 0; k < depth; k++) if (!apex[chosen[k]] && partner[k] < 0) { unp++; if (!has[k]) return; }
    if (unp > 10 - depth) return;
    int *nal = alive[depth + 1], *nti = tie[depth + 1];
    for (t = 0; t < n; t++) {
        int i = al[t], a = ti[t];
        if (!((mask[i] >> best) & 1ULL)) continue;
        if (!signfixed && xi[i] > 3) continue;
        if (a >= 0 && partner[a] >= 0) continue;
        for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]--;
        chosen[depth] = i; partner[depth] = a; if (a >= 0) partner[a] = depth;
        int m = 0, s;
        for (s = 0; s < n; s++) {
            int j = al[s], b = ti[s];
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
        dfs(depth + 1, signfixed || xi[i] != 0);
        if (a >= 0) partner[a] = -1;
        for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]++;
        if (timeout || (LIMIT && nsol >= LIMIT)) return;
    }
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int i, k, t;
    if (!f) return 2;
    if (fscanf(f, "%d %d %d %d %d %lld", &NI, &U, &C0, &USE_REAL, &LIMIT, &MAXNODES) != 6) return 3;
    for (k = 0; k < 36; k++) fscanf(f, "%d", &dem[k]);
    for (i = 0; i < NI; i++) {
        mask[i] = 0;
        for (k = 0; k < 6; k++) { fscanf(f, "%d", &mem[i][k]); mask[i] |= 1ULL << mem[i][k]; }
        fscanf(f, "%d %d", &xi[i], &apex[i]);
        for (k = 0; k < 36; k++) { fscanf(f, "%d", &t); hv[i][k] = (signed char)t; }
        fscanf(f, "%lf", &en[i]);
        for (k = 0; k < 36; k++) fscanf(f, "%lf", &hvr[i][k]);
    }
    fclose(f);
    for (k = 0; k < 12; k++) { alive[k] = malloc(sizeof(int) * (NI + 1)); tie[k] = malloc(sizeof(int) * (NI + 1)); }
    int m = 0;
    for (i = 0; i < NI; i++) { if (USE_REAL && en[i] > B + 1e-9) continue; alive[0][m] = i; tie[0][m] = -1; m++; }
    nalive[0] = m;
    dfs(0, 0);
    printf("items %d (alive at root %d) nodes %lld solutions %d timeout %d\n", NI, m, nodes, nsol, timeout);
    return 0;
}
