"""Victim-carried observer, aligned with the helper puller only at its fire slot.

Extends the split front by three glue cells, or two with --direct. Rear carriers and helper remain
prescribed; all three front moves are natural. No closed flyer is claimed.
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
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--direct", action="store_true", help="two support cells; observer powers sticky directly")
    parser.add_argument("--compact", action="store_true", help="with --direct: trim two glue cells and move redstone into trailing corner")
    args = parser.parse_args()
    if args.compact and not args.direct: raise ValueError("--compact requires --direct")
    if args.cycles < 1: raise ValueError("positive cycle count required")
    f = Flyer.load(args.interface / "check/solution.flyer")
    c = json.loads((args.interface / "problem.json").read_text())
    d = json.loads((args.interface / "scope.json").read_text())["translation"]
    shift = lambda p:tuple(a+b for a,b in zip(p,d))
    helper = (3,1,1) if args.direct else (3,-1,1)
    observer = (4,-1,1) if args.direct else (4,-2,1)
    supports = ((2,-1,1),(3,-1,1)) if args.direct else ((1,-2,1),(2,-2,1),(3,-2,1))
    added = [(helper,Block.decode(2)),((3,0,1),Block.piston(1,sticky=True,state=2)),
             ((2,0,1),Block.decode(10)),(observer,Block.observer(2,powered=True))]
    added += [(p,Block.decode(1)) for p in supports]
    for p,b in added:
        q = shift(p)
        if q in f._cells: raise ValueError("overlap")
        f.set(q,b)
    if args.compact:
        for p in ((0,-1,1),(1,0,0),(0,0,0)):
            f.remove(shift(p))
        f.set(shift((0,-1,1)),Block.decode(6))
    f.push_limit=11
    (args.output / "source").mkdir(parents=True,exist_ok=True)
    f.save(args.output / "source/problem.flyer")
    if {p:b.encode() for p,b in f._cells.items()} != {p:b.encode() for p,b in Flyer.load(args.output / "source/problem.flyer")._cells.items()}:
        raise ValueError("unexpected save normalization")
    name = "split_puller_compact" if args.compact else "split_puller_direct" if args.direct else "split_puller_selective"
    c.update(name=name,flyer="problem.flyer",cycles=args.cycles)
    c["ports"].append({"name":"pull_helper","role":"output","at":list(shift(helper)),"word":"wmmmw"})
    c["required_cells"]=[{"at":list(p),"cell":b.encode()} for p,b in f._cells.items() if b.kind != 10]
    c["boundary_envelope"]={"min":[min(p[i] for p in f._cells)-5 for i in range(3)],
                              "max":[max(p[i] for p in f._cells)+5 for i in range(3)]}
    (args.output / "source/problem.json").write_text(json.dumps(c,indent=2)+"\n")
    ext_contract(c,0,11,args.output / "check",args.output / "source/problem.flyer",None)
    contract=json.loads((args.output / "check/problem.json").read_text())
    for order in ("before_natural","after_natural","interleaved"):
        (args.output / f"check/{order}.json").write_text(json.dumps(dict(contract,prescribed_order=order),indent=2)+"\n")
    (args.output / "construction.json").write_text(json.dumps({"natural_flyer":False,
        "power":"observer moves with front; +Y power to sticky directly only at slot4" if args.direct else "observer moves with front; +Y hard-power to honey helper only at slot4",
        "extra_front_glue":len(supports),"compact_column":args.compact,
        "trimmed_glue":[list(shift(p)) for p in ((0,-1,1),(1,0,0))] if args.compact else [],
        "redstone_at":list(shift((0,-1,1))) if args.compact else list(shift((0,0,0))),
        "added":[[*shift(p),b.encode()] for p,b in added]},indent=2)+"\n")


if __name__=="__main__":
    main()
