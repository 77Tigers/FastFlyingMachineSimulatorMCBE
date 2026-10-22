"""PL26 V9 screw ring with B's slot-7 push replaced by a sticky pull from A (B's predecessor).
Sticky S rigid on A, in A's hole column above B's cover, facing -X; extends at A-local 0, pulls B at A-local 1.
Power: a rod on D (A's predecessor) faces A's plate cell (1,0,2) only at A-local 0, hard-powering it; that
plate cell soft-powers S. usage: python pull26.py OUT.flyer PL [norod]"""
import sys, pathlib, pickle
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from close_ring import chain
from ring_designer import Ring, route_all, V9
from fastflyer import Block, Kind


def build(pl, rod=True, pull=True):
    place, _ = chain([(d, (5, 4), 1) for d in (-1, 0, -1, 2)])
    ring = Ring(V9, {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()})
    route_all(ring)
    assert ring.place['A'] == (0, (0, 0), 0)
    fl = ring.flyer(pl)
    if not pull: return fl
    # remove B's canonical f7 pusher (B is at B-local 6 at global 0: ready, state 0)
    occ = ring.world(0, canon=True)
    rm = [c for c, l in occ.items() if l[0][0] == 'B' and l[0][1] == 'P' and l[0][2][0] == 5]
    assert len(rm) == 1, rm
    fl.remove(rm[0])
    new = {(1, 1, 2): Block.piston(1, sticky=True, state=0)}
    if rod:
        new[(1, -1, 2)] = Block.rod(2)          # faces +Y onto A plate (1,0,2)
        for c in [(0, -1, 2), (-1, -1, 2), (-1, -2, 2)]: new[c] = Block(fl.get((-1, -3, 2)).kind)   # D's material (D glue at (-1,-3,2))
    for c, b in new.items():
        assert fl.get(c) is None, (c, fl.get(c))
        fl.set(c, b)
    return fl


if __name__ == '__main__':
    fl = build(int(sys.argv[2]), rod=not (len(sys.argv) > 3 and sys.argv[3] == 'norod'),
               pull=not (len(sys.argv) > 3 and sys.argv[3] == 'base'))
    fl.save(sys.argv[1]); print('saved', sys.argv[1], fl.occupied_count())
