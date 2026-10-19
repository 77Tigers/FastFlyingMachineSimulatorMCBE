"""Strip only generated G pushers/sources in the joint-template coordinate frame."""
import argparse
import json
from pathlib import Path

from assemble import Flyer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    if (a.output / "problem.json").exists():
        raise ValueError("existing prepared contract")
    f = Flyer.load(a.source / "problem.flyer")
    c = json.loads((a.source / "problem.json").read_text(encoding="utf-8"))
    removed = [p for p, b in f._cells.items() if (p[0] == 17 and b.kind == 9 and b.direction == 0)
               or (p[0] == 18 and b.kind == 6)]
    assert len(removed) == 3, removed
    for p in removed:
        f.remove(p)
    f.save(a.output / "problem.flyer")
    assert f._cells == Flyer.load(a.output / "problem.flyer")._cells
    c["required_cells"] = [q for q in c["required_cells"] if tuple(q["at"]) not in removed]
    c["name"] = "tip5_G_core_trim_regenerate"
    (a.output / "problem.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
    (a.output / "drive.txt").write_bytes((a.source / "drive.txt").read_bytes())
    target = next(i for i, p in enumerate(c["ports"]) if p["name"] == "G0")
    (a.output / "preparation.json").write_text(json.dumps({"source": str(a.source), "target_port": target,
        "removed_hardware": removed, "scope": "tip all natural; G slot3 and all other natural moves retained; synthesize G1/2"}, indent=2) + "\n", encoding="utf-8")
    print(f"target index {target}, removed {removed}")


if __name__ == "__main__":
    main()
