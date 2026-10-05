"""Exhaustive-ish rear cap search (Z, Y, Hz) on altchain(n) with the front ignored.
Enumerates Y contact lanes; prefers extra pushers adjacent to existing power cells; then Hz contact / observer /
rides; then minimal power placement. Reports designs with max rear load <= TARGET (check(ignore front))."""
import itertools, copy, sys, pickle, random, re
from collections import Counter
from alt import altchain
from capped2 import make_rider, rider_world, wpos, lpos, sub
from rigid import Seg, add, D6, check, reserved_cells, loads, kind_of, glue_path, unique_offset, E as EX, W_
from capped4 import observer_options, ride_options, power_options, best_of
X = (1, 0, 0)
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 8
N = 6
DBG = Counter()

def rear_load(segs, names):
    """max action load over the rear segments/slots (mover cells + riders it carries)."""
    best = 0
    for t in range(4):
        for s in segs:
            if s.rider or s.name not in names or not s.moves(t): continue
            cj = s.at(t); n = len(cj)
            for r in segs:
                if r.rider and r.moves(t):
                    rc = list(r.at(t))[0]
                    if any(add(c, X) == rc for c in cj) or any(k == 'g' and any(add(c, d) == rc for d in D6) for c, k in cj.items()):
                        n += 1
            best = max(best, n)
    return best

def fix_power_ignore(segs, rng, ignore, rounds=8):
    for _ in range(rounds):
        r = check(segs, ignore=ignore)
        if r is None or 'power missing' not in r: return segs, r
        m = re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        t = int(m.group(1)); si = [i for i, x in enumerate(segs) if x.name == m.group(2)][0]
        pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        opts = power_options(segs, si, pw, t, m.group(3), rng)
        if not opts: return segs, r
        mn = min(rear_load(o[1], REAR) * 100 + o[0] for o in opts)
        segs = rng.choice([o[1] for o in opts if rear_load(o[1], REAR) * 100 + o[0] == mn])
    return segs, check(segs, ignore=ignore)

REAR = {'Z', 'Y', 'K0', 'K1'}

def run(a, c, rng, out):
    chain = altchain(N, a, c)
    K0 = chain[0]
    for cc, k in list(K0.cells.items()):
        if k == 'R': del K0.cells[cc]
    att = (0, -c[0], -c[1])
    if K0.cells.get(att) == 'g': del K0.cells[att]
    hub0 = (0, c[0] - a[0], c[1] - a[1])      # K0's sticky/pusher common free neighbour (K1's RB lands here at s2)
    Zo = (K0.origin[0] - 1, K0.origin[1] - a[0], K0.origin[2] - a[1])
    Zp = (0, a[0], a[1])
    k0x = K0.origin[0]; base = (K0.origin[1], K0.origin[2])
    lanes = [(base[0] + dy, base[1] + dz) for dy in range(-3, 4) for dz in range(-3, 4)]
    ignore = {chain[-1].name, chain[-2].name}
    for l1, l2, ym, zm in itertools.product(lanes, lanes, ('slime', 'honey'), ('slime', 'honey')):
        Z = Seg('Z', (2, 3), Zo, {(0, 0, 0): 'g', Zp: 'P'}, zm)
        Y = Seg('Y', (0, 2), (0, 0, 0), {(k0x, l1[0], l1[1]): 'g'}, ym)
        segs = [Z, Y] + copy.deepcopy(chain)
        Zs, Ys, K0s = segs[0], segs[1], segs[2]
        cY1 = (k0x, l1[0], l1[1]); cY2 = (k0x + 2, l2[0], l2[1])
        zp = lpos(Zs, sub(cY1, X), 0); kp = lpos(K0s, sub(wpos(Ys, cY2, 2), X), 2)
        if zp in Zs.cells or kp in K0s.cells: DBG['incells'] += 1; continue
        # power-sharing preference: kp next to hub0 (not via its front), zp at L1 distance 2 from Zp
        pass
        if sum(abs(u - v) for u, v in zip(zp, Zp)) != 2 or zp[0] != 0: DBG['zp_noshare'] += 1; continue
        if cY2 in reserved_cells(segs, Ys): DBG['cY2res'] += 1; continue
        Zs.cells[zp] = 'P'; K0s.cells[kp] = 'P'
        if glue_path(Ys, [add(cY2, d) for d in D6], segs, rng, maxlen=3, extra_block=[cY2]) is None: DBG['Ybridge'] += 1; continue
        Ys.cells[cY2] = 'g'
        if glue_path(Zs, [add(zp, d) for d in D6], segs, rng, maxlen=2) is None: DBG['Zglue'] += 1; continue
        if glue_path(K0s, [add(kp, d) for d in D6], segs, rng, maxlen=2) is None: DBG['K0glue'] += 1; continue
        DBG['lanes_ok'] += 1
        # Hz
        cands = [cc for cc, k in Zs.cells.items() if k == 'g']
        for cc in list(cands):
            for d in D6[2:]:
                if add(cc, d) not in Zs.cells: cands.append(add(cc, d))
        for cc in cands:
            cs = copy.deepcopy(segs); Z2 = cs[0]
            if cc not in Z2.cells:
                if cc in reserved_cells(cs, Z2) or not any(Z2.cells.get(add(cc, d)) == 'g' for d in D6): continue
                Z2.cells[cc] = 'g'
            Hz = make_rider('Hz', 'S', 1, Z2, cc); cs.append(Hz)
            if list(Hz.cells)[0] in reserved_cells(cs, Hz, glue=False): DBG['Hzclash'] += 1; continue
            oo = observer_options(cs, 2, rider_world(Hz, 1), 1, rng, maxlen=2) + observer_options(cs, 1, rider_world(Hz, 1), 1, rng, maxlen=2)
            for _, c2 in oo:
                states = [c2]
                for t, ci in ((0, 1), (3, 0)):
                    states = [s for st in states for _, s in ride_options(st, len(st) - 1, t, ci, rng, maxlen=2)]
                if not states: DBG['Hzride'] += 1; continue
                for st in states:
                    if rear_load(st, REAR) > TARGET: DBG['over'] += 1; continue
                    st2, r = fix_power_ignore(st, rng, ignore)
                    if r is not None: DBG[re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
                    L = rear_load(st2, REAR)
                    if L <= TARGET:
                        out.append((L, a, c, st2)); print('VALID rear load', L, [(s.name, len(s.cells)) for s in st2 if not s.rider][:4], flush=True)

if __name__ == '__main__':
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rng = random.Random(seed); out = []
    for a, c in [((1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, 1)), ((-1, 0), (0, -1)),
                 ((0, 1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (1, 0)), ((0, -1), (-1, 0))]:
        run(a, c, rng, out)
        print('orient', a, c, 'valid so far', len(out), dict(DBG.most_common(8)), flush=True)
    out.sort(key=lambda x: x[0])
    pickle.dump(out[:30], open(f'rear_best_{seed}.pkl', 'wb'))
    print('best', [o[0] for o in out[:10]])
