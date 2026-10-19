"""Diagnostic control only: test pruning on reference-matching generated options.

Never use this output as a synthesized flyer. The production assembler has no
reference input; this audit determines whether its partial checks are sound.
"""
import argparse
import json
import subprocess
from itertools import combinations
from pathlib import Path

from assemble import ROOT, Flyer, ext_contract


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("problem", type=Path)
    ap.add_argument("reference", type=Path)
    ap.add_argument("pools", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--pairs", action="store_true", help="audit all body pairs in all three prescribed orders")
    a = ap.parse_args()
    c = json.loads(a.problem.read_text())
    ref = {p: b.encode() for p, b in Flyer.load(a.reference)._cells.items()}
    union, counts, own = {}, [], []
    for bi in range(len(c["ports"])):
        pool = json.loads((a.pools / f"body{bi}/sol/pool.json").read_text())
        matches = [hw for hw in pool if all(ref.get(tuple(row[:3])) == row[3] for row in hw)]
        if not matches:
            raise RuntimeError(f"body{bi}: no exact control option")
        chosen = max(matches, key=len)
        counts.append(len(matches))
        dest = a.out / f"body{bi}/sol"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "pool.json").write_text(json.dumps([chosen]))
        hardware = {}
        for x, y, z, v in chosen:
            from fastflyer import Block
            hardware[(x, y, z)] = Block.decode(v)
        own.append(hardware)
        union.update(hardware)
    # Check the complete control independently before examining prefix pruning.
    src = a.problem.parent / c["flyer"]
    ext_contract(c, list(range(len(c["ports"]))), 12, a.out / "complete_control", src, union)
    r = subprocess.run(["python", "tools/extension_contract.py", str(a.out / "complete_control/problem.json"),
                        "--out", str(a.out / "complete_control/check.json")], cwd=ROOT, capture_output=True, text=True)
    print("complete control:", r.stdout.strip(), r.stderr.strip(), flush=True)
    if r.returncode:
        raise RuntimeError("complete control does not pass; cannot diagnose prefix pruning")
    if a.pairs:
        results = []
        for i, j in combinations(range(len(own)), 2):
            dest = a.out / f"pairs/{i}_{j}"
            ext_contract(c, [i, j], 12, dest, src, {**own[i], **own[j]})
            problem = dest / "problem.json"
            contract = json.loads(problem.read_text())
            cases = []
            for order in ("before_natural", "after_natural", "interleaved"):
                contract["prescribed_order"] = order
                problem.write_text(json.dumps(contract))
                r = subprocess.run(["python", "tools/extension_contract.py", str(problem)], cwd=ROOT, capture_output=True, text=True)
                cases.append({"order": order, "passed": r.returncode == 0, "message": (r.stdout + r.stderr).strip()[-600:]})
            results.append({"bodies": [i, j], "cases": cases})
            failed = sum(any(not t["passed"] for t in pair["cases"]) for pair in results)
            (a.out / "pair_audit.json").write_text(json.dumps({"diagnostic_only": True,
                "complete_control_passed": True, "checked": len(results), "failed_pairs": failed, "pairs": results}, indent=2))
            if len(results) % 20 == 0 or failed and any(not t["passed"] for t in cases):
                print(f"pairs checked={len(results)}/190 failed={failed}; latest={i},{j}", flush=True)
        return
    exe = ROOT / "target/release/column-assemble.exe"
    r = subprocess.run([str(exe), str(a.problem), str(a.out), str(a.out / "pruning"), "30", "--static"],
                       cwd=ROOT, capture_output=True, text=True)
    print(r.stdout, r.stderr, flush=True)
    (a.out / "audit.json").write_text(json.dumps({"diagnostic_only": True, "matching_options": counts,
        "complete_control_passed": True, "pruning": json.loads((a.out / "pruning/report.json").read_text())}, indent=2))


if __name__ == "__main__":
    main()
