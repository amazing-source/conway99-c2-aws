/* Case (3,3): both components have 7-torsion of rank 3.  At rank 37 the balanced torsion must be the graph of an
   isomorphism theta: E_1 -> E_2, i.e. every shadow n satisfies sigma1(n) + M sigma2(n) = 0 with M in GL_3(F_7)
   (sigma_i(n) = the three phi-sums of n on component i).  For every M this program keeps the candidate shadows through u
   that satisfy the condition and looks for ten of them with sum = dem and pairwise intersections <= 2 (a necessary,
   purely combinatorial condition).  Prints the number of M with at least one such family.
   Input: ncand u / dem[36] / per candidate: 6 members, s1, s2 (coordinates packed in base 7). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int NC, U, dem[36], mem[20000][6], s1[20000], s2[20000]; static unsigned long long mask[20000];
static int *bucket[343][343], bsize[343][343];
static int kept[20000], nk, chosen[10]; static long long found = 0;

static int cover(int depth, int *al, int n) {
    int w, k, t, cnt[36];
    if (depth == 10) { for (w = 0; w < 36; w++) if (dem[w]) return 0; return 1; }
    memset(cnt, 0, sizeof cnt);
    for (t = 0; t < n; t++) for (k = 0; k < 6; k++) cnt[mem[al[t]][k]]++;
    int best = -1;
    for (w = 0; w < 36; w++) if (dem[w] > 0) { if (cnt[w] < dem[w]) return 0; if (best < 0 || cnt[w] < cnt[best]) best = w; }
    if (best < 0) return 0;
    int *nal = malloc(sizeof(int) * (n + 1)), res = 0;
    for (t = 0; t < n && !res; t++) {
        int i = al[t];
        if (!((mask[i] >> best) & 1ULL)) continue;
        for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]--;
        int m = 0, s;
        for (s = 0; s < n; s++) {
            int j = al[s];
            if (j == i || mask[j] == mask[i]) continue;
            if (__builtin_popcountll(mask[i] & mask[j]) > 2) continue;
            int okd = 1; for (k = 0; k < 6; k++) if (mem[j][k] != U && dem[mem[j][k]] <= 0) { okd = 0; break; }
            if (okd) nal[m++] = j;
        }
        res = cover(depth + 1, nal, m);
        for (k = 0; k < 6; k++) if (mem[i][k] != U) dem[mem[i][k]]++;
    }
    free(nal);
    return res;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int i, k, a, b;
    if (!f) return 2;
    fscanf(f, "%d %d", &NC, &U);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &dem[k]);
    for (i = 0; i < NC; i++) { mask[i] = 0; for (k = 0; k < 6; k++) { fscanf(f, "%d", &mem[i][k]); mask[i] |= 1ULL << mem[i][k]; } fscanf(f, "%d %d", &s1[i], &s2[i]); }
    fclose(f);
    for (i = 0; i < NC; i++) bsize[s2[i]][s1[i]]++;
    for (a = 0; a < 343; a++) for (b = 0; b < 343; b++) { bucket[a][b] = bsize[a][b] ? malloc(sizeof(int) * bsize[a][b]) : NULL; bsize[a][b] = 0; }
    for (i = 0; i < NC; i++) bucket[s2[i]][s1[i]][bsize[s2[i]][s1[i]]++] = i;
    long long nM = 0, passcount = 0; int m[9], maxkept = 0;
    for (int code = 0; code < 40353607; code++) {
        int c = code; for (k = 0; k < 9; k++) { m[k] = c % 7; c /= 7; }
        int det = m[0] * (m[4] * m[8] - m[5] * m[7]) - m[1] * (m[3] * m[8] - m[5] * m[6]) + m[2] * (m[3] * m[7] - m[4] * m[6]);
        if (((det % 7) + 7) % 7 == 0) continue;
        nM++; nk = 0;
        for (a = 0; a < 343; a++) {
            int x0 = a % 7, x1 = (a / 7) % 7, x2 = a / 49;
            int y0 = (7 - (m[0] * x0 + m[1] * x1 + m[2] * x2) % 7) % 7, y1 = (7 - (m[3] * x0 + m[4] * x1 + m[5] * x2) % 7) % 7, y2 = (7 - (m[6] * x0 + m[7] * x1 + m[8] * x2) % 7) % 7;
            int t = y0 + 7 * y1 + 49 * y2, sz = bsize[a][t];
            for (k = 0; k < sz; k++) kept[nk++] = bucket[a][t][k];
        }
        if (nk > maxkept) maxkept = nk;
        if (nk < 10) continue;
        int cnt[36]; memset(cnt, 0, sizeof cnt);
        for (i = 0; i < nk; i++) for (k = 0; k < 6; k++) cnt[mem[kept[i]][k]]++;
        int ok = 1; for (k = 0; k < 36; k++) if (dem[k] > 0 && cnt[k] < dem[k]) { ok = 0; break; }
        if (!ok) continue;
        passcount++;
        if (cover(0, kept, nk)) { found++; if (found <= 3) { printf("M with a combinatorial family:"); for (k = 0; k < 9; k++) printf(" %d", m[k]); printf("  (%d candidates)\n", nk); } }
    }
    printf("matrices %lld, passing the coverage count %lld, with a combinatorial family %lld, largest candidate set %d\n", nM, passcount, found, maxkept);
    return 0;
}
