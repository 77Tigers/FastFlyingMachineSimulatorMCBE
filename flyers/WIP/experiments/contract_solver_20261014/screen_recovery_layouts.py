"""Optimistic vacant-cell recovery distances on existing supplied-tip cores.

Counts glue additions, not carried load. Omits intermediate new H glue from G
obstacles, so distances are lower bounds for the stated retained-hardware model.
No timing verification, observer relocation, or design acceptance is implied.
"""
import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

from assemble import Flyer
from repair_sticky_pickup import adjacent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("variants", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--h-cells", type=int, default=5)
    ap.add_argument("--max-link", type=int, default=5)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("refusing existing screen")
    cases = []
    for name in json.loads((a.variants / "summary.json").read_text())["leads"]:
        src = Path(name)
        c = json.loads((src / "problem.json").read_text())
        f = Flyer.load(src / c["flyer"])
        glue = {tuple(p["at"]) for p in c["ports"] if p["name"].startswith("G")}
        tip = tuple(next(p["at"] for p in c["ports"] if p["name"] == "tip"))
        # All contact cells reachable by a planar connected H shape of <=N cells.
        queue, seen, contacts = deque([(tip, [tip])]), {tip}, []
        while queue:
            p, path = queue.popleft()
            contacts.append((p, path))
            if len(path) >= a.h_cells:
                continue
            for q in adjacent(p):
                if q[0] == tip[0] and q not in seen and q not in f._cells:
                    seen.add(q)
                    queue.append((q, path + [q]))
        results = []
        for contact, hpath in contacts:
            actor = (tip[0] + 3, *contact[1:])
            pulse = (actor[0] + 1, *actor[1:])
            if actor in f._cells or pulse in f._cells:
                continue
            targets = {(p[0] - 1, *p[1:]) for p in adjacent(actor)}
            # Ignore the other added H cells to make this an optimistic bound.
            blocked = set(f._cells) | {contact, actor, pulse}
            queue, seen = deque((p, []) for p in sorted(glue)), set(glue)
            while queue:
                p, route = queue.popleft()
                if p in targets:
                    results.append({"added_G": len(route), "H_path": hpath,
                                    "G_route": route, "actor": actor})
                    break
                if len(route) >= a.max_link:
                    continue
                for q in adjacent(p):
                    if q not in seen and q not in blocked:
                        seen.add(q)
                        queue.append((q, route + [q]))
        best = min(results, key=lambda x: (x["added_G"], len(x["H_path"]))) if results else None
        cases.append({"source": str(src), "hash": f.content_hash(), "contacts": len(contacts), "best": best})
    result = {"scope": "geometry lower bound for retained hardware and front sticky wwmmm recovery via G4/6; no timing/load acceptance",
              "h_cells": a.h_cells, "max_link": a.max_link, "cases": cases,
              "counts": dict(Counter(str(c["best"]["added_G"]) if c["best"] else "none" for c in cases)),
              "sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), a.variants / "summary.json"]}}
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ["cases", "sha256"]}))


if __name__ == "__main__":
    main()
