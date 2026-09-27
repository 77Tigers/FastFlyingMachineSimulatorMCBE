"""Reproduce the bounded 50-seed structural screen of the three-drive relay."""
from pathlib import Path
import csv
import extra_front

HERE = Path(__file__).resolve().parent
CENTERS = [(0,0),(0,8),(8,8),(8,0),(4,-6)]
FRONTS = [0,1,1,1,2]
CAPS = (8,17,11,11)
rows = []
for seed in range(50):
    before = extra_front.REJECT.copy()
    result = extra_front.make(CENTERS, FRONTS, seed, caps=CAPS)
    after = extra_front.REJECT - before
    reason = "routed" if result else next(iter(after), "unknown")
    rows.append((seed, reason))
with (HERE / "repaired_screen.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["seed", "outcome"])
    w.writerows(rows)

with (HERE / "relay_screen.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["candidate", "distance160", "extensions160", "end_blocks",
                "limit", "note"])
    for line in (HERE / "relay_results.tsv").read_text().splitlines():
        fields = line.split("\t")
        if len(fields) >= 4:
            w.writerow([*fields[:4], 100, "one-drive relay timing invalid"])
print(extra_front.REJECT.most_common())
