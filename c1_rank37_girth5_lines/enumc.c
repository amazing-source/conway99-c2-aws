/* Enumerates the triangle-free components with m lines per layer (m = 2, 3, 4) in the normal form
   (iota, t1, t2, pi) on 0..2m-1 of comp66.py, iota = (01)(23)...; keeps one representative per orbit of the centraliser
   of iota acting by simultaneous conjugation (= one per isomorphism type with ORDERED layers), i.e. the keys that are
   lexicographically minimal among their conjugates.  Conditions: cubic, connected, no triangle, at most two common
   neighbours for non-adjacent vertices.  Output lines: t1 t2 pi (2m numbers each) flagI flag4
     flagI = 1 if there is a 4-cycle of type I (mate, transversal, mate, transversal), flag4 = 1 if there is any 4-cycle.
   usage: enumc m outfile [onlyP0]     (onlyP0 = 1 keeps only the components without type-I 4-cycle) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int m, n, N;
static int nm = 0, mt[105][8];
static int ncent = 0, cent[384][8], centinv[384][8];
static int iota[8];

static void gen_match(int *cur, int used) {
    int i, j;
    for (i = 0; i < n; i++) if (!((used >> i) & 1)) break;
    if (i == n) { memcpy(mt[nm++], cur, sizeof(int) * 8); return; }
    for (j = i + 1; j < n; j++) if (!((used >> j) & 1)) { cur[i] = j; cur[j] = i; gen_match(cur, used | (1 << i) | (1 << j)); }
}
static void gen_cent(int *p, int k, int used) {
    if (k == n) { int i, ok = 1; for (i = 0; i < n; i++) if (p[iota[i]] != iota[p[i]]) ok = 0; if (ok) { memcpy(cent[ncent], p, sizeof(int) * 8); for (i = 0; i < n; i++) centinv[ncent][p[i]] = i; ncent++; } return; }
    for (int v = 0; v < n; v++) if (!((used >> v) & 1)) { p[k] = v; gen_cent(p, k + 1, used | (1 << v)); }
}

int main(int argc, char **argv) {
    m = atoi(argv[1]); n = 2 * m; N = 3 * n;
    FILE *out = fopen(argv[2], "w"); int onlyP0 = argc > 3 ? atoi(argv[3]) : 0;
    int cur[8], i, j, k;
    for (i = 0; i < n; i++) iota[i] = i ^ 1;
    gen_match(cur, 0);
    int p[8]; gen_cent(p, 0, 0);
    long long total = 0, kept = 0, nI = 0, n4 = 0;
    int pi[8], c[8];
    for (int a = 0; a < nm; a++) for (int b = 0; b < nm; b++) {
        int *t1 = mt[a], *t2 = mt[b];
        for (i = 0; i < n; i++) { pi[i] = i; c[i] = 0; }
        int first = 1;
        while (1) {
            if (!first) {            /* Heap's algorithm, next permutation */
                i = 1;
                while (i < n) {
                    if (c[i] < i) { int s = (i % 2 == 0) ? 0 : c[i]; int tmp = pi[s]; pi[s] = pi[i]; pi[i] = tmp; c[i]++; break; }
                    else { c[i] = 0; i++; }
                }
                if (i >= n) break;
            }
            first = 0;
            /* adjacency as bitmasks */
            unsigned int ad[24];
            for (i = 0; i < n; i++) {
                ad[i] = (1u << iota[i]) | (1u << (n + i)) | (1u << (2 * n + i));
                ad[n + i] = (1u << (n + t1[i])) | (1u << i) | (1u << (2 * n + pi[i]));
            }
            for (i = 0; i < n; i++) ad[2 * n + i] = (1u << (2 * n + t2[i])) | (1u << i);
            for (i = 0; i < n; i++) ad[2 * n + pi[i]] |= (1u << (n + i));
            int ok = 1, f4 = 0;
            for (i = 0; i < N && ok; i++) for (j = i + 1; j < N; j++) {
                int cm = __builtin_popcount(ad[i] & ad[j]);
                if ((ad[i] >> j) & 1) { if (cm) { ok = 0; break; } }
                else { if (cm > 2) { ok = 0; break; } if (cm == 2) f4 = 1; }
            }
            if (!ok) continue;
            unsigned int seen = 1, fr = 1;
            while (fr) { unsigned int nx = 0; for (i = 0; i < N; i++) if ((fr >> i) & 1) nx |= ad[i]; fr = nx & ~seen; seen |= nx; }
            if (seen != ((N == 32) ? 0xffffffffu : ((1u << N) - 1))) continue;
            total++;
            /* type I: mates w, x in a layer, mates y, z in another layer, w ~ y and x ~ z */
            int fI = 0;
            for (i = 0; i < n && !fI; i++) {
                /* layer 0 point i with mate iota[i]; its neighbours i^1 (layer 1) and i^2 (layer 2) */
                if (t1[i] == iota[i]) fI = 1;              /* i^0 ~ i^1, iota(i)^0 ~ iota(i)^1, and i^1, iota(i)^1 mates */
                if (t2[i] == iota[i]) fI = 1;
                if (t2[pi[i]] == pi[t1[i]]) fI = 1;        /* i^1 ~ pi(i)^2, t1(i)^1 ~ pi(t1 i)^2, mates in both layers */
            }
            if (fI) nI++;
            if (f4) n4++;
            if (onlyP0 && fI) continue;
            /* canonical under the centraliser */
            int minimal = 1;
            for (k = 1; k < ncent && minimal; k++) {
                int *s = cent[k], *si = centinv[k], cmp = 0;
                for (i = 0; i < n && !cmp; i++) { int v = s[t1[si[i]]]; cmp = (v < t1[i]) ? -1 : (v > t1[i]) ? 1 : 0; }
                for (i = 0; i < n && !cmp; i++) { int v = s[t2[si[i]]]; cmp = (v < t2[i]) ? -1 : (v > t2[i]) ? 1 : 0; }
                for (i = 0; i < n && !cmp; i++) { int v = s[pi[si[i]]]; cmp = (v < pi[i]) ? -1 : (v > pi[i]) ? 1 : 0; }
                if (cmp < 0) minimal = 0;
            }
            if (!minimal) continue;
            kept++;
            for (i = 0; i < n; i++) fprintf(out, "%d ", t1[i]);
            for (i = 0; i < n; i++) fprintf(out, "%d ", t2[i]);
            for (i = 0; i < n; i++) fprintf(out, "%d ", pi[i]);
            fprintf(out, "%d %d\n", fI, f4);
        }
    }
    fclose(out);
    printf("m = %d: matchings %d, centraliser %d, triangle-free connected normal forms %lld (with a type-I 4-cycle %lld, with a 4-cycle %lld), ordered types written %lld\n", m, nm, ncent, total, nI, n4, kept);
    return 0;
}
