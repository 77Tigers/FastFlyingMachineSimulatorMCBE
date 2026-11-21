"""Audit the encoded limit and its lower control. Label simulator loads by tower and level."""

import argparse
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

from fastflyer import Flyer

HERE = Path(__file__).resolve().parent
BIN = HERE.parents[4] / "target" / "release"


def audit(path):
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        working = Path(tmp) / path.name
        flyer = Flyer.load(str(path))
        encoded = flyer.push_limit
        for pl in (encoded, encoded - 1):
            for phase in (0, 7):
                flyer.push_limit = pl
                flyer.phase_x = flyer.phase_z = phase
                flyer.rng_state = 0
                flyer.save(str(working))
                for ticks in (240, 10000):
                    out = subprocess.check_output(
                        [BIN / "fastflyer-research", "audit", working, str(ticks), "0"],
                        text=True,
                    )
                    print(out.replace(str(working), path.name).strip(), flush=True)
                    v = {k: int(x) for k, x in re.findall(r"(\w+)=(-?\d+)", out)}
                    assert (v["limit"], v["phase_x"], v["phase_z"]) == (
                        pl,
                        phase,
                        phase,
                    )
                    clean = not any(
                        v[k]
                        for k in (
                            "extension_failures",
                            "movement_failures",
                            "conservation_mismatch_ticks",
                        )
                    )
                    passed = clean and v["distance"] >= ticks // 3
                    assert passed == (pl == encoded)


def ledger(path, geometry, start):
    blocks = defaultdict(list)
    metadata = {}
    for row in geometry.read_text().splitlines()[1:]:
        body, kind, *coord = row.split()
        body = int(body)
        if kind == "body":
            metadata[body] = list(map(int, coord))
        else:
            blocks[body, kind].append(tuple(map(int, coord)))
    # Serialization translates the world by an integral chunk offset. Glue keeps its shape.
    flyer = Flyer.load(str(path))
    from fastflyer import Kind

    saved = [p for p, b in flyer.blocks() if b.kind in (Kind.SLIME, Kind.HONEY)]
    raw = {}
    for i, (_, _, rest, _) in metadata.items():
        dx = sum((s - rest) % 6 >= 2 for s in range(start))
        for x, y, z in blocks[i, "G"]:
            raw[x + dx, y, z] = i
    offset = tuple(a - b for a, b in zip(map(min, zip(*saved)), map(min, zip(*raw))))
    labels = {tuple(a + b for a, b in zip(p, offset)): i for p, i in raw.items()}
    assert set(saved) == set(labels)
    output = subprocess.check_output(
        [BIN / "flyer-ledger", path, "--t0", "0", "--period", "12", "--periods", "2"],
        text=True,
    )
    body_ids = {}
    for key, x, y, z in re.findall(
        r"^b(\d+):.*?e.g. \((-?\d+),(-?\d+),(-?\d+)\)", output, re.MULTILINE
    ):
        body_ids[int(key)] = labels[int(x), int(y), int(z)]
    assert set(body_ids.values()) == set(metadata)
    loads = defaultdict(list)
    for tick, action, load, key in re.findall(
        r"tick\s+(\d+) slot \d+ (\w+)\s+load\s+(\d+)\s+moves (b\d+)\s", output
    ):
        loads[body_ids[int(key[1:])]].append((int(tick), action, int(load)))
    actors = re.findall(
        r"tick\s+(\d+) slot \d+ (\w+)\s+load\s+[1-9]\d* .*?piston #(\d+)", output
    )
    pistons = sum(len(blocks[i, k]) for i in metadata for k in ("H", "L", "S"))
    assert len({actor for _, _, actor in actors}) == pistons
    pushes = sum(int(t) < 12 and a == "extend" for t, a, _ in actors)
    pulls = sum(int(t) < 12 and a == "retract" for t, a, _ in actors)
    print(
        "active pistons",
        pistons,
        "loaded pushes per period",
        pushes,
        "loaded pulls",
        pulls,
    )
    for i, (c, j, rest, _) in metadata.items():
        actions = loads[i]
        assert len(actions) == 8
        peak = max(m[2] for m in actions)
        sizes = [len(blocks[i, k]) for k in ("G", "R", "S")]
        print(
            "body",
            c,
            "level",
            j,
            "glue, red, sticky",
            *sizes,
            "piston riders",
            peak - sum(sizes),
            "peak",
            peak,
            "loads",
            [m[2] for m in actions[:4]],
        )
    assert max(v for acts in loads.values() for _, _, v in acts) == flyer.push_limit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("flyer", type=Path)
    parser.add_argument("geometry", type=Path)
    parser.add_argument("--slot", type=int, choices=range(6), required=True)
    args = parser.parse_args()
    audit(args.flyer)
    ledger(args.flyer, args.geometry, args.slot)
