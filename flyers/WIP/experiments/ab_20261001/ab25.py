"""A/B 2.5 bps two-body flyer (classic-flying-machine generalization).

Bodies: A (honey) is only pulled, B (slime) only pushed. Word mwmw:
A moves slots 0,2; B moves slots 1,3 (slot = 2 ticks). Initial state = start of slot 1.
Group G1 = {P1 normal +X pushes B at slot 1, Q2 sticky -X extends slot 1, pulls A slot 2};
frozen slots 1,2, carried by B at slot 3 and by A at slot 0. G3 = mirror(z) of G1, shifted
by two slots (at slot-1 start it sits one block behind, x-1).
A observer pulses after each A move (odd slots) and hard-powers honey H next to the group.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind

E, W, U, D, S, N = range(6)


def mirror(c):
    return (c[0], c[1], -c[2])


def build(A_half, B_half, A_link, B_link, P1, Q2, O1, limit=30, rng=5):
    f = Flyer(rng_state=rng, push_limit=limit)
    A = set(A_half) | {mirror(c) for c in A_half} | set(A_link)
    B = set(B_half) | {mirror(c) for c in B_half} | set(B_link)
    assert not (A & B)
    for c in A:
        f.set(c, Block(Kind.HONEY))
    for c in B:
        f.set(c, Block(Kind.SLIME))
    # G1 at home (x as given), G3 mirrored and one block behind.
    f.set(P1, Block.piston(E))
    f.set(Q2, Block.piston(W, sticky=True))
    p3 = mirror(P1); p3 = (p3[0] - 1, p3[1], p3[2])
    q0 = mirror(Q2); q0 = (q0[0] - 1, q0[1], q0[2])
    f.set(p3, Block.piston(E))
    f.set(q0, Block.piston(W, sticky=True))
    (oc, od) = O1
    f.set(oc, Block.observer(od, powered=True))
    om = mirror(oc)
    md = {S: N, N: S}.get(od, od)
    f.set(om, Block.observer(md, powered=True))
    return f


if __name__ == '__main__':
    out = Path(__file__).resolve().parent
    A_half = [(0, 1, 1), (-1, 1, 1), (-2, 1, 1), (-2, 1, 2)]
    A_link = [(-2, 1, 0)]
    B_half = [(1, 0, 1), (1, 0, 2), (1, 0, 3), (0, 0, 3), (-1, 0, 3), (-1, 0, 2)]
    B_link = [(1, 0, 0)]
    f = build(A_half, B_half, A_link, B_link, P1=(0, 0, 1), Q2=(0, 1, 2), O1=((0, 2, 1), D))
    f.translate(10, 10, 10)
    f.save(out / 'ab25_v1.flyer')
    print('saved', len(f.blocks()), 'blocks')
