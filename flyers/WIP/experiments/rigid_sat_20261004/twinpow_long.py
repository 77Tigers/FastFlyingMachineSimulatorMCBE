"""Long-chain twin-powered front (2026-10-06): like twinpow_sweep.py but for any LAST (chain K2..K_last).
K_{last-2}, K_{last-1}, K_last in boxes nbhd(template, r); K_{last-2} must contain its template, K_{last-1} only the
origin glue ORG[last-1], K_last free. Rider V (mode V, mirror_gen.chain logic for `last`) or none.
usage: LOAD=7 python twinpow_long.py TAG LAST MODE TL m3 m4 m5 r [maps|all] [dxlo,dxhi] [fmax] [nproc]"""
import sys, time, os, pickle
from multiprocessing import Pool
from pathlib import Path
from subB_lib import nbhd, Pins, solve, report, show, tcells, candidates, YZ, add3, ORG, G
from subB_lib import KALL  # noqa

HERE = Path(__file__).resolve().parent
RUNS = HERE / 'runs' / 'twinpow_long'; RUNS.mkdir(parents=True, exist_ok=True)


def buildL(mp, d, mode, L, last, segs, maxsize):
    """segs: {'K3': ('box', cells), ...} for chain segments; others = templates."""
    def chain(last_, free, r, mode_):
        half = []
        for nm, w, cells, m in G.START:
            if nm in ('K0', 'N', 'K1'):
                half.append((nm, tuple(w), {c: G.ks(k) for c, k in cells.items()}, None, None))
        for K in range(2, last_ + 1):
            c, w = tcells(K); nm = f'K{K}'
            if nm in segs: half.append((nm, w, None, list(segs[nm][1]), None))
            else: half.append((nm, w, c, None, None))
        wl = tcells(last_)[1]; k = G.second_slot(wl)
        if mode_ == 'V':
            rw = tuple(sorted(((k + 2) % 4, (k + 3) % 4)))
            o = ORG[last_]
            half.append(('V', rw, None, [add3(o, (a, b, e)) for a in range(-3, 2) for b in range(-G.VR, G.VR + 1)
                                         for e in range(-G.VR, G.VR + 1)], 'P'))
        return half
    old = G.chain; G.chain = chain; G.PIN = None
    try:
        return G.build(mp, d, mode, L, last, (), 2, maxsize=maxsize)
    finally:
        G.chain = old


def one(args):
    mp, d, mode, tl, m3, m4, m5, r = args[:8]
    last = args[8] if len(args) > 8 else 5
    t0 = time.time()
    Ta, Tb, Tc = (tcells(last - 2)[0], tcells(last - 1)[0], tcells(last)[0])
    na, nb, nc = f'K{last-2}', f'K{last-1}', f'K{last}'
    segs = {na: ('box', nbhd(list(Ta), r)), nb: ('box', nbhd(list(Tb), r)), nc: ('box', nbhd(list(Tc), r))}
    ms = {na: m3, nb: m4, nc: m5}
    if mode == 'V': ms['V'] = 1
    L = int(os.environ.get('LOAD', 7))
    M = buildL(mp, d, mode, L, last, segs, ms)
    if isinstance(M, str): return args, M, 0, None, None
    P = Pins(M); P.cells(na, Ta); P.cells(nb, {ORG[last - 1]: 'g'})
    st, dt, _ = solve(M, tl, 1)
    rep = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        rep = report(M) + '\n' + show(M.extract())
        sol = M.extract()
        tag = f'twinlong_last{last}_{mode}_L{L}_{mp}_{d[0]}_{d[1]}_{d[2]}'
        pickle.dump({'sol': sol, 'map': mp, 'd': d, 'riders': sorted(M.names[x] for x in M.riders),
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]}, open(RUNS / f'{tag}.pkl', 'wb'))
    return args, st, dt, time.time() - t0, rep


if __name__ == '__main__':
    tag, last, mode, tl = sys.argv[1], int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
    m3, m4, m5, r = (int(v) for v in sys.argv[5:9])
    maps = list(YZ) if len(sys.argv) <= 9 or sys.argv[9] == 'all' else sys.argv[9].split(',')
    lo, hi = (int(v) for v in (sys.argv[10] if len(sys.argv) > 10 else 'm3,1').replace('m', '-').split(','))
    fmax = int(sys.argv[11]) if len(sys.argv) > 11 else 4
    nproc = int(sys.argv[12]) if len(sys.argv) > 12 else 4
    cands = sorted(candidates(maps, last, fmax, range(lo, hi + 1)), key=lambda c: (c[2], abs(c[1][0] + 1)))
    print('candidates', len(cands), flush=True)
    log = open(RUNS / f'{tag}.log', 'a'); cnt = {}; t00 = time.time()
    with Pool(nproc) as pool:
        for args, st, dt, tot, rep in pool.imap_unordered(one, [(mp, d, mode, tl, m3, m4, m5, r, last) for mp, d, _ in cands]):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{args[0]} {args[1]} {mode} {st} {dt:.1f}\n'); log.flush()
            if rep: print('FOUND', args[0], args[1], st, '\n' + rep, flush=True)
            if st == 'UNKNOWN': print('UNKNOWN', args[0], args[1], flush=True)
            if sum(cnt.values()) % 50 == 0: print(cnt, f'{time.time()-t00:.0f}s', flush=True)
    print('done', cnt, f'total {time.time()-t00:.0f}s', flush=True)
