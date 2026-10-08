"""opus_cool (2026-10-07): long mirrored "bird" = the banked PL8 mechanism (mirrored_chains_shared_mwmw) with long arms.
Chain 1 = load-7 start cap (K0, N, K1) + alt templates K2..K_last; chain 2 = its yz-mirror image (half-cycle shift);
both push ONE shared passive mwmw front F. Only K_{last-1}, K_last, rider V and F are free (mirror_gen.build).
Extends cfgsat.ORG in place so chains can be longer than 11 segments.

usage: python bird.py MAP dx,dy,dz MODE LOAD LAST [--tl 600] [--wk 4] [--r 2] [--obj maxload] [--vr 2]
Writes runs/bird_MAP_dx_dy_dz_MODE_L{LOAD}_last{LAST}.pkl and .flyer (encoded PL = max load) when solved.
"""
import sys, pathlib, pickle, time, argparse
HERE = pathlib.Path(__file__).resolve().parent
RS = HERE.parent / 'rigid_sat_20261004'
sys.path.insert(0, str(RS)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
sys.argv_saved = list(sys.argv)
import cfgsat
from chainflyer import origins, ORIENTS
if len(cfgsat.ORG) < 48:
    cfgsat.ORG.extend(origins(48, *ORIENTS[0])[len(cfgsat.ORG):])   # same list object -> mirror_gen sees it too
import mirror_gen as mg
from satflyer import to_rigid, show
import rigid


def run(mp, d, mode, L, last, tl, wk, r=2, obj=None, vr=2, free=None, tag=None):
    mg.VR = vr
    free = free or (last - 1, last)
    t0 = time.time()
    M = mg.build(mp, d, mode, L, last, free, r)
    if isinstance(M, str):
        print(mp, d, mode, L, last, M, flush=True); return M, None
    tb = time.time() - t0
    st, dt = M.solve(tl, wk, objective=obj)
    print(mp, d, mode, 'L', L, 'last', last, st, f'build {tb:.1f}s solve {dt:.1f}s', flush=True)
    if st not in ('OPTIMAL', 'FEASIBLE'):
        return st, None
    sv = M.solver
    loads = {f'{M.names[j] if isinstance(j, int) else j}@{t}': sv.Value(e) for (j, t), e in M.loadexpr.items()}
    PL = max(loads.values())
    sol = M.extract()
    tag = tag or f'bird_{mp}_{d[0]}_{d[1]}_{d[2]}_{mode}_L{L}_last{last}'
    out = HERE / 'runs'; out.mkdir(exist_ok=True)
    pickle.dump({'sol': sol, 'map': mp, 'd': d, 'last': last, 'mode': mode,
                 'riders': sorted(M.names[x] for x in M.riders),
                 'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])], 'loads': loads}, open(out / f'{tag}.pkl', 'wb'))
    rigid.to_flyer(to_rigid(sol), PL).save(str(out / f'{tag}.flyer'))
    nb = sum(len(c) for _, _, c, _ in sol)
    big = sorted(((v, k) for k, v in loads.items() if v >= 6), reverse=True)
    print('saved', out / f'{tag}.flyer', 'PL', PL, 'blocks', nb, 'segments', len(sol), 'loads>=6', big[:12], flush=True)
    for nm, w, c, m in sol:
        if nm.rstrip("'") in {f'K{k}' for k in free} | {'V', 'F'}:
            print(' ', nm, w, len(c), sorted(c.items()))
    return st, sol


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('map'); ap.add_argument('d'); ap.add_argument('mode'); ap.add_argument('L', type=int)
    ap.add_argument('last', type=int)
    ap.add_argument('--tl', type=float, default=600); ap.add_argument('--wk', type=int, default=4)
    ap.add_argument('--r', type=int, default=2); ap.add_argument('--obj', default=None); ap.add_argument('--vr', type=int, default=2)
    ap.add_argument('--free', default=None); ap.add_argument('--tag', default=None)
    a = ap.parse_args()
    d = tuple(int(v) for v in a.d.replace('m', '-').split(','))
    free = tuple(int(v) for v in a.free.split(',')) if a.free else None
    run(a.map, d, a.mode, a.L, a.last, a.tl, min(a.wk, 4), a.r, a.obj, a.vr, free, a.tag)
