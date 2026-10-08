"""psat (power-rider satflyer copy) must accept the banked PL8 mirrored design at load 8 and reject it at 7, with and
without leafrod.  usage: python validate_bank.py"""
import sys, pathlib, pickle, time
HERE = pathlib.Path(__file__).resolve().parent
RS = HERE.parent / 'rigid_sat_20261004'
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(RS)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from psat import FlyerSAT
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'


def check(sol, L, riders, merges, leafrod=False, tl=120, wk=4, kbs=None):
    segs = [(nm, tuple(w), {c: ks(k) for c, k in cells.items()}, mat) for nm, w, cells, mat in sol]
    kinds = sorted({k for s in segs for k in s[2].values()} | {'g', 'P', 'S', 'R'})
    M = FlyerSAT([s[1] for s in segs], None, L, kinds=kinds, leaf=True, maxglue=30,
                 fixed=[(s[2], None) for s in segs], names=[s[0] for s in segs], riders=riders, merges=merges,
                 leafrod=leafrod, kinds_by_seg=kbs or {r: sorted(set(dict(segs)[r] if False else [k for s in segs if s[0] == r for k in s[2].values()])) for r in riders})
    st, dt = M.solve(tl, wk)
    return M, st, dt


if __name__ == '__main__':
    D = pickle.load(open(RS / 'runs' / 'assembled' / 'mirror_freeF_L8.pkl', 'rb'))
    for lr in (False, True):
        for L in (8, 7):
            M, st, dt = check(D['sol'], L, D['riders'], D['merges'], lr)
            print(f'banked PL8 fixed, leafrod={lr}, load {L}: {st} {dt:.1f}s', flush=True)
