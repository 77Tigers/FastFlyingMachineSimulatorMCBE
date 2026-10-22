"""N6 (16 ticks, +6, 3.75 bps) four-body all-push ring, first construction.

Bodies A,B,C,D rest at global slots {0,1},{2,3},{4,5},{6,7}. W(X) = next body (B,C,D,A).
Module X (frame: X's redstone blocks at x=0): X front plate x=1 over P+R columns, RBs at x=0,
six +X pushers in P columns (ready x=0, spent x=-1/-2), W(X) back plate in P+R columns at x=b(k).
Every ready pusher is powered by X's RBs; whichever updates first pushes X, the others ride X.
Spent pushers ride W(X)'s back plate and regain 2 cells during X's rest.
usage: python build_n6.py OUT.flyer [PL]
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from fastflyer import Flyer, Block, Kind

R = [(0, 0), (0, 2)]
P = [(0, -1), (1, 0), (0, 1), (1, 2), (0, 3), (-1, 0)]
PLATE = P + R
BACK = P + R
ORDER = ['A', 'B', 'C', 'D']
REST = {'A': 0, 'B': 2, 'C': 4, 'D': 6}
MAT = {'A': Kind.SLIME, 'B': Kind.HONEY, 'C': Kind.SLIME, 'D': Kind.HONEY}
ORIG = {'A': 0, 'B': 0, 'C': -1, 'D': -1}                 # module x origins
YZ = {'A': (0, 0), 'B': (0, 7), 'C': (-5, 7), 'D': (-5, 0)}
NEXT = {X: ORDER[(i + 1) % 4] for i, X in enumerate(ORDER)}
PREV = {v: k for k, v in NEXT.items()}
# connectors (world coords at global slot 0), owner body -> cells
CONN = {
    'B': [(-3, 0, 4), (-3, 0, 5), (-2, 0, 5), (-1, 0, 5), (0, 0, 5), (1, 0, 5)],
    'C': [(-3, -2, 7), (-3, -3, 7), (-2, -3, 7), (-1, -3, 7), (0, -3, 7)],
    'D': [(-4, -5, 5), (-4, -5, 4), (-3, -5, 4), (-2, -5, 4), (-1, -5, 4), (0, -5, 4)],
    'A': [(-2, -3, 0), (-2, -2, 0), (-1, -2, 0), (0, -2, 0), (1, -2, 0)],
}


def k0(X): return (0 - REST[X]) % 8
def b(k): return {1: -2, 2: -1, 3: -2}.get(k, -3)


def pusher_state(f, k):
    """V-frame x, piston state, arm? for a pusher with fire slot f (2..7) at local slot k."""
    if 2 <= k <= 7:
        if k <= f: return 0, 0, False
        if k == f + 1: return -1, 2, True
        return -2, 0, False
    if k == 0: return (-1, 2, True) if f == 7 else (-2, 0, False)
    return -1, 0, False   # k == 1


def build(pl=40, pull=True):
    fl = Flyer(push_limit=pl)
    cells = {}

    def put(c, blk, who):
        assert c not in cells, (c, who, cells[c][1])
        cells[c] = (blk, who)

    for X in ORDER:
        x0 = ORIG[X]; oy, oz = YZ[X]; k = k0(X)
        w = lambda dx, yz: (x0 + dx, oy + yz[0], oz + yz[1])
        for r in R: put(w(0, r), Block(Kind.REDSTONE_BLOCK), X + ' RB')
        for c in PLATE: put(w(1, c), Block(MAT[X]), X + ' plate')
        for j, p in enumerate(P):
            if pull and X == 'C' and j + 2 == 7: continue      # C's slot-7 push becomes a pull by B
            dx, st, arm = pusher_state(j + 2, k)
            put(w(dx, p), Block.piston(0, state=st), f'{X} pusher f{j + 2}')
            if arm: put(w(dx + 1, p), Block(Kind.PISTON_ARM), f'{X} arm f{j + 2}')
        Wb = NEXT[X]
        for c in BACK: put(w(b(k), c), Block(MAT[Wb]), Wb + ' back')
    for X, cs in CONN.items():
        for c in cs: put(c, Block(MAT[X]), X + ' conn')
    if pull:
        # sticky on B (host, rests global 2,3) pulls C at C-local 7 (global 3); extends at global 2
        put((1, 1, 6), Block.piston(1, sticky=True, state=0), 'B sticky')
        # C target glue: one cell above C's back plate (C frame), pulled at global 3
        put((-3, 1, 6), Block(MAT['C']), 'C target')
        put((-2, 1, 6), Block(MAT['C']), 'C target')
        # A's redstone block: lateral to the sticky only at global slot 2 (B-local 0)
        put((3, 1, 5), Block(Kind.REDSTONE_BLOCK), 'A RBpull')
        for c in [(2, 1, 5), (2, 1, 4), (2, 1, 3), (1, 1, 3)]: put(c, Block(MAT['A']), 'A pullarm')
    for c, (blk, _) in cells.items(): fl.set(c, blk)
    return fl, cells


if __name__ == '__main__':
    out = sys.argv[1]; pl = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    fl, cells = build(pl, pull=(len(sys.argv) <= 3 or sys.argv[3] != 'nopull'))
    fl.save(out)
    from collections import Counter
    print(len(cells), 'blocks', Counter(w.split()[0] + ' ' + w.split()[1] for _, w in cells.values()))
