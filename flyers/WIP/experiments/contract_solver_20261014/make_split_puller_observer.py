"""Add a helper-carried sticky and observer to the fresh split interface.

The entire front word becomes natural; both rear carriers and the helper
remain prescribed. This constructs a local interface, not a natural flyer.
"""
import argparse
import json
from pathlib import Path

from assemble import ext_contract, Flyer
from fastflyer import Block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("interface", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    f = Flyer.load(args.interface / "check/solution.flyer")
    c = json.loads((args.interface / "problem.json").read_text())
    d = json.loads((args.interface / "scope.json").read_text())["translation"]
    shift = lambda p:[a+b for a,b in zip(p,d)]
    added = [(4,0,1,2),(3,0,1,2345),(2,0,1,10),(4,1,1,103)]
    for x,y,z,cell in added:
        p = tuple(shift((x,y,z)))
        if p in f._cells: raise ValueError("new hardware overlaps the split interface")
        f.set(p,Block.decode(cell))
    f.push_limit = 11
    (args.output / "source").mkdir(parents=True,exist_ok=True)
    f.save(args.output / "source/problem.flyer")
    if set(f._cells) != set(Flyer.load(args.output / "source/problem.flyer")._cells):
        raise ValueError("unexpected normalization")
    c["name"] = "split_puller_observer"
    c["ports"].append({"name":"pull_helper","role":"output","at":shift((4,0,1)),"word":"wmmmw"})
    c["required_cells"] = [{"at":list(p),"cell":b.encode()} for p,b in f._cells.items() if b.kind != 10]
    c["boundary_envelope"] = {"min":[min(p[i] for p in f._cells)-5 for i in range(3)],
                               "max":[max(p[i] for p in f._cells)+5 for i in range(3)]}
    (args.output / "source/problem.json").write_text(json.dumps(c,indent=2)+"\n")
    ext_contract(c,0,11,args.output / "check",args.output / "source/problem.flyer",None)
    contract = json.loads((args.output / "check/problem.json").read_text())
    for order in ("before_natural","after_natural","interleaved"):
        q = dict(contract,prescribed_order=order)
        (args.output / f"check/{order}.json").write_text(json.dumps(q,indent=2)+"\n")


if __name__=="__main__":
    main()
