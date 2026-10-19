"""Bounded helper placements that replace the split front's supplied slot0.

Existing column hardware is pinned; carriers and new helper remain supplied.
The hardware search uses an empty library. Successful leads need independent
80-case checks in all three supplied-event orders at encoded11.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from assemble import body_of, ext_contract, Flyer, ROOT
from fastflyer import Block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("interface", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--budget", type=float, default=5)
    args = parser.parse_args()
    seed = args.interface / "check/solution.flyer"
    base = Flyer.load(seed)
    original = json.loads((args.interface / "check/solution_before_natural.json").read_text())
    bodies = [body_of(base._cells,tuple(p["at"])) for p in original["ports"]]
    directions = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    # Sticky initially extended two cells in front of any victim glue cell;
    # helper glue may touch any face except the sticky's -X front.
    sites = sorted({(p[0]+2+d[0],p[1]+d[1],p[2]+d[2]) for p in bodies[0]
                    for d in directions if d != (-1,0,0)} - set(base._cells))
    args.output.mkdir(parents=True, exist_ok=True)
    library = args.output / "empty_library.json"
    library.write_text("[]\n")
    binary = ROOT / "target/release/contract-solve.exe"
    state = {"natural_flyer":False,"purpose":"replace supplied front slot0 with a real actuator",
             "seed_sha256":hashlib.sha256(seed.read_bytes()).hexdigest(),
             "binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
             "library":"explicit empty array","budget_per_case":args.budget,"cases":[]}
    save = lambda: (args.output / "summary.json").write_text(json.dumps(state,indent=2)+"\n")
    for site in sites:
        row = {"helper_glue":site};state["cases"].append(row)
        f = Flyer.load(seed);f.set(site,Block.decode(2))
        if any(body_of(f._cells,tuple(p["at"])) != b for p,b in zip(original["ports"],bodies)):
            row["status"]="merges_components";save();continue
        out = args.output / f"case{len(state['cases'])-1}"
        (out / "source").mkdir(parents=True,exist_ok=True)
        f.save(out / "source/problem.flyer")
        g = Flyer.load(out / "source/problem.flyer")
        minimum = lambda cells: tuple(min(p[i] for p in cells) for i in range(3))
        delta = tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)))
        shift = lambda p:[a+b for a,b in zip(p,delta)]
        ports = [dict(p,role="output",at=shift(p["at"])) for p in original["ports"]]
        ports.append({"name":"pull_helper","role":"output","at":shift(site),"word":"wmmmw"})
        c = {"version":1,"name":"split_column_puller","flyer":"problem.flyer","period_ticks":10,
             "advance":3,"cycles":3,"recurrence":"bounded","ports":ports,
             "required_cells":[{"at":shift(p),"cell":b.encode()} for p,b in f._cells.items() if b.kind != 10],
             "boundary_envelope":{"min":[min(p[i] for p in g._cells)-5 for i in range(3)],
                                  "max":[max(p[i] for p in g._cells)+5 for i in range(3)]}}
        (out / "source/problem.json").write_text(json.dumps(c,indent=2)+"\n")
        ext_contract(c,0,11,out / "contract",out / "source/problem.flyer",None)
        cmd=[str(binary),str(out / "contract/problem.json"),str(out / "solve"),"--budget",str(args.budget),
             "--library",str(library),"--holdout","--quiet","--seed","1"]
        row["command"]=cmd;save();start=time.monotonic()
        with (out / "solve.log").open("w") as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        report=json.loads((out / "solve/report.json").read_text())
        row.update(status=report["status"],elapsed_seconds=time.monotonic()-start,
                   first_failure=report.get("first_failure"),max_load=report.get("all_max_load_all_samples"))
        if report["status"]=="verified" and row["max_load"] is not None and row["max_load"]<=11:
            solution=out / "solve/solution.flyer";answer=Flyer.load(solution);answer.push_limit=11;answer.save(solution)
            # Raising the encoded allowance does not shift coordinates.
            checks=[]
            for order in ("before_natural","after_natural","interleaved"):
                result=out / f"independent_{order}.json"
                with (out / f"independent_{order}.log").open("w") as log:
                    subprocess.run([sys.executable,str(ROOT / "tools/extension_contract.py"),
                                    str(out / f"solve/solution_{order}.json"),"--samples","--out",str(result)],
                                   stdout=log,stderr=subprocess.STDOUT)
                checks.append(json.loads(result.read_text()))
            row["independent_passed"]=[sum(c["passed"] for c in check["cases"]) for check in checks]
            if all(check["passed"] for check in checks):
                state.update(local_verified=True,lead=str(out));save();print(json.dumps(row),flush=True);return
        save();print(json.dumps({k:v for k,v in row.items() if k!="command"}),flush=True)
    state["complete"]=True;save()


if __name__=="__main__":
    main()
