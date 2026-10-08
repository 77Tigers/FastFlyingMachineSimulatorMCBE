"""Real-simulator test of the 'leaf PUSH race' (2026-10-04), companion of rigid_chain_20261003/leaf_race_test.py.

Rig: two stationary pushers fire in the same tick. Segment J = one slime block pushed by P1; its destination cell
holds a LEAF (piston / -X sticky / redstone block / observer) of segment O (two honey blocks pushed by P2, leaf attached to
O's front honey). If O moves first the leaf leaves with O and J moves into the freed cell; if J moves first it pushes the
leaf +1 as an obstruction (where it was going anyway) and O's adhesion then skips the moving leaf.
Expected: one outcome at PL12; at PL2 still one outcome (J first: slime + leaf = 2; O first: 2 honey + leaf = 3 > 2 fails
-> split), i.e. the leaf counts toward whichever segment goes first.
usage: python leafpush_test.py
"""
import subprocess, sys, tempfile, pathlib
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
from fastflyer.research import simulate


def rig(leaf, rng, pl):
    f = Flyer(rng_state=rng, push_limit=pl)
    f.set((-1, 0, 0), Block(Kind.REDSTONE_BLOCK)); f.set((0, 0, 0), Block.piston(0))      # P1 -> J
    f.set((-1, 0, 1), Block(Kind.REDSTONE_BLOCK)); f.set((0, 0, 1), Block.piston(0))      # P2 -> O
    f.set((1, 0, 0), Block(Kind.SLIME))                                                   # J
    f.set((1, 0, 1), Block(Kind.HONEY)); f.set((2, 0, 1), Block(Kind.HONEY))              # O glue
    f.set((2, 0, 0), {'piston': Block.piston(2), 'sticky_-X': Block.piston(1, sticky=True),
                      'redstone': Block(Kind.REDSTONE_BLOCK), 'observer': Block.observer(2)}[leaf])  # O leaf in J's way
    return f


if __name__ == '__main__':
    tmp = pathlib.Path(tempfile.mkdtemp())
    for pl in (12, 2):
        for leaf in ('piston', 'sticky_-X', 'redstone', 'observer'):
            res = Counter()
            for i in range(60):
                a, b = tmp / 'in.flyer', tmp / 'out.flyer'
                rig(leaf, i * 7919 + 13, pl).save(a)
                simulate(a, b, 1)
                g = Flyer.load(b); mn = min(p[0] for p, _ in g.blocks())
                res[tuple(sorted((p[0], p[2], bl.kind.name) for p, bl in g.blocks() if bl.kind != Kind.PISTON_ARM))] += 1
            print(f'PL{pl} {leaf}: {len(res)} outcome(s) {sorted(res.values())}')
            if len(res) > 1 or pl == 12:
                for k in res: print('   ', res[k], k)
