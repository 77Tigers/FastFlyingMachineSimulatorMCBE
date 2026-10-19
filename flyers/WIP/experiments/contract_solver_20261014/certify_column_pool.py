"""Certify raw columns against their original coupled contract at an explicit cap."""
import argparse,json,subprocess,time
from pathlib import Path
from assemble import Flyer,ROOT
from fastflyer import Block


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("problem",type=Path);ap.add_argument("pool",type=Path);ap.add_argument("output",type=Path)
    ap.add_argument("--seconds",type=float,default=180)
    ap.add_argument("--push-limit",type=int,default=11);a=ap.parse_args()
    if a.push_limit <= 0:raise ValueError("push limit must be positive")
    if a.output.exists():raise ValueError("refusing existing certification")
    a.output.mkdir(parents=True);c=json.loads(a.problem.read_text());pool=json.loads(a.pool.read_text())
    drive=[list(map(int,s.split())) for s in (a.problem.parent/c["prescribed_script"]).read_text().splitlines()]
    start=time.monotonic();state={"tested":0,"total":len(pool),"complete":False,"push_limit":a.push_limit,"cases":[]}
    save=lambda:(a.output/"summary.json").write_text(json.dumps(state,indent=2)+"\n")
    for i,hardware in enumerate(pool):
        if time.monotonic()-start>=a.seconds:break
        out=a.output/f"case{i:04d}";out.mkdir();f=Flyer.load(a.problem.parent/c["flyer"]);f.push_limit=a.push_limit
        for x,y,z,v in hardware:
            if (x,y,z) in f._cells:raise ValueError("pool overlaps base")
            f.set((x,y,z),Block.decode(v))
        f.save(out/"problem.flyer");g=Flyer.load(out/"problem.flyer")
        minimum=lambda cells:tuple(min(p[k] for p in cells) for k in range(3))
        delta=tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)));sh=lambda p:tuple(x+d for x,d in zip(p,delta))
        if {sh(p):b.encode() for p,b in f._cells.items()}!={p:b.encode() for p,b in g._cells.items()}:raise ValueError("normalization")
        q=json.loads(json.dumps(c));q.update(flyer="problem.flyer",prescribed_script="drive.txt")
        for p in q["ports"]:p["at"]=list(sh(p["at"]))
        for r in q["required_cells"]:r["at"]=list(sh(r["at"]))
        if "boundary_envelope" in q:q["boundary_envelope"]={k:list(sh(v)) for k,v in q["boundary_envelope"].items()}
        (out/"problem.json").write_text(json.dumps(q,indent=2)+"\n")
        lines=[" ".join(map(str,(t,*sh((x,y,z)),min(l,a.push_limit)))) for t,x,y,z,l in drive]
        (out/"drive.txt").write_text("\n".join(lines)+"\n")
        run=subprocess.run([str(ROOT/"target/release/contract-verify.exe"),str(out/"problem.json"),str(out/"result.json"),"10","4"],capture_output=True,text=True)
        report=json.loads((out/"result.json").read_text());state["cases"].append({"index":i,"exit_code":run.returncode,**report});state["tested"]+=1;save()
        if report["verified"]:state["lead"]=str(out);break
    state["complete"]=state["tested"]==len(pool);state["elapsed_seconds"]=time.monotonic()-start;save()
    print(json.dumps({k:v for k,v in state.items() if k!="cases"}))


if __name__=="__main__":main()
