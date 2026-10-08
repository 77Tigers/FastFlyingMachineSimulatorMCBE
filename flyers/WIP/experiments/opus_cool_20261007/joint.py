"""Elbow joint between two alternating template chains of different orientation (for a gull-wing bird).
Module: K_{j-1}, K_j = templates in orientation OA (ORIENTS index), K_{j+1}..K_{j+nf} free, then two templates in
orientation OB shifted by yz offset `off` (relative to the natural OA->OB continuation). Ends are open
(BND_BACK / BND_FRONT, as modules.py). Control: OA == OB with nf = 1 must be FEASIBLE (it is the template).

usage: python joint.py J OA OB [--nf 1] [--L 7] [--tl 120] [--wk 4] [--r 2] [--offs all|dy,dz]
Writes runs/joint_j{J}_{OA}{OB}_{dy}_{dz}_L{L}.pkl for every solved offset.
"""
import sys, pathlib, pickle, time, argparse
HERE = pathlib.Path(__file__).resolve().parent
RS = HERE.parent / 'rigid_sat_20261004'
sys.path.insert(0, str(RS)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, add, Infeasible, show
from chainflyer import ORIENTS, template, origins
from modules import BND_BACK, BND_FRONT
from cfgsat import KALL


def tc(K, o, org):
    cells, w = template(K, *ORIENTS[o])
    return {add(org, u): k for u, k in cells.items()}, w


def build(j, OA, OB, off, L, nf=1, r=2, kinds=KALL):
    oa = origins(j + nf + 4, *ORIENTS[OA]); ob = origins(j + nf + 4, *ORIENTS[OB])
    # natural continuation: OB origins re-based so K_{j+1} sits where the OA chain would put it, then + off
    base = tuple(oa[j + 1][i] - ob[j + 1][i] for i in range(3))
    sh = add(base, (0,) + tuple(off))
    names, words, fixed, boxes, opens = [], [], [], [], {}
    for K in (j - 1, j):
        c, w = tc(K, OA, oa[K]); names.append(f'K{K}'); words.append(w); fixed.append((c, None)); boxes.append(None)
    for K in range(j + 1, j + nf + 1):
        o = oa[K] if K == j + 1 else add(ob[K], sh)
        w = (0, 1) if K % 2 == 0 else (2, 3)
        names.append(f'K{K}'); words.append(w); fixed.append(None)
        boxes.append([add(o, (a, b, e)) for a in range(-2, 3) for b in range(-r, r + 1) for e in range(-r, r + 1)])
    for K in (j + nf + 1, j + nf + 2):
        c, w = tc(K, OB, add(ob[K], sh)); names.append(f'K{K}'); words.append(w); fixed.append((c, None)); boxes.append(None)
    opens = {0: BND_BACK, len(names) - 1: BND_FRONT}
    M = FlyerSAT(words, None, L, kinds=kinds, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=boxes,
                 open_segs=opens)
    return M, names


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('j', type=int); ap.add_argument('OA', type=int); ap.add_argument('OB', type=int)
    ap.add_argument('--nf', type=int, default=1); ap.add_argument('--L', type=int, default=7)
    ap.add_argument('--tl', type=float, default=120); ap.add_argument('--wk', type=int, default=4)
    ap.add_argument('--r', type=int, default=2); ap.add_argument('--offs', default='all')
    ap.add_argument('--obj', default=None)
    a = ap.parse_args()
    offs = [(dy, dz) for dy in range(-2, 3) for dz in range(-2, 3)] if a.offs == 'all' else \
        [tuple(int(v) for v in a.offs.replace('m', '-').split(','))]
    for off in offs:
        t0 = time.time()
        try:
            M, names = build(a.j, a.OA, a.OB, off, a.L, a.nf, a.r)
        except Infeasible:
            print(off, 'TRIV_INFEASIBLE', flush=True); continue
        st, dt = M.solve(a.tl, min(a.wk, 4), objective=a.obj)
        print(off, st, f'{time.time() - t0:.1f}s', flush=True)
        if st in ('OPTIMAL', 'FEASIBLE'):
            sol = M.extract()
            sv = M.solver
            loads = {f'{M.names[j_] if isinstance(j_, int) else j_}@{t}': sv.Value(e) for (j_, t), e in M.loadexpr.items()}
            print('  max load', max(loads.values()))
            for nm, w, c, m in sol:
                print('  ', nm, w, m, len(c), sorted(c.items()))
            pickle.dump({'sol': sol, 'j': a.j, 'OA': a.OA, 'OB': a.OB, 'off': off, 'nf': a.nf, 'loads': loads},
                        open(HERE / 'runs' / f'joint_j{a.j}_{a.OA}{a.OB}_{off[0]}_{off[1]}_nf{a.nf}_L{a.L}.pkl', 'wb'))
