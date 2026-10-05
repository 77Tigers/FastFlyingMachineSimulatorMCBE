"""Front pull-pull closure of the user's design (F1 mmww end of chain 1, F2 wwmm end of chain 2), back ends ignored.
Closure stickies placed by ring3.place_closure2 (hub neighbour or redstone block on the target), remaining power
repaired from ANY segment (unique offsets; e.g. F2's own chain block can power F1 at slot 2 and vice versa).
usage: [LEAF=1] python frontmin.py SHARD NSHARDS OUTDIR
"""
import sys, pathlib, pickle, random, re, itertools
from collections import Counter
from rigid import check, loads, to_flyer
from ring3 import skeleton, ORIENTS, any_overlap, place_closure2, DBG
from capped4 import power_options2, best_of

def repair_power(segs, rng, ignore=('A', 'B'), rounds=12):
    for _ in range(rounds):
        r = check(segs, ignore=set(ignore))
        if r is None or 'power missing' not in r: return segs, r
        m = re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        t = int(m.group(1)); si = [i for i, x in enumerate(segs) if x.name == m.group(2)][0]
        pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        opts = []
        for cst, cs in power_options2(segs, si, pw, t, m.group(3), rng, maxlen=3):
            rr = check(cs, ignore=set(ignore))
            if rr is None or ('power missing' in rr and rr != r): opts.append((cst, cs))
        st = best_of(opts, rng)
        if st is None: return segs, r
        segs = st
    return segs, check(segs, ignore=set(ignore))

def run(L1, L2, o1, o2, off, mats, rng, out, tag, best):
    segs, A, B, F1, F2, hubs = skeleton(L1, L2, o1, o2, off, mats)
    if any_overlap(segs): return best
    f1, f2 = F1.name, F2.name
    if check(segs, ignore={'A', 'B', f1, f2}) is not None: return best
    DBG['configs'] += 1
    for s3 in place_closure2(segs, f1, f2, 'S', 3, hubs[f1], rng, 3, beam=5):
        for s4 in place_closure2(s3, f2, f1, 'S', 1, hubs[f2], rng, 3, beam=5):
            s5, r = repair_power(s4, rng)
            if r is not None: DBG['front ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
            r = check(s5, ignore={'A', 'B'})
            if r is not None: DBG['chk ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
            Lo = max(len(s.cells) for s in s5 if s.name in (f1, f2))
            DBG['OK %d' % Lo] += 1
            print('FRONT', Lo, L1, L2, o2, off, mats, [(s.name, len(s.cells)) for s in s5], flush=True)
            if Lo <= best:
                best = Lo
                pickle.dump(s5, open(out / f'fm_{tag}_F{Lo}.pkl', 'wb'))
            return best
    return best

if __name__ == '__main__':
    shard, nsh, out = int(sys.argv[1]), int(sys.argv[2]), pathlib.Path(sys.argv[3])
    out.mkdir(exist_ok=True); rng = random.Random(shard)
    jobs = [(2, 2, o2, (dx, dy, dz)) for o2 in ORIENTS for dx in range(-3, 4) for dy in range(-4, 5) for dz in range(-4, 5)]
    random.Random(11).shuffle(jobs)
    best = 99; n = 0
    for L1, L2, o2, off in jobs[shard::nsh]:
        for mats in itertools.product(['slime', 'honey'], repeat=4):
            if mats[0] == mats[1] or mats[2] == mats[3]: continue
            n += 1
            best = run(L1, L2, ORIENTS[0], o2, off, list(mats), rng, out, f'{shard}_{n}', best)
        if n % 40 == 0: print('dbg', n, dict(DBG.most_common(8)), flush=True)
    print('done', best, dict(DBG.most_common(14)), flush=True)
