"""Uniform human-topology stacks on the families' back modules with the topology stage's offsets (research driver).
Back: the lat module families.py picks for k-1 hoppers (bits.json word for k-1, box / mirror / corner) when that
family is lat, else stack_all's near-square boxes. Offsets: stack_topo.measure_reach (a few plain back rings) +
stack_topo.evaluate of the uniform structure -> the link offsets that balance the back loads (instead of the
balanced frame offsets). Then stack.construct (layout margins 1,1 then 0,1), simulated.
python stack_all2.py K1,K2,..   (SW env = workers, default 4); writes out/stack/all2.txt lines."""
import sys, os, time, json
from concurrent.futures import ProcessPoolExecutor
import stack, stack_scan, stack_topo, stack_all
import families as F


def back_specs(k):
    out = []
    w = json.load(open('bits.json')).get(str(k - 1))
    if w is not None:
        fam, (a, b), sz, cy, cz = F.unpack(w, k - 1)
        if fam == 'lat':
            out.append((f'lat:{a},{b},0,1,{(w >> 7) & 1}', (cy, cz)))
    for a, b in stack_all.boxes(k, 1):
        out.append((f'lat:{a},{b},0,1,0', (a - 1, b + 1)))
    return out


def job(args):
    k, spec, cv = args
    t = time.time()
    try:
        e = stack_scan.back_entry(k, spec)
        n, sym = stack_topo.positions(k)
        f = stack_topo.measure_reach(k, (e['mod'], e['step']), cv, budget=16)
        ev = stack_topo.evaluate(k, f, [[(k - 1, 0, 1), (k, 0, 1), (k, 0, 0)]] * n)
        if ev is None: return k, spec, cv, None, 'no offsets', round(time.time() - t, 1)
        links_in = ev[3]; lk = [links_in[(q + 1) % n] for q in range(n)]
        best = None
        for mg in ((1, 1), (0, 1)):
            st = {}
            res = stack.construct(k, (e['mod'], e['step']), [(k - 1, 0), (k, 0), (k, 0)], cv,
                                  stack_topo.xoff_for(k, lk), 3, stats=st, mg=mg, max_leaves=6)
            if res and (best is None or res[0] < best[0]): best = (res[0], mg, res[2])
        if best is None: return k, spec, cv, None, f'pred {ev[0]} links {links_in}', round(time.time() - t, 1)
        p, mg, r = best
        name = f'out/stack/all2_n{k:02d}_pl{p}.flyer'
        r.flyer(p).save(name)
        return k, spec, cv, p, f'pred {ev[0]} mg {mg} links {links_in} {name}', round(time.time() - t, 1)
    except Exception as ex:
        return k, spec, cv, None, 'err ' + repr(ex)[:80], round(time.time() - t, 1)


if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    jobs = [(k, s, cv) for k in ks for s, cv in back_specs(k)]
    best = {}
    with ProcessPoolExecutor(int(os.environ.get('SW', 4))) as ex, open('out/stack/all2.txt', 'a') as fo:
        for res in ex.map(job, jobs):
            print(*res, flush=True); fo.write(' '.join(map(str, res)) + '\n'); fo.flush()
            k, p = res[0], res[3]
            if p is not None and (k not in best or p < best[k]): best[k] = p
    print('BEST', dict(sorted(best.items())), flush=True)
