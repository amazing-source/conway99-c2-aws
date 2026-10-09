/* Action of the six orders of the layers on the ordered types written by enumc.c.
   A type is a key (t1, t2, pi) on 0..n-1 (n = 2m, iota = (01)(23)...): vertices (l, i), edges (0,i)~(0,iota i),
   (1,i)~(1,t1 i), (2,i)~(2,t2 i), (0,i)~(1,i), (0,i)~(2,i), (1,i)~(2,pi i).
   For an order (a, b, c) the layers are re-read as: new layer 0 = old layer a, new 1 = old b, new 2 = old c; the new key
   is brought to the canonical form of enumc.c (lexicographic minimum of (t1, t2, pi) under the centraliser of iota)
   and looked up in the list.  Output: one line per type with the six indices, orders in the order
   (0,1,2) (0,2,1) (1,0,2) (1,2,0) (2,0,1) (2,1,0)  (the order of itertools.permutations).
   usage: actc m typesfile outfile */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int m, n;
static int ncent = 0, cent[384][8], centinv[384][8], iota[8];
typedef struct { unsigned char k[24]; } Key;
static Key *keys; static int nk = 0;
static int *htab; static unsigned int hsize;

static void gen_cent(int *p, int k, int used) {
    if (k == n) { int i, ok = 1; for (i = 0; i < n; i++) if (p[iota[i]] != iota[p[i]]) ok = 0; if (ok) { memcpy(cent[ncent], p, sizeof(int) * 8); for (i = 0; i < n; i++) centinv[ncent][p[i]] = i; ncent++; } return; }
    for (int v = 0; v < n; v++) if (!((used >> v) & 1)) { p[k] = v; gen_cent(p, k + 1, used | (1 << v)); }
}
static unsigned int hash(const unsigned char *k) {
    unsigned long long h = 1469598103934665603ULL; int i;
    for (i = 0; i < 3 * n; i++) { h ^= k[i]; h *= 1099511628211ULL; }
    return (unsigned int)(h % hsize);
}
static int lookup(const unsigned char *k) {
    unsigned int h = hash(k);
    while (htab[h] >= 0) { if (!memcmp(keys[htab[h]].k, k, 3 * n)) return htab[h]; h = (h + 1) % hsize; }
    return -1;
}

int main(int argc, char **argv) {
    m = atoi(argv[1]); n = 2 * m;
    FILE *f = fopen(argv[2], "r"), *out = fopen(argv[3], "w"); int i, j, x, a, b;
    if (!f || !out) return 2;
    for (i = 0; i < n; i++) iota[i] = i ^ 1;
    int p[8]; gen_cent(p, 0, 0);
    int cap = 1 << 20; keys = malloc(sizeof(Key) * cap);
    while (1) {
        int ok = 1;
        for (i = 0; i < 3 * n; i++) { if (fscanf(f, "%d", &x) != 1) { ok = 0; break; } keys[nk].k[i] = (unsigned char)x; }
        if (!ok) break;
        fscanf(f, "%d %d", &a, &b);
        nk++; if (nk >= cap) return 3;
    }
    hsize = 4 * nk + 7; htab = malloc(sizeof(int) * hsize);
    for (i = 0; i < (int)hsize; i++) htab[i] = -1;
    for (i = 0; i < nk; i++) { unsigned int h = hash(keys[i].k); while (htab[h] >= 0) h = (h + 1) % hsize; htab[h] = i; }
    static const int ord[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
    long long missing = 0;
    for (int ty = 0; ty < nk; ty++) {
        int mate[3][8], pi[8], pinv[8];
        for (i = 0; i < n; i++) { mate[0][i] = iota[i]; mate[1][i] = keys[ty].k[i]; mate[2][i] = keys[ty].k[n + i]; pi[i] = keys[ty].k[2 * n + i]; }
        for (i = 0; i < n; i++) pinv[pi[i]] = i;
        /* nb[l][l2][i] = index in layer l2 of the neighbour of (l, i) */
        int nb[3][3][8];
        for (i = 0; i < n; i++) { nb[0][1][i] = i; nb[0][2][i] = i; nb[1][0][i] = i; nb[1][2][i] = pi[i]; nb[2][0][i] = i; nb[2][1][i] = pinv[i]; }
        for (int o = 0; o < 6; o++) {
            int A = ord[o][0], B = ord[o][1], C = ord[o][2];
            int new0[8], lab0[8], new1[8], lab1[8], new2[8], lab2[8], cnt = 0;
            for (i = 0; i < n; i++) lab0[i] = -1;
            for (i = 0; i < n; i++) if (lab0[i] < 0) { lab0[i] = cnt; new0[cnt++] = i; j = mate[A][i]; lab0[j] = cnt; new0[cnt++] = j; }
            for (i = 0; i < n; i++) { new1[i] = nb[A][B][new0[i]]; lab1[new1[i]] = i; new2[i] = nb[A][C][new0[i]]; lab2[new2[i]] = i; }
            int t1[8], t2[8], q[8];
            for (i = 0; i < n; i++) {
                if (lab0[mate[A][new0[i]]] != iota[i]) return 4;
                t1[i] = lab1[mate[B][new1[i]]]; t2[i] = lab2[mate[C][new2[i]]]; q[i] = lab2[nb[B][C][new1[i]]];
            }
            unsigned char best[24], cur[24];
            for (int k = 0; k < ncent; k++) {
                int *s = cent[k], *si = centinv[k];
                for (i = 0; i < n; i++) { cur[i] = (unsigned char)s[t1[si[i]]]; cur[n + i] = (unsigned char)s[t2[si[i]]]; cur[2 * n + i] = (unsigned char)s[q[si[i]]]; }
                if (k == 0 || memcmp(cur, best, 3 * n) < 0) memcpy(best, cur, 3 * n);
            }
            int idx = lookup(best);
            if (idx < 0) missing++;
            fprintf(out, "%d%c", idx, o == 5 ? '\n' : ' ');
        }
    }
    fclose(out);
    printf("m = %d: types %d, centraliser %d, images not found in the list %lld\n", m, nk, ncent, missing);
    return 0;
}
