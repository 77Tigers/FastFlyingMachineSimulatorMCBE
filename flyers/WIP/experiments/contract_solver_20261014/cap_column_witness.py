"""Recertify a partial witness at encoded/supplied11, with a repeated input word."""
import argparse
import json
from pathlib import Path

from assemble import Flyer, port_pos


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("witness",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--cycles",type=int,default=3)
    ap.add_argument("--share-power",action="store_true",help="specific helper1351: reuse column source for front sticky")
    a=ap.parse_args()
    if a.cycles < 1: raise ValueError("positive cycle count")
    f=Flyer.load(a.witness/"solution.flyer"); f.push_limit=11
    c=json.loads((a.witness/"solution_before_natural.json").read_text())
    back=next(p for p in c["ports"] if p["name"]=="back")
    old_back=dict(back)
    if a.share_power:
        expected={(18,0,15):6,(19,0,15):2,(17,0,16):297,(14,0,16):2}
        if any(p not in f._cells or f._cells[p].encode()!=v for p,v in expected.items()):
            raise ValueError("share-power requires helper1351 saved frame")
        sticky=f._cells[(17,0,16)]; honey=f._cells[(14,0,16)]
        for p in expected: f.remove(p)
        f.set((17,2,16),sticky); f.set((14,2,16),honey)
        back["at"]=[14,2,16]
    check=a.output/"check"; check.mkdir(parents=True,exist_ok=True)
    f.save(check/"problem.flyer")
    g=Flyer.load(check/"problem.flyer")
    minimum=lambda cells: tuple(min(p[i] for p in cells) for i in range(3))
    delta=tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)))
    sh=lambda p: tuple(x+d for x,d in zip(p,delta))
    if {sh(p):b.encode() for p,b in f._cells.items()}!={p:b.encode() for p,b in g._cells.items()}: raise ValueError("normalization")
    for p in c["ports"]: p["at"]=list(sh(p["at"]))
    c["required_cells"]=[{"at":list(p),"cell":b.encode()} for p,b in g._cells.items() if b.kind!=10]
    c["boundary_envelope"]={k:list(sh(v)) for k,v in c["boundary_envelope"].items()}
    c.update(flyer="problem.flyer",prescribed_script="drive.txt",cycles=a.cycles)
    first=[list(map(int,line.split())) for line in (a.witness/"solution_drive.txt").read_text().splitlines()
           if int(line.split()[0]) < c["period_ticks"]]
    for row in first:
        t,x,y,z,_=row
        if a.share_power and (x,y,z)==port_pos(old_back,t,c["period_ticks"],c["advance"]): y=2
        row[1:4]=sh((x,y,z))
    rows=sorted((t+k*c["period_ticks"],x+k*c["advance"],y,z,11)
                for k in range(a.cycles) for t,x,y,z,_ in first)
    (check/"drive.txt").write_text("\n".join(" ".join(map(str,r)) for r in rows)+"\n")
    for order in ("before_natural","after_natural","interleaved"):
        (check/f"{order}.json").write_text(json.dumps(dict(c,prescribed_order=order),indent=2)+"\n")
    (a.output/"construction.json").write_text(json.dumps({"natural_flyer":False,
        "scope":"front all moves, back slot2, helper slots1/2 natural; back slots0/1, neighbor and helper slot3 supplied",
        "witness":json.loads((a.witness/"witness.json").read_text()),
        "shared_power":a.share_power,"normalization_delta":delta,
        "reproduction":"cap_column_witness.py WITNESS OUT " + ("--share-power " if a.share_power else "") + "--cycles 1000"},indent=2)+"\n")


if __name__=="__main__": main()
