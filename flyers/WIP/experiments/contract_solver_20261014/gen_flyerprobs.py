"""Generate strip-the-pistons problems from every banked flyer (all speeds/timings) with contract-from-flyer.

usage: python flyers/WIP/experiments/contract_solver_20261014/gen_flyerprobs.py [--max-bodies 4]
Writes flyerprobs/<flyer-stem>/{reference,all,near<k>}/ and flyerprobs/summary.txt.
"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EXE = ROOT / "target/release" / ("contract-from-flyer.exe" if sys.platform == "win32" else "contract-from-flyer")
mb = sys.argv[sys.argv.index("--max-bodies") + 1] if "--max-bodies" in sys.argv else "4"
cat = json.loads((ROOT / "flyers/bank/catalogue.json").read_text())["entries"]
lines = []
for path, e in sorted(cat.items()):
    stem = Path(path).parent.name + "_" + Path(path).stem
    out = HERE / "flyerprobs" / stem
    r = subprocess.run([str(EXE), str(ROOT / path), str(out), "--speed", str(e["speed_bps"]), "--max-bodies", mb],
                       capture_output=True, text=True, cwd=ROOT, timeout=120)
    msg = (r.stdout.splitlines() or [""])[0] if r.returncode == 0 else "FAIL " + r.stderr.strip()[-160:]
    lines.append(f"{stem}: {msg}")
    print(lines[-1], flush=True)
(HERE / "flyerprobs" / "summary.txt").write_text("\n".join(lines) + "\n")
