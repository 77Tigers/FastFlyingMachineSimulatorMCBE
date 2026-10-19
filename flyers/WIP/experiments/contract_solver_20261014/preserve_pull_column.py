"""Extract existing pull actors and adjacent power as an explicit retrofit seed.

Usage: preserve_pull_column.py REFERENCE.json TRACE.jsonl PORT_NAME OUT
The reference and trace must share coordinates. The resulting pool is unverified;
certify it with column-assemble against the target contract before integration.
"""
import argparse
import hashlib
import json
from pathlib import Path

from assemble import Flyer, body_of


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("reference", type=Path)
    ap.add_argument("trace", type=Path)
    ap.add_argument("port")
    ap.add_argument("out", type=Path)
    a = ap.parse_args()
    c = json.loads(a.reference.read_text(encoding="utf-8"))
    f = Flyer.load(a.reference.parent / c["flyer"])
    port = next(p for p in c["ports"] if p["name"] == a.port)
    body = body_of(f._cells, tuple(port["at"]))
    initial = {p: b.encode() for p, b in f._cells.items()}
    origins = {p: p for p, cell in initial.items() if cell & 15 != 10}
    snapshots, actors, actions = [], set(), []
    for index, line in enumerate(a.trace.read_text(encoding="utf-8").splitlines()):
        tick = json.loads(line)
        if index == 0:
            assert {tuple(r[:3]): r[3] for r in tick["initial"]} == initial, "reference/trace frame mismatch"
        assert {tuple(r[:3]) for r in tick["initial"] if r[3] & 15 != 10} == set(origins)
        snapshots.append(dict(origins))
        for step in tick["steps"]:
            mv = step.get("movement")
            if not mv or mv["failure"]:
                continue
            src = [tuple(p) for p in mv["sources"]]
            dst = [tuple(p) for p in mv["destinations"]]
            moved = [origins[p] for p in src]
            if body.intersection(moved):
                actor = origins[tuple(step["active_piston"])]
                assert step["action"] == "retract", "target is not pull-only"
                assert initial[actor] & 0x100, "pull actor must be sticky"
                actors.add(actor)
                actions.append({"tick": step["tick"], "actor_origin": actor, "load": len(src)})
            for p in src:
                del origins[p]
            origins.update(zip(dst, moved))
    assert actors and actions
    # A conservative adjacent-source seed, not a power eligibility proof.
    # Native certification checks the actual timing, source motion and loads.
    sources = set()
    for snapshot in snapshots:
        for p, origin in snapshot.items():
            if origin not in actors:
                continue
            for axis in range(3):
                for delta in (-1, 1):
                    q = list(p)
                    q[axis] += delta
                    source = snapshot.get(tuple(q))
                    if source is not None and initial[source] & 15 in (6, 7, 8):
                        sources.add(source)
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    arms = set()
    for p in actors:
        d = directions[(initial[p] >> 5) & 7]
        q = tuple(p[i] + d[i] for i in range(3))
        if initial.get(q, 0) & 15 == 10:
            arms.add(q)
        assert not f._piston_blocks.get(p), "settle moving actors before extracting a pool"
    hardware = [[*p, initial[p]] for p in sorted(actors | sources | arms)]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "pool.json").write_text(json.dumps([hardware]) + "\n", encoding="utf-8")
    evidence = {"scope": "Unverified existing-hardware retrofit seed; not reference-free synthesis.",
                "port": a.port, "actors": sorted(actors), "sources": sorted(sources), "arms": sorted(arms),
                "actions": actions, "hardware": hardware,
                "reference_sha256": hashlib.sha256(a.reference.read_bytes()).hexdigest(),
                "trace_sha256": hashlib.sha256(a.trace.read_bytes()).hexdigest()}
    (a.out / "provenance.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"Preserved {len(actors)} pullers and {len(sources)} adjacent power sources; unverified")


if __name__ == "__main__":
    main()
