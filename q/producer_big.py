"""The package's stream producer with a higher cap on the y2 candidates of one y1 (C2, 2026-10-07). NOT part of the package: no
package file is changed.

  python producer_big.py <package dir> <max_out> <the arguments of c1/code/y_pairs_gamma.py ...>      (cwd = <package>/c1/code)

c1/code/y2_engine.py stops the enumeration of the y2 of one y1 at max_out = 10^6 candidates and marks the result "truncated"; the
producer then ends its stream with "complete": false, the consumer answers chunk_ok false and the job FAILS, whatever the mode.
Five one-y1 jobs of lattices 003 and 005 failed three times for this reason on 07/10 (y2_candidates 1,006,595 and 1,001,405).
This launcher changes only the default value of max_out of that method, then runs y_pairs_gamma.py as it is. A stream that was
complete under the package's cap is byte for byte the same under a higher one (checked: same sha256), so only truncated jobs
change, from incomplete to complete. The record then carries merged.producer_max_out (written by q/par_consumer.py)."""
import sys, os, runpy

PKG = os.path.abspath(sys.argv[1]); MAXOUT = int(sys.argv[2]); CODE = os.path.join(PKG, "c1", "code")
sys.path.insert(0, CODE); sys.argv = [os.path.join(CODE, "y_pairs_gamma.py")] + sys.argv[3:]
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
