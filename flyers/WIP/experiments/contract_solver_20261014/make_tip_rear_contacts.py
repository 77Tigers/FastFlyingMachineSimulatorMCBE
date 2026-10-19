"""Reference-free 3D tip variants: add one rear slime contact to the fixed tip.

All existing natural actions stay natural. Certify each supplied-tip control
before using it as a new hardware-synthesis scaffold.
"""
import argparse
import copy
import json
import subprocess
from pathlib import Path

from assemble import Flyer, ROOT, port_pos
from fastflyer import Block


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("existing rear-contact variants")
    a.output.mkdir(parents=True)
    base = Flyer.load(a.source / "problem.flyer")
    old = json.loads((a.source / "problem.json").read_text())
    hports = [p for p in old["ports"] if p["name"] == "tip" or p["name"].startswith("tip_extra")]
    assert len(hports) == 5 and all(base._cells[tuple(p["at"])].kind == 1 for p in hports)
    assert not any(p not in {tuple(r["at"]) for r in old["required_cells"]} and b.kind in (6,9) for p,b in base._cells.items())
    state = {"scope":"one new rear tip-glue contact; T/G/back pull natural; tip/rear inputs supplied", "cases":[], "leads":[]}
    for port in hports:
        x,y,z = port["at"]
        at = (x-1,y,z)
        if at in base._cells:
            continue
        f = Flyer.load(a.source / "problem.flyer")
        f.set(at, Block.decode(1))
        out = a.output / f"case{len(state['cases']):04d}"
        out.mkdir()
        f.save(out / "problem.flyer")
        assert f._cells == Flyer.load(out / "problem.flyer")._cells
        c = copy.deepcopy(old)
        for p in c["ports"]:
            if p["name"] == "tip" or p["name"].startswith("tip_extra"):
                p["role"] = "input"
        c["ports"].append({"name":"tip_extra_rear","at":list(at),"word":"mmwwm","role":"input"})
        c["required_cells"].append({"at":list(at),"cell":1})
        rows = [tuple(map(int,s.split())) for s in (a.source / old["prescribed_script"]).read_text().splitlines()]
        tip = next(p for p in c["ports"] if p["name"] == "tip")
        rows += [(t,*port_pos(tip,t,10,3),11) for t in range(30) if t%10 in (0,2,8)]
        c.update(flyer="problem.flyer",prescribed_script="drive.txt",name="tip_rear_contact")
        (out / "problem.json").write_text(json.dumps(c,indent=2)+"\n",encoding="utf-8")
        (out / "drive.txt").write_text("\n".join(" ".join(map(str,r)) for r in sorted(rows))+"\n")
        subprocess.run([str(ROOT / "target/release/contract-verify.exe"),str(out / "problem.json"),str(out / "result.json"),"10","4"],capture_output=True)
        report = json.loads((out / "result.json").read_text())
        state["cases"].append({"case":out.name,"rear_contact":at,**report})
        if report["verified"]:
            state["leads"].append(str(out))
    (a.output / "summary.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in state.items() if k!="cases"}))


if __name__ == "__main__":
    main()
