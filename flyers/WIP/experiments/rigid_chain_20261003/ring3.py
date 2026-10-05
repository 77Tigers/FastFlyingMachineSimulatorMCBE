"""User's design, hub-powered closures: back loop A>B, B>A + one 5-block chain per loop segment + fronts that pull
each other. ALL four closure pistons sit next to their segment's power hub, so they share the chain's power:
  A's extra pusher (->B, fires 2) next to A's hub, powered by a1's redstone block;
  B's extra pusher (->A, fires 0) next to B's hub, powered by b1's redstone block;
  F1's extra sticky (->F2, fires 2) next to F1's hub, powered by a new redstone block on F2;
  F2's extra sticky (->F1, fires 0) next to F2's hub, powered by a new redstone block on F1.
Contacts (the target glue in front of each closure piston at its slot) are grown by shortest glue paths.
Enumerates chain-2 orientation/offset, chain lengths, materials and every hub-neighbour choice.
usage: python ring3.py SEED OUTDIR SHARD NSHARDS [maxglue]
"""
import random, sys, pathlib, re, copy, pickle, os, itertools
from collections import Counter
from rigid import Seg, check, to_flyer, add, D6, loads, glue_path, reserved_cells
from alt import altchain
from capped2 import wpos, lpos, sub
X = (1, 0, 0); W = (-1, 0, 0)
ORIENTS = [((1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, 1)), ((-1, 0), (0, -1)),
           ((0, 1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (1, 0)), ((0, -1), (-1, 0))]
DBG = Counter()

def any_overlap(segs):
    for t in range(4):
        occ = set()
        for s in segs:
            for c in s.at(t):
                if c in occ: return True
                occ.add(c)
    return False

def hub_of(K, a, c):
    neg = lambda v: (-v[0], -v[1])
    S, P = (neg(a), c) if K % 2 == 0 else (neg(c), a)
    return (0, P[0] + S[0], P[1] + S[1])

def skeleton(L1, L2, o1, o2, off, mats):
    ch1 = altchain(L1 + 1, *o1)
    ch2 = altchain(L2 + 2, *o2)[1:]
    for s in ch2: s.origin = add(s.origin, off)
    for i, s in enumerate(ch1): s.name = 'A' if i == 0 else f'a{i}'; s.mat = mats[0] if i % 2 == 0 else mats[1]
    for i, s in enumerate(ch2): s.name = 'B' if i == 0 else f'b{i}'; s.mat = mats[2] if i % 2 == 0 else mats[3]
    A, F1, B, F2 = ch1[0], ch1[L1], ch2[0], ch2[L2]
    for s in (A, B):   # no rear: drop sticky, redstone block and its attach glue
        for cc, k in list(s.cells.items()):
            if k in ('S', 'R'): del s.cells[cc]
        R_att = [cc for cc, k in s.cells.items() if k == 'g' and cc != (0, 0, 0)]
        for cc in R_att: del s.cells[cc]
    for s in (F1, F2):  # no front: drop pusher
        for cc, k in list(s.cells.items()):
            if k == 'P': del s.cells[cc]
    hubs = {'A': hub_of(0, *o1), 'B': hub_of(1, *o2), F1.name: hub_of(L1, *o1), F2.name: hub_of(L2 + 1, *o2)}
    return ch1 + ch2, A, B, F1, F2, hubs

def contact(segs, actor, cell, kind, target, slot, rng, maxglue):
    """actor gets piston `kind` at local `cell` (must already be set); grow target glue at the cell it acts on."""
    pw = wpos(actor, cell, slot)
    cw = add(pw, X) if kind == 'P' else sub(pw, (2, 0, 0))
    cl = lpos(target, cw, slot)
    k = target.cells.get(cl)
    if k == 'g': return 0
    if k is not None: return None
    target.cells[cl] = 'g'
    resv = reserved_cells(segs, target)
    del target.cells[cl]
    if cl in resv: return None
    if any(target.cells.get(add(cl, d)) == 'g' for d in D6):
        target.cells[cl] = 'g'; return 1
    p = glue_path(target, [add(cl, d) for d in D6], segs, rng, maxlen=maxglue, extra_block=[cl])
    if p is None: return None
    target.cells[cl] = 'g'
    return 1 + len(p)

def attach(segs, seg, cell, rng, maxglue):
    if any(seg.cells.get(add(cell, d)) == 'g' for d in D6): return 0
    p = glue_path(seg, [add(cell, d) for d in D6], segs, rng, maxlen=maxglue)
    return None if p is None else len(p)

def place_closure(segs, an, tn, kind, slot, hub, rng, maxglue):
    """yield deep-copied states with the closure piston at each free hub neighbour."""
    names = [s.name for s in segs]
    front = X if kind == 'P' else W
    for d in D6:
        cell = add(hub, d)
        if add(cell, front) == hub: continue
        cs = copy.deepcopy(segs); A_ = cs[names.index(an)]; T_ = cs[names.index(tn)]
        if cell in A_.cells: continue
        A_.cells[cell] = kind
        if any_overlap(cs): DBG['cl overlap'] += 1; continue
        if cell in reserved_cells(cs, A_, glue=False): DBG['cl resv'] += 1; continue
        if attach(cs, A_, cell, rng, maxglue) is None: DBG['cl attach'] += 1; continue
        if contact(cs, A_, cell, kind, T_, slot, rng, maxglue) is None: DBG['cl contact'] += 1; continue
        if any_overlap(cs): DBG['cl overlap2'] += 1; continue
        yield cs

def size_key(segs):
    return (max(len(s.cells) for s in segs), sum(len(s.cells) for s in segs))

def place_closure2(segs, an, tn, kind, slot, hub, rng, maxglue, beam=6):
    """closure piston anywhere in a box around the actor. Power: hub neighbour (chain block) or a redstone block
    on the TARGET next to the piston at the fire slot (user rule: the block on X powers the piston acting on X)."""
    names = [s.name for s in segs]
    front = X if kind == 'P' else W
    act = segs[names.index(an)]
    xs = [c[0] for c in act.cells]; ys = [c[1] for c in act.cells]; zs = [c[2] for c in act.cells]
    opts = []
    for cell in itertools.product(range(min(xs) - 1, max(xs) + 2), range(min(ys) - 2, max(ys) + 3), range(min(zs) - 2, max(zs) + 3)):
        if cell in act.cells or add(cell, front) == hub or cell == hub: continue
        cs = copy.deepcopy(segs); A_ = cs[names.index(an)]; T_ = cs[names.index(tn)]
        A_.cells[cell] = kind
        if any_overlap(cs): continue
        if cell in reserved_cells(cs, A_, glue=False): continue
        if attach(cs, A_, cell, rng, maxglue) is None: continue
        if contact(cs, A_, cell, kind, T_, slot, rng, maxglue) is None: continue
        if any_overlap(cs): continue
        fs = slot - 1 if kind == 'S' else slot   # slot = pull slot for stickies, fire slot for pushers
        pw = wpos(A_, cell, fs)
        if sum(abs(u - v) for u, v in zip(cell, hub)) == 1:
            opts.append(cs); continue
        for d in D6:
            if add(pw, d) == add(pw, front): continue
            c2 = copy.deepcopy(cs); T2 = c2[names.index(tn)]
            rl = lpos(T2, add(pw, d), fs)
            if rl in T2.cells or rl in reserved_cells(c2, T2, glue=False): continue
            T2.cells[rl] = 'R'
            if attach(c2, T2, rl, rng, maxglue) is None: continue
            if any_overlap(c2): continue
            opts.append(c2)
    opts.sort(key=size_key)
    return opts[:beam]

def add_rb(segs, carrier_n, partner_n, hub, rng, maxglue):
    names = [s.name for s in segs]
    carrier = segs[names.index(carrier_n)]; partner = segs[names.index(partner_n)]
    k = partner.fire_slot()
    hl = lpos(carrier, wpos(partner, hub, k), k)
    if hl in carrier.cells: return False
    if hl in reserved_cells(segs, carrier, glue=False): return False
    carrier.cells[hl] = 'R'
    if attach(segs, carrier, hl, rng, maxglue) is None: del carrier.cells[hl]; return False
    return not any_overlap(segs)

def build_all(L1, L2, o1, o2, off, mats, rng, maxglue=3):
    segs, A, B, F1, F2, hubs = skeleton(L1, L2, o1, o2, off, mats)
    if any_overlap(segs): DBG['skel overlap'] += 1; return
    f1, f2 = F1.name, F2.name
    r0 = check(segs, ignore={'A', 'B', f1, f2})
    if r0 is not None: DBG['skel: ' + re.sub(r'[-0-9(), ]+', '#', r0)] += 1; return
    PC = place_closure2 if os.environ.get('WIDE') else place_closure
    for s1 in PC(segs, 'A', 'B', 'P', 2, hubs['A'], rng, maxglue):
        for s2 in PC(s1, 'B', 'A', 'P', 0, hubs['B'], rng, maxglue):
            r = check(s2, ignore={f1, f2})
            if r is not None: DBG['back: ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
            DBG['BACK OK'] += 1
            if os.environ.get('BACKONLY'):
                yield s2; continue
            for s3 in PC(s2, f1, f2, 'S', 3, hubs[f1], rng, maxglue):
                for s4 in PC(s3, f2, f1, 'S', 1, hubs[f2], rng, maxglue):
                    s5 = copy.deepcopy(s4)
                    if not add_rb(s5, f2, f1, hubs[f1], rng, maxglue): s5 = copy.deepcopy(s4); DBG['rb1'] += 1
                    t5 = copy.deepcopy(s5)
                    if not add_rb(t5, f1, f2, hubs[f2], rng, maxglue): DBG['rb2'] += 1
                    else: s5 = t5
                    from ringchain2 import repair_power
                    s5, r = repair_power(s5, rng)
                    if r is not None: DBG['front: ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
                    r = check(s5)
                    if r is not None: DBG['front: ' + re.sub(r'[-0-9(), ]+', '#', r)] += 1; continue
                    yield s5

if __name__ == '__main__':
    seed, out, shard, nsh = int(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    maxglue = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    out.mkdir(exist_ok=True); rng = random.Random(seed)
    o1 = ORIENTS[0]
    jobs = [(L1, L2, o2, (dx, dy, dz)) for L1 in (2, 4) for L2 in (2, 4) for o2 in ORIENTS
            for dx in range(-3, 4) for dy in range(-4, 5) for dz in range(-4, 5)]
    rng.shuffle(jobs)
    best = 99; n = 0
    for L1, L2, o2, off in jobs[shard::nsh]:
        for mats in itertools.product(['slime', 'honey'], repeat=4):
            if mats[0] == mats[1] or mats[2] == mats[3]: continue
            n += 1
            for segs in build_all(L1, L2, o1, o2, off, list(mats), rng, maxglue):
                Lo = loads(segs)
                print('FOUND load', Lo, L1, L2, o2, off, mats, [(s.name, len(s.cells)) for s in segs], flush=True)
                if Lo <= best:
                    best = Lo; tag = f'r3_{shard}_{n:06d}_load{Lo}'
                    to_flyer(segs, Lo).save(out / f'{tag}.flyer'); pickle.dump(segs, open(out / f'{tag}.pkl', 'wb'))
                break
        if n % 200 < 2: print('dbg', n, dict(DBG.most_common(10)), flush=True)
    print('done best', best, dict(DBG.most_common(14)), flush=True)
