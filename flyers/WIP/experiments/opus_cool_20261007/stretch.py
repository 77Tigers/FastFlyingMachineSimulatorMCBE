"""Stretch the banked PL8 mirrored-chain flyer (rigid_sat_20261004/runs/assembled/mirror_freeF_L8.pkl, flipz,
d = (-1,0,8), last = K5) to long arms WITHOUT a new search.

Why it works: alt template K+2 = template K shifted by (4,1,1) (orientation ORIENTS[0]). Put 2m extra template
segments into chain 1 and shift its front part (K4, K5, rider V -> K_{last-1}, K_last, V) and F by s = (4m, m, m).
Under flipz with d' = (-1, 0, 8 + 2m) the image of the shifted front is the old image shifted by the SAME s, so the
whole front region (both chain ends, both riders, F) is the banked front translated rigidly; only the two start caps
move apart (the V opens up at the back). Each half is still one valid alternating chain.

The assembled design is re-checked exactly in satflyer with all cells fixed (materials re-chosen by the solver,
riders V/V', merges K0+N@1, K0'+N'@3), then exported with the max load as encoded PL.
usage: python stretch.py LAST [--src PKL --ls 5] [--tag NAME] [--tl 300] [--wk 4]   (LAST - ls even; any yz map:
       d' = d + (0, s_yz - A(s_yz)) keeps the front region a rigid translate)
"""
import sys, pathlib, pickle, time, argparse
HERE = pathlib.Path(__file__).resolve().parent
RS = HERE.parent / 'rigid_sat_20261004'
sys.path.insert(0, str(RS)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
import cfgsat
from chainflyer import origins, ORIENTS
if len(cfgsat.ORG) < 64:
    cfgsat.ORG.extend(origins(64, *ORIENTS[0])[len(cfgsat.ORG):])
from cfgsat import tcells, add
from satflyer import FlyerSAT, wpos, to_rigid, show
from front_mirror import shiftword
import mirror_gen as mg
import rigid

BANK = RS / 'runs' / 'assembled' / 'mirror_freeF_L8.pkl'
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'


def design(last, src_pkl=BANK, ls=5):
    """src_pkl: a mirror_gen-style design with chain 1 = K0, N, K1, templates K2..K_{ls-2}, free K_{ls-1}, K_ls,
    optional rider V; images '; shared F. Returns the design with last = K_last (same parity as ls)."""
    S = pickle.load(open(src_pkl, 'rb'))
    mp, d0 = S.get('map', 'flipz'), S.get('d', (-1, 0, 8))
    assert (last - ls) % 2 == 0 and last >= ls
    m = (last - ls) // 2
    s = (4 * m, m, m)
    f = mg.YZ[mp]; As = f(m, m)
    d = (d0[0], d0[1] + m - As[0], d0[2] + m - As[1])     # image of the shifted front = old image + s
    src = {nm: (tuple(w), {c: ks(k) for c, k in cells.items()}) for nm, w, cells, mat in S['sol']}
    for K in range(2, ls - 1):
        assert src[f'K{K}'][1] == tcells(K)[0], f'K{K} is not a template'
    half = [('K0',) + src['K0'], ('N',) + src['N'], ('K1',) + src['K1']]
    for K in range(2, last - 1):
        c, w = tcells(K)
        half.append((f'K{K}', w, c))
    for old, new in ((f'K{ls - 1}', f'K{last - 1}'), (f'K{ls}', f'K{last}'), ('V', 'V')):
        if old not in src: continue
        w, c = src[old]
        half.append((new, w, {add(u, s): k for u, k in c.items()}))
    T, km = mg.mapper(mp, d)
    segs = list(half)
    for nm, w, c in half:
        p = wpos(w, 2)
        segs.append((nm + "'", shiftword(w), {T(u, p): km(k) for u, k in c.items()}))
    w, c = src['F']
    segs.append(('F', w, {add(u, s): k for u, k in c.items()}))
    return segs, d, mp


def check(segs, tl=300, wk=4):
    names = [s[0] for s in segs]
    kinds = sorted({k for s in segs for k in s[2].values()} | {'g', 'P', 'S', 'R'})
    M = FlyerSAT([s[1] for s in segs], None, None, kinds=kinds, leaf=True, maxglue=30,
                 fixed=[(s[2], None) for s in segs], names=names, riders=[r for r in ('V', "V'") if r in names],
                 merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])])
    st, dt = M.solve(tl, wk)
    return M, st, dt


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('last', type=int); ap.add_argument('--tag', default=None)
    ap.add_argument('--tl', type=float, default=300); ap.add_argument('--wk', type=int, default=4)
    ap.add_argument('--src', default=str(BANK)); ap.add_argument('--ls', type=int, default=5)
    a = ap.parse_args()
    segs, d, mp = design(a.last, a.src, a.ls)
    occ = {}
    for t in range(4):
        seen = {}
        for nm, w, c in segs:
            for u in c:
                cc = (u[0] + wpos(w, t), u[1], u[2])
                if cc in seen: print('OVERLAP slot', t, cc, seen[cc], nm)
                seen[cc] = nm
    t0 = time.time()
    M, st, dt = check(segs, a.tl, min(a.wk, 4))
    print('last', a.last, 'd', d, 'segments', len(segs), 'blocks', sum(len(s[2]) for s in segs), '->', st,
          f'{time.time() - t0:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sv = M.solver
        loads = {f'{M.names[j] if isinstance(j, int) else j}@{t}': sv.Value(e) for (j, t), e in M.loadexpr.items()}
        PL = max(loads.values())
        print('max load', PL, 'loads>=7', sorted((v, k) for k, v in loads.items() if v >= 7))
        print('riders', [(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if sv.Value(v)])
        sol = M.extract()
        tag = a.tag or f'bird_last{a.last}'
        out = HERE / 'runs'; out.mkdir(exist_ok=True)
        pickle.dump({'sol': sol, 'map': mp, 'd': d, 'last': a.last, 'riders': [r for r in ('V', "V'") if r in M.names],
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])], 'loads': loads}, open(out / f'{tag}.pkl', 'wb'))
        rigid.to_flyer(to_rigid(sol), PL).save(str(out / f'{tag}.flyer'))
        print('saved', out / f'{tag}.flyer', 'encoded PL', PL)
