"""Remove only optional hardware identified by a strict envelope failure.

Never deletes required geometry or relaxes verification. Recheck the complete
contract after each deletion; a later timing failure remains a rejection.
"""
import os as _research_os
import argparse,json,re,subprocess,time
from pathlib import Path
from assemble import Flyer,ROOT


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cert",type=Path);ap.add_argument("output",type=Path)
    ap.add_argument("--seconds",type=float,default=120);a=ap.parse_args()
    if a.output.exists():raise ValueError("refusing repeated pruning run")
    a.output.mkdir(parents=True)
    old=json.loads((a.cert/"summary.json").read_text())
    cases=[r for r in old["cases"] if "outside translated envelope" in (r.get("failure") or "")]
    start=time.monotonic();state={"total":len(cases),"complete":False,"cases":[]}
    save=lambda:(a.output/"summary.json").write_text(json.dumps(state,indent=2)+"\n")
    for record in cases:
        if time.monotonic()-start>=a.seconds:break
        src=a.cert/f"case{record['index']:04d}"; report=record
        row={"candidate":record["index"],"steps":[]};state["cases"].append(row)
        for step in range(3):
            m=re.search(r"permanent identity (\d+).*outside translated envelope",report.get("failure") or "")
            if not m:break
            f=Flyer.load(src/"problem.flyer");c=json.loads((src/"problem.json").read_text())
            origins=[p for p,b in sorted(f._cells.items()) if b.kind!=10];p=origins[int(m[1])];b=f._cells[p]
            if p in {tuple(r["at"]) for r in c["required_cells"]} or b.kind not in (6,7,8,9) or b.state:
                row["not_optional_simple_hardware"]=list(p);break
            f.remove(p);out=a.output/f"case{record['index']:04d}_step{step}";out.mkdir()
            f.save(out/"problem.flyer");g=Flyer.load(out/"problem.flyer")
            minimum=lambda cells:tuple(min(p[k] for p in cells) for k in range(3))
            delta=tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)));sh=lambda p:tuple(x+d for x,d in zip(p,delta))
            if {sh(p):b.encode() for p,b in f._cells.items()}!={p:b.encode() for p,b in g._cells.items()}:raise ValueError("normalization")
            for port in c["ports"]:port["at"]=list(sh(port["at"]))
            for r in c["required_cells"]:r["at"]=list(sh(r["at"]))
            c["boundary_envelope"]={k:list(sh(v)) for k,v in c["boundary_envelope"].items()}
            drive=[list(map(int,s.split())) for s in (src/c["prescribed_script"]).read_text().splitlines()]
            c.update(flyer="problem.flyer",prescribed_script="drive.txt")
            (out/"problem.json").write_text(json.dumps(c,indent=2)+"\n")
            lines=[" ".join(map(str,(t,*sh((x,y,z)),l))) for t,x,y,z,l in drive]
            (out/"drive.txt").write_text("\n".join(lines)+"\n")
            run=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/"problem.json"),str(out/"result.json"),"10","4"],capture_output=True,text=True)
            report=json.loads((out/"result.json").read_text());row["steps"].append({"removed":[*p,b.encode()],"exit_code":run.returncode,**report});src=out;save()
            if report["verified"]:state["lead"]=str(out);break
        if "lead" in state:break
    state["complete"]=len(state["cases"])==len(cases);state["elapsed_seconds"]=time.monotonic()-start;save()
    print(json.dumps({k:v for k,v in state.items() if k!="cases"}))


if __name__=="__main__":main()
