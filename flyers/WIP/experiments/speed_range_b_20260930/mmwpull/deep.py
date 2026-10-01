"""placement sampling + many routing retries per promising placement.
python deep.py OUT n0 n1 maxload procs retries"""
import sys, json, random, collections
from pathlib import Path
from multiprocessing import Pool
import gen, model

def one(args):
    seed, out, maxload, retries = args
    rng = random.Random(seed)
    place = gen.rand_place(rng)
    B, why, info = gen.build(seed * 1000, place=place)
    if B is None and why == 'template':
        return (seed, 'template', None)
    best = None
    for r in range(retries):
        B, why, info = gen.build(seed * 1000 + r, place=place, jitter=0 if r == 0 else 2.0)
        if B is None:
            continue
        L0 = B.d.max_load()
        if L0 > maxload + 4:
            continue
        d = model.trim(B.d, random.Random(r))
        L = d.max_load()
        g = sorted(sum(1 for it in d.items if it.cat == 'glue' and it.body == b) for b in range(3))
        key = (L, sum(g))
        if best is None or key < best[0]:
            best = (key, d, r)
        if r >= 3 and best[0][0] > maxload + 2:
            break
    if best is None or best[0][0] > maxload:
        return (seed, 'over', best[0] if best else None)
    (L, gs), d, r = best
    f = d.to_flyer(limit=L); f.translate(20, 20, 20)
    name = f's{seed:06d}_L{L}'
    f.save(Path(out) / f'{name}.flyer')
    return (seed, 'ok', dict(name=name, L=L, glue=gs, r=r, place=place))

if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    n0, n1, maxload, procs, retries = map(int, sys.argv[2:7])
    st = collections.Counter(); rows = []
    with Pool(procs) as p:
        for seed, why, info in p.imap_unordered(one, [(s, str(out), maxload, retries) for s in range(n0, n1)], chunksize=5):
            st[why] += 1
            if why == 'ok':
                rows.append(info); print(info['name'], info['glue'], flush=True)
    print(dict(st))
    (out / f'manifest_{n0}_{n1}.json').write_text(json.dumps(rows, indent=1))
