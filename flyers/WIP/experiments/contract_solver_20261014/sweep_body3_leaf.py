"""Relocate the interfering body3 leaf on the compact-body0 geometry.

Input is joint_compact_0_3's bare five-cell body3 core. Sequential bounded
generation stops at the first pair of nonempty body0/body3 pools.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from assemble import body_of, ext_contract, Flyer, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    c = json.loads(args.problem.read_text())
    src = args.problem.parent / c["flyer"]
    base = Flyer.load(src)
    bodies = [body_of(base._cells, tuple(p["at"])) for p in c["ports"]]
    assert len(bodies[0]) == 8 and len(bodies[3]) == 5
    directions = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    sites = sorted({tuple(a+b for a,b in zip(p,d)) for p in bodies[3] for d in directions}
                   - set(base._cells) - {(3,5,5)})
    binary = ROOT / "target/release/column-solve.exe"
    state = {"verified": False, "source_sha256": hashlib.sha256(args.problem.read_bytes()).hexdigest(),
             "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "cases": []}
    args.output.mkdir(parents=True, exist_ok=True)
    save = lambda: (args.output / "summary.json").write_text(json.dumps(state, indent=2)+"\n")
    for position in sites:
        f = Flyer.load(src)
        cell = f._cells[tuple(c["ports"][3]["at"])]
        f.set(position, cell)
        row = {"added": position}; state["cases"].append(row)
        if any(body_of(f._cells,tuple(p["at"])) != (bodies[i] | {position} if i == 3 else bodies[i])
               for i,p in enumerate(c["ports"])):
            row["status"] = "merges_components";save();continue
        out = args.output / f"case{len(state['cases'])-1}"
        (out / "source").mkdir(parents=True, exist_ok=True)
        f.save(out / "source/problem.flyer")
        if {p:b.encode() for p,b in f._cells.items()} != {p:b.encode() for p,b in Flyer.load(out / "source/problem.flyer")._cells.items()}:
            raise ValueError("unexpected save translation")
        candidate = dict(c, name=c["name"]+"-relocated-leaf", flyer="problem.flyer",
                         required_cells=c["required_cells"]+[{"at":list(position),"cell":cell.encode()}])
        (out / "source/problem.json").write_text(json.dumps(candidate,indent=2)+"\n")
        counts = {}; row["candidates"] = counts
        for body in (0,3):
            target = out / f"generated/body{body}"
            assert ext_contract(candidate,body,11,target,out / "source/problem.flyer",None) == (0,0,0)
            cmd = [str(binary),str(target / "problem.json"),str(target / "sol"),"45","--pool-only","--wide"]
            row.setdefault("commands",[]).append(cmd)
            with (out / f"body{body}.log").open("w") as log:
                subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
            counts[str(body)] = len(json.loads((target / "sol/pool.json").read_text()))
            save()
            if not counts[str(body)]: break
        row["status"] = "locally_nonempty" if counts.get("0") and counts.get("3") else "generator_gap"
        save();print(json.dumps({k:v for k,v in row.items() if k != "commands"}),flush=True)
        if row["status"] == "locally_nonempty":
            state["next"] = "fresh full-pool generation/certification on modified geometry"
            save();return
    state["complete"] = True;save()


if __name__ == "__main__":
    main()
