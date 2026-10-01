"""parallel batch: python batch.py OUT n0 n1 maxload procs [spread xspread]"""
import sys, json, random
from pathlib import Path
from multiprocessing import Pool
import gen, model

def one(args):
    seed, out, maxload, spread, xspread = args
    B, why, info = gen.build(seed, spread=spread, xspread=xspread)
    if B is None:
        return (seed, why, None)
    L0 = B.d.max_load()
    if L0 > maxload + 3:
        return (seed, 'over', L0)
    d = model.trim(B.d, random.Random(seed))
    L = d.max_load()
    if L > maxload:
        return (seed, 'over', L)
    f = d.to_flyer(limit=L); f.translate(20, 20, 20)
    name = f's{seed:06d}_L{L}'
    f.save(Path(out) / f'{name}.flyer')
    g = [sum(1 for it in d.items if it.cat == 'glue' and it.body == b) for b in range(3)]
    return (seed, 'ok', dict(name=name, L0=L0, L=L, glue=g, info=info))

if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    n0, n1, maxload, procs = map(int, sys.argv[2:6])
    spread = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    xspread = int(sys.argv[7]) if len(sys.argv) > 7 else 2
    import collections; st = collections.Counter(); rows = []
    with Pool(procs) as p:
        for seed, why, info in p.imap_unordered(one, [(s, str(out), maxload, spread, xspread) for s in range(n0, n1)], chunksize=20):
            st[why] += 1
            if why == 'ok':
                rows.append(info); print(info['name'], info['L0'], '->', info['L'], info['glue'], flush=True)
    print(dict(st))
    (out / f'manifest_{n0}_{n1}.json').write_text(json.dumps(rows, indent=1))
