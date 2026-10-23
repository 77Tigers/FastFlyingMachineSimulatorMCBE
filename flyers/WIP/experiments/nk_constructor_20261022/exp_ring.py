"""experiment: even k with a bigger square ring (L = 4 * base ring, m = base ring, side copy works)."""
import sys, json
import square, families as F, calibrate as C
from nk import bodies_for
orig = square.ring_size
def big(k, m_min=1):
    L0 = bodies_for(k); L = orig(k, m_min)
    return max(L, 4 * L0) if (k + 2) % 2 == 0 else L
square.ring_size = big
import sqbuild; sqbuild.square.ring_size = big
if __name__ == '__main__':
    for k in [int(x) for x in sys.argv[1].split(',')]:
        print(k, square.ring_size(k), C.one(k, [0, 1]), flush=True)
