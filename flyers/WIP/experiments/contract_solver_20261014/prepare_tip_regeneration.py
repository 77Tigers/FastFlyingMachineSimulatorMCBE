"""Expose tip strokes on a regenerated G variant, preserving all other actions."""
import argparse
import json
from pathlib import Path

from assemble import Flyer, port_pos


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("original_tip", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("existing tip regeneration")
    a.output.mkdir(parents=True)
    c = json.loads((a.source / "problem.json").read_text())
    old = json.loads((a.original_tip / "problem.json").read_text())
    anchor = lambda q: next(p["at"] for p in q["ports"] if p["name"] == "T0")
    delta = tuple(b-v for v,b in zip(anchor(old),anchor(c)))
    sh = lambda p: tuple(v+d for v,d in zip(p,delta))
    reference = Flyer.load(a.original_tip / "problem.flyer")
    f = Flyer.load(a.source / "problem.flyer")
    required = {tuple(p["at"]) for p in old["required_cells"]}
    removed = {p for p,b in reference._cells.items() if b.kind in (6,9) and p not in required}
    assert len(removed) == 5, removed
    for p in list(removed):
        b = reference._cells[p]
        if b.kind == 9 and b.state == 2:
            assert b.direction == 0
            removed.add((p[0]+1,*p[1:]))
    for p in removed:
        assert f._cells[sh(p)].encode() == reference._cells[p].encode()
        f.remove(sh(p))
    f.save(a.output / "problem.flyer")
    assert f._cells == Flyer.load(a.output / "problem.flyer")._cells
    target, tip = next((i,p) for i,p in enumerate(c["ports"]) if p["name"] == "tip")
    for p in c["ports"]:
        if p["name"] == "tip" or p["name"].startswith("tip_extra"):
            p["role"] = "input"
    rows = [tuple(map(int,s.split())) for s in (a.source/c["prescribed_script"]).read_text().splitlines()]
    rows += [(t,*port_pos(tip,t,10,3),11) for t in range(30) if t%10 in (0,2,8)]
    c.update(name="regenerated_G_tip_control",flyer="problem.flyer",prescribed_script="drive.txt")
    (a.output/"problem.json").write_text(json.dumps(c,indent=2)+"\n",encoding="utf-8")
    (a.output/"drive.txt").write_text("\n".join(" ".join(map(str,row)) for row in sorted(rows))+"\n")
    (a.output/"preparation.json").write_text(json.dumps({"source":str(a.source),"original_tip":str(a.original_tip),"removed_optional_hardware":[sh(p) for p in sorted(removed)],"target_port":target},indent=2)+"\n",encoding="utf-8")
    print(f"prepared supplied-tip control, target {target}")


if __name__ == "__main__":
    main()
