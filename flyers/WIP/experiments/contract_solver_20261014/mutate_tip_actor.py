"""Move the optional extended tip actor implicated in the G/H bridge.

Preserve geometry and every natural/supplied obligation; move its arm with it,
or test a retracted start. Every variant gets strict encoded11 standard checks.
"""
import argparse
import copy
import itertools
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer, ROOT
from fastflyer import Block


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--seconds", type=float, default=120)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("existing mutation search")
    a.output.mkdir(parents=True)
    base = Flyer.load(a.source / "problem.flyer")
    original = json.loads((a.source / "problem.json").read_text())
    required = {tuple(r["at"]) for r in original["required_cells"]}
    targets = [p for p, b in base._cells.items() if b.kind == 9 and b.state == 2 and p not in required]
    assert len(targets) == 1, targets
    actor = targets[0]
    arm = (actor[0]+1, *actor[1:])
    assert base._cells[arm].kind == 10 and base._cells[actor].direction == 0
    drive = [list(map(int, s.split())) for s in (a.source / original["prescribed_script"]).read_text().splitlines()]
    state = {"scope": "optional tip actuator/arm placement; T/G/H all natural; other rear strokes supplied",
             "source": str(a.source), "actor": actor, "cases": [], "complete": False}
    save = lambda: (a.output / "summary.json").write_text(json.dumps(state, indent=2)+"\n", encoding="utf-8")
    start = time.monotonic()
    offsets = sorted((d for d in itertools.product(range(-2, 3), repeat=3) if sum(map(abs, d)) <= 2), key=lambda d:(sum(map(abs, d)),d))
    for delta, extended, sticky in itertools.product(offsets, (True, False), (False, True)):
        if delta == (0, 0, 0) and extended and not sticky:
            continue
        if time.monotonic() - start >= a.seconds:
            break
        f = Flyer.load(a.source / "problem.flyer")
        f.remove(actor)
        f.remove(arm)
        at = tuple(p+d for p, d in zip(actor, delta))
        tip = (at[0]+1, *at[1:])
        if at in f._cells or (extended and tip in f._cells):
            continue
        f.set(at, Block.piston(0, sticky=sticky, state=2 if extended else 0))
        if extended:
            f.set(tip, Block.decode(10))
        out = a.output / f"case{len(state['cases']):04d}"
        out.mkdir()
        f.save(out / "problem.flyer")
        g = Flyer.load(out / "problem.flyer")
        minimum = lambda cells: tuple(min(p[k] for p in cells) for k in range(3))
        shift = tuple(b-v for v,b in zip(minimum(f._cells), minimum(g._cells)))
        sh = lambda p:[v+d for v,d in zip(p,shift)]
        assert {tuple(sh(p)):b.encode() for p,b in f._cells.items()} == {p:b.encode() for p,b in g._cells.items()}
        c = copy.deepcopy(original)
        for p in c["ports"]:
            p["at"] = sh(p["at"])
        for r in c["required_cells"]:
            r["at"] = sh(r["at"])
        c["boundary_envelope"] = {k:sh(v) for k,v in c["boundary_envelope"].items()}
        c.update(flyer="problem.flyer", prescribed_script="drive.txt")
        (out / "problem.json").write_text(json.dumps(c, indent=2)+"\n", encoding="utf-8")
        (out / "drive.txt").write_text("\n".join(" ".join(map(str,(t,*sh((x,y,z)),cap))) for t,x,y,z,cap in drive)+"\n")
        subprocess.run([str(ROOT / "target/release/contract-verify.exe"),str(out / "problem.json"),str(out / "result.json"),"10","4"], capture_output=True)
        report = json.loads((out / "result.json").read_text())
        state["cases"].append({"case":out.name,"delta":delta,"extended":extended,"sticky":sticky,**report})
        save()
        if report["verified"]:
            state["lead"] = str(out)
            break
    else:
        state["complete"] = True
    state["elapsed_seconds"] = time.monotonic()-start
    save()
    print(json.dumps({k:v for k,v in state.items() if k!="cases"}))


if __name__ == "__main__":
    main()
