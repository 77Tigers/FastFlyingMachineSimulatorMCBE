"""Load-6 start cap search on psat (power riders allowed).

Chain: K0 (mmww) + N (wmmw), merged at slot 1 and pulled by K1 (wwmm); K2, K3 templates, K4 template = front boundary.
K0 = 7b start cap minus its rod-AND relay: P (0,-1,-1), g (0,0,-1), g (0,0,0), P (0,0,1).  N = g (2,-1,-1), S (2,0,-1).
K1 = template cells required (+ up to K1MAX - 5 extra blocks in a box).  Power riders W1..Wn: one block (R/rod/observer),
free word, box around the cap.  Optionally piston riders.
usage: python back6.py L NRIDERS [K1MAX] [TL] [WORKERS] [--k0free] [--words w1,w2]
"""
import sys, pathlib, itertools, pickle, time, argparse
HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
for p in (str(EXP / 'rigid_chain_20261003'), str(EXP / 'rigid_sat_20261004'), str(EXP / 'power_riders_20261007')):
    if p in sys.path: sys.path.remove(p)
    sys.path.insert(0, p)
from psat import FlyerSAT, Infeasible, WORDS, show, D6
from cfgsat import tcells, report
from modules import BND_FRONT

KPOW = ['R'] + [f'D{i}' for i in range(6)] + [f'O{i}' for i in range(6)]
KALL = ['g', 'P', 'S'] + KPOW
K0 = {(0, -1, -1): 'P', (0, 0, -1): 'g', (0, 0, 0): 'g', (0, 0, 1): 'P'}
N = {(2, -1, -1): 'g', (2, 0, -1): 'S'}


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def cube(c, xr, r): return [add(c, (a, b, e)) for a in xr for b in range(-r, r + 1) for e in range(-r, r + 1)]


def build(L, rwords, k1max=6, k0free=False, wbox=None, k1box=None, k0max=4, nmax=2):
    names = ['K0', 'N', 'K1', 'K2', 'K3', 'K4']
    words = [WORDS['mmww'], WORDS['wmmw'], WORDS['wwmm'], tcells(2)[1], tcells(3)[1], tcells(4)[1]]
    k1c = {u: k for u, k in tcells(1)[0].items() if k in 'gSP'}   # template glue/pistons; power block free
    k1box = k1box or cube((2, 0, 0), range(-1, 3), 2)
    k1box = sorted(set(k1box) | set(k1c))
    if k0free:
        fixed = [None, None, None, (tcells(2)[0], None), (tcells(3)[0], None), (tcells(4)[0], None)]
        boxes = [cube((0, 0, 0), range(-1, 1), 2), cube((2, 0, -1), range(-1, 2), 2), k1box, None, None, None]
        must = {'K0': {(0, 0, 0): 'g', (0, 0, 1): 'P'}, 'K1': k1c}
        maxsize = [k0max, nmax, k1max, None, None, None]
    else:
        fixed = [(K0, None), (N, None), None, (tcells(2)[0], None), (tcells(3)[0], None), (tcells(4)[0], None)]
        boxes = [None, None, k1box, None, None, None]
        must = {'K1': k1c}
        maxsize = [None, None, k1max, None, None, None]
    riders, kbs = [], {}
    wbox = wbox or cube((1, 0, 0), range(-2, 5), 2)
    for i, w in enumerate(rwords):
        nm = f'W{i + 1}'
        names.append(nm); words.append(WORDS[w]); fixed.append(None); boxes.append(wbox); maxsize.append(None)
        riders.append(nm); kbs[nm] = KPOW
    M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=max(L - 1, 1), fixed=fixed, names=names, boxes=boxes,
                 open_segs={5: BND_FRONT}, riders=riders, kinds_by_seg=kbs, merges=[(1, ['K0', 'N'])], must=must,
                 maxsize=maxsize, leafrod=True)
    # symmetry: riders with equal words are interchangeable -> order them lexicographically is skipped (small cases)
    return M


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('nr', type=int)
    ap.add_argument('k1max', type=int, nargs='?', default=6)
    ap.add_argument('tl', type=float, nargs='?', default=120)
    ap.add_argument('wk', type=int, nargs='?', default=4)
    ap.add_argument('--k0free', action='store_true')
    ap.add_argument('--words', default=None)
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    out = HERE / 'runs'; out.mkdir(exist_ok=True)
    combos = [tuple(a.words.split(','))] if a.words else list(itertools.combinations_with_replacement(list(WORDS), a.nr))
    for rw in combos:
        t0 = time.time()
        try:
            M = build(a.L, rw, a.k1max, a.k0free)
        except Infeasible as e:
            print(rw, 'TRIV_INFEASIBLE', e, flush=True); continue
        st, dt = M.solve(a.tl, a.wk)
        print(rw, st, f'{dt:.1f}s', flush=True)
        if st in ('OPTIMAL', 'FEASIBLE'):
            sol = M.extract(); print(show(sol)); print(report(M), flush=True)
            tag = f"b6_L{a.L}_{'_'.join(rw)}_k1{a.k1max}{'_free' if a.k0free else ''}{a.tag}"
            pickle.dump({'sol': sol, 'riders': sorted(M.names[r] for r in M.riders)}, open(out / f'{tag}.pkl', 'wb'))
            print('saved', out / f'{tag}.pkl', flush=True)
