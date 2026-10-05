"""Back loop of the user's design with EXACT minimum glue: A>B, B>A + chains (ring3 skeleton, fronts ignored).
Closure pushers at hub neighbours (powered by the chain's own block), contacts on the partner, then
hop4.min_glue (smallest connected glue set) for A and B. Reports the max segment size of valid backs.
usage: python backmin.py SHARD NSHARDS OUTDIR [maxseg]
"""
import sys, os, pathlib, pickle, random, itertools, copy, re
from collections import Counter
from rigid import check, add, D6, loads, reserved_cells, to_flyer
from capped2 import wpos, lpos, sub
from hop4 import min_glue
from ring3 import skeleton, ORIENTS, any_overlap
X = (1, 0, 0); W = (-1, 0, 0)
DBG = Counter()

def hub_cells(hub, kind):
    front = X if kind == 'P' else W
    return [add(hub, d) for d in D6 if add(add(hub, d), front) != hub]

def put_contact(actor, cell, kind, target, slot):
    pw = wpos(actor, cell, slot)
    cw = add(pw, X) if kind == 'P' else sub(pw, (2, 0, 0))
    return lpos(target, cw, slot)

def glue_fill(segs, seg, maxseg, rng):
    pist = [c for c, k in seg.cells.items() if k in ('P', 'S')]
    reqs = []
    for p in pist:
        fr = add(p, X) if seg.cells[p] == 'P' else add(p, W)
        reqs.append({add(p, d) for d in D6 if add(p, d) != fr})
    for c, k in seg.cells.items():
        if k == 'R' or (isinstance(k, tuple)): reqs.append({add(c, d) for d in D6})
    bad = reserved_cells(segs, seg)
    if any(c in bad for c, k in seg.cells.items() if k == 'g'): return None
    nonglue = len([c for c, k in seg.cells.items() if k != 'g'])
    xs = [c[0] for c in seg.cells]; ys = [c[1] for c in seg.cells]; zs = [c[2] for c in seg.cells]
    box = ((min(xs) - 1, max(xs) + 1), (min(ys) - 1, max(ys) + 1), (min(zs) - 1, max(zs) + 1))
    sols = min_glue(seg, reqs, bad, maxseg - nonglue, box, rng, cap=6000)
    return sols

def run(L1, L2, o1, o2, off, mats, rng, maxseg, out, tag):
    segs, A, B, F1, F2, hubs = skeleton(L1, L2, o1, o2, off, mats)
    if any_overlap(segs): DBG['skel overlap'] += 1; return
    ign = {F1.name, F2.name}
    if check(segs, ignore=ign | {'A', 'B'}) is not None: DBG['skel bad'] += 1; return
    found = []
    for ca in hub_cells(hubs['A'], 'P'):
        for cb in hub_cells(hubs['B'], 'P'):
            cs = copy.deepcopy(segs); A_ = cs[0]; B_ = [s for s in cs if s.name == 'B'][0]
            if ca in A_.cells or cb in B_.cells: continue
            A_.cells[ca] = 'P'; B_.cells[cb] = 'P'
            kB = put_contact(A_, ca, 'P', B_, 2); kA = put_contact(B_, cb, 'P', A_, 0)
            if B_.cells.get(kB, 'g') != 'g' or A_.cells.get(kA, 'g') != 'g': DBG['contact occupied'] += 1; continue
            B_.cells[kB] = 'g'; A_.cells[kA] = 'g'
            if any_overlap(cs): DBG['overlap'] += 1; continue
            if any(c in reserved_cells(cs, s, glue=False) for s in (A_, B_) for c in s.cells): DBG['resv'] += 1; continue
            # exact glue: A then B (each against the other's current cells), both orders
            for first, second in ((A_, B_), (B_, A_)):
                c2 = copy.deepcopy(cs); f = [s for s in c2 if s.name == first.name][0]; s2 = [s for s in c2 if s.name == second.name][0]
                sa = glue_fill(c2, f, maxseg, rng)
                if not sa: DBG['glue ' + first.name] += 1; continue
                for G in sa[:6]:
                    c3 = copy.deepcopy(c2); f3 = [s for s in c3 if s.name == first.name][0]
                    for c in G: f3.cells.setdefault(c, 'g')
                    s3 = [s for s in c3 if s.name == second.name][0]
                    sb = glue_fill(c3, s3, maxseg, rng)
                    if not sb: DBG['glue ' + second.name] += 1; continue
                    for H in sb[:6]:
                        c4 = copy.deepcopy(c3); s4 = [s for s in c4 if s.name == second.name][0]
                        for c in H: s4.cells.setdefault(c, 'g')
                        r = check(c4, ignore=ign)
                        if r is not None: DBG['chk ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
                        Lo = max(len(c4[0].cells), len(s4.cells) if second.name == 'B' else len([s for s in c4 if s.name == 'B'][0].cells))
                        Lo = max(len(s.cells) for s in c4 if s.name in ('A', 'B'))
                        found.append((Lo, c4))
                        break
                    if found: break
    if found:
        found.sort(key=lambda x: x[0])
        Lo, c4 = found[0]
        DBG['OK %d' % Lo] += 1
        print('BACK', Lo, L1, L2, o2, off, mats, [(s.name, len(s.cells)) for s in c4], flush=True)
        pickle.dump(c4, open(out / f'bm_{tag}_A{Lo}.pkl', 'wb'))

if __name__ == '__main__':
    shard, nsh, out = int(sys.argv[1]), int(sys.argv[2]), pathlib.Path(sys.argv[3])
    maxseg = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    out.mkdir(exist_ok=True); rng = random.Random(shard)
    o1 = ORIENTS[0]
    jobs = [(L1, L2, o2, (dx, dy, dz)) for L1 in (2,) for L2 in (2,) for o2 in ORIENTS
            for dx in range(-3, 3) for dy in range(-4, 5) for dz in range(-4, 5)]
    random.Random(7).shuffle(jobs)
    n = 0
    for L1, L2, o2, off in jobs[shard::nsh]:
        for mats in (('slime', 'honey', 'honey', 'slime'), ('slime', 'honey', 'slime', 'honey')):
            n += 1
            run(L1, L2, o1, o2, off, list(mats), rng, maxseg, out, f'{shard}_{n}')
        if n % 40 == 0: print('dbg', n, dict(DBG.most_common(8)), flush=True)
    print('done', dict(DBG.most_common(14)), flush=True)
