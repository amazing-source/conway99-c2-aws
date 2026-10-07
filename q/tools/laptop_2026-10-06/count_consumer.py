"""Count, for one stream job, how many pairs would be searched in full in quick deferral mode, WITHOUT searching (laptop, 07/10).
  <producer> | python count_consumer.py <package dir> <lid> - <out.jsonl> 4000000000
Runs the package's consumer with `search` replaced by a classifier: char-vector trap / dual minimum 9/7 (the engine's own two
immediate tests) / witness root (would be DEFERRED) / none of these (would be SEARCHED IN FULL). The record it writes is NOT a
result: every pair that reaches the classifier gets the verdict "COUNT ONLY ...", which is not an exclusion."""
import sys, os
PKG = os.path.abspath(sys.argv[1]); sys.argv = [os.path.join(PKG, "scripts", "hstage_stream_next.py")] + sys.argv[2:]
sys.path.insert(0, os.path.join(PKG, "scripts"))
import numpy as np
import frame_dfs_next as FD
import hstage_stream_next as HS
_RG = {}


def search(L, y1, y2, node_limit=0, cap=2_000_000):
    if os.environ.get("FD_CHAR", "1") == "1" and FD.char_trap(L, y1, y2) is not None: return {"verdict": "COUNT ONLY: char-vector trap"}
    if os.environ.get("FD_MIN97", "0") == "1" and FD.min97_witness(L, y1, y2) is not None: return {"verdict": "COUNT ONLY: dual min 9/7"}
    RG = _RG.get(id(L))
    if RG is None: RG = _RG[id(L)] = (L["R"] @ L["G"]).astype(np.int64)
    a = RG @ y1; b = RG @ y2; Y = a * a + b * b
    if (Y == 5).any(): return {"verdict": "COUNT ONLY: would be DEFERRED T18"}
    if (Y == 4).any(): return {"verdict": "COUNT ONLY: would be DEFERRED T20"}
    return {"verdict": "COUNT ONLY: would be SEARCHED IN FULL (max Y %d)" % int(Y.max())}


HS.search = search
HS.main()
