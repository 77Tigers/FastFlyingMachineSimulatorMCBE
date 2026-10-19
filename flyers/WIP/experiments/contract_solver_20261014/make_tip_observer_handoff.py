"""Selective tip power by handing an observer between the tip and honey helper.

Observer misses tip slot0, moves at slot1 (safe race), then with G at slots2/3.
Its slot2 pulse aligns; later pulses miss. Tip strokes remain supplied. Local.
"""
import argparse
import json
from pathlib import Path

from assemble import Flyer,port_pos
from fastflyer import Block


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shared",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--limit",type=int,default=11)
    ap.add_argument("--cycles",type=int,default=3)
    a=ap.parse_args()
    source=a.shared/"check"; f=Flyer.load(source/"problem.flyer")
    c=json.loads((source/"before_natural.json").read_text())
    # Coordinates in the verified shared12 frame (Y one lower than case000).
    added=[((20,2,17),Block.decode(2)),((21,2,17),Block.decode(2)),
           ((21,2,16),Block.decode(1)),((21,2,15),Block.piston(1,sticky=True)),
           ((22,2,17),Block.observer(5))]
    for p,b in added:
        if p in f._cells: raise ValueError("overlap")
        f.set(p,b)
    f.push_limit=a.limit
    check=a.output/"check"; check.mkdir(parents=True,exist_ok=True)
    f.save(check/"problem.flyer")
    if Flyer.load(check/"problem.flyer").content_hash()!=f.content_hash(): raise ValueError("normalization")
    helper=next(p for p in c["ports"] if p["name"]=="pull_helper"); helper["role"]="output"
    tip={"name":"tip_helper","role":"input","at":[21,2,16],"word":"mmwwm"}; c["ports"].append(tip)
    c.update(cycles=a.cycles,name="tip_observer_handoff")
    c["required_cells"]=[{"at":list(p),"cell":b.encode()} for p,b in f._cells.items() if b.kind!=10]
    c["boundary_envelope"]={"min":[min(p[i] for p in f._cells)-5 for i in range(3)],"max":[max(p[i] for p in f._cells)+5 for i in range(3)]}
    first=[list(map(int,line.split())) for line in (source/"drive.txt").read_text().splitlines() if int(line.split()[0])<10]
    first=[r for r in first if tuple(r[:4])!=(6,*port_pos(helper,6,10,3))]
    first += [(t,*port_pos(tip,t,10,3),a.limit) for t in (0,2,8)]
    rows=sorted((t+10*k,x+3*k,y,z,a.limit) for k in range(a.cycles) for t,x,y,z,_ in first)
    (check/"drive.txt").write_text("\n".join(" ".join(map(str,r)) for r in rows)+"\n")
    for order in ("before_natural","after_natural","interleaved"):
        (check/f"{order}.json").write_text(json.dumps(dict(c,prescribed_order=order),indent=2)+"\n")
    (a.output/"construction.json").write_text(json.dumps({"natural_flyer":False,
        "scope":"front/helper all moves and rear slot2 natural; rear slots0/1, neighbor and tip supplied",
        "added":[[*p,b.encode()] for p,b in added],"helper_body_without_observer":10,
        "reproduction":f"make_tip_observer_handoff.py SHARED OUT --limit {a.limit} --cycles 1000"},indent=2)+"\n")


if __name__=="__main__": main()
