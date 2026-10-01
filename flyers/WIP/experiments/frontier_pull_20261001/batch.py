"""python batch.py SPEC OUT n0 n1 maxload procs [spread xspread]"""
import sys, json, random, collections
from pathlib import Path
from multiprocessing import Pool
import gen, pmodel, specs, os
MODE = os.environ.get('GMODE', 'inc')
RETRY = int(os.environ.get('GRETRY', '6'))

def one(args):
    specname, seed, out, maxload, spread, xspread = args
    spec = specs.SPECS[specname]()
    import random as _r
    rng = _r.Random(seed * 7 + 1)
    place = None
    if MODE == 'inc':
        for _ in range(8):
            place = gen.inc_place(spec, rng, spread, xspread)
            if place is None:
                continue
            Bt = gen.Builder(spec, rng, *place); Bt.setup()
            if 'rsgroups' in spec:
                N_ = len(spec['S'])
                if all(Bt.rs_feasible(Y, [Bt.pidx[((Y + o) % N_, kn)] for kn, o in spec['rsgroups']]) for Y in range(N_)):
                    break
                place = None
                continue
            if all(Bt.og_feasible((v + 0) % 5, [Bt.pidx[(v, k1)], Bt.pidx[((v + o2) % 5, k2)]])
                   for k1, o1, k2, o2, w in spec.get('share', []) for v in range(len(spec['S']))):
                break
            place = None
    if MODE == 'inc' and place is None:
        return (seed, 'incfail', None)
    best = None
    for r in range(RETRY if MODE == 'inc' else 1):
        B, why, info = gen.build(spec, seed * 100 + r, place=place, spread=spread, xspread=xspread, jitter=0 if r == 0 else 2.0)
        if B is None:
            continue
        d = pmodel.trim(B.d, random.Random(r))
        key = (d.max_load(), sum(d.glue_counts()))
        if best is None or key < best[0]:
            best = (key, d, B)
    if best is None:
        return (seed, why, info if why == 'final' else None)
    d = best[1]
    L = d.max_load()
    if L > maxload:
        return (seed, 'over', L)
    f = d.to_flyer(limit=L); f.translate(20, 20, 20)
    name = f's{seed:06d}_L{L}'
    f.save(Path(out) / f'{name}.flyer')
    return (seed, 'ok', dict(name=name, L0=L, L=L, glue=d.glue_counts(), place=place))
    B, why, info = None, None, None
    if B is None:
        return (seed, why, info if why == 'final' else None)
    L0 = B.d.max_load()
    if L0 > maxload + 4:
        return (seed, 'over', L0)
    d = pmodel.trim(B.d, random.Random(seed))
    L = d.max_load()
    if L > maxload:
        return (seed, 'over', L)
    f = d.to_flyer(limit=L); f.translate(20, 20, 20)
    name = f's{seed:06d}_L{L}'
    f.save(Path(out) / f'{name}.flyer')
    return (seed, 'ok', dict(name=name, L0=L0, L=L, glue=d.glue_counts(), place=info))

if __name__ == '__main__':
    specname = sys.argv[1]
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    n0, n1, maxload, procs = map(int, sys.argv[3:7])
    spread = int(sys.argv[7]) if len(sys.argv) > 7 else 3
    xspread = int(sys.argv[8]) if len(sys.argv) > 8 else 2
    st = collections.Counter(); rows = []
    with Pool(procs) as p:
        for seed, why, info in p.imap_unordered(one, [(specname, s, str(out), maxload, spread, xspread) for s in range(n0, n1)], chunksize=10):
            st[why] += 1
            if why == 'ok':
                rows.append(info); print(info['name'], info['L0'], '->', info['L'], info['glue'], flush=True)
            elif why == 'final':
                print('final', seed, info, flush=True)
    print(dict(st))
    (out / f'manifest_{n0}_{n1}.json').write_text(json.dumps(rows, indent=1))
