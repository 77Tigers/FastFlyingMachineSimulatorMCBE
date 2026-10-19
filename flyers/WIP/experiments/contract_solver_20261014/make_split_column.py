"""Fresh local split-carrier column interface; surrounding strokes are supplied.

This is a geometry/pickup experiment, not a closed natural flyer.
"""
import argparse
import json
from pathlib import Path

from assemble import ext_contract, Flyer
from fastflyer import Block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare-checks", action="store_true",
                        help="cap and extend an existing column-witness check to three cycles")
    args = parser.parse_args()
    # Adjacent column rows share a trailing glue corner, which carries whichever
    # piston fires second. Separate rear carriers each recover one fixed row.
    shapes = [([(1,-1,0),(1,0,0),(1,0,1),(1,-1,1),(0,-1,1)],1,"mwwmm"),
              ([(-2,-2,0)],2,"mmmww"), ([(-2,0,2)],2,"mmmww")]
    f = Flyer(push_limit=11)
    for cells, material, _ in shapes:
        for p in cells: f.set(p,Block.decode(material))
    args.output.mkdir(parents=True, exist_ok=True)
    f.save(args.output / "problem.flyer")
    g = Flyer.load(args.output / "problem.flyer")
    minimum = lambda cells: tuple(min(p[i] for p in cells) for i in range(3))
    d = tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)))
    shift = lambda p: [a+b for a,b in zip(p,d)]
    c = {"version":1,"name":"fresh_split_column","flyer":"problem.flyer","period_ticks":10,
         "advance":3,"cycles":3,"recurrence":"bounded",
         "boundary_envelope":{"min":[min(p[i] for p in g._cells)-4 for i in range(3)],
                              "max":[max(p[i] for p in g._cells)+4 for i in range(3)]},
         "ports":[{"name":name,"role":"output","at":shift(cells[0]),"word":word}
                  for name,(cells,_,word) in zip(("front","back","front_neighbor"),shapes)],
         "required_cells":[{"at":shift(p),"cell":material} for cells,material,_ in shapes for p in cells]}
    (args.output / "problem.json").write_text(json.dumps(c,indent=2)+"\n")
    delta = ext_contract(c,0,11,args.output / "body0",args.output / "problem.flyer",None)
    if delta != (0,0,0): raise ValueError("unexpected extension shift")
    hardware = [(0,0,0,6),(-2,-1,0,9),(-1,0,1,2057),(0,0,1,10)]
    (args.output / "column.json").write_text(json.dumps([shift(p[:3])+[p[3]] for p in hardware])+"\n")
    (args.output / "scope.json").write_text(json.dumps({"natural_flyer":False,
        "supplied":"both carriers plus front's slot0 stroke","natural":"front pushes at slots3,4",
        "provenance":"fresh cells and column template; no reference hardware", "translation":d},indent=2)+"\n")
    if args.prepare_checks:
        target = args.output / "check"
        fixture = Flyer.load(target / "solution.flyer")
        envelope = {"min":[min(p[i] for p in fixture._cells)-4 for i in range(3)],
                    "max":[max(p[i] for p in fixture._cells)+4 for i in range(3)]}
        drive = target / "solution_drive.txt"
        first = [list(map(int,line.split())) for line in drive.read_text().splitlines()
                 if int(line.split()[0]) < 10]
        rows = sorted((t+10*k,x+3*k,y,z,11) for k in range(3) for t,x,y,z,_ in first)
        drive.write_text("\n".join(" ".join(map(str,row)) for row in rows)+"\n")
        for order in ("before_natural","after_natural","interleaved"):
            path = target / f"solution_{order}.json"
            contract = json.loads(path.read_text())
            contract.update(cycles=3,boundary_envelope=envelope)
            path.write_text(json.dumps(contract,indent=2)+"\n")


if __name__ == "__main__":
    main()
