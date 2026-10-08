/* Balanced torsion of ranks (a, b), a <= b <= 3: the balanced vectors are the graph of an injective linear map from the
   torsion space of the first component (dimension a) to that of the second (dimension b), i.e. every shadow n satisfies
        sigma1(n)_k + sum_l M[k][l] sigma2(n)_l = 0     (k < a),   M an a x b matrix of rank a over F_7.
   For every such M: keep the candidate shadows through u satisfying it and look for ten of them with sum = dem and
   pairwise intersections <= 2 (necessary, purely combinatorial).  Writes the codes of the matrices that pass.
   usage: thetaAB inst a b out [list]   (with a list of codes, only those are tested: intersection over several vertices)
   Input: ncand u / dem[36] / per candidate: 6 members, s1, s2 (coordinates packed in base 7). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int NC, U, dem[36], mem[20000][6], s1[20000], s2[20000]; static unsigned long long mask[20000];
static int *bucket[343][343], bsize[343][343];
static int kept[20000], nk;

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

static int rank_ok(int a, int b, int M[3][3]) {
    /* rank of the a x b matrix equals a ? */
    int A[3][3], i, j, r = 0, c;
    for (i = 0; i < a; i++) for (j = 0; j < b; j++) A[i][j] = M[i][j];
    for (c = 0; c < b && r < a; c++) {
        int p = -1; for (i = r; i < a; i++) if (A[i][c] % 7) { p = i; break; }
        if (p < 0) continue;
        for (j = 0; j < b; j++) { int t = A[r][j]; A[r][j] = A[p][j]; A[p][j] = t; }
        int inv = 1; while ((A[r][c] * inv) % 7 != 1) inv++;
        for (j = 0; j < b; j++) A[r][j] = (A[r][j] * inv) % 7;
        for (i = 0; i < a; i++) if (i != r && A[i][c] % 7) { int f = A[i][c]; for (j = 0; j < b; j++) A[i][j] = ((A[i][j] - f * A[r][j]) % 7 + 7) % 7; }
        r++;
    }
    return r == a;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int a = atoi(argv[2]), b = atoi(argv[3]), i, k, x, y;
    if (!f) return 2;
    FILE *out = fopen(argv[4], "w"), *lf = argc > 5 ? fopen(argv[5], "r") : NULL;
    fscanf(f, "%d %d", &NC, &U);
    for (k = 0; k < 36; k++) fscanf(f, "%d", &dem[k]);
    for (i = 0; i < NC; i++) { mask[i] = 0; for (k = 0; k < 6; k++) { fscanf(f, "%d", &mem[i][k]); mask[i] |= 1ULL << mem[i][k]; } fscanf(f, "%d %d", &s1[i], &s2[i]); }
    fclose(f);
    for (i = 0; i < NC; i++) bsize[s2[i]][s1[i]]++;
    for (x = 0; x < 343; x++) for (y = 0; y < 343; y++) { bucket[x][y] = bsize[x][y] ? malloc(sizeof(int) * bsize[x][y]) : NULL; bsize[x][y] = 0; }
    for (i = 0; i < NC; i++) bucket[s2[i]][s1[i]][bsize[s2[i]][s1[i]]++] = i;
    long long total = 1, nM = 0, pass = 0, found = 0; for (k = 0; k < a * b; k++) total *= 7;
    int nb = 1; for (k = 0; k < b; k++) nb *= 7;
    long long code = -1;
    while (1) {
        if (lf) { if (fscanf(lf, "%lld", &code) != 1) break; } else { code++; if (code >= total) break; }
        int M[3][3] = {{0}}, c = (int)code, d[9];
        for (k = 0; k < a * b; k++) { d[k] = c % 7; c /= 7; }
        for (i = 0; i < a; i++) for (k = 0; k < b; k++) M[i][k] = d[i * b + k];
        if (!rank_ok(a, b, M)) continue;
        nM++; nk = 0;
        for (x = 0; x < nb; x++) {
            int xs[3] = {x % 7, (x / 7) % 7, x / 49}, t = 0, mul = 1;
            for (i = 0; i < a; i++) { int v = 0; for (k = 0; k < b; k++) v += M[i][k] * xs[k]; t += ((7 - v % 7) % 7) * mul; mul *= 7; }
            int sz = bsize[x][t];
            for (k = 0; k < sz; k++) kept[nk++] = bucket[x][t][k];
        }
        if (nk < 10) continue;
        int cnt[36]; memset(cnt, 0, sizeof cnt);
        for (i = 0; i < nk; i++) for (k = 0; k < 6; k++) cnt[mem[kept[i]][k]]++;
        int ok = 1; for (k = 0; k < 36; k++) if (dem[k] > 0 && cnt[k] < dem[k]) { ok = 0; break; }
        if (!ok) continue;
        pass++;
        if (cover(0, kept, nk)) { found++; fprintf(out, "%lld\n", code); }
    }
    fclose(out);
    printf("matrices of rank %d tested %lld, passing the coverage count %lld, with a combinatorial family %lld\n", a, nM, pass, found);
    return 0;
}
