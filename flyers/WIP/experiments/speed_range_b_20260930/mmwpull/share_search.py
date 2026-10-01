"""python share_search.py OUT procs  -- two aligned pairs (Y=0: V1->U2, Y=1: V2->U0), drop observers of bodies 2 and 0."""
import sys, json, random, itertools, collections
from pathlib import Path
from multiprocessing import Pool
import share, model, gen

GTS = [('S', 'H', 'S'), ('S', 'S', 'H'), ('H', 'S', 'S')]

def job(args):
    s1, gt, o1, out = args
    rng = random.Random(s1 * 100 + GTS.index(gt) * 10 + o1)
    res = []
    base = (gt, [(0, (0, 0, 0)), (s1, (0, 0, 0)), (0, (0, 0, 0))], [0, o1, 0])
    al2 = share.aligned_places(rng, 0, 1, 2, base)
    st = collections.Counter()
    for p2 in al2:
        b2 = (gt, [(0, (0, 0, 0)), (s1, (0, 0, 0)), p2], [0, o1, 0])
        al0 = share.aligned_places(rng, 1, 2, 0, b2)
        for p0 in al0:
            place = (gt, [p0, (s1, (0, 0, 0)), p2], [0, o1, 0])
            best = None
            for seed in range(3):
                B, why = share.build(seed, place, {0, 2})
                st[why.split(':')[0]] += 1
                if B is None:
                    if why == 'template': break
                    continue
                d = model.trim(B.d, random.Random(seed))
                key = (d.max_load(), sum(1 for it in d.items if it.cat == 'glue'))
                if best is None or key < best[0]: best = (key, d)
            if best:
                (L, g), d = best
                res.append((L, g, place))
                if L <= 22:
                    name = f's{s1}_{GTS.index(gt)}_{o1}_L{L}_g{g}_{len(res)}'
                    f = d.to_flyer(limit=L); f.translate(20, 20, 20); f.save(Path(out) / f'{name}.flyer')
                    (Path(out) / f'{name}.json').write_text(json.dumps(place))
    return (s1, gt, o1, dict(st), sorted(res)[:3])

if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(exist_ok=True)
    jobs = [(s1, gt, o1, str(out)) for s1 in range(8) for gt in GTS for o1 in (0, 1)]
    with Pool(int(sys.argv[2])) as p:
        for r in p.imap_unordered(job, jobs):
            print(r, flush=True)
