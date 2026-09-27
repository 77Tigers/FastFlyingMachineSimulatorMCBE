"""Causal screen of the first oversized pull in helper_ring_v2/c1s1287.

Generate one- and two-cell deletions around the tick-6 honey bridge. All
distances are produced by the Rust flyer_batch executable, not Python physics.
"""
from pathlib import Path
import csv
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind, Block

HERE = Path(__file__).resolve().parent
BASE = Flyer.load(ROOT / "flyers/WIP/experiments/astra_pull3/helper_ring_v2/c1s1287.flyer")
OUT = HERE / "merge_probe"
OUT.mkdir(parents=True, exist_ok=True)

# The trace is in serialized coordinates. At tick 6 the bad pull starts from
# honey (19,5,22) and links down to the broad honey bridge around x20,y2-3.
# Include the rest of the moving middle/front honey near that bridge so the
# screen is not predicated on one guessed cut point.
region = []
for p, b in sorted(BASE._cells.items()):
    x, y, z = p
    if b.kind == Kind.HONEY and 17 <= x <= 22 and 0 <= y <= 8 and 18 <= z <= 23:
        region.append(p)

rows = []
for idx, p in enumerate(region):
    f = Flyer(rng_state=BASE.rng_state, push_limit=100,
              phase_x=BASE.phase_x, phase_z=BASE.phase_z)
    f._cells = BASE._cells.copy()
    del f._cells[p]
    name = f"single_{idx:03d}"
    f.save(OUT / (name + ".flyer"))
    rows.append((name, "single", str(p), ""))

    for replacement in (Kind.SLIME, Kind.GLAZED_TERRACOTTA):
        g = Flyer(rng_state=BASE.rng_state, push_limit=100,
                  phase_x=BASE.phase_x, phase_z=BASE.phase_z)
        g._cells = BASE._cells.copy()
        g._cells[p] = Block(replacement)
        name = f"replace_{idx:03d}_{replacement.name.lower()}"
        g.save(OUT / (name + ".flyer"))
        rows.append((name, "replace", str(p), replacement.name))

batch = Path(os.environ["TEMP"]) / "flyer_batch.exe"
result = subprocess.run([str(batch), "160", str(OUT)], text=True,
                        capture_output=True, check=True)
score = {}
for line in result.stdout.splitlines():
    fields = line.split("\t")
    if len(fields) >= 4:
        score[fields[0]] = fields[1:4]

with (HERE / "merge_probe.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["candidate", "mutation", "cell", "other", "distance160",
                "extensions160", "end_blocks"])
    for name, mutation, cell, other in rows:
        w.writerow([name, mutation, cell, other, *score.get(name, ("", "", ""))])

print("tested", len(rows), "honey removals/replacements")
for name, mutation, cell, other in rows:
    if int(score.get(name, ("0",))[0]) >= 10:
        print(name, cell, score[name])
