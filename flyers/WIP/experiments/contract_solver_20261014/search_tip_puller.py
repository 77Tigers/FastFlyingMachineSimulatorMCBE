"""Bounded one-cell tip-helper placements for the shared helper's third pull.

All verified mechanism cells pinned; no external hardware library. Search cap64
results are leads only and need independent encoded11 checking before acceptance.
"""
import os as _research_os
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer, ROOT, body_of, port_pos
from fastflyer import Block

DIRS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shared",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--budget",type=float,default=3)
    a=ap.parse_args()
    if a.output.exists(): raise ValueError("refusing to repeat existing search")
    a.output.mkdir(parents=True)
    source=a.shared/"check"
    base=Flyer.load(source/"problem.flyer")
    original=json.loads((source/"before_natural.json").read_text())
    target=next(p for p in original["ports"] if p["name"]=="pull_helper")
    victim=body_of(base._cells,tuple(target["at"]))
    sites=sorted({(p[0]+2+d[0],p[1]+d[1],p[2]+d[2]) for p in victim for d in DIRS if d!=(-1,0,0)}-set(base._cells))
    empty=a.output/"empty_library.json"; empty.write_text("[]\n")
    rows=[list(map(int,line.split())) for line in (source/"drive.txt").read_text().splitlines()]
    omitted={(t,*port_pos(target,t,10,3)) for t in range(6,original["cycles"]*10,10)}
    rows=[row for row in rows if tuple(row[:4]) not in omitted]
    state={"scope":"tip strokes supplied; seek natural helper slot3; not closed flyer", "budget_per_case":a.budget,
           "source_sha256":hashlib.sha256((source/"problem.flyer").read_bytes()).hexdigest(),
           "sites":len(sites),"cases":[],"complete":False,"library":"explicit empty external library; automatic self_entry allowed"}
    save=lambda:(a.output/"summary.json").write_text(json.dumps(state,indent=2)+"\n")
    start=time.monotonic()
    for site in sites:
        folder=a.output/f"case{len(state['cases']):03d}"
        row={"site":site,"case":folder.name}; state["cases"].append(row)
        f=Flyer.load(source/"problem.flyer"); f.set(site,Block.decode(1))
        if any(body_of(f._cells,tuple(p["at"]))!=body_of(base._cells,tuple(p["at"])) for p in original["ports"]):
            row["status"]="merges_glue_components"; save(); continue
        folder.mkdir(); f.save(folder/"problem.flyer")
        g=Flyer.load(folder/"problem.flyer")
        minimum=lambda cells:tuple(min(p[i] for p in cells) for i in range(3))
        delta=tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)))
        sh=lambda p:tuple(x+d for x,d in zip(p,delta))
        if {sh(p):b.encode() for p,b in f._cells.items()}!={p:b.encode() for p,b in g._cells.items()}: raise ValueError("normalization")
        c=json.loads(json.dumps(original)); c["name"]="shared_helper_tip_pull"
        for port in c["ports"]:
            port["at"]=list(sh(port["at"]))
            if port["name"]=="pull_helper": port["role"]="output"
        tip={"name":"tip_helper","role":"input","at":list(sh(site)),"word":"mmwwm"}; c["ports"].append(tip)
        c["required_cells"]=[{"at":list(p),"cell":b.encode()} for p,b in g._cells.items() if b.kind!=10]
        c["boundary_envelope"]={"min":[min(p[i] for p in g._cells)-5 for i in range(3)],"max":[max(p[i] for p in g._cells)+5 for i in range(3)]}
        supplied=[(t,*sh((x,y,z)),11) for t,x,y,z,_ in rows]
        supplied += [(t,*port_pos(tip,t,10,3),11) for t in range(c["cycles"]*10) if t%10 in (0,2,8)]
        (folder/"drive.txt").write_text("\n".join(" ".join(map(str,r)) for r in sorted(supplied))+"\n")
        (folder/"problem.json").write_text(json.dumps(c,indent=2)+"\n")
        cmd=[str(ROOT/('target/release/contract-solve' + ('.exe' if _research_os.name == 'nt' else ''))),str(folder/"problem.json"),str(folder/"solve"),"--budget",str(a.budget),"--threads","4","--library",str(empty),"--holdout","--quiet","--seed","1"]
        row["command"]=cmd; save()
        with (folder/"solve.log").open("w") as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        report=json.loads((folder/"solve/report.json").read_text())
        row.update(status=report["status"],max_load=report.get("all_max_load_all_samples"),failure=report.get("first_failure"))
        if row["status"]=="verified" and row["max_load"] is not None and row["max_load"]<=11:
            state["lead"]=str(folder); save(); break
        save()
    else: state["complete"]=True
    state["elapsed_seconds"]=time.monotonic()-start; save()
    print(json.dumps({k:v for k,v in state.items() if k!="cases"}))


if __name__=="__main__": main()
