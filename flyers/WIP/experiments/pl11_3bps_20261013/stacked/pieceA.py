"""Piece A: n3_134 back loop + one extra normal piston riding each back body (stand-in for a front pusher), all caps 11."""
import json, shutil, subprocess, sys, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "extract"))
import xlib as X
from xlib import Flyer, Block, Kind, ROOT, DIRECTIONS
SRC = ROOT / "flyers/extension_bank/n3/n3_134"
PLAN = ROOT / "flyers/WIP/experiments/pl11_3bps_20261013/extract/work/human_3bps_original/R/t100p1np/plan.json"
plan = json.load(open(PLAN))
base = Flyer.load(SRC / "candidate.flyer")
ORDERS = X.ORDERS

def make(dirp: Path, pistons, cap=11):
    """pistons: list of (pos, dir). Writes candidate + contracts (bounded, new envelope) + drive with caps."""
    dirp.mkdir(parents=True, exist_ok=True)
    f = Flyer(rng_state=base.rng_state, phase_x=base.phase_x, phase_z=base.phase_z, push_limit=base.push_limit)
    for p, b in base.blocks(): f.set(p, b)
    for p, d in pistons:
        if f.get(p) is not None: return None
        f.set(p, Block.piston(d))
    f.save(dirp / "candidate.flyer")
    g = Flyer.load(dirp / "candidate.flyer")
    if {p: b.encode() for p, b in g.blocks()} != {**{p: b.encode() for p, b in base.blocks()}, **{p: Block.piston(d).encode() for p, d in pistons}}:
        return None  # canonical save would translate
    rows = [l.split() for l in (SRC / "drive.txt").read_text().split("\n") if l.strip()]
    (dirp / "drive.txt").write_text("\n".join(" ".join(r[:4] + [str(min(int(r[4]), cap))]) for r in rows) + "\n")
    ids = [p for p, b in g.blocks() if b.kind != Kind.PISTON_ARM]
    env = {"min": [min(p[i] for p in ids) for i in range(3)], "max": [max(p[i] for p in ids) for i in range(3)]}
    for o in ORDERS:
        c = json.loads((SRC / f"{o}.json").read_text())
        for p in c["ports"]:
            if "baseline_load" in p:
                p["baseline_load"] = [None if b is None else min(b, cap) for b in p["baseline_load"]]
        c["boundary_envelope"] = env
        c["name"] = f"stackedA-{o}"
        (dirp / f"bounded_{o}.json").write_text(json.dumps(c, indent=2) + "\n")
    return g

def passes(dirp):
    return [o for o in ORDERS if X.evaluate(dirp, "bounded", o).get("pass")]

def candidates(body):
    cells = {tuple(p) for p in plan["pinned"][body]}
    glue = [tuple(p) for p in cells if base.get(tuple(p)).kind in (Kind.SLIME, Kind.HONEY)]
    out = set()
    for g in glue:
        for d in DIRECTIONS:
            q = (g[0] + d[0], g[1] + d[1], g[2] + d[2])
            if q[1] >= 0 and base.get(q) is None: out.add(q)
    return sorted(out)

if __name__ == "__main__":
    res = {}
    for b in plan["pinned"]:
        ok = []
        for q in candidates(b):
            d = HERE / "A_work" / f"{b}_{q[0]}_{q[1]}_{q[2]}"
            if make(d, [(q, 0)]) is None: continue
            po = passes(d)
            if po: ok.append((q, po))
        res[b] = ok
        print(b, len(candidates(b)), "candidates;", len(ok), "pass:", [(q, [o[0] for o in po]) for q, po in ok][:12], flush=True)
    json.dump({b: [[list(q), po] for q, po in v] for b, v in res.items()}, open(HERE / "A_single.json", "w"))
