"""Keep verified front/back pulls natural while exposing helper column obligations."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from assemble import port_pos


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("link", type=Path, help="verified link run directory")
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    source = a.link / "check"
    c = json.loads((source/"before_natural.json").read_text())
    index, helper = next((i,p) for i,p in enumerate(c["ports"]) if p["name"] == "pull_helper")
    helper["role"] = "output"
    omitted = {(t,*port_pos(helper,t,c["period_ticks"],c["advance"]))
               for t in range(c["cycles"]*c["period_ticks"])
               if t % 2 == 0 and helper["word"][(t % c["period_ticks"])//2] == "m"}
    rows = [list(map(int,line.split())) for line in (source/"drive.txt").read_text().splitlines()]
    kept = [r for r in rows if tuple(r[:4]) not in omitted]
    if len(rows)-len(kept) != len(omitted): raise ValueError("missing helper rows")
    a.output.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source/"problem.flyer",a.output/"problem.flyer")
    c["name"] = "split_front_link_helper_natural"
    (a.output/"problem.json").write_text(json.dumps(c,indent=2)+"\n")
    (a.output/"drive.txt").write_text("\n".join(" ".join(map(str,r)) for r in kept)+"\n")
    (a.output/"preparation.json").write_text(json.dumps({"target_port":index,
        "omitted_helper_rows":len(omitted),"retained_supplied_rows":len(kept),
        "scope":"front/back pulls remain natural; helper all moves natural; other strokes supplied",
        "source_sha256":hashlib.sha256((source/"before_natural.json").read_bytes()).hexdigest()},indent=2)+"\n")


if __name__ == "__main__":
    main()
