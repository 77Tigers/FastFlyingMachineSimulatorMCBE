import json, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pieceA import *
from pieceA2 import verify
good = {b: [tuple(q) for q in v] for b, v in json.load(open(HERE / "A_good.json")).items()}
words = {p["body"]: p["word"] for p in plan["ports"]}
rng = random.Random(1)
names = list(good)
def tryc(combo, tag):
    d = HERE / "A_all"
    make(d, [(combo[b], 0) for b in names])
    po = passes(d)
    return d, po
best = None
for k in range(200):
    combo = {b: (good[b][0] if k == 0 else rng.choice(good[b])) for b in names}
    if len(set(combo.values())) < 5: continue
    d, po = tryc(combo, k)
    if len(po) == 3:
        v = verify(d, combo)
        wslots = lambda b: [i for i, ch in enumerate(words[b]) if ch == "m"]
        if all(a == 0 and s == wslots(b) and n == 9 for b in names for a, s, n in v[b]):
            print("joint combo ok after", k + 1, "tries:", combo); best = combo; break
if best:
    json.dump({b: list(q) for b, q in best.items()}, open(HERE / "A_final.json", "w"))
    for o in ORDERS:
        r = subprocess.run([sys.executable, "-B", str(X.ROOT / "tools/extension_contract.py"), str(d / f"bounded_{o}.json"), "--samples", "--out", str(d / f"samples_{o}.json")], capture_output=True, text=True, cwd=X.ROOT)
        print(o, (r.stdout + r.stderr).strip()[:600])
