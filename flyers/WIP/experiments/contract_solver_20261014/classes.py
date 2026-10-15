"""Classify extension contracts by how the target body is moved (push / pull / mixed, rigid vs rider) and
report solver success per class.  usage: python classes.py TAG   (reads runs/TAG/results.csv, flyerprobs_ext)
Class key: <family>|<moves of target: P=push(extend) L=pull(retract)>|<carriers: rigid if the actor touches
one body, rider if it touches two or more>. Uses target/release/flyer-ledger on the source flyer.
"""
import csv, json, re, subprocess, sys, collections, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEDGER = str(ROOT / "target/release" / ("flyer-ledger.exe" if os.name == "nt" else "flyer-ledger"))
tag = sys.argv[1]
cache = {}
def ledger(src, period):
    key = (src, period)
    if key not in cache:
        out = subprocess.run([LEDGER, str(ROOT / src), "--period", str(period)], capture_output=True, text=True).stdout
        cache[key] = out
    return cache[key]
fam = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(HERE / f"runs/{tag}/results.csv")):
    fl, kind = r["id"].split("/")
    m = json.loads((HERE / f"flyerprobs_ext/{fl}/{kind}/problem_meta.json").read_text())
    if m.get("reference_pass") is not True:
        continue
    src = m["source"].replace("\\", "/").split("FastFlyerPlayground/")[-1]
    led = ledger(src, m["period"])
    # body index in the ledger is by size, same ordering rule as contract-from-flyer (size desc), mostly aligned
    k = m["target_body"]
    acts = []
    for line in led.splitlines():
        mm = re.match(r"tick\s+\d+ slot (\d+) (extend|retract)\s+load\s+(\d+)\s+moves (\S*)\s+\(.*\)\s+by (.*)", line)
        if mm and f"b{k}" in mm.group(4).split(","):
            rider = "+" in mm.group(5).split(" on ")[-1]
            acts.append(("P" if mm.group(2) == "extend" else "L") + ("r" if rider else ""))
    moves = "".join(sorted(acts)) or "?"
    family = f"P{m['period']}/+{m['advance']}"
    key = f"{family}|{moves}"
    fam[key][0] += 1
    fam[key][1] += r["status"] == "verified" and int(r["load"]) <= int(m["reference_load"])
for k in sorted(fam, key=lambda k: (-fam[k][0], k)):
    print(f"{k:28s} n={fam[k][0]:3d} solved<=ref={fam[k][1]:3d}")
