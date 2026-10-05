"""Back loop, exact and pruned: closure pushers anywhere in a box around A/B; power from the hub (chain block) or a
redstone block on the TARGET next to the pusher at its fire slot (user rule). Exact min glue (hop4.min_glue) as a
lower bound after every step, budget MAXSEG cells per loop segment. Fronts ignored (open chains).
usage: python backmin2.py SHARD NSHARDS OUTDIR [maxseg]
"""
import sys, pathlib, pickle, random, itertools, copy, re
from collections import Counter
from rigid import check, add, D6, reserved_cells
from capped2 import wpos, lpos, sub
from ring3 import skeleton, ORIENTS, any_overlap
from backmin import glue_fill, put_contact
X = (1, 0, 0); W = (-1, 0, 0)
DBG = Counter()

def seg(cs, n): return [s for s in cs if s.name == n][0]

def lb_ok(cs, names, maxseg, rng):
    for n in names:
        sols = glue_fill(cs, seg(cs, n), maxseg, rng)
        if not sols: return False
    return True

def closure_opts(cs, an, tn, slot, hub, maxseg, rng):
    """yield states with an's pusher (+ contact glue on tn, + power) placed; pruned by exact glue bound."""
    A = seg(cs, an)
    for cell in itertools.product(range(-2, 2), range(-2, 3), range(-2, 3)):
        if cell in A.cells: continue
        c1 = copy.deepcopy(cs); A1 = seg(c1, an); T1 = seg(c1, tn)
        A1.cells[cell] = 'P'
        k = put_contact(A1, cell, 'P', T1, slot)
        if T1.cells.get(k, 'g') != 'g': continue
        T1.cells[k] = 'g'
        if any_overlap(c1): continue
        if any(c in reserved_cells(c1, s, glue=False) for s in (A1, T1) for c in s.cells): continue
        pw = wpos(A1, cell, slot)
        variants = []
        if sum(abs(u - v) for u, v in zip(cell, hub)) == 1: variants.append(c1)
        else:
            for d in D6[1:]:
                c2 = copy.deepcopy(c1); T2 = seg(c2, tn)
                rl = lpos(T2, add(pw, d), slot)
                if rl in T2.cells: continue
                T2.cells[rl] = 'R'
                if any_overlap(c2) or rl in reserved_cells(c2, T2, glue=False): continue
                variants.append(c2)
        for v in variants:
            DBG['cand'] += 1
            if lb_ok(v, (an, tn), maxseg, rng): yield v
            else: DBG['lb fail'] += 1

def finish(cs, ign, maxseg, rng):
    best = None
    for first, second in (('A', 'B'), ('B', 'A')):
        sa = glue_fill(cs, seg(cs, first), maxseg, rng)
        for G in (sa or [])[:8]:
            c3 = copy.deepcopy(cs)
            for c in G: seg(c3, first).cells.setdefault(c, 'g')
            sb = glue_fill(c3, seg(c3, second), maxseg, rng)
            for H in (sb or [])[:8]:
                c4 = copy.deepcopy(c3)
                for c in H: seg(c4, second).cells.setdefault(c, 'g')
                r = check(c4, ignore=ign)
                if r is not None: DBG['chk ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
                Lo = max(len(seg(c4, 'A').cells), len(seg(c4, 'B').cells))
                if best is None or Lo < best[0]: best = (Lo, c4)
    return best

def run(L1, L2, o1, o2, off, mats, rng, maxseg, out, tag):
    segs, A, B, F1, F2, hubs = skeleton(L1, L2, o1, o2, off, mats)
    if any_overlap(segs): return
    ign = {F1.name, F2.name}
    if check(segs, ignore=ign | {'A', 'B'}) is not None: return
    DBG['configs'] += 1
    for s1 in closure_opts(segs, 'A', 'B', 2, hubs['A'], maxseg, rng):
        for s2 in closure_opts(s1, 'B', 'A', 0, hubs['B'], maxseg, rng):
            res = finish(s2, ign, maxseg, rng)
            if res:
                Lo, c4 = res
                DBG['OK %d' % Lo] += 1
                print('BACK', Lo, L1, L2, o2, off, mats, [(s.name, len(s.cells)) for s in c4], flush=True)
                pickle.dump(c4, open(out / f'bm2_{tag}_A{Lo}.pkl', 'wb'))
                return

if __name__ == '__main__':
    shard, nsh, out = int(sys.argv[1]), int(sys.argv[2]), pathlib.Path(sys.argv[3])
    maxseg = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    out.mkdir(exist_ok=True); rng = random.Random(shard)
    o1 = ORIENTS[0]
    jobs = [(2, 2, o2, (dx, dy, dz)) for o2 in ORIENTS for dx in range(-3, 3) for dy in range(-4, 5) for dz in range(-4, 5)]
    random.Random(7).shuffle(jobs)
    n = 0
    for L1, L2, o2, off in jobs[shard::nsh]:
        for mats in (('slime', 'honey', 'honey', 'slime'), ('slime', 'honey', 'slime', 'honey')):
            n += 1
            run(L1, L2, o1, o2, off, list(mats), rng, maxseg, out, f'{shard}_{n}')
        if n % 10 == 0: print('dbg', n, dict(DBG.most_common(8)), flush=True)
    print('done', dict(DBG.most_common(14)), flush=True)
