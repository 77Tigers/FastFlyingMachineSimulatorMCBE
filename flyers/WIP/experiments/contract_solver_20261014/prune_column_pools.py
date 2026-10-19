"""Prune fixed column pools by necessary static cell compatibility.

Usage: prune_column_pools.py POOLS OUT [--count 21]
Equal shared cells are allowed. Empty domains exclude these exact pools only;
nonempty domains do not prove joint compatibility or a working mechanism.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pools", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--count", type=int, default=21)
    a = ap.parse_args()
    if a.out.exists():
        raise ValueError("refusing to overwrite pool evidence")
    raw, pools, provenance = [], [], []
    for i in range(a.count):
        p = a.pools / f"body{i}/sol/pool.json"
        values = json.loads(p.read_text(encoding="utf-8"))
        raw.append(values)
        pools.append([{tuple(row[:3]): row[3] for row in hw} for hw in values])
        provenance.append({"body": i, "path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    domains = [list(range(len(p))) for p in pools]
    initial = [len(d) for d in domains]
    cache, witnesses = {}, []
    start = time.monotonic()

    def compatible(i, x, j, y):
        key = (i, x, j, y) if i < j else (j, y, i, x)
        if key not in cache:
            left, right = pools[i][x], pools[j][y]
            cache[key] = all(p not in right or right[p] == value for p, value in left.items())
        return cache[key]

    changed = True
    empty = next((i for i, d in enumerate(domains) if not d), None)
    while changed and empty is None:
        changed = False
        for i in range(a.count):
            for j in range(a.count):
                if i == j:
                    continue
                keep = []
                for x in domains[i]:
                    if any(compatible(i, x, j, y) for y in domains[j]):
                        keep.append(x)
                    else:
                        changed = True
                        witnesses.append({"body": i, "option": x, "no_support_in_body": j,
                                          "against_options": list(domains[j])})
                domains[i] = keep
                if not keep:
                    empty = i
                    break
            if empty is not None:
                break
    a.out.mkdir(parents=True)
    for i, domain in enumerate(domains):
        p = a.out / f"body{i}/sol/pool.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps([raw[i][x] for x in domain]) + "\n", encoding="utf-8")
    report = {"scope": "Necessary static compatibility only; no timing or acceptance proof.",
              "initial_counts": initial, "remaining_counts": [len(d) for d in domains],
              "remaining_options": domains, "empty_body": empty, "removed_options": len(witnesses),
              "pair_checks": len(cache), "elapsed_seconds": time.monotonic() - start,
              "sources": provenance, "witnesses": witnesses}
    (a.out / "pruning.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("remaining_counts", "empty_body", "removed_options")}))


if __name__ == "__main__":
    main()
