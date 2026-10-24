"""Towers of height h on the square side-contact ring (tm_smol style), any small k.
Level 0 = back ring body V_i; level j >= 1 = segment T(j, i) stacked on T(j-1, i):
- rests 2 slots before the level below (rest = rest(V_i) - 2j), so the level below carries its hoppers: the hoppers
  stand on the lower level's plate cells (that plate is their cover);
- its sticky stands on a lower-level plate cell and pulls the lower level on that level's last move, so levels
  0..h-1 need only k-1 hoppers; the top level has k;
- the sticky of level j < h is powered by a redstone block of level j+1 hanging beside it (level j+1 is at its lowest
  relative to level j exactly at the start of level j's rest); the top sticky by a block of the previous tower's top.
python tower2.py K H"""
import sys, itertools
import families as F, square, sqbuild
from nk import Timing, add
from nk2 import Timing2, Ring2, power_problems
from tower import route_all, min_pl

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


def level_layouts(n, below, a, b, mg=0, relax=False):
    """lanes for a level with n hoppers over the lower level's plate lanes `below` (RB / attach lanes within the
    box widened by mg = m or (my, mz))."""
    my, mz = mg if isinstance(mg, tuple) else (mg, mg)
    inb = lambda l: -my <= l[0] < a + my and -mz <= l[1] < b + mz
    lanes = [(y, z) for y in range(-1, a + 1) for z in range(-1, b + 1)]
    bl = set(below)
    for s in sorted(bl):
        for H in itertools.combinations(sorted(bl - {s}), n):
            Hs = set(H)
            cand = [l for l in lanes if (relax or (l not in bl and s not in nb(l))) and l not in Hs and l != s
                    and any(h in nb(l) for h in H) and inb(l)]
            done = False
            for nr in range(1, n + 1):
                for R in itertools.combinations(cand, nr):
                    if all(any(r in nb(h) for r in R) for h in H):
                        if any(l in nb(s) for l in H + R):   # sticky held by the cell behind it (human towers)
                            yield s, list(H), list(R), None
                        for s2 in nb(s):
                            if s2 in Hs or s2 in R or s2 in bl or not inb(s2): continue
                            yield s, list(H), list(R), s2
                        done = True; break
                if done: break


def hs_layouts(n, below, a, b, mg=0, top=False, free=None):
    """human-sticky level layouts, cheapest (fewest redstone blocks) first: hoppers H on the lower plate lanes, the
    sticky lane s (not for a power-only top) beside a hopper / RB lane so its side neighbours hold it, RB lanes R
    touching every hopper. `free`: a lane whose block is placed anyway (the top level's power block behind the lower
    sticky), usable at no cost."""
    my, mz = mg if isinstance(mg, tuple) else (mg, mg)
    inb = lambda l: -my <= l[0] < a + my and -mz <= l[1] < b + mz
    lanes = [(y, z) for y in range(-1 - my, a + 1 + my) for z in range(-1 - mz, b + 1 + mz)]
    bl = set(below); out = []
    for s in ([None] if top else sorted(bl)):
        for H in itertools.combinations(sorted(bl - {s}), n):
            Hs = set(H)
            cand = [l for l in lanes if l not in Hs and l != s and l != free and inb(l) and any(h in nb(l) for h in H)]
            fr = [free] if free is not None and free not in Hs else []
            for nr in range(0, n + 1):
                found = [R for R in itertools.combinations(cand, nr)
                         if all(any(r in nb(h) for r in list(R) + fr) for h in H)
                         and (top or any(l in nb(s) for l in H + R))]
                if found:
                    out += [(len(R), s, list(H), list(R), None) for R in found]
                    break
    out.sort(key=lambda t: t[0])
    return [t[1:] for t in out]


def build(k, word, h, choice, power_top=True, box=None, back=None, cv=None, mg=0, hs=False, xoff=None, keep_back=True):
    """choice: tuple of layout indices, one per level 1..h; box overrides the word's (a, b).
    back = (module, step): a given back-body module (e.g. back_cp) and its straight step; cv its corner offset.
    hs (human sticky): the sticky stands in the plate layer (x = 1) between plate cells that hold it sideways, pulls
    an extra lower-level cell at (2, s), and leaves the cell behind it free for its power block.
    xoff: per back body x shift (see balanced_xoff).
    keep_back (with hs; user rule: the back is sacred): level 1's sticky stays on the hopper layer, held by the level-1
    cell behind it, and pulls the back body's existing plate cell, so the back body gets no extra cell."""
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    if box:
        a, b = box; l = (word >> 6) & 15
        cy, cz = a - 1 + ((l >> 3) & 1), b + 1 + ((l >> 2) & 1)
    if back:
        vmod, step = back
    else:
        vmod = F.lat_module(k - 1, a, b)
        if vmod is None: return None
        if (word >> 7) & 1: vmod = F.mirror_y(vmod)
        step = (vmod['size'][0] + 1, sz)
    a, b = vmod['size']
    L = square.ring_size(k)
    T0 = Timing(k, L)
    place = square.square_layout(L, a, b, step, cv or (cy, cz))
    if xoff: place = [(p[0] + xoff[i],) + tuple(p[1:]) for i, p in enumerate(place)]
    below = [tuple(c[1:]) for c in vmod['PLATE']]
    lays = []
    for j in range(1, h + 1):
        n = k if (j >= h - 1 if power_top else j == h) else k - 1
        if hs and keep_back == 's2' and j == 1:   # level 1: tower2 attach lane (cells on level 1, none on the back)
            g = sorted(level_layouts(n, below, a, b, mg, relax=True), key=lambda t: (len(t[2]), t[3] is None))
            g = [t for t in g if t[3] is not None]
        elif hs:
            top = power_top and j == h
            g = hs_layouts(n, below, a, b, mg, top=top, free=lays[-1][0] if top and lays else None)
        else:
            g = list(itertools.islice(level_layouts(n, below, a, b, mg), choice[j - 1] + 1))
        if len(g) <= choice[j - 1]: return None
        s, H, R, s2 = g[choice[j - 1]]
        lays.append((s, H, R, s2))
        below = H + R + ([s2] if hs and keep_back == 's2' and j == 1 else [s] if hs and keep_back and j == 1 else
                         [] if hs else [s if s2 is None else s2])
    S = T0.S
    rests, nxt = list(T0.rest), [T0.nxt(i) for i in range(L)]
    for j in range(1, h + 1):
        rests += [(T0.rest[i] - 2 * j) % S for i in range(L)]
        nxt += [(j - 1) * L + i for i in range(L)]
    T = Timing2(k, rests, nxt)
    mods = [vmod] * L; places = list(place); mats = ['slime' if i % 2 == 0 else 'honey' for i in range(L)]
    for j in range(1, h + 1):
        s, H, R, s2 = lays[j - 1]
        for i in range(L):
            X, Y = j * L + i, (j - 1) * L + i
            D = T.shift(X, T.rest[X]) - T.shift(Y, T.rest[X])
            x0 = places[Y][0] + 4 - D
            top_only = power_top and j == h
            if hs and keep_back == 's2' and j == 1 and not top_only:
                plate = [(1,) + tuple(c) for c in H + R] + [(0,) + tuple(s2), (1,) + tuple(s2)]
                rig = [dict(pos=(0,) + tuple(s), dir=-1, victim=Y)]
            elif hs and keep_back and j == 1 and not top_only:
                plate = [(1,) + tuple(c) for c in H + R] + [(1,) + tuple(s)]
                rig = [dict(pos=(0,) + tuple(s), dir=-1, victim=Y)]
            elif hs:
                plate = [(1,) + tuple(c) for c in H + R]
                rig = [] if top_only else [dict(pos=(1,) + tuple(s), dir=-1, victim=Y)]
                if not top_only:
                    mods[Y] = dict(mods[Y], PLATE=list(mods[Y]['PLATE']) + [(2,) + tuple(s)])
            else:
                plate = [(1,) + tuple(c) for c in H + R] + ([] if top_only else [(1,) + tuple(s)] if s2 is None else
                                                            [(0,) + tuple(s2), (1,) + tuple(s2)])
                rig = [] if top_only else [dict(pos=(0,) + tuple(s), dir=-1, victim=Y)]
            mods.append(dict(P=[tuple(c) for c in H], R=[(0,) + tuple(c) for c in R], PLATE=plate,
                             CONT=[(-3,) + tuple(c) for c in H], size=(a, b), RIG=rig))
            places.append((x0,) + place[i][1:])
            mats.append('honey' if (i + j) % 2 else 'slime')
    r = Ring2(T, mods, places, mat=mats)
    r.lays, r.h, r.L0, r.power_top = lays, h, L, power_top
    return r


def balanced_xoff(k, L, phase):
    """x shifts making every link's frame offset D the same (rounded): over each base ring of L0 links the offsets
    sum to a fixed total; all links get its floor except `phase`-indexed ones, which take the remainder."""
    from nk import bodies_for
    T = Timing(k, L); L0 = bodies_for(k)
    D = [T.shift(T.nxt(U), T.rest[U]) - T.shift(U, T.rest[U]) for U in range(L)]
    tot = sum(D[:L0]); lo = tot // L0; extra = tot - lo * L0
    tg = [lo + (1 if (U - phase) % L0 < extra else 0) for U in range(L)]
    e = [0]
    for U in range(L - 1): e.append(e[-1] + tg[U] - D[U])
    return e


def add_power(r, choices):
    """choices[j-1] picks the block cell / attach cell for the stickies of level j."""
    T = r.T; L = r.L0; h = r.h
    for j in range(1, h + 1):
        if r.power_top and j == h: continue
        for i in range(L):
            tgt = j * L + i
            src = (j + 1) * L + i if j < h else j * L + (i - 1) % L
            st = T.rest[tgt]
            sp = r.mw(tgt, r.mods[tgt]['RIG'][0]['pos'], st)
            occ = r.world(st)
            opts = []
            for d in N4:
                w = (sp[0], sp[1] + d[0], sp[2] + d[1])
                if occ.get(w): continue
                cx = w[0] - r.place[src][0] - T.shift(src, st)
                loc = sqbuild.to_local(r.place[src], (cx, w[1], w[2]))
                for att in ((1, 0, 0), (-1, 0, 0)) + tuple((0,) + d2 for d2 in N4):
                    opts.append((loc, att))
            if not opts: return None
            loc, att = opts[choices[j - 1] % len(opts)]
            mod = dict(r.mods[src]); mod['R'] = list(mod['R']) + [loc]; r.mods[src] = mod
            a_ = r.mw(src, add(loc, att), 0, src)
            r.extra[src] = set(r.extra[src]) | {a_}; r.glue[src] = r.glue[src] | {a_}
    r.__dict__.pop('_hw', None); r.invalidate()
    return r


def add_power_greedy(r):
    """like add_power, but per sticky: the first block cell (4 sides or behind the sticky) / attach cell that adds
    no collision and no power problem for the bodies around it."""
    from terrace import collisions
    from nk2 import power_problems
    T = r.T; L = r.L0; h = r.h
    for j in range(1, h + 1):
        if r.power_top and j == h: continue
        for i in range(L):
            tgt = j * L + i
            src = (j + 1) * L + i if j < h else j * L + (i - 1) % L
            st = T.rest[tgt]
            sp = r.mw(tgt, r.mods[tgt]['RIG'][0]['pos'], st)
            occ = r.world(st)
            near = r.near(tgt, margin=3)
            done = False
            for d in ((1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                w = add(sp, d)
                if occ.get(w): continue
                cx = w[0] - r.place[src][0] - T.shift(src, st)
                loc = sqbuild.to_local(r.place[src], (cx, w[1], w[2]))
                for att in ((1, 0, 0), (-1, 0, 0)) + tuple((0,) + d2 for d2 in N4):
                    old = (r.mods[src], set(r.extra[src]), set(r.glue[src]))
                    mod = dict(r.mods[src]); mod['R'] = list(mod['R']) + [loc]; r.mods[src] = mod
                    a_ = r.mw(src, add(loc, att), 0, src)
                    r.extra[src] = set(r.extra[src]) | {a_}; r.glue[src] = r.glue[src] | {a_}
                    r.__dict__.pop('_hw', None)
                    bad = collisions(r, near) or [p for p in power_problems(r, near)
                                                  if p[2] == src or (p[3] == tgt and 'unpowered' in p[1])]
                    if not bad:   # nobody's glue may drag the new block (plates / contacts; routing comes later)
                        r.invalidate()
                        bad = [b for b in r.check(near) if f'drags {src} RB' in b[2] or f"({src}, 'RB'" in b[2]]
                    if not bad: done = True; break
                    r.mods[src], r.extra[src], r.glue[src] = old
                    r.__dict__.pop('_hw', None)
                if done: break
            if not done: return None
    r.invalidate()
    return r


def scan(k, word, h, nlay=6, npow=12, keep=4, verbose=False, box=None, tag=None, **kw):
    from terrace import collisions
    res = []
    for lc in itertools.product(range(nlay), repeat=h):
        base = build(k, word, h, lc, box=box, **kw)
        if base is None or collisions(base): continue
        for pc in itertools.product(range(npow), repeat=h - 1):
            pc = pc + (0,)
            r = build(k, word, h, lc, box=box, **kw)
            if add_power(r, pc) is None or collisions(r): continue
            if power_problems(r): continue
            try: route_all(r)
            except RuntimeError: continue
            if r.check(): continue
            L = r.L0
            res.append((max(r.size()[:L]), max(r.size()), lc, pc))
            if verbose: print(res[-1], flush=True)
    res.sort(key=lambda t: (t[1], t[0]))
    out = []
    for back, sz, lc, pc in res[:keep]:
        r = build(k, word, h, lc, box=box, **kw); add_power(r, pc); route_all(r)
        p = f'out/tower2_{k}_{h}_{tag or word}_{box}_{len(out)}.flyer'.replace(' ', ''); r.flyer(4 * k + 30).save(p)
        out.append((back, sz, lc, pc, min_pl(p, k, 4 * k + 10)))
    return out


def _job(args):
    k, h, word, nlay, npow, box = args
    try: return (word, box), scan(k, word, h, nlay, npow, keep=2, box=box)
    except Exception as e: return word, repr(e)[:80]


if __name__ == '__main__':
    from concurrent.futures import ProcessPoolExecutor
    k, h = int(sys.argv[1]), int(sys.argv[2])
    nlay, npow = int(sys.argv[3]), int(sys.argv[4])
    if len(sys.argv) > 5:   # explicit boxes "A,B;A,B..." x all 16 layouts
        boxes = [tuple(map(int, b.split(','))) for b in sys.argv[5].split(';')]
        jobs = [(k, h, 1 | (l << 6), nlay, npow, bx) for bx in boxes for l in range(16)]
    else:
        jobs = [(k, h, 1 | (v << 2) | (l << 6), nlay, npow, None) for v in range(16) for l in range(16)]
    with ProcessPoolExecutor(12) as ex:
        for key, res in ex.map(_job, jobs):
            if res: print(key, res, flush=True)
