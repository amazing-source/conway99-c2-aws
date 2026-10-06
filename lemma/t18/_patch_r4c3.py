import os, ast
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, "r4_verifyC2.py")
s = open(fn, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# explicit list of triples (indices in the sorted, R4V_TAUS-filtered list) and incremental saving after every triple
rep("    mine = [e for n_item, e in enumerate(items) if n_item % nparts == part]\n",
    "    mine = [e for n_item, e in enumerate(items) if n_item % nparts == part]\n"
    "    idx_list = None\n"
    "    if os.environ.get(\"R4V_IDX\"):\n"
    "        idx_list = [int(x) for x in os.environ[\"R4V_IDX\"].split(\",\")]\n"
    "        mine = [items[q] for q in idx_list]\n"
    "        tag += f\"_idx{idx_list[0]}\"\n")
rep("    survivors = []\n    done = 0\n    timed_out = False\n",
    "    survivors = []\n    done = 0\n    timed_out = False\n"
    "    outname = None\n"
    "    def dump():\n"
    "        json.dump({\"s\": s, \"part\": part, \"nparts\": nparts, \"n_items\": len(items), \"in_part\": len(mine), \"skip\": skip,\n"
    "                   \"idx_list\": idx_list, \"completed\": done, \"timed_out\": timed_out, \"stats\": ST, \"survivors\": survivors},\n"
    "                  open(os.path.join(HERE, outname), \"w\"))\n")
rep("    for e in mine[skip:]:\n        if time.time() - T0 > tl:\n",
    "    outname = f\"r4v_C2_{s}_{part}of{nparts}{tag}.json\"\n"
    "    for e in mine[skip:]:\n        if done:\n            dump()\n        if time.time() - T0 > tl:\n")
old_tail = s[s.index("    json.dump({\"s\": s, \"part\": part, \"nparts\": nparts, \"n_items\": len(items), \"in_part\": len(mine), \"skip\": skip,\n               \"completed\""):s.index("\n\nif __name__")]
s = s.replace(old_tail, "    dump()\n")
open(fn, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
print("r4_verifyC2 patched (explicit indices, incremental save), syntax ok")
