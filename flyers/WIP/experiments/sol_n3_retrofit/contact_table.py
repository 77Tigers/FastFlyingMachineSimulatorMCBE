"""Enumerate front-redstone contact sites for all five N3 pull interfaces."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from flyers.WIP.experiments.astra_pull3.retrofit import PH, H, CENTERS, delta
from flyers.WIP.astra_ringgen_safe import make

_, _, (segments, _) = make(3, CENTERS, 3, 100)
def distance(a, b):
    return sum(abs(a[d] - b[d]) for d in range(3))

for i in range(5):
    t = (-PH[i]) % 5
    j = (i + 1) % 5
    k = (i + 2) % 5
    cycle, phase = divmod(PH[k] + t + 1, 5)
    front_redstone_x = H[k] + 3 * cycle + min(phase, 3)
    support = (front_redstone_x - 1 - delta(j, t + 1), *CENTERS[k])
    contact = (support[0] + delta(j, t) - 3 - delta(i, t), support[1], support[2])
    print('target', i, 'slot', t, 'middle', j, 'front', k,
          'support_at_t0', support, 'contact_at_t0', contact,
          'middle_route_gap', min(distance(support, p) for p in segments[j]),
          'target_route_gap', min(distance(contact, p) for p in segments[i]))
