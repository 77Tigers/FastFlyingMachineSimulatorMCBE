"""lat family with balanced per-link x offsets (tower2.balanced_xoff, every phase) vs without: python lat_xoff_test.py K,K"""
import sys, json
from concurrent.futures import ProcessPoolExecutor
import families as F, square, sqbuild, tower2
from nk import bodies_for


def job(args):
    k, w, ph = args
    fam, (a, b), sz, cy, cz = F.unpack(w, k)
    L = F.big_ring(k) if fam == 'latbig' else square.ring_size(k); m = L // 4
    mod = F.lat_module(k, a, b) if fam != 'slab' else None
    if mod is None: return args, None
    if m > 1 and (w >> 7) & 1: mod = F.mirror_y(mod)
    a2 = mod['size'][0]
    step = (a2 + 2, 0) if m == 1 else (a2 + 1, sz)
    xo = None if ph is None else tower2.balanced_xoff(k, L, ph)
    try:
        r = sqbuild.assemble(k, mod, step, (cy, cz), L, xoff=xo)
        if r is None: return args, None
        Lr = r.T.L; mm = Lr // 4
        if r.check(sorted({(X + d) % Lr for X in (0, 1, mm) for d in range(-3, 4)})): return args, 'bad'
        return args, F.predicted_pl(r)
    except (RuntimeError, AssertionError, KeyError, IndexError) as e:
        return args, None


if __name__ == '__main__':
    bits = json.load(open('bits.json'))
    jobs = []
    for k in [int(x) for x in sys.argv[1].split(',')]:
        w = bits[str(k)]
        if F.fam_of(w) not in ('lat', 'latbig'): continue
        jobs += [(k, w, None)] + [(k, w, ph) for ph in range(bodies_for(k))]
    out = {}
    with ProcessPoolExecutor(8) as ex:
        for (k, w, ph), pl in ex.map(job, jobs):
            out.setdefault(k, []).append((ph, pl))
    for k in sorted(out): print(k, out[k], flush=True)
