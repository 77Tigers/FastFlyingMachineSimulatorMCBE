"""Independent re-check (bug catching) of verified answers in a run with tools/extension_contract.py.

usage: python pycheck_run.py TAG [N] -> prints per-answer result and writes runs/TAG/pycheck_summary.txt
Natural contracts (no prescribed_script) are checked once (orders are the same simulation); others in all 3 orders.
"""
import csv, json, random, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
tag = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
rows = [r for r in csv.DictReader(open(HERE / f"runs/{tag}/results.csv")) if r["status"] == "verified"]
random.seed(11)
pick = random.sample(rows, min(n, len(rows)))
lines = []
for r in pick:
    out = HERE / "runs" / tag / r["id"].replace("/", "__")
    natural = "prescribed_script" not in json.loads((out / "solution_before_natural.json").read_text())
    orders = ["before_natural"] if natural else ["before_natural", "after_natural", "interleaved"]
    res = []
    for o in orders:
        p = subprocess.run([sys.executable, str(ROOT / "tools/extension_contract.py"), str(out / f"solution_{o}.json"), "--samples",
                            "--out", str(out / f"pycheck_{o}.json")], capture_output=True, text=True, cwd=ROOT)
        res.append(f"{o[:3]}:{'ok' if p.returncode == 0 else 'FAIL'}")
    lines.append(f"{r['id']} load={r['load']} {' '.join(res)}")
    print(lines[-1], flush=True)
bad = [l for l in lines if "FAIL" in l]
lines.append(f"checked {len(pick)}, failures {len(bad)}")
(HERE / "runs" / tag / "pycheck_summary.txt").write_text("\n".join(lines) + "\n")
print(lines[-1])
