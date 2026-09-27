"""Rank N3 center orderings by distance to five pull contact cells."""
from pathlib import Path
from itertools import permutations
import csv
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from flyers.WIP.astra_ringgen_safe import make
from flyers.WIP.experiments.astra_pull3.retrofit import PH, H, delta

OUT = Path(__file__).resolve().parent
SITES = [(0, 0), (0, 4), (3, 5), (5, 2), (3, -1)]


def dist(a, b):
    return sum(abs(a[d] - b[d]) for d in range(3))


def gaps(centers, segments):
    answer = []
    for i in range(5):
        t = (-PH[i]) % 5
        j, k = (i + 1) % 5, (i + 2) % 5
        cycle, phase = divmod(PH[k] + t + 1, 5)
        rx = H[k] + 3 * cycle + min(phase, 3)
        support = (rx - 1 - delta(j, t + 1), *centers[k])
        contact = (support[0] + delta(j, t) - 3 - delta(i, t), *centers[k])
        answer.append((min(dist(support, p) for p in segments[j]),
                       min(dist(contact, p) for p in segments[i])))
    return answer


def main():
    rows = []
    for rest in permutations(SITES[1:]):
        centers = [SITES[0], *rest]
        result = make(3, centers, 3, 100)
        if result is None:
            continue
        _, counts, (segments, _) = result
        gs = gaps(centers, segments)
        rows.append((centers, counts, gs,
                     sum(g[1] for g in gs), max(g[1] for g in gs)))
    rows.sort(key=lambda r: (r[4], r[3], max(r[1])))
    with (OUT / 'center_order.csv').open('w', newline='') as h:
        w = csv.writer(h)
        w.writerow(('centers', 'counts', 'gaps_support_target', 'sum_target_gap', 'max_target_gap'))
        w.writerows(rows)
    for row in rows[:10]:
        print(row)
    print('VALID', len(rows))


if __name__ == '__main__':
    main()
