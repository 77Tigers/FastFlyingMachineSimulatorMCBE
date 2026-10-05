"""User's design, flexible closures: back loop A>B, B>A + one 5-block chain per loop segment + fronts that pull
each other. Chains are altchain templates (chain 2 offset/oriented); A/B lose sticky+redstone+attach, fronts lose
their pusher. The 4 closure pistons are placed by timing from a CHOSEN contact cell on the target (existing glue or
a new glue cell grown up to 2 cells from it), then glued to the actor; the cheapest option (by max action load) wins.
Power is repaired with capped4.power_options2 (any segment). usage: python ringchain2.py L SEED OUTDIR N
"""
import random, sys, pathlib, re, copy, pickle, os, itertools
from collections import Counter
from rigid import Seg, check, to_flyer, add, D6, loads, glue_path, reserved_cells, kind_of
from alt import altchain
from capped4 import power_options2, best_of
from capped2 import wpos, lpos, sub
X = (1, 0, 0)
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

def skeleton(L, o1, o2, off, mats, L2=None):
    L2 = L if L2 is None else L2
    a1, c1 = o1; a2, c2 = o2
    ch1 = altchain(L + 1, a1, c1)
    ch2 = altchain(L2 + 2, a2, c2)[1:]
    for s in ch2: s.origin = (s.origin[0] + off[0], s.origin[1] + off[1], s.origin[2] + off[2])
    for i, s in enumerate(ch1): s.name = 'A' if i == 0 else f'a{i}'; s.mat = mats[0] if i % 2 == 0 else mats[1]
    for i, s in enumerate(ch2): s.name = 'B' if i == 0 else f'b{i}'; s.mat = mats[2] if i % 2 == 0 else mats[3]
    A, F1, B, F2 = ch1[0], ch1[L], ch2[0], ch2[L2]
    for s in (A, B):
        for cc, k in list(s.cells.items()):
            if k in ('S', 'R'): del s.cells[cc]
        # drop the attach glue that only held the redstone block (keep if it is the only neighbour of something)
    for s in (F1, F2):
        for cc, k in list(s.cells.items()):
            if k == 'P': del s.cells[cc]
    return ch1 + ch2, A, B, F1, F2

def piston_world(kind, target, contact, slot):
    w = wpos(target, contact, slot)
    return sub(w, X) if kind == 'P' else add(w, (2, 0, 0))

def contact_options(seg, segs, maxext=3):
    """existing glue cells, plus cells reachable by growing 1..maxext new glue cells."""
    out = [(c, ()) for c, k in seg.cells.items() if k == 'g']
    res = reserved_cells(segs, seg)
    frontier = [(c, ()) for c, _ in out]
    seen = {c for c, _ in out}
    for _ in range(maxext):
        nxt = []
        for c, path in frontier:
            for d in D6[2:] + D6[:2]:
                n = add(c, d)
                if n in seen or n in seg.cells or n in res: continue
                seen.add(n); nxt.append((n, path + (n,))); out.append((n, path + (n,)))
        frontier = nxt
    return out

def place_closure(segs, actor, target, kind, slot, rng, maxglue=4):
    """all options: (cost, newsegs)."""
    opts = []
    ai = [s.name for s in segs].index(actor.name); ti = [s.name for s in segs].index(target.name)
    for contact, path in contact_options(target, segs):
        cs = copy.deepcopy(segs); A_ = cs[ai]; T_ = cs[ti]
        for c in path: T_.cells[c] = 'g'
        pw = piston_world(kind, T_, contact, slot)
        pl = lpos(A_, pw, slot)
        if pl in A_.cells: continue
        if any(pw in o.at(slot) for o in cs if o is not A_): continue
        A_.cells[pl] = kind
        if any_overlap(cs): continue
        if not any(A_.cells.get(add(pl, d)) == 'g' for d in D6):
            p = glue_path(A_, [add(pl, d) for d in D6], cs, rng, maxlen=maxglue)
            if p is None: continue
        opts.append((len(path), cs))
    return opts

def repair_power(segs, rng, rounds=12):
    for _ in range(rounds):
        r = check(segs)
        if r is None or 'power missing' not in r: return segs, r
        m = re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        t = int(m.group(1)); si = [i for i, x in enumerate(segs) if x.name == m.group(2)][0]
        pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        opts = []
        for cst, cs in power_options2(segs, si, pw, t, m.group(3), rng, maxlen=3):
            rr = check(cs)
            if rr is None or ('power missing' in rr and rr != r): opts.append((cst, cs))
        st = best_of(opts, rng)
        if st is None: return segs, r
        segs = st
    return segs, check(segs)

def build(L, o1, o2, off, mats, rng, beam=8):
    segs, A, B, F1, F2 = skeleton(L, o1, o2, off, mats)
    if any_overlap(segs): return None, 'skeleton overlap'
    closures = [('A', 'B', 'P', B.word[0]), ('B', 'A', 'P', A.word[0]),
                (F1.name, F2.name, 'S', F2.word[1]), (F2.name, F1.name, 'S', F1.word[1])]
    states = [segs]
    for an, tn, kind, slot in closures:
        nxt = []
        for st in states:
            names = [s.name for s in st]
            nxt += place_closure(st, st[names.index(an)], st[names.index(tn)], kind, slot, rng)
        if not nxt: return None, f'closure {an}->{tn}'
        nxt.sort(key=lambda o: (loads(o[1]), max(len(s.cells) for s in o[1]), o[0]))
        states = [o[1] for o in nxt[:beam]]
    best = None
    for st in states:
        st2, r = repair_power(st, rng)
        if r is None:
            if best is None or loads(st2) < loads(best): best = st2
        else: DBG[re.sub(r'[-0-9(), ]+', '#', r)] += 1
    if best is None: return None, 'power/check'
    return best, None

if __name__ == '__main__' and sys.argv[1] != 'vac':
    L = int(sys.argv[1]); rng = random.Random(int(sys.argv[2])); out = pathlib.Path(sys.argv[3]); out.mkdir(exist_ok=True)
    N = int(sys.argv[4]) if len(sys.argv) > 4 else 500
    best = 99
    for it in range(N):
        o1 = rng.choice(ORIENTS); o2 = rng.choice(ORIENTS)
        off = (rng.randint(-4, 0), rng.randint(-4, 4), rng.randint(-4, 4))
        mats = [rng.choice(['slime', 'honey']) for _ in range(4)]
        segs, why = build(L, o1, o2, off, mats, rng)
        if segs is None:
            DBG[re.sub(r'[-0-9(), ]+', '#', str(why))] += 1
            if it % 50 == 49: print('dbg', it + 1, dict(DBG.most_common(6)), flush=True)
            continue
        Lo = loads(segs)
        print('FOUND load', Lo, L, l2, o1, o2, off, mats, [(s.name, len(s.cells)) for s in segs], flush=True)
        if Lo <= best:
            best = Lo; tag = f'L{L}_s{os.getpid()}_{it:05d}_load{Lo}'
            to_flyer(segs, Lo).save(out / f'rc2_{tag}.flyer'); pickle.dump(segs, open(out / f'rc2_{tag}.pkl', 'wb'))
    print('done best', best, dict(DBG.most_common(8)), flush=True)

# ---------------- power-aware variant: closure pistons go into vacated chain-piston cells ----------------
def template_parts(K, a, c):
    neg = lambda v: (-v[0], -v[1])
    if K % 2 == 0: S, P, att = neg(a), c, neg(c)
    else: S, P, att = neg(c), a, neg(a)
    hub = (P[0] + S[0], P[1] + S[1])
    return (0,) + S, (0,) + P, (0,) + att, (0,) + hub

def build_vacated(L, o1, o2, off, mats, rng, L2=None):
    L2 = L if L2 is None else L2
    a1, c1 = o1; a2, c2 = o2
    segs, A, B, F1, F2 = skeleton(L, o1, o2, off, mats, L2)
    if any_overlap(segs): return None, 'skeleton overlap'
    # chain indices: A = chain1 K0, F1 = chain1 KL; B = chain2 K1, F2 = chain2 K(L+1)
    SA, PA, _, hubA = template_parts(0, a1, c1)
    SB, PB, _, hubB = template_parts(1, a2, c2)
    SF1, PF1, _, hubF1 = template_parts(L, a1, c1)
    SF2, PF2, _, hubF2 = template_parts(L2 + 1, a2, c2)
    # back closures: flexible contacts (best by load), then front closures at the hubs
    for an, tn, kind, slot in (('A', 'B', 'P', B.word[0]), ('B', 'A', 'P', A.word[0])):
        names = [s.name for s in segs]
        opts = place_closure(segs, segs[names.index(an)], segs[names.index(tn)], kind, slot, rng)
        if not opts: return None, f'closure {an}->{tn}'
        opts.sort(key=lambda o: (loads(o[1]), max(len(x.cells) for x in o[1]), o[0]))
        segs = rng.choice(opts[:3])[1]
        A, B, F1, F2 = [segs[[s.name for s in segs].index(nm)] for nm in ('A', 'B', F1.name, F2.name)]
    plan = [(F1, hubF1, 'S', F2, F2.word[1]), (F2, hubF2, 'S', F1, F1.word[1])]
    for actor, hub, kind, target, slot in plan:
        front = X if kind == 'P' else (-1, 0, 0)
        cands = [add(hub, d) for d in D6 if add(hub, d) not in actor.cells and add(add(hub, d), front) != hub]
        rng.shuffle(cands)
        placed = False
        for cell in cands:
            snap = (dict(actor.cells), dict(target.cells))
            actor.cells[cell] = kind
            pw = wpos(actor, cell, slot)
            cw = add(pw, X) if kind == 'P' else sub(pw, (2, 0, 0))
            cl = lpos(target, cw, slot)
            ok = not any_overlap(segs) and target.cells.get(cl, 'g') == 'g'
            if ok and target.cells.get(cl) != 'g':
                target.cells[cl] = 'g'; resv = reserved_cells(segs, target); del target.cells[cl]
                ok = cl not in resv
                if ok and not any(target.cells.get(add(cl, d)) == 'g' for d in D6):
                    ok = glue_path(target, [add(cl, d) for d in D6], segs, rng, maxlen=4, extra_block=[cl]) is not None
                if ok: target.cells[cl] = 'g'
            if ok and not any(actor.cells.get(add(cell, d)) == 'g' for d in D6):
                ok = glue_path(actor, [add(cell, d) for d in D6], segs, rng, maxlen=3) is not None
            if ok and not any_overlap(segs): placed = True; break
            actor.cells, target.cells = snap
        if not placed: return None, f'closure {actor.name}->{target.name}'
    # fronts carry a redstone block on the partner front's hub at the partner's fire slot
    for carrier, partner, hub in ((F2, F1, hubF1), (F1, F2, hubF2)):
        k = partner.fire_slot()
        hw = wpos(partner, hub, k); hl = lpos(carrier, hw, k)
        if hl in carrier.cells or hl in reserved_cells(segs, carrier, glue=False): return None, f'hub RB busy on {carrier.name}'
        carrier.cells[hl] = 'R'
        if not any(carrier.cells.get(add(hl, d)) == 'g' for d in D6):
            p = glue_path(carrier, [add(hl, d) for d in D6], segs, rng, maxlen=4)
            if p is None: return None, f'RB attach {carrier.name}'
    if any_overlap(segs): return None, 'final overlap'
    segs, r = repair_power(segs, rng)
    if r is not None: return None, r
    return segs, None

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'vac':
    pass

if __name__ == '__main__' and sys.argv[1] == 'vac':
    L = int(sys.argv[2]); seed = int(sys.argv[3]); out = pathlib.Path(sys.argv[4]); out.mkdir(exist_ok=True)
    rng = random.Random(seed); best = 99; n = 0
    L2s = [L, L + 2] if len(sys.argv) <= 7 else [int(sys.argv[7])]
    jobs = [(o1, o2, (dx, dy, dz), l2) for o1 in ORIENTS for o2 in ORIENTS for dx in range(-4, 1) for dy in range(-4, 5) for dz in range(-4, 5) for l2 in L2s]
    rng.shuffle(jobs)
    shard, nsh = int(sys.argv[5]), int(sys.argv[6])
    for o1, o2, off, l2 in jobs[shard::nsh]:
        for mats in itertools.product(['slime', 'honey'], repeat=4):
            segs, why = build_vacated(L, o1, o2, off, list(mats), rng, l2)
            n += 1
            if segs is None:
                DBG[re.sub(r'[-0-9(), ]+', '#', str(why))] += 1
                if 'overlap' in str(why) or 'busy' in str(why): break
                continue
            Lo = loads(segs)
            print('FOUND load', Lo, L, l2, o1, o2, off, mats, [(s.name, len(s.cells)) for s in segs], flush=True)
            if Lo <= best:
                best = Lo; tag = f'vac_L{L}_{shard}_{n:06d}_load{Lo}'
                to_flyer(segs, Lo).save(out / f'{tag}.flyer'); pickle.dump(segs, open(out / f'{tag}.pkl', 'wb'))
        if n % 500 < 16: print('dbg', n, dict(DBG.most_common(6)), flush=True)
    print('done best', best, dict(DBG.most_common(10)), flush=True)
