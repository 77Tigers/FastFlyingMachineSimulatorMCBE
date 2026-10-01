"""python ilpbatch.py OUTDIR Lmax radius procs files..."""
import sys, json, glob
from pathlib import Path
from multiprocessing import Pool
import ilp

def one(args):
    fn, rs, Lmax, radius, out = args
    g, p, o = json.load(open(fn)); place = (tuple(g), [(a, tuple(b)) for a, b in p], o)
    try:
        d, L = ilp.solve(place, rs, radius=radius, Lmax=Lmax, time_limit=120, verbose=False)
    except Exception as e:
        return (fn, rs, 'err ' + str(e)[:80])
    if d is None:
        return (fn, rs, L)
    ml = d.max_load()
    name = Path(fn).stem + f'_rs{rs}_L{ml}'
    f = d.to_flyer(limit=ml); f.translate(20, 20, 20); f.save(Path(out) / (name + '.flyer'))
    (Path(out) / (name + '.json')).write_text(json.dumps(place))
    return (fn, rs, ml)

if __name__ == '__main__':
    out = sys.argv[1]; Path(out).mkdir(exist_ok=True, parents=True)
    Lmax, radius, procs = map(int, sys.argv[2:5])
    files = sys.argv[5:]
    jobs = [(f, rs, Lmax, radius, out) for f in files for rs in range(3)]
    with Pool(procs) as p:
        for r in p.imap_unordered(one, jobs):
            print(*r, flush=True)
