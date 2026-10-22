"""Bound one-source repairs around an unpowered generated completion actor.

Uses exact rejected hardware witnesses, with no geometry or simulator change.
Every proposal still needs strict all-sample certification and long validation.
"""
import os as _research_os
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from assemble import Flyer
from fastflyer import Block


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("problem", type=Path)
    ap.add_argument("witness_pool", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--actor", nargs=3, type=int, required=True)
    ap.add_argument("--fire-position", nargs=3, type=int, required=True)
    ap.add_argument("--seconds", type=float, default=180)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("refusing an existing repair run")
    a.output.mkdir(parents=True)
    contract = json.loads(a.problem.read_text(encoding="utf-8"))
    base = Flyer.load(a.problem.parent / contract["flyer"])
    cells = {p: b.encode() for p, b in base._cells.items()}
    positions = set()
    for center in [a.actor, a.fire_position]:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                for dz in range(-2, 3):
                    if abs(dx) + abs(dy) + abs(dz) <= 2:
                        positions.add(tuple(v + d for v, d in zip(center, (dx, dy, dz))))
    sources = [Block.decode(6)]
    sources += [Block.rod(d) for d in range(6)]
    sources += [Block.observer(d, powered=p) for p in (False, True) for d in range(6)]
    pool, metadata, seen = [], [], set()
    for wi, witness in enumerate(json.loads(a.witness_pool.read_text(encoding="utf-8"))):
        occupied = set(cells) | {tuple(row[:3]) for row in witness}
        for source in sources:
            for p in sorted(positions - occupied):
                hardware = sorted(witness + [[*p, source.encode()]])
                key = tuple(tuple(row) for row in hardware)
                if key in seen:
                    continue
                seen.add(key)
                pool.append(hardware)
                metadata.append({"witness": wi, "added": [*p, source.encode()]})
    (a.output / "pool.json").write_text(json.dumps(pool) + "\n", encoding="utf-8")
    (a.output / "proposals.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
    provenance = {"problem": str(a.problem), "witness_pool": str(a.witness_pool),
                  "actor": a.actor, "fire_position": a.fire_position, "proposals": len(pool),
                  "sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [a.problem, a.witness_pool, Path(__file__),
                                       Path(('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else '')))]}}
    (a.output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["python", str(Path(__file__).with_name("certify_column_pool.py")),
                    str(a.problem), str(a.output / "pool.json"), str(a.output / "cert"),
                    "--seconds", str(a.seconds)], check=True)


if __name__ == "__main__":
    main()
