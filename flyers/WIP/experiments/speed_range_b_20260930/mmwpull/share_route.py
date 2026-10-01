import sys, json, random, collections
from pathlib import Path
from multiprocessing import Pool
import share, model
def job(args):
    i, pl, out = args
    gt, places, oo = pl; place = (tuple(gt), [(a, tuple(b)) for a, b in places], oo)
    best = None; st = collections.Counter()
    for seed in range(8):
        B, why = share.build(seed, place, {0, 2})
        st[why.split(':')[0]] += 1
        if B is None: continue
        d = model.trim(B.d, random.Random(seed))
        key = (d.max_load(), sum(1 for it in d.items if it.cat == 'glue'))
        if best is None or key < best[0]: best = (key, d)
    if best is None: return (i, None, dict(st))
    (L, g), d = best
    gl = [sum(1 for it in d.items if it.cat == 'glue' and it.body == b) for b in range(3)]
    if L <= 23:
        name = f'd{i:03d}_L{L}_g{g}'
        f = d.to_flyer(limit=L); f.translate(20, 20, 20); f.save(Path(out) / f'{name}.flyer')
        (Path(out) / f'{name}.json').write_text(json.dumps(place))
    return (i, (L, g, gl), dict(st))
if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(exist_ok=True)
    pls = json.load(open('double_legal.json'))
    with Pool(5) as p:
        for r in p.imap_unordered(job, [(i, pl, str(out)) for i, pl in enumerate(pls)]):
            print(r, flush=True)
