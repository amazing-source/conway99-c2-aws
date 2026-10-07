"""The package's stream producer with the lab PC's reduced basis for a lattice that is not in the package's basis cache
(C2 lab, 2026-10-07). NOT part of the package: no package file is changed.

  python producer_lll.py <package dir> <lll file json> <max_out or 0> <the arguments of c1/code/y_pairs_gamma.py ...>   (cwd = <package>/c1/code)

Why: a plan lists its y1 representatives in the coordinates of the reduced basis of the machine that made it, and the producer
refuses a plan made in another basis ("plan made in another LLL basis"). The reduction of c1/code/envelope_trap.lll is a float
Gram-Schmidt that depends on the CPU; the package therefore ships the lab PC's bases for 58 lattices (lll_cache.json) and returns
them "for the same exact input, after an EXACT check that they span the same lattice". This launcher does the same for other
lattices: it adds to that cache, in memory, the entries of <lll file> (same key = sha256 of the exact input basis, same value =
rows as fraction strings), then runs y_pairs_gamma.py as it is. The package's own exact check (integral change of basis with
determinant +-1) is applied to the added bases as to the shipped ones, so a wrong file cannot give a wrong lattice: it aborts.
An entry that contradicts a shipped one is refused. <max_out> > 0 also raises the cap of the y2 enumeration, as q/producer_big.py."""
import sys, os, json, runpy

PKG = os.path.abspath(sys.argv[1]); LLLF = sys.argv[2]; MAXOUT = int(sys.argv[3]); CODE = os.path.join(PKG, "c1", "code")
sys.path.insert(0, CODE); sys.argv = [os.path.join(CODE, "y_pairs_gamma.py")] + sys.argv[4:]
import envelope_trap as ET

p = os.path.join(CODE, "lll_cache.json"); cache = json.load(open(p)) if os.path.exists(p) else {}
extra = json.load(open(LLLF)); assert isinstance(extra, dict) and extra
for k, v in extra.items():
    assert len(k) == 64 and len(v) == 24 and all(len(r) == 24 for r in v), "bad entry in the lll file"
    assert k not in cache or cache[k] == v, "the lll file contradicts the package cache"
cache.update(extra); ET._LLL_CACHE = cache
if MAXOUT:
    import y2_engine
    n = 0
    for name in dir(y2_engine):
        obj = getattr(y2_engine, name)
        if isinstance(obj, type) and "pairs_for" in vars(obj):
            f = vars(obj)["pairs_for"]; d = list(f.__defaults__)
            assert d[-1] == 10 ** 6 and f.__code__.co_varnames[:f.__code__.co_argcount][-1] == "max_out", "unexpected signature of pairs_for"
            d[-1] = MAXOUT; f.__defaults__ = tuple(d); n += 1
    assert n == 1 and MAXOUT >= 10 ** 6, "pairs_for not found exactly once"
runpy.run_path(sys.argv[0], run_name="__main__")
