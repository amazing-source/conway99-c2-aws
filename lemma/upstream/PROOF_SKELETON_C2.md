# Nonexistence of an involution of srg(99,14,1,2) — proof skeleton (auto-generated 2026-10-01 19:49)

**Status: excluded 93, open 62, partial 1**

## Part I — reduction (mathematics; each item needs its written proof)
1. Involution structure: 1 fixed vertex p, 49 transpositions, 7 edges = the 7 triangles at p (trace formulas; Makhnev–Minakova).
2. Signed quotient M (49x49), M^2+M=12I; the 49 odd vectors form a 7-tight frame of rank 22 (7 h of norm 4, 42 u of norm 3).
3. Envelope theorem: the frame + two orthogonal norm-7 y lies in an odd unimodular lattice U of rank 24 with min U >= 2
   (min N* >= 8/7, Astra dossier / AUDIT_NORME1). By Borcherds' classification U is one of 156 lattices.
4. Frame identity at new roots: w(beta) in {1,3}; admissibility |(h,beta)|<=1; y-hit/flex/exact targets (C1 notes 142/145, Lemma U+).

## Part II — lemmas used by the exclusions (each: statement + proof reference)
- Component budget (C2 28/09); packing (C1 envelope_pack); per-pair root-class budget (C2).
- Characteristic trap: (z,y1)^2+(z,y2)^2 <= 66 for characteristic z of norm 16 (Astra 28/09; C2 check).
- Swap rule (unordered pairs; enumerator symmetric; verified on full 078 list).
- Twin envelope U+ = F(U)+J carries the same frame; transfer/deferral (Astra shell theorems §5–7).
- Endpoint confinement; boundary points Y_z=58 = twin new roots (Astra/5.6 flex package; C2 check).
- Symmetry breaking by reflections fixing y1,y2,beta0 (C2 28/09).
- Pair enumeration completeness: W(R)-dominant y1 mod Gamma, y2 mod Stab(y1) x signs (C1 y_pairs_gamma; Gamma verified).

## Part III — the 156 envelopes

| id | roots | status | method / provenance |
|---|---|---|---|
| 000 | (none) | partial | O24: 141 (y1,y2) classes (C1 48eabf2). 86 EXCLUDED by the whole-class LP (structures 4e48848; integer certificates verified twice: structure |
| 001 | a_1^8 | open | 27/09 ~21:20 structures (Golay pipeline a9bb407/3e9690b): y1 classes c00 (819 pair classes) and c01 (1957) enumerated; whole-pair frame LP ( |
| 002 | a_1^{12} | open | open |
| 003 | a_2^2a_1^{10} | open | open |
| 004 | a_1^{16} | open | open |
| 005 | a_2^4a_1^8 | open | open |
| 006 | a_3^2a_1^{12} | open | open |
| 007 | a_3a_2^4a_1^6 | open | open |
| 008 | a_2^8 | open | open |
| 009 | a_2^6a_1^6 | open | open |
| 010 | a_1^{24} | open | open |
| 011 | a_3^2a_2^4a_1^4 | open | open |
| 012 | a_2^8a_1^4 | open | open |
| 013 | a_3^4a_2^2a_1^2 | open | open |
| 014 | a_4a_3a_2^4a_1^4 | open | open |
| 015 | a_3^2a_3a_2^4a_1^2 | open | open |
| 016 | a_3^4a_1^4a_1^4 | open | open |
| 017 | a_3^4a_1^8 | open | open |
| 018 | a_4a_3^2a_3a_2^2a_1^2 | open | open |
| 019 | a_4^2a_2^4a_1^4 | open | open |
| 020 | a_3^6 | open | open |
| 021 | a_3^4a_2^4 | open | open |
| 022 | d_4a_4a_2^6 | open | open |
| 023 | d_4a_3^4a_1^4 | open | open |
| 024 | a_5a_3^3a_1^6a_1 | open | open |
| 025 | a_4^2a_3^2a_3a_1^2 | open | open |
| 026 | a_5a_3^2a_2^4a_1 | open | open |
| 027 | d_4a_3^4a_1^4 | open | open |
| 028 | d_4^2a_1^{16} | open | open |
| 029 | a_4^2a_3^2a_2^2a_1^2 | open | open |
| 030 | a_3^4a_3^2a_1^4 | open | open |
| 031 | a_4^4a_1^4 | open | open |
| 032 | a_5a_4a_3a_3a_2a_2a_1 | open | open |
| 033 | a_4^2a_3^4 | open | open |
| 034 | a_4^2a_4a_3a_2^2a_1^2 | open | open |
| 035 | a_5a_4^3a_1^3 | open | open |
| 036 | a_5^2a_3^2a_2^2 | open | open |
| 037 | a_6a_3^3a_2^3 | open | open |
| 038 | d_4a_4^2a_4a_2^2 | open | open |
| 039 | a_5d_4a_3^2a_3a_1^2a_1 | open | open |
| 040 | a_5^2a_3^2a_1^2a_1^2a_1^2 | open | open |
| 041 | a_5a_4^2a_3a_3a_1 | open | open |
| 042 | d_4^2a_3^4 | open | open |
| 043 | a_4^3a_3^3 | open | open |
| 044 | a_3^8 | excluded | 29/09 C2 h-stage sweep (a): all 14496 pairs of gpairs_044 EXCLUDED (last 34 incl. hard pair 11781 with the 29/09 code: trap+EC+boundary poin |
| 045 | a_5^2a_4^2a_1^2 | open | open |
| 046 | a_6a_4a_4a_3a_2a_1a_1 | open | open |
| 047 | a_5^2a_4a_3a_2^2 | open | open |
| 048 | a_4^4a_3^2 | open | open |
| 049 | d_5d_4a_3^4 | open | open |
| 050 | d_5a_5a_3^2a_3a_1^2a_1 | open | open |
| 051 | a_5^2d_4^2a_1^2 | open | open |
| 052 | a_7a_3^4a_1^4 | open | open |
| 053 | d_5a_4a_4^2a_2^2 | open | open |
| 054 | a_6d_4a_4^2a_2 | open | open |
| 055 | a_6a_5a_4a_3a_2a_1 | open | open |
| 056 | a_5^2d_4a_3^2a_1^2 | open | open |
| 057 | a_5a_5a_4^2a_3 | open | open |
| 058 | a_5^2d_4a_3^2a_1^2 | open (pending twins) | open |
| 059 | d_4^4a_1^8 | open | open |
| 060 | a_7a_4^2a_3^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 568181 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 061 | a_6^2a_4a_3a_1^2 | open | open |
| 062 | a_6a_5a_5a_3a_2 | open | open |
| 063 | a_6^2a_3^2a_2^2 | open | open |
| 064 | a_5^4 | open | open |
| 065 | a_7a_5^2a_2^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 170548 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 066 | a_7a_5a_4^2a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 304034 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 067 | a_7a_5d_4a_3a_1a_1a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 559433 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 068 | a_6d_5a_4a_4a_2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 620319 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 069 | d_5^2a_3^4 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 64133 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 070 | d_5a_5^2d_4a_1^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 295716 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 071 | a_5^2a_5d_4a_3a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 171216 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 072 | a_5^4a_1^4 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 073 | a_8a_4^2a_3^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 161453 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) o |
| 074 | a_7a_6a_5a_2a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 367327 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 075 | a_6a_6a_5a_4a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 248990 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) o |
| 076 | a_7^2d_4a_1^4 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 52015 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 077 | d_6a_5^2a_3^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 62031 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 078 | a_8a_5^2a_3 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 103,280 ordered pairs: char-vector trap (Astra, norm-16 characteristic z, (z,y1)^2+(z,y2)^2<=66; |
| 079 | d_6a_5^2a_3^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 100895 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 080 | d_6d_4^3a_1^6 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 31122 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 081 | a_7d_5a_5a_3a_1a_1a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 154990 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 082 | d_5d_5a_5^2a_1^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 90976 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 083 | a_7d_5d_4a_3a_3 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 166234 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 084 | a_6a_6d_5a_4 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 169401 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 085 | d_5^2a_5^2a_1^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 38140 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 086 | a_6^2a_5^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 74583 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 087 | d_4^6 | excluded | C2 27/09 (computer, h-stage): frame_dfs (rigid mode) on ALL 3913 Gamma-reduced (y1,y2) pairs of C1 gpairs_087.json (conway99-c1 ca5dd2d, sha |
| 088 | a_8a_6a_5a_2a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 107203 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 089 | a_7^2a_4^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 49570 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 090 | a_9a_5d_4a_3a_1a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 60345 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 091 | a_7d_6a_5a_3a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 71608 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 092 | a_8a_6d_5a_2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 67915 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 093 | d_6d_5a_5^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 32952 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 094 | d_5^4 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 84 > 80 new roots |
| 095 | a_8a_7a_4a_3 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 144220 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums /  |
| 096 | a_7d_5^2a_3^2 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 097 | a_7^2d_4^2 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 098 | a_8^2a_3^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 82476 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 099 | a_9a_6a_5a_2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 93802 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 100 | a_7^3 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 58356 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 101 | d_7a_5^2a_5a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 62300 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 102 | a_9d_5^2a_1^2a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 49692 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 103 | a_7e_6d_4a_3^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 17228 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums / t |
| 104 | e_6a_6^2a_4 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 70108 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 105 | e_6d_5a_5^2a_1^2 | excluded | 29/09 C2 h-stage sweep (a): all 14169 pairs of gpairs_105 EXCLUDED (finished with the 29/09 frame_dfs) |
| 106 | d_6^2d_4^2a_1^4 | excluded | 29/09 C2 h-stage sweep (a): all 12,410 pairs of gpairs_106 (C1) EXCLUDED (u_ + c_ files in data/finishC/frame_dfs/106, every index checked) |
| 107 | a_7^2d_6a_1^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 49804 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 108 | a_7^2d_5d_4 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 109 | a_{10}a_6a_5a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 16386 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 110 | a_8a_7^2 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 6920 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or  |
| 111 | a_9^2a_2^2 | excluded | C2 27/09 21:45 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 3992/3992 Gamma-reduced pairs of gpairs_111.json (sha256 4ca28044d792. |
| 112 | d_7a_7d_5a_3 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 20846 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 113 | a_9d_6a_5a_3 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 12184 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 114 | a_9a_8a_5 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 19806 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 115 | a_7^2d_5^2 | excluded | C1: 1472 Gamma-reduced pairs, rigid; structures 8b74348 frame LP 1470/1472 excluded with certificates, the 2 LP-feasible (1077, 1113) dead i |
| 116 | a_8^2a_7 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 117 | d_8d_4^4 | excluded | C1 notes/139 s.2 criterion (E): D8 spinor cost 28 > 26; depends on Sol's theta theorems; independently packing (C1 envelope_pack.py 19af6fb, |
| 118 | a_9d_7a_5a_1a_1 | excluded | 29/09 C2 stream sweep (a): 8/8 chunks done, 11980 ordered pairs, all EXCLUDED (char trap / stage 1 with EC + boundary points / star sums) or |
| 119 | a_{11}d_5d_4a_3 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 120 | a_9a_7d_6a_1 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 121 | a_9a_7d_6a_1 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 122 | d_6^2d_6d_4a_1^2 | excluded | C2 27/09 (a) DONE: frame_dfs + C1 Lemma U+ on all 4158 Gamma-reduced pairs (external_runs\c1_pairs\gpairs_122.json, sha256 896184379fc3...): |
| 123 | a_{11}a_8a_3 | excluded | C2 27/09 22:42 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 3809/3809 Gamma-reduced pairs of gpairs_123.json (sha256 bf021e359247. |
| 124 | d_8a_7^2 | excluded | C2 27/09 (a) DONE: frame_dfs general mode + C1 Lemma U+ (notes/145; frame_dfs FD_LEMMA_U=1) on all 1286/1286 Gamma-reduced pairs (conway99-c |
| 125 | a_{11}d_6a_5a_1 | excluded | C2 27/09 22:37 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 2147/2147 Gamma-reduced pairs of gpairs_125.json (sha256 0a6c5a49cf65. |
| 126 | a_{10}e_6a_6 | excluded | C2 27/09 (a) DONE: frame_dfs general mode + C1 Lemma U+ (notes/145; frame_dfs FD_LEMMA_U=1) on all 2084/2084 Gamma-reduced pairs (conway99-c |
| 127 | d_7a_7e_6a_3 | excluded | open / 28/09 evening C2: h-stage sweep (a): all pairs EXCLUDED |
| 128 | a_9e_6d_6a_1 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 84 > 64 new roots |
| 129 | e_6^2d_5^2 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 84 > 64 new roots |
| 130 | a_{12}a_7a_4 | excluded | open / 28/09 evening C2: component-budget test (lattice level, exact integer check) + h-stage sweep (a): all pairs EXCLUDED |
| 131 | d_8d_6^2a_1^2a_1^2 | excluded | C2 27/09 (a) DONE: frame_dfs + C1 Lemma U+ (FD_LEMMA_U=1) on all 1257/1257 Gamma-reduced pairs of C1 external_runs/c1_pairs/gpairs_131.json  |
| 132 | d_6^4 | excluded | C1 40b37bf: 304 Gamma-reduced (y1,y2) pairs (complete up to Aut(U) x signs), rigid, pair_h_check (fixed bitsets) finds no h-configuration fo |
| 133 | a_{13}d_6a_3a_1 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 168 > 128 new roots |
| 134 | d_9a_7^2 | excluded | C1 notes/139 s.2 criterion (E): 36 > 32; independently packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing-admissib |
| 135 | a_{11}d_7d_5 | excluded | C2 27/09 22:12 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 464/464 Gamma-reduced pairs of gpairs_135.json (sha256 4e8030694f48... |
| 136 | a_{11}^2 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 84 > 48 new roots |
| 137 | a_9e_7a_7 | excluded | C2 27/09 22:20 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 604/604 Gamma-reduced pairs of gpairs_137.json (sha256 f005dba54c5d... |
| 138 | e_7d_6d_6d_4a_1 | excluded | C2 27/09 (a) DONE: frame_dfs + C1 Lemma U+ (FD_LEMMA_U=1) on all 558/558 Gamma-reduced pairs of C1 external_runs/c1_pairs/gpairs_138.json (s |
| 139 | d_8^2d_4^2 | excluded | C2 27/09 (a) DONE: frame_dfs + C1 Lemma U+ (FD_LEMMA_U=1) on all 504/504 Gamma-reduced pairs of C1 external_runs/c1_pairs/gpairs_139.json (s |
| 140 | a_{11}d_9a_3 | excluded | C2 27/09 21:37 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 288/288 Gamma-reduced pairs of gpairs_140.json (sha256 744a30d76556... |
| 141 | a_{12}a_{11} | excluded | C2 27/09 21:15 (a) DONE (sweep-first): frame_dfs + C1 Lemma U+ on all 319/319 Gamma-reduced pairs of gpairs_141.json (sha256 6d86bedb188b... |
| 142 | d_{10}d_6^2a_1^2 | excluded | C1 notes/139 s.2 criterion (E): 45 > 38; independently packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smal |
| 143 | a_{15}a_8 | excluded | open / 28/09 evening C2: component-budget test (lattice level, no pairs; MILP + exact integer enumeration agree; scripts/component_budget.py |
| 144 | a_{16}a_7 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 168 > 104 new roots |
| 145 | d_8^2d_8 | excluded | Sol 0836 D8^3; re-read C1 notes/139 (check_d8cube_trap.py); also packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packin |
| 146 | d_8^3 | excluded | Sol 0836 D8^3; re-read C1 notes/139 (check_d8cube_trap.py); also packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packin |
| 147 | a_{15}d_8 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 84 > 32 new roots |
| 148 | a_{15}e_7a_1 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 168 > 64 new roots |
| 149 | d_{10}e_7d_6a_1 | excluded | C2 27/09 (a) DONE: frame_dfs + C1 Lemma U+ (FD_LEMMA_U=1) on all 44/44 Gamma-reduced pairs of C1 external_runs/c1_pairs/gpairs_149.json (sha |
| 150 | d_8e_7^2a_1^2 | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 168 > 64 new roots |
| 151 | d_{12}d_8d_4 | excluded | Sol 0836 D>=12 (G18_G20_D12_COLLAGE); re-read C1 notes/139 s.3; also packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): pa |
| 152 | e_8d_8^2 | excluded | Sol 0836 E8 (minuscule weight 0 => span E8 in N-perp); re-read C1 notes/139 s.2-3; also packing (C1 envelope_pack.py 19af6fb, run + argument |
| 153 | d_{12}^2 | excluded | Sol 0836 D>=12; re-read C1 notes/139 s.3 |
| 154 | a_{23} | excluded | packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m sum to 252 > 48 new roots |
| 155 | d_{16}d_8 | excluded | Sol 0836 D>=12; re-read C1 notes/139 s.3; also packing (C1 envelope_pack.py 19af6fb, run + argument re-read by C2): packing: 42 smallest m s |

## Part IV — verification data
- Every stream chunk: data/finishC/stream/<id>/chunks.jsonl (pair-stream sha256, verdict counts, code_sha of frame_dfs/hstage_stream/twin_transfer).
- Monster pairs: incomplete_resolved.jsonl (no node limit). Rank-17 side: conway99-rank17 r17_char/ (228 certificates, C1-verified).
- Engine controls: identity checks of each optimisation (same verdicts + nodes per depth); positive control scripts/positive_control.py.
