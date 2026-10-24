"""build every k from bits.json, save to out/best/nKK_plPL_family.flyer, simulate at PL (must pass) and PL-1
(must fail): python verify_all.py"""
import json, os, glob, time
from concurrent.futures import ProcessPoolExecutor
import families as F, simk


def one(k):
    w = json.load(open('bits.json'))[str(k)]
    t = time.time(); r = F.build(k, w); dt = time.time() - t
    if r is None: return k, None, None, None, dt
    pl = F.predicted_pl(r); fam = F.fam_of(w)
    p = f'out/best/n{k:02d}_pl{pl}_{fam}.flyer'
    for old in glob.glob(f'out/best/n{k:02d}_pl*.flyer'):
        if os.path.normpath(old) != os.path.normpath(p): os.remove(old)
    r.flyer(pl).save(p)
    ok = 'pass=true' in simk.flies(p, k, pl)[1]
    below = 'pass=true' in simk.flies(p, k, pl - 1)[1]
    return k, pl, fam, (ok, below), dt


if __name__ == '__main__':
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, F.KS))
    tot = sum(r[1] or 0 for r in res); wt = sum((r[1] or 0) * (3 if r[0] <= 6 else 1) for r in res)
    for r in res: print(r, flush=True)
    print('sum', tot, 'weighted', wt, 'all fly at PL:', all(r[3] and r[3][0] for r in res),
          'none below:', not any(r[3] and r[3][1] for r in res))
