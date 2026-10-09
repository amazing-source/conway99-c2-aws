/* Pair test for balanced torsion subspaces (combinatorial, no rank condition).
   A subspace B of the torsion space E (dimension t <= 4) is "balanced" when b(n) = 0 for every shadow n and every b in B.
   Two near points a, b with K_ab = c > 0 lie together in exactly c shadows, so at least c admissible 6-sets containing
   both must be B-balanced.  For every subspace given in the input the program says whether all pairs can be covered.
   Admissible 6-set (same conditions as the candidate lists of the star search): two points per layer, not mates, the
   prescribed number of points in each component, K > 0 for every pair, at most one G-neighbour of a member inside,
   at most two G-neighbours of an outside point inside.
   Input: t nsub d ncomp / quota[ncomp] / lay[36] / comp[36] / adj[36][3] / K[36][36] / E[t][36] / nsub blocks of d rows of t.
   Output: one line "shadows S subspaces N passing P :" followed by the indices of the passing subspaces. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
#define W 10
static int lay[36], comp[36], adj[36][3], K[36][36], E[4][36], quota[8], pid[36][36];
static u64 m1[2401][W], m2[2401][W], need1[W], need2[W];
static int used[2401];

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int t, nsub, d, ncomp, i, j, k, a, b;
    if (!f) return 2;
    if (fscanf(f, "%d %d %d %d", &t, &nsub, &d, &ncomp) != 4) return 3;
    for (i = 0; i < ncomp; i++) fscanf(f, "%d", &quota[i]);
    for (i = 0; i < 36; i++) fscanf(f, "%d", &lay[i]);
    for (i = 0; i < 36; i++) fscanf(f, "%d", &comp[i]);
    for (i = 0; i < 36; i++) for (j = 0; j < 3; j++) fscanf(f, "%d", &adj[i][j]);
    for (i = 0; i < 36; i++) for (j = 0; j < 36; j++) fscanf(f, "%d", &K[i][j]);
    for (k = 0; k < t; k++) for (i = 0; i < 36; i++) fscanf(f, "%d", &E[k][i]);
    int np = 0;
    for (a = 0; a < 36; a++) for (b = a + 1; b < 36; b++) {
        pid[a][b] = pid[b][a] = np;
        if (K[a][b] >= 1) need1[np >> 6] |= 1ULL << (np & 63);
        if (K[a][b] >= 2) need2[np >> 6] |= 1ULL << (np & 63);
        np++;
    }
    int L[3][12], nl[3] = {0, 0, 0}, A[36][36];
    memset(A, 0, sizeof A);
    for (i = 0; i < 36; i++) { L[lay[i]][nl[lay[i]]++] = i; for (j = 0; j < 3; j++) A[i][adj[i][j]] = 1; }
    if (nl[0] != 12 || nl[1] != 12 || nl[2] != 12) return 4;
    long long nsh = 0; int s[6], i0, j0, i1, j1, i2, j2;
    for (i0 = 0; i0 < 12; i0++) for (j0 = i0 + 1; j0 < 12; j0++) {
        s[0] = L[0][i0]; s[1] = L[0][j0];
        if (A[s[0]][s[1]] || K[s[0]][s[1]] == 0) continue;
        for (i1 = 0; i1 < 12; i1++) for (j1 = i1 + 1; j1 < 12; j1++) {
            s[2] = L[1][i1]; s[3] = L[1][j1];
            if (A[s[2]][s[3]]) continue;
            int ok = 1;
            for (a = 0; a < 4 && ok; a++) for (b = a + 1; b < 4; b++) if (K[s[a]][s[b]] == 0) { ok = 0; break; }
            if (!ok) continue;
            for (i2 = 0; i2 < 12; i2++) for (j2 = i2 + 1; j2 < 12; j2++) {
                s[4] = L[2][i2]; s[5] = L[2][j2];
                if (A[s[4]][s[5]]) continue;
                ok = 1;
                for (a = 0; a < 6 && ok; a++) for (b = (a < 4 ? 4 : a + 1); b < 6; b++) if (b > a && K[s[a]][s[b]] == 0) { ok = 0; break; }
                if (!ok) continue;
                int cnt[8] = {0}, in[36] = {0};
                for (a = 0; a < 6; a++) { cnt[comp[s[a]]]++; in[s[a]] = 1; }
                for (a = 0; a < ncomp; a++) if (cnt[a] != quota[a]) { ok = 0; break; }
                if (!ok) continue;
                for (a = 0; a < 36 && ok; a++) {
                    int c = in[adj[a][0]] + in[adj[a][1]] + in[adj[a][2]];
                    if (c > (in[a] ? 1 : 2)) ok = 0;
                }
                if (!ok) continue;
                nsh++;
                int code = 0, mul = 1;
                for (k = 0; k < t; k++) { int v = 0; for (a = 0; a < 6; a++) v += E[k][s[a]]; code += (v % 7) * mul; mul *= 7; }
                u64 pm[W]; memset(pm, 0, sizeof pm);
                for (a = 0; a < 6; a++) for (b = a + 1; b < 6; b++) { int p = pid[s[a]][s[b]]; pm[p >> 6] |= 1ULL << (p & 63); }
                for (k = 0; k < W; k++) { m2[code][k] |= m1[code][k] & pm[k]; m1[code][k] |= pm[k]; }
                used[code] = 1;
            }
        }
    }
    int ncode = 1; for (k = 0; k < t; k++) ncode *= 7;
    int npass = 0, *pass = malloc(sizeof(int) * (nsub + 1));
    for (i = 0; i < nsub; i++) {
        int rows[4][4];
        for (a = 0; a < d; a++) for (k = 0; k < t; k++) fscanf(f, "%d", &rows[a][k]);
        u64 g1[W], g2[W]; memset(g1, 0, sizeof g1); memset(g2, 0, sizeof g2);
        int code;
        for (code = 0; code < ncode; code++) {
            if (!used[code]) continue;
            int c = code, sg[4], ok = 1;
            for (k = 0; k < t; k++) { sg[k] = c % 7; c /= 7; }
            for (a = 0; a < d && ok; a++) { int v = 0; for (k = 0; k < t; k++) v += rows[a][k] * sg[k]; if (v % 7) ok = 0; }
            if (!ok) continue;
            for (k = 0; k < W; k++) { g2[k] |= m2[code][k] | (g1[k] & m1[code][k]); g1[k] |= m1[code][k]; }
        }
        int ok = 1;
        for (k = 0; k < W; k++) if ((need1[k] & ~g1[k]) || (need2[k] & ~g2[k])) { ok = 0; break; }
        if (ok) pass[npass++] = i;
    }
    printf("shadows %lld subspaces %d passing %d :", nsh, nsub, npass);
    for (i = 0; i < npass; i++) printf(" %d", pass[i]);
    printf("\n");
    return 0;
}
