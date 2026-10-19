"""Sequential tip-column tests on distinct verified local carrier geometries.

Prefer tips outside the helper glue's YZ projection to avoid the observed
same-tick retraction/forward-obstruction conflict. No reference hardware input.
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("variants", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--seconds", type=float, default=150)
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--tip-cells", type=int, default=4)
    ap.add_argument("--tip-min-cells", type=int, default=1)
    ap.add_argument("--budget", type=float, default=1)
    ap.add_argument("--per-variant-seconds", type=float, default=45)
    ap.add_argument("--rider-completion", action="store_true")
    ap.add_argument("--exclude-artifact", type=Path)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("existing search")
    a.output.mkdir(parents=True)
    summary = json.loads((a.variants / "summary.json").read_text())
    seen = set()
    if a.exclude_artifact:
        seen.add(json.loads(a.exclude_artifact.read_text())["content_hash"])
    options = []
    for path in summary.get("leads", []):
        p = Path(path)
        c = json.loads((p / "problem.json").read_text())
        f = Flyer.load(p / "problem.flyer")
        h = f.content_hash()
        if h in seen:
            continue
        seen.add(h)
        tip = next(q for q in c["ports"] if q["name"] == "tip")
        projection = {tuple(q["at"][1:]) for q in c["ports"] if q["name"].startswith("G")}
        options.append((tuple(tip["at"][1:]) in projection, p, h))
    options.sort(key=lambda q: (q[0], str(q[1])))
    state = {"scope": "local T/G/back pull natural; rear strokes and neighbor supplied; tip synthesis",
             "options": len(options), "cases": [], "complete": False}
    save = lambda: (a.output / "summary.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    start = time.monotonic()
    here = Path(__file__).parent
    for overlap, case, h in options[:a.limit]:
        remaining = a.seconds - (time.monotonic() - start)
        if remaining <= 1:
            break
        out = a.output / case.name
        row = {"source": str(case), "hash": h, "tip_in_G_projection": overlap}
        state["cases"].append(row)
        save()
        subprocess.run(["python", str(here / "prepare_local_checks.py"), str(case), str(out / "core"),
                        "--reproduction", "joint_tip_layout.py: source variant in parent summary"], check=True, capture_output=True)
        subprocess.run(["python", str(here / "grow_joint_tip.py"), str(out / "core"), str(out / "tip"),
                        "--seconds", str(min(a.per_variant_seconds, remaining)), "--budget", str(a.budget),
                        "--cells", str(a.tip_cells), "--min-cells", str(a.tip_min_cells)]
                       + (["--rider-completion"] if a.rider_completion else []), check=True, capture_output=True)
        result = json.loads((out / "tip/summary.json").read_text())
        row.update({k: v for k, v in result.items() if k != "cases"})
        if result.get("lead"):
            state["lead"] = result["lead"]
            save()
            break
        save()
    state["complete"] = len(state["cases"]) == min(a.limit, len(options))
    state["elapsed_seconds"] = time.monotonic() - start
    save()
    print(json.dumps({k: v for k, v in state.items() if k != "cases"}))


if __name__ == "__main__":
    main()
