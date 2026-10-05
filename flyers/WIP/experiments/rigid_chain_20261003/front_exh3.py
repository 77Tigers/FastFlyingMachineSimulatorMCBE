"""Front cap, G-plan, enumerated with the rear ignored. Chain altchain(N) whose last segment G (wwmm) keeps only
glue+attach+redstone (powers F's sticky at s2, chain rule). H: pusher rider fires s1 -> F, rides E@s3, F@s0,
observer on F. H3: pusher rider fires s3 -> G, rides F@s1, G@s2, observer on G."""
import itertools, copy, sys, pickle, random, re
from collections import Counter
from alt import altchain
from capped2 import make_rider, rider_world, lpos, sub
from rigid import add, D6, check, reserved_cells, glue_path
from capped4 import observer_options, ride_options, power_options
from rear_exh import rear_load
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 0
N = 7
DBG = Counter()
def contacts(seg):
    g = [c for c, k in seg.cells.items() if k == 'g']; out = list(g)
    for x in g:
        for d in D6[2:]:
            n = add(x, d)
            if n not in seg.cells and n not in out: out.append(n)
    return out
def place_rider(segs, name, kind, fire, ti, cc):
    cs = copy.deepcopy(segs); t2 = cs[ti]
    if cc not in t2.cells:
        if cc in reserved_cells(cs, t2) or not any(t2.cells.get(add(cc, d)) == 'g' for d in D6): return None
        t2.cells[cc] = 'g'
    r = make_rider(name, kind, fire, t2, cc); cs.append(r)
    if list(r.cells)[0] in reserved_cells(cs, r, glue=False): return None
    return cs
def run(a, c, rng, out):
    base = altchain(N, a, c)
    G = base[-1]
    for cc, k in list(G.cells.items()):
        if k in ('P', 'S'): del G.cells[cc]
    G.name = 'G'
    iG, iF, iE = N - 1, N - 2, N - 3
    FRONT = {'G', base[iF].name, base[iE].name, base[iE - 1].name}
    ignore = {base[0].name, base[1].name}
    for hc in contacts(base[iF]):
        s1 = place_rider(base, 'H', 'P', 1, iF, hc)
        if s1 is None: DBG['Hplace'] += 1; continue
        iH = len(s1) - 1
        for ost in observer_options(s1, iF, rider_world(s1[iH], 1), 1, rng, maxlen=2):
            s2 = ost[1]
            st = [s for _, s in ride_options(s2, iH, 3, iE, rng, maxlen=2)]
            st = [s for x in st for _, s in ride_options(x, iH, 0, iF, rng, maxlen=2)]
            if not st: DBG['Hride'] += 1; continue
            for s3 in st:
                if rear_load(s3, FRONT) > TARGET: DBG['overH'] += 1; continue
                for h3c in contacts(s3[iG]):
                    s4 = place_rider(s3, 'H3', 'P', 3, iG, h3c)
                    if s4 is None: DBG['H3place'] += 1; continue
                    iH3 = len(s4) - 1
                    for ost2 in observer_options(s4, iG, rider_world(s4[iH3], 3), 3, rng, maxlen=2):
                        s5 = ost2[1]
                        st2 = [s for _, s in ride_options(s5, iH3, 1, iF, rng, maxlen=2)]
                        st2 = [s for x in st2 for _, s in ride_options(x, iH3, 2, iG, rng, maxlen=2)]
                        if not st2: DBG['H3ride'] += 1; continue
                        for s6 in st2:
                            L = rear_load(s6, FRONT)
                            if L > TARGET: DBG['over'] += 1; continue
                            r = check(s6, ignore=ignore)
                            if r is not None: DBG[re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
                            out.append((L, a, c, s6)); print('VALID front load', L, [(s.name, len(s.cells)) for s in s6 if s.name in FRONT], flush=True)
if __name__ == '__main__':
    rng = random.Random(SEED); out = []
    for a, c in [((1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, 1)), ((-1, 0), (0, -1)),
                 ((0, 1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (1, 0)), ((0, -1), (-1, 0))]:
        run(a, c, rng, out)
        print('orient', a, c, 'valid', len(out), dict(DBG.most_common(8)), flush=True)
    out.sort(key=lambda x: x[0]); pickle.dump(out[:30], open(f'front_best_{SEED}.pkl', 'wb'))
    print('best', [o[0] for o in out[:10]])
