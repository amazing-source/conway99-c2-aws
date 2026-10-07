"""Small independent checks of the route-B specification's printed data.

No search-engine imports, no enumeration of N-configurations or X2 orbits.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "lemma/t20_R3_I/SPEC_ROUTE_B_N3.txt"
PROOF = ROOT / "lemma/T20_PROOF.md"


def automorphisms(rows):
    assigned = []

    def visit(unused):
        i = len(assigned)
        if i == len(rows):
            yield tuple(assigned)
            return
        for j in sorted(unused):
            if all((rows[i] >> a & 1) == (rows[j] >> b & 1)
                   for a, b in enumerate(assigned)):
                assigned.append(j)
                yield from visit(unused - {j})
                assigned.pop()

    return list(visit(set(range(len(rows)))))


def image(mask, permutation):
    return sum(1 << permutation[i] for i in range(10) if mask >> i & 1)


def canonical(pair, group):
    return min(tuple(sorted(image(mask, g) for mask in pair)) for g in group)


def passes_budget(support, u, v):
    # p=20 is isolated here; z=21 and z'=22 are nonadjacent word mates.
    rows = support[:] + [0, 0, 0]
    for i in range(10):
        for vertex, mask in ((i, u), (10 + i, v)):
            if mask >> i & 1:
                rows[21] |= 1 << vertex
                rows[vertex] |= 1 << 21
        for vertex, mask in ((i, v), (10 + i, u)):
            if mask >> i & 1:
                rows[22] |= 1 << vertex
                rows[vertex] |= 1 << 22
    return all((rows[i] & rows[j]).bit_count() <= 2 - (rows[i] >> j & 1)
               for i in range(23) for j in range(i))


def main():
    started = time.monotonic()
    text = SPEC.read_text(encoding="utf-8")
    proof = PROOF.read_text(encoding="utf-8")
    triples = [sum(1 << i for i in triple) for triple in combinations(range(10), 3)]
    results = []
    expected_ordered = [8, 46, 30, 24, 24, 50]
    expected_classes = [1, 9, 3, 4, 5, 3]
    for number in range(6):
        label = f"I.{number}"
        edges = re.search(rf"^    I\.{number}: ([0-9 ]+)$", text, re.M).group(1).strip()
        assert edges in proof
        b = [0] * 10
        support = [0] * 20
        for edge in edges.split():
            i, j = map(int, edge)
            b[i] |= 1 << j
            b[j] |= 1 << i
            for a, c in ((i, 10 + j), (j, 10 + i)):
                support[a] |= 1 << c
                support[c] |= 1 << a
        assert all(row.bit_count() == 4 for row in b)
        group = automorphisms(b)
        unordered = [(u, v) for u, v in combinations(triples, 2)
                     if passes_budget(support, u, v)]
        classes = {canonical(pair, group) for pair in unordered}
        line = re.search(rf"^    I\.{number} \([^)]+\):[ \t]*(.+)$", text, re.M).group(1)
        printed = []
        for word in line.split():
            printed.append(tuple(sum(1 << int(i) for i in part) for part in word.split(";")))
        assert len(unordered) * 2 == expected_ordered[number]
        assert len(classes) == len(printed) == expected_classes[number]
        assert {canonical(pair, group) for pair in printed} == classes
        assert all(passes_budget(support, *pair) for pair in printed)
        eps_one = []
        for word, (u, v) in zip(line.split(), printed):
            assert (u & v).bit_count() <= 1
            need = [2 - (b[i] & b[j]).bit_count()
                    - int(bool(u >> i & 1) and bool(u >> j & 1))
                    - int(bool(v >> i & 1) and bool(v >> j & 1))
                    for i, j in combinations(range(10), 2)]
            assert min(need) >= 0 and sum(need) == 24
            if u & v:
                eps_one.append(word)
        results.append({"graph": label, "automorphisms": len(group),
                        "ordered_types": 2 * len(unordered), "classes": len(classes),
                        "epsilon_one_representatives": eps_one})
    assert sum(len(row["epsilon_one_representatives"]) for row in results) == 8

    # Seven labelled mate edges. With a Z edge (12,13), its local flip acts
    # freely on the attachments using Z and trivially on all others.
    full = {pair for pair in combinations(range(14), 2) if pair[0] // 2 != pair[1] // 2}
    reduced = {pair for pair in full if 13 not in pair}
    def flip_z(pair):
        return tuple(sorted(25 - i if i >= 12 else i for i in pair))
    classes_z = {min(pair, flip_z(pair)) for pair in full}
    assert len(full) == 84 and len(reduced) == 72 and classes_z == reduced
    assert Counter(any(i >= 12 for i in pair) for pair in full) == {False: 60, True: 24}
    assert Counter(any(i >= 12 for i in pair) for pair in reduced) == {False: 60, True: 12}

    # Only consistency of the archived summary, not replay of its 86,968 nodes.
    verification = ROOT / "lemma/t20_R3_I/n3_verify.out"
    table = []
    for line in verification.read_text().splitlines():
        if not re.match(r"^I[0-5]_(340|421)_t\d+\s", line):
            continue
        fields = line.split("|")
        left = fields[0].split()
        classes_pair = tuple(map(int, left[3].split("/")))
        assert classes_pair[0] == classes_pair[1] and left[4] == "agrees"
        if "no base" in fields[1]:
            assert int(left[2]) == 0
            nodes = 0
        else:
            middle = fields[1].split()
            assert int(middle[0]) == int(left[2])
            counts = tuple(map(int, middle[1].split("/")))
            kept = tuple(map(int, middle[2].split("/")))
            assert counts[0] == counts[1] and kept[0] == kept[1]
            assert middle[3:] == ["0", "agrees"]
            nodes = counts[0]
        table.append((left[0], int(left[2]), classes_pair[0], nodes))
    assert len(table) == 50 and len({row[0] for row in table}) == 50
    assert tuple(sum(row[i] for row in table) for i in (1, 2, 3)) == (64528, 64498, 86968)

    sources = {}
    for path in (SPEC, PROOF, verification, ROOT / "lemma/t20_R3_I/n3_check.out"):
        raw = path.read_bytes()
        sources[str(path.relative_to(ROOT)).replace("\\", "/")] = {
            "sha256_bytes": sha256(raw).hexdigest(),
            "sha256_lf": sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
        }
    result = {"types": results, "attachments_without_Z": 84,
              "attachments_with_Z_before_quotient": 84,
              "attachments_with_Z_after_quotient": 72,
              "I0_421_reference_representatives": 1875,
              "I0_421_raw_attachment_count": 1875 * 84,
              "I0_421_reduced_attachment_count": 1875 * 72,
              "archived_summary_rows_checked": 50,
              "archived_summary_totals": {"bases": 64528, "classes": 64498, "nodes": 86968},
              "seconds": time.monotonic() - started, "sources": sources,
              "scope": "Printed small type list, attachment quotient and summary arithmetic; no N-configuration enumeration, no search-code audit, no large search replay."}
    Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "sources"}))


if __name__ == "__main__":
    main()
