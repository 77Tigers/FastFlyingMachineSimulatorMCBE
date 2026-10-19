"""Add the front's own sticky and helper-carried power; back's slot2 pull natural.

Front fully natural; back slots0/1, neighbor and helper remain supplied. Local only.
"""
import argparse
import json
from pathlib import Path

from assemble import Flyer, ext_contract, port_pos
from fastflyer import Block


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("compact", type=Path, help="compact run's source directory")
    ap.add_argument("output", type=Path)
    ap.add_argument("--cycles", type=int, default=3)
    a = ap.parse_args()
    if a.cycles < 1: raise ValueError("positive cycle count required")
    f = Flyer.load(a.compact / "problem.flyer")
    c = json.loads((a.compact / "problem.json").read_text())
    # Source compact uses the split interface's [16,2,0] translation.
    shift = lambda p: (p[0]+16,p[1]+2,p[2])
    added = [((1,-2,0),Block.piston(1,sticky=True)),((2,-2,-1),Block.decode(6))]
    added += [(p,Block.decode(2)) for p in ((3,1,0),(3,1,-1),(3,0,-1),(3,-1,-1),(3,-2,-1))]
    for p,b in added:
        q = shift(p)
        if q in f._cells: raise ValueError("overlap")
        f.set(q,b)
    target = a.output / "source"
    target.mkdir(parents=True,exist_ok=True)
    f.save(target / "problem.flyer")
    g = Flyer.load(target / "problem.flyer")
    minimum = lambda cells: tuple(min(p[i] for p in cells) for i in range(3))
    delta = tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)))
    sh = lambda p: tuple(x+d for x,d in zip(p,delta))
    if {sh(p):b.encode() for p,b in f._cells.items()} != {p:b.encode() for p,b in g._cells.items()}:
        raise ValueError("unexpected normalization")
    for port in c["ports"]: port["at"] = list(sh(port["at"]))
    c.update(name="split_front_link",cycles=a.cycles)
    c["required_cells"] = [{"at":list(p),"cell":b.encode()} for p,b in g._cells.items() if b.kind != 10]
    c["boundary_envelope"] = {"min":[min(p[i] for p in g._cells)-5 for i in range(3)],
                              "max":[max(p[i] for p in g._cells)+5 for i in range(3)]}
    (target/"problem.json").write_text(json.dumps(c,indent=2)+"\n")
    check = a.output/"check"
    if ext_contract(c,0,11,check,target/"problem.flyer",None) != (0,0,0):
        raise ValueError("unexpected extension shift")
    back = next(p for p in c["ports"] if p["name"] == "back")
    omitted = {(t,*port_pos(back,t,c["period_ticks"],c["advance"]))
               for t in range(4,a.cycles*10,10)}
    rows = [list(map(int,line.split())) for line in (check/"drive.txt").read_text().splitlines()]
    kept = [row for row in rows if tuple(row[:4]) not in omitted]
    if len(rows)-len(kept) != a.cycles: raise ValueError("missing supplied back stroke")
    (check/"drive.txt").write_text("\n".join(" ".join(map(str,row)) for row in kept)+"\n")
    contract = json.loads((check/"problem.json").read_text())
    for order in ("before_natural","after_natural","interleaved"):
        (check/f"{order}.json").write_text(json.dumps(dict(contract,prescribed_order=order),indent=2)+"\n")
    (a.output/"construction.json").write_text(json.dumps({"natural_flyer":False,
        "scope":"front all moves natural; back slot2 natural; other strokes supplied",
        "normalization_delta":delta,"added":[[*sh(shift(p)),b.encode()] for p,b in added],
        "helper_body_cells":8,"front_body_cells":8},indent=2)+"\n")


if __name__=="__main__":
    main()
