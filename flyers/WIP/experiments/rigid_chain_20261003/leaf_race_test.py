"""Real-simulator test of the 'leaf race' rule (2026-10-04).

Rig: two stationary pushers fire in the same tick (same chunk, random order). Segment J = one slime block pushed by
P1; segment O = two honey blocks pushed by P2 plus a LEAF (piston / redstone block / observer) attached to O's honey
and touching J's slime. Whichever segment moves first drags the leaf +1 (where it was going anyway); the other then
finds the leaf moving (immovable) and adhesion skips it.

Result: at push limit 12 every seed gives ONE outcome after 1 tick (all blocks +1). At push limit 2 the outcome splits
~30/30 by update order: when O goes first it moves 2 honey + leaf = 3 > 2 and fails, so the dragged leaf counts
toward the first mover's push count (as modelled in rigid.loads with LEAF=1).
Not tested: a dragged redstone block whose power is needed later in the same tick.
usage: python leaf_race_test.py
"""
import subprocess, sys, tempfile, pathlib
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
from fastflyer.research import simulate

def rig(leaf, rng, pl):
    f = Flyer(rng_state=rng, push_limit=pl)
    f.set((-1, 0, 0), Block(Kind.REDSTONE_BLOCK)); f.set((0, 0, 0), Block.piston(0))
    f.set((-1, 0, 3), Block(Kind.REDSTONE_BLOCK)); f.set((0, 0, 3), Block.piston(0))
    f.set((1, 0, 0), Block(Kind.SLIME))
    f.set((1, 0, 3), Block(Kind.HONEY)); f.set((1, 0, 2), Block(Kind.HONEY))
    f.set((1, 0, 1), {'piston': Block.piston(2), 'redstone': Block(Kind.REDSTONE_BLOCK),
                      'observer': Block.observer(2)}[leaf])
    return f

if __name__ == '__main__':
    tmp = pathlib.Path(tempfile.mkdtemp())
    for pl in (12, 2):
        for leaf in ('piston', 'redstone', 'observer'):
            res = Counter()
            for i in range(60):
                a, b = tmp / 'in.flyer', tmp / 'out.flyer'
                rig(leaf, i * 7919 + 13, pl).save(a)
                simulate(a, b, 1)
                g = Flyer.load(b); mn = min(p[0] for p, _ in g.blocks())
                res[tuple(sorted((p[0] - mn, p[2], bl.kind.name) for p, bl in g.blocks() if bl.kind != Kind.PISTON_ARM))] += 1
            print(f'PL{pl} {leaf}: {len(res)} outcome(s) {sorted(res.values())}')
