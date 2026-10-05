"""Exhaustive 2-body hopper search: contacts enumerated, bodies = exact minimum glue sets (Steiner with
'adjacent to rider at its ride slot' requirements), then power (redstone, shared where possible), then check."""
import itertools, random, sys, pathlib, re, copy, pickle, os
from collections import Counter
from rigid import Seg, check, to_flyer, add, D6, loads, reserved_cells
from capped2 import make_rider, rider_world, lpos, sub
from capped4 import power_options, power_options2, best_of
DBG = Counter()

def min_glue(seg, reqs, bad, maxg, box, rng, cap=30000):
    """seg has its contact glue already. reqs: list of sets of seg-frame cells (need >=1 glue in each).
    Return list of minimal glue sets (frozensets incl. existing glue)."""
    start = frozenset(c for c, k in seg.cells.items() if k == 'g')
    def connected(G):
        G = set(G); s = next(iter(G)); seen = {s}; st = [s]
        while st:
            c = st.pop()
            for d in D6:
                n = add(c, d)
                if n in G and n not in seen: seen.add(n); st.append(n)
        return len(seen) == len(G)
    def ok(G): return all(G & r for r in reqs) and connected(G)
    frontier = {start}
    for size in range(len(start), maxg + 1):
        sols = [G for G in frontier if ok(G)]
        if sols: return sols
        nxt = set()
        for G in frontier:
            for c in G:
                for d in D6:
                    n = add(c, d)
                    if n in G or n in bad or n in seg.cells: continue
                    if not all(lo <= v <= hi for v, (lo, hi) in zip(n, box)): continue
                    nxt.add(G | {n})
        if len(nxt) > cap: nxt = set(rng.sample(sorted(nxt, key=sorted), cap))
        frontier = nxt
    return []

def build(cA2, cB1, cB2, mats, rng, maxg=6):
    A = Seg('A', (0, 2), (0, 0, 0), {(0, 0, 0): 'g'}, mats[0])
    B = Seg('B', (1, 3), (0, 0, 0), {cB1: 'g'}, mats[1])
    if cA2 != (0, 0, 0): A.cells[cA2] = 'g'
    if cB2 != cB1: B.cells[cB2] = 'g'
    if set(A.cells) & set(B.cells): return None, 'overlap'
    riders = [make_rider('X1', 'P', 0, A, (0, 0, 0)), make_rider('X2', 'P', 2, A, cA2),
              make_rider('Y1', 'S', 0, B, cB1), make_rider('Y2', 'S', 2, B, cB2)]
    if len({list(r.cells)[0] for r in riders}) < 4: return None, 'rider overlap'
    segs = [A, B] + riders
    for r in riders:
        if list(r.cells)[0] in reserved_cells(segs, r, glue=False): return None, 'rider clash'
    ride = {'A': [(riders[1], 0), (riders[3], 0), (riders[0], 2), (riders[2], 2)],
            'B': [(riders[1], 1), (riders[3], 1), (riders[0], 3), (riders[2], 3)]}
    for body in (A, B):
        reqs = [{lpos(body, add(rider_world(r, t), d), t) for d in D6} for r, t in ride[body.name]]
        bad = reserved_cells(segs, body)
        xs = [c[0] for c in body.cells] + [lpos(body, rider_world(r, t), t)[0] for r, t in ride[body.name]]
        ys = [c[1] for c in body.cells]; zs = [c[2] for c in body.cells]
        box = ((min(xs) - 1, max(xs) + 1), (min(ys) - 2, max(ys) + 2), (min(zs) - 2, max(zs) + 2))
        sols = min_glue(body, reqs, bad, maxg, box, rng)
        if not sols: return None, f'glue {body.name}'
        G = rng.choice(sols)
        for c in G: body.cells.setdefault(c, 'g')
        DBG[f'glue{body.name}_{len(G)}'] += 1
    for _ in range(6):
        r = check(segs)
        if r is None or 'power missing' not in r: return segs, r
        m = re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        t = int(m.group(1)); si = [i for i, x in enumerate(segs) if x.name == m.group(2)][0]
        pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        opts = []
        for cst, cs in power_options2(segs, si, pw, t, m.group(3), rng, maxlen=2):
            rr = check(cs)
            if rr is None or ('power missing' in rr and rr != r): opts.append((cst, cs))
        st = best_of(opts, rng)
        if st is None: return segs, r
        segs = st
    return segs, check(segs)

if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(exist_ok=True)
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    maxg = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    found = []
    lat = [(0, dy, dz) for dy in range(-2, 3) for dz in range(-2, 3) if (dy, dz) != (0, 0) and abs(dy) + abs(dz) <= 2]
    cBs = [(x, y, z) for x in range(-3, 4) for y in range(-2, 3) for z in range(-2, 3)]
    jobs = list(itertools.product(lat, cBs, lat, [('slime', 'honey'), ('honey', 'slime'), ('slime', 'slime'), ('honey', 'honey')]))
    rng.shuffle(jobs)
    for cA2, cB1, dB, mats in jobs:
        cB2 = add(cB1, dB)
        segs, why = build(cA2, cB1, cB2, mats, rng, maxg)
        if segs is None or why is not None:
            DBG[re.sub(r'[-0-9(), ]+', '#', str(why))] += 1; continue
        L = loads(segs); found.append(L)
        if L > 8: continue
        tag = f's{os.getpid()}_{len(found):04d}_L{L}'
        to_flyer(segs, L).save(out / f'h4_{tag}.flyer'); pickle.dump(segs, open(out / f'h4_{tag}.pkl', 'wb'))
        print('FOUND load', L, [(s.name, len(s.cells)) for s in segs if not s.rider], flush=True)
    print('found', len(found), 'best', sorted(found)[:10])
    for k, v in DBG.most_common(12): print(v, k)
