"""Piece B (fresh arrangement): X=B9 (bank shape), T=B33 shape shifted up one row so that T's first-fired pusher (y=3) touches no X cell
and is carried by a supplied glue cell N above it; second pusher (y=1) is carried by X at s1,s2 and rides T at s3."""
import json, sys, copy
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "extract"))
import xlib as X
from xlib import Flyer, Block, Kind
SRC = HERE / "B0_work/p1np"
OUT = HERE / "pieceB"
base = Flyer.load(SRC / "candidate.flyer")
bc = json.loads((SRC / "bounded_before_natural.json").read_text())
Xcells = {(14,2,9),(14,2,10),(15,2,9),(16,1,9),(16,2,9),(17,0,9),(17,1,9),(17,1,10),(17,2,9)}
def build(dy=1, ncells=((17,4,8),), nmat=Kind.SLIME, out=OUT, cap=11, nword="mmmww", extra_pistons=()):
    out.mkdir(parents=True, exist_ok=True)
    f = Flyer(rng_state=base.rng_state, phase_x=base.phase_x, phase_z=base.phase_z, push_limit=base.push_limit)
    mv = lambda p: p if p in Xcells else (p[0], p[1] + dy, p[2])
    for p, b in base.blocks():
        f.set(mv(p), b)
    for p, b in base.blocks():
        if b.kind == Kind.PISTON:
            ob = base.get_piston_blocks(p)
            if ob: f.set_piston_blocks(mv(p), [mv(q) for q in ob])
    for c in ncells: f.set(c, Block(nmat))
    for c, d in extra_pistons: f.set(c, Block.piston(d))
    f.save(out / "candidate.flyer")
    g = Flyer.load(out / "candidate.flyer")
    want = {}
    for p, b in f.blocks(): want[p] = b.encode()
    assert {p: b.encode() for p, b in g.blocks()} == want, "save translated"
    # ports
    ports = []
    rows = []
    word = lambda w: "".join("m" if i in w else "w" for i in range(5))
    def port(name, at, w, presc, caps, role="input", cap_=None):
        p = {"name": name, "role": role, "at": list(at), "word": word(w)}
        if role == "input":
            base_l = [(cap_ or cap) if i in w else None for i in range(5)]
            p["baseline_load"] = base_l; p["spare_load"] = [None if b is None else 0 for b in base_l]
            for s in presc:
                for cyc in range(3):
                    x = at[0] + cyc * 3 + sum(1 for q in w if q < s)
                    t = cyc * 10 + 2 * s
                    rows.append((t, -x, len(rows), f"{t} {x} {at[1]} {at[2]} {base_l[s]}"))
        ports.append(p)
    # X = b9 (cell (17,1,10)? use (15,2,9)); word mmmww, s0,s1 supplied, s2 natural pull
    port("x", (15,2,9), (0,1,2), (0,1), None)
    port("t", mv((20,0,8)), (3,4,0), (0,), None)
    port("n", ncells[0], tuple(i for i, ch in enumerate(nword) if ch == "m"), tuple(i for i, ch in enumerate(nword) if ch == "m"), None)
    # power cell (word of the old PW: slots 1,2,3 per the reference link)
    pw = [p for p in bc["ports"] if p["name"].startswith("pw")][0]
    pws = tuple(i for i, ch in enumerate(pw["word"]) if ch == "m")
    c = copy.deepcopy(pw); port("pw", mv(tuple(pw["at"])), pws, pws, None, cap_=1)
    rows.sort()
    lines = [r[3] for r in rows]
    (out / "drive.txt").write_text("\n".join(lines) + "\n")
    req = [{"at": list(p), "cell": want[p]} for p in sorted(want) if (g.get(p).kind != Kind.PISTON_ARM and g.get(p).kind != Kind.PISTON)]
    idp = [p for p in want if (want[p] & 15) != 10]
    env = {"min": [min(p[i] for p in idp) for i in range(3)], "max": [max(p[i] for p in idp) for i in range(3)]}
    for rec in ("exact", "bounded"):
        for o in X.ORDERS:
            cc = {"version": 1, "name": f"stackedB-{o}", "flyer": "candidate.flyer", "prescribed_script": "drive.txt", "prescribed_order": o,
                  "period_ticks": 10, "advance": 3, "cycles": 3, "recurrence": rec, "ports": ports, "required_cells": req}
            if rec == "bounded": cc["boundary_envelope"] = env
            (out / f"{rec}_{o}.json").write_text(json.dumps(cc, indent=2) + "\n")
    return g
if __name__ == "__main__":
    build()
    res = X.evaluate_all(OUT)
    for k, v in res.items(): print(k, v.get("pass"), v.get("samples_passed"), str(v.get("first_failure"))[:200])
