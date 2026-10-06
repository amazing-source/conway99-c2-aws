"""Deferral wrapper around the package's stream consumer (C2, 2026-10-06 night). NOT part of the package: no package file is changed.

  python defer_consumer.py <package dir> <lid> <stream path | -> <out.jsonl> <node_limit>

Runs main() of scripts/hstage_stream_next.py as it is, with ONE substitution: the name `search` of that module is bound to the
function below. For every pair the consumer still applies its own filters (swap, twin transfer, twin-canonical) and then calls
`search`, which here
  1. calls the engine's own search(L, y1, y2) with the small node budget Q_DEFER_NODES (default 10000, the engine's own phase-1
     budget FD_SYM2_T). Everything the engine decides within that budget is returned unchanged: char-vector trap, dual minimum
     9/7, pair-setup exclusions, and searches that finish. A node limit that is not reached changes nothing in the search;
  2. if the engine answers INCOMPLETE (budget reached) and U has a root r with (r,y1)^2 + (r,y2)^2 = 5, resp. = 4 when no root
     gives 5, returns that same result with the verdict "DEFERRED (pending T18 ...)", resp. "(pending T20 ...)". These are the
     pairs the open lemmas T18 (dual minimum >= 10/7) and T20 (>= 11/7) would exclude (LEMMA_TARGET_2026-10-06.md). A DEFERRED
     verdict is not an exclusion: the consumer lists the pair in not_excluded and chunk_done is false;
  3. otherwise (INCOMPLETE and no such root) runs the engine's search again with the production node limit.
So a deferral record is the full record with the long searches of the lemma-covered pairs replaced by DEFERRED, and nothing else.
User's decision of 06/10 evening: set those pairs aside, never count them as excluded on the strength of an unproved lemma."""
import sys, os

PKG = os.path.abspath(sys.argv[1])
sys.argv = [os.path.join(PKG, "scripts", "hstage_stream_next.py")] + sys.argv[2:]
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
import hstage_stream_next as HS

REAL = HS.search
BUDGET = int(os.environ.get("Q_DEFER_NODES", "10000"))
DEF18 = "DEFERRED (pending T18: root r with (r,y1)^2+(r,y2)^2 = 5)"
DEF20 = "DEFERRED (pending T20: root r with (r,y1)^2+(r,y2)^2 = 4)"
_RG = {}


def search(L, y1, y2, node_limit=0, cap=2_000_000):
    r = REAL(L, y1, y2, node_limit=BUDGET, cap=cap)
    if r.get("verdict") != "INCOMPLETE":
        return r
    RG = _RG.get(id(L))
    if RG is None:
        RG = _RG[id(L)] = (L["R"] @ L["G"]).astype(np.int64)             # one row per +- pair of roots
    if len(RG):
        a = RG @ y1; b = RG @ y2; Y = a * a + b * b
        if (Y == 5).any(): r["verdict"] = DEF18; return r
        if (Y == 4).any(): r["verdict"] = DEF20; return r
    return REAL(L, y1, y2, node_limit=node_limit, cap=cap)


if __name__ == "__main__":
    assert BUDGET > 0
    HS.search = search
    HS.main()
