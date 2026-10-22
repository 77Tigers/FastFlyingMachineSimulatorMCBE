"""Add one forward G pickup cell and move its observer beside the tip sticky."""
import os as _research_os
import argparse
import copy
import json
import subprocess
from pathlib import Path

from assemble import Flyer, ROOT, port_pos
from fastflyer import Block
from joint_tip_layout import near, direction


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("existing forward pickup experiment")
    a.output.mkdir(parents=True)
    old = json.loads((a.source/"problem.json").read_text())
    base = Flyer.load(a.source/"problem.flyer")
    obs = max((p for p,b in base._cells.items() if b.kind == 7), key=lambda p:p[0])
    sticky = next(p for p,b in base._cells.items() if b.kind == 9 and b.sticky and p[0] == 21)
    candidates = sorted(near(obs[1:]) & near(sticky[1:]))
    state = {"scope":"G forward pickup geometry; tip supplied control; other natural actions retained", "cases":[]}
    for yz in candidates:
        at = (obs[0],*yz)
        if at in base._cells:
            continue
        f = Flyer.load(a.source/"problem.flyer")
        f.remove(obs)
        f.set(obs,Block.decode(2))
        f.set(at,Block.observer(direction(yz,sticky[1:])))
        out = a.output/f"case{len(state['cases']):04d}"
        out.mkdir()
        f.save(out/"problem.flyer")
        assert f._cells == Flyer.load(out/"problem.flyer")._cells
        c = copy.deepcopy(old)
        for p in c["ports"]:
            if p["name"] == "tip" or p["name"].startswith("tip_extra"):
                p["role"] = "input"
        c["ports"].append({"name":"G_forward_pickup","at":list(obs),"word":"wmmmw","role":"output"})
        c["required_cells"] = [{"at":list(p),"cell":b.encode()} for p,b in f._cells.items() if b.kind != 10]
        c["boundary_envelope"] = {"min":[min(p[k] for p in f._cells)-5 for k in range(3)],"max":[max(p[k] for p in f._cells)+5 for k in range(3)]}
        rows = [tuple(map(int,s.split())) for s in (a.source/old["prescribed_script"]).read_text().splitlines()]
        tip = next(p for p in c["ports"] if p["name"] == "tip")
        rows += [(t,*port_pos(tip,t,10,3),11) for t in range(30) if t%10 in (0,2,8)]
        c.update(flyer="problem.flyer",prescribed_script="drive.txt",name="G_forward_pickup")
        (out/"problem.json").write_text(json.dumps(c,indent=2)+"\n",encoding="utf-8")
        (out/"drive.txt").write_text("\n".join(" ".join(map(str,r)) for r in sorted(rows))+"\n")
        subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/"problem.json"),str(out/"result.json"),"10","4"],capture_output=True)
        report = json.loads((out/"result.json").read_text())
        state["cases"].append({"case":out.name,"observer":at,**report})
        if report["verified"]:
            state["lead"] = str(out)
            break
    (a.output/"summary.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state))


if __name__ == "__main__":
    main()
