"""Deferral wrapper around the package's pair consumers (C2, 2026-10-06 night). NOT part of the package: no package file is changed.

  python defer_consumer.py <package dir> <lid> <stream path | -> <out.jsonl> <node_limit>      stream job (called by par_consumer.py)
  python defer_consumer.py <package dir> --golay <lid> <k> <n> <res.jsonl>                      golay_pairs job

Runs main() of scripts/hstage_stream_next.py, resp. scripts/golay_pairs_job.py, as it is, with ONE substitution: the name `search`
those scripts call is bound to the function below. For every pair the script still applies its own filters (swap, characteristic
trap, twin transfer, twin-canonical) and then calls `search`, which here
  1. calls the engine's own search(L, y1, y2) with the small node budget Q_DEFER_NODES (default 10000, the engine's own phase-1
     budget FD_SYM2_T). Everything the engine decides within that budget is returned unchanged: char-vector trap, dual minimum
     9/7, pair-setup exclusions, and searches that finish. A node limit that is not reached changes nothing in the search;
  2. if the engine answers INCOMPLETE (budget reached) and U has a root r with (r,y1)^2 + (r,y2)^2 = 5, resp. = 4 when no root
     gives 5, returns that same result with the verdict "DEFERRED (pending T18 ...)", resp. "(pending T20 ...)". These are the
     pairs the open lemmas T18 (dual minimum >= 10/7) and T20 (>= 11/7) would exclude (LEMMA_TARGET_2026-10-06.md). A DEFERRED
     verdict is not an exclusion: the script lists the pair in not_excluded and chunk_done is false;
  3. otherwise (INCOMPLETE and no such root) runs the engine's search again with the node limit the script asked for.
So a deferral record is the full record with the long searches of the lemma-covered pairs replaced by DEFERRED, and nothing else.
Quick variant, Q_DEFER_NODES=0 (07/10; measured on the fleet: the set-up of a budget-limited search costs 0.3 s per pair, 70 % of a
deferral job): a pair that has such a root is first put through the engine's own two immediate tests, char_trap and (when FD_MIN97=1)
min97_witness, with the engine's own switches. If one of them fires, the engine's search is called and returns its EXCLUDED verdict
as usual. If none fires the pair is DEFERRED without calling the engine's search at all. Pairs without such a root go to the engine
unchanged. Compared with the budget variant, the few searches that would end within the budget are deferred too; no verdict
other than DEFERRED is ever produced by this file.
A golay_pairs record also gets the field "deferral" (node budget, sha256 of this file); a stream record gets it from par_consumer.
User's decision of 06/10 evening: set those pairs aside, never count them as excluded on the strength of an unproved lemma."""
import sys, os, json, hashlib

PKG = os.path.abspath(sys.argv[1]); GOLAY = sys.argv[2] == "--golay"
sys.argv = [os.path.join(PKG, "scripts", "golay_pairs_job.py" if GOLAY else "hstage_stream_next.py")] + sys.argv[(3 if GOLAY else 2):]
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
import frame_dfs_next as FD

REAL = FD.search
BUDGET = int(os.environ.get("Q_DEFER_NODES", "10000"))
DEF18 = "DEFERRED (pending T18: root r with (r,y1)^2+(r,y2)^2 = 5)"
DEF20 = "DEFERRED (pending T20: root r with (r,y1)^2+(r,y2)^2 = 4)"
_RG = {}


def witness(L, y1, y2):
    """DEF18 / DEF20 if U has a root r with (r,y1)^2 + (r,y2)^2 = 5 / = 4 (5 first), else None."""
    RG = _RG.get(id(L))
    if RG is None:
        RG = _RG[id(L)] = (L["R"] @ L["G"]).astype(np.int64)             # one row per +- pair of roots
    if len(RG):
        a = RG @ y1; b = RG @ y2; Y = a * a + b * b
        if (Y == 5).any(): return DEF18
        if (Y == 4).any(): return DEF20
    return None


def search(L, y1, y2, node_limit=0, cap=2_000_000):
    if BUDGET == 0:                                                    # quick variant: no engine search for a lemma-covered pair
        w = witness(L, y1, y2)
        if w is not None and not (os.environ.get("FD_CHAR", "1") == "1" and FD.char_trap(L, y1, y2) is not None)                 and not (os.environ.get("FD_MIN97", "0") == "1" and FD.min97_witness(L, y1, y2) is not None):
            return {"verdict": w}
        return REAL(L, y1, y2, node_limit=node_limit, cap=cap)
    r = REAL(L, y1, y2, node_limit=BUDGET, cap=cap)
    if r.get("verdict") != "INCOMPLETE":
        return r
    w = witness(L, y1, y2)
    if w is not None:
        r["verdict"] = w; return r
    return REAL(L, y1, y2, node_limit=node_limit, cap=cap)


if __name__ == "__main__":
    assert BUDGET >= 0
    if GOLAY:
        FD.search = search                                             # golay_pairs_job imports search from the module at each call
        import golay_pairs_job as GJ
        res = sys.argv[4]; GJ.main()
        lines = [l for l in open(res) if l.strip()]; rec = json.loads(lines[-1])
        rec["deferral"] = {"defer_nodes": BUDGET, "defer_consumer_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
                           "rule": "pair not decided by the engine within defer_nodes nodes, and U has a root r (one per +- pair) with "
                                   "(r,y1)^2 + (r,y2)^2 = 5 (T18) or, failing that, = 4 (T20); the pairs are listed in not_excluded"}
        open(res, "w").write("".join(lines[:-1]) + json.dumps(rec) + "\n")
    else:
        import hstage_stream_next as HS
        HS.search = search
        HS.main()
