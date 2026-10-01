"""Bounded single-block trims of the two clean PL17 graft candidates."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from fastflyer import Flyer, Kind

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
for n in (17, 21):
    src = ROOT / "free_human" / f"c{n:04d}"
    f = Flyer.load(src.with_suffix(".flyer"))
    meta = json.loads(src.with_suffix(".json").read_text())
    p = tuple(meta["ports"][0]["p"])
    # Serialization translates the whole flyer into nonnegative coordinates.
    pistons = [c for c, b in f._cells.items() if b.kind == Kind.PISTON and c[2] == p[2]]
    offsets = []
    for q in pistons:
        d = tuple(q[i] - p[i] for i in range(3))
        if all(tuple(v[i] + d[i] for i in range(3)) in f._cells for v in (tuple(x["p"]) for x in meta["ports"])):
            offsets.append(d)
    assert len(offsets) == 1, (n, offsets)
    d = offsets[0]
    glue = {tuple(c) for c in meta["rail"]}
    for port in meta["ports"]:
        glue.update(map(tuple, port["extra"]))
        glue.update(map(tuple, port["sextra"]))
    for i, c in enumerate(sorted(glue)):
        q = tuple(c[k] + d[k] for k in range(3))
        assert f._cells[q].kind in (Kind.SLIME, Kind.HONEY), (n, c, q, f._cells.get(q))
        g = Flyer.load(src.with_suffix(".flyer"))
        g.push_limit = 16
        del g._cells[q]
        g.save(OUT / f"c{n:04d}_drop{i:02d}.flyer")
    print(n, "offset", d, "glue", len(glue))
