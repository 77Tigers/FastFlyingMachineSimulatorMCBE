"""Validate satflyer's encoding: fixed known-good designs (accepted by rigid.check) must be FEASIBLE."""
import sys, pathlib, itertools, pickle, os
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
os.environ['LEAF'] = '1'
import rigid
rigid.LEAF = True
from satflyer import FlyerSAT, show
from alt import altchain


def kindstr(k): return k if isinstance(k, str) else f'{k[0]}{k[1]}'


def run(segs, open_names, leaf, kinds=('g', 'P', 'S', 'R'), extra_kinds=()):
    rigid.LEAF = leaf
    print('rigid.check:', rigid.check(segs, ignore=set(open_names)))
    world = [({(s.origin[0] + c[0], s.origin[1] + c[1], s.origin[2] + c[2]): kindstr(k) for c, k in s.cells.items()}, s.mat)
             for s in segs]
    allc = [c for w, _ in world for c in w]
    lo = [min(c[i] for c in allc) - 1 for i in range(3)]; hi = [max(c[i] for c in allc) + 1 for i in range(3)]
    box = list(itertools.product(*[range(lo[i], hi[i] + 1) for i in range(3)]))
    ks = sorted({k for w, _ in world for k in w.values()} | set(kinds))
    names = [s.name for s in segs]
    M = FlyerSAT([s.word for s in segs], box, None, kinds=ks, leaf=leaf, maxglue=12, fixed=world, names=names,
                 open_segs={names.index(x) for x in open_names})
    st, dt = M.solve(60, 8)
    print('sat:', st, f'{dt:.1f}s')
    return st


if __name__ == '__main__':
    segs = pickle.load(open(HERE.parent / 'rigid_chain_20261003' / 'back_leaf_A8B8_load9.pkl', 'rb'))
    print('== A8B8 back, fronts open, leaf'); run(segs, ['a2', 'b2'], True)
    ch = altchain(6)
    print('== alt chain 6, ends open'); run(ch, ['K0', 'K5'], False)
