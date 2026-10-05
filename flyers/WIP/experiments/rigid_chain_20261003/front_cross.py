"""Targeted front: offsets where F1's chain redstone block (on rear(F1)'s hub at slot 0) also touches F2's chain sticky
(F2 fires at slot 0 too). F2's closure sticky goes on another free face of that block; F1's two stickies get power
from a new redstone block on F2 at F1's hub (slot 2, unique offset). Contacts grown by shortest glue paths.
usage: [LEAF=1] python front_cross.py OUTDIR
"""
import sys, pathlib, pickle, random, copy, itertools, re
from collections import Counter
from rigid import check, loads, add, D6, reserved_cells
from capped2 import wpos, lpos, sub
from ring3 import skeleton, ORIENTS, any_overlap, contact, attach, add_rb
DBG = Counter()
X = (1, 0, 0)

def seg(cs, n): return [s for s in cs if s.name == n][0]

def adj(a, b): return sum(abs(u - v) for u, v in zip(a, b)) == 1

def build(L1, L2, o2, off, mats, rng, maxglue=3):
    segs, A, B, F1, F2, hubs = skeleton(L1, L2, ORIENTS[0], o2, off, mats)
    if any_overlap(segs): return []
    f1, f2 = F1.name, F2.name
    R1 = [c for c, k in F1.at(0).items() if k == 'R'][0]
    S2 = [c for c, k in F2.at(0).items() if k == 'S'][0]
    if not (adj(R1, S2) and S2 != add(R1, X)): return []
    if check(segs, ignore={'A', 'B', f1, f2}) is not None: DBG['skel'] += 1; return []
    DBG['cfg'] += 1
    out = []
    for d in D6:                              # F2's closure sticky next to R1 at slot 0
        w = add(R1, d)
        if w == S2 or add(w, (-1, 0, 0)) == R1: continue
        cs = copy.deepcopy(segs); F2_ = seg(cs, f2); F1_ = seg(cs, f1)
        cl = lpos(F2_, w, 0)
        if cl in F2_.cells: continue
        F2_.cells[cl] = 'S'
        if any_overlap(cs) or cl in reserved_cells(cs, F2_, glue=False): DBG['s2 place'] += 1; continue
        if attach(cs, F2_, cl, rng, maxglue) is None: DBG['s2 attach'] += 1; continue
        if contact(cs, F2_, cl, 'S', F1_, 1, rng, maxglue) is None: DBG['s2 contact'] += 1; continue
        hub1 = hubs[f1]
        for e in D6:                          # F1's closure sticky next to F1's hub
            c1 = add(hub1, e)
            if c1 in F1_.cells or add(c1, (-1, 0, 0)) == hub1: continue
            c2 = copy.deepcopy(cs); F1b = seg(c2, f1); F2b = seg(c2, f2)
            F1b.cells[c1] = 'S'
            if any_overlap(c2) or c1 in reserved_cells(c2, F1b, glue=False): DBG['s1 place'] += 1; continue
            if attach(c2, F1b, c1, rng, maxglue) is None: DBG['s1 attach'] += 1; continue
            if contact(c2, F1b, c1, 'S', F2b, 3, rng, maxglue) is None: DBG['s1 contact'] += 1; continue
            if not add_rb(c2, f2, f1, hub1, rng, maxglue): DBG['rb'] += 1; continue
            r = check(c2, ignore={'A', 'B'})
            if r is not None: DBG['chk ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
            out.append(c2)
    return out

if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(exist_ok=True); rng = random.Random(1)
    best = 99
    for L1, L2 in ((2, 2), (2, 4), (4, 2), (4, 4)):
        for o2 in ORIENTS:
            for off in itertools.product(range(-6, 7), repeat=3):
                for mats in itertools.product(['slime', 'honey'], repeat=4):
                    if mats[0] == mats[1] or mats[2] == mats[3]: continue
                    for rep in range(3):
                        for c2 in build(L1, L2, o2, off, list(mats), rng):
                            f = [s for s in c2 if s.name not in ('A', 'B')]
                            Lo = max(len(s.cells) for s in c2[-1:] + [s for s in c2 if s.name.startswith(('a', 'b')) and s is not None])
                            sizes = [(s.name, len(s.cells)) for s in c2]
                            Lf = max(n for nm, n in sizes if nm not in ('A', 'B'))
                            print('FRONT', Lf, L1, L2, o2, off, mats, sizes, flush=True)
                            if Lf <= best:
                                best = Lf; pickle.dump(c2, open(out / f'fx_{L1}{L2}_F{Lf}_{len(list(out.iterdir()))}.pkl', 'wb'))
        print('dbg', L1, L2, dict(DBG.most_common(10)), flush=True)
    print('done', best, dict(DBG.most_common(12)), flush=True)
