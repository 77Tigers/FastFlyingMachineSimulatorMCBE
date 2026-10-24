"""Stack family (user's spec 2026-10-24): N3-like towers for any k.
Levels: back (level 0, a hopper ring), middle levels 1..M (each pulls the level below once per cycle with one
sticky), front (level M+1, no pull; it powers the last middle level's sticky). Body i of level j rests 2j slots
before back body i, so both of its possible hopper carriers rest 2 slots after it:
  - the body below it (level j-1, same tower): m hoppers standing on that body's plate (the plate is their cover);
  - its loop neighbour (level j, next tower, the same link as the back ring): s hoppers covered by that
    neighbour's cells beside the spent hoppers (x = -2), like a back link.
Moves per cycle: m + s + (pulled by the level above ? 1 : 0) = k; the back has s0 = k - 1 loop hoppers.
Parameters are uniform per level: params = [(m1, s1), ..., (mM, sM), (mF, sF)].
Stickies: level 1 holds its sticky on the hopper layer with its own attach lane and pulls the back's existing plate
cell (the back is sacred); levels >= 2 use the human sticky (plate layer, power block behind it).
python stack.py K "m1,s1;m2,s2;...;mF,sF" [NLAY]"""
import sys, itertools, time
import tower2, square
from nk import Timing, bodies_for, add
from nk2 import Timing2, Ring2, power_problems
from terrace import collisions
from tower import route_all

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


class Ring3(Ring2):
    """Ring2 with a second hopper carrier per body: hopper j of X is carried by T.nxt(X) (tag 'B', the body below
    in a tower, or NEXT on the back ring) or by loop[X] (tag 'L'); mods[X]['PC'] holds the tags and
    mods[X]['CONTL'] the loop carrier's cover cells (X frame, X-local slot 0)."""

    def __init__(self, T, mods, place, mat, loop):
        self.loop = loop
        Ring2.__init__(self, T, mods, place, mat=mat)
        for U in range(T.L):
            W = loop[U]
            if W is None or not mods[U].get('CONTL'): continue
            assert (T.rest[W] - T.rest[U]) % T.S == 2, (U, W)
            for c in mods[U]['CONTL']: self.contacts[W].add(self.cw(U, c, W=W))
        self.glue = [self.plates[X] | self.contacts[X] | set(self.extra[X]) for X in range(T.L)]

    def carrier(self, X, j):
        pc = self.mods[X].get('PC')
        return self.loop[X] if pc and pc[j] == 'L' else self.T.nxt(X)

    def cell_ok(self, X, g, worlds, why=False, strict=None):
        """strict about foreign redstone blocks: glue touching another body's block while moving either drags it or
        takes it along, and the block then pushes its owner's plate in front of it (the bodies merge; seen in
        simulation when the owner's move in that slot is a pull)."""
        T = self.T
        cap = getattr(self, 'xcap', {}).get(X)
        if cap is not None and g[0] - self.place[X][0] > cap:
            return (False, 'above the plate layer') if why else False
        for s in range(T.S):
            if not T.moves(X, s):
                # resting: an own spent hopper right behind this cell must not be carried forward into it
                w = (g[0] + T.shift(X, s), g[1], g[2])
                for Q, kind, info in worlds[s].get((w[0] - 1, w[1], w[2]), []):
                    if Q == X and kind == 'P' and info[1] == 0 and info[2] == 'spent':
                        C = self.carrier(X, info[0])
                        if C is not None and T.moves(C, s):
                            return (False, f's{s} own spent hopper carried into it') if why else False
                continue
            w = (g[0] + T.shift(X, s), g[1], g[2])
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                for Q, kind, info in worlds[s].get((w[0] + d[0], w[1] + d[1], w[2] + d[2]), []):
                    if kind == 'RB' and Q != X:
                        return (False, f's{s} touches {Q} RB') if why else False
        return Ring2.cell_ok(self, X, g, worlds, why, strict)


def pieces(cells):
    """number of 4-connected components of a lane set"""
    cells = set(cells); seen = set(); n = 0
    for c in cells:
        if c in seen: continue
        n += 1; st = [c]
        while st:
            u = st.pop()
            if u in seen: continue
            seen.add(u); st += [v for v in nb(u) if v in cells and v not in seen]
    return n


def level_opts(m, s, below, a, b, step, mode, mg=(0, 1), free=None, cap=4000, forbid=frozenset(), low=None,
               periodic=True, lowR=frozenset(), side=False):
    """layouts for one level over the lower level's plate lanes `below`, cheapest first.
    side (levels 3 apart instead of 4, as in the human 3 bps flyer): the hoppers carried by the lower level stand
    beside its plate lanes (their spent position touches the lower plate cell sideways, x = -2) instead of on them;
    no RB over the lower plate; loop hoppers and covers not beside it; stickies are human stickies that pull the
    lower plate cell directly (no extra cell, no attach lane).
    mode 's2' (level 1: sticky on the hopper layer held by an attach lane s2), 'hs' (human sticky), 'top' (front).
    Returns dicts st (sticky lane), s2, Hm (hoppers on `below`), Hs (loop hoppers off `below`), R (RB lanes),
    Q (loop cover lanes at x = -2, owned by the loop neighbour), cost.
    forbid: lanes where the lower level has cells near its top (x >= -1); the lower level rises by up to 2 relative
    to this one, so no loop hopper may stand there and no loop cover may lie there or in the neighbouring towers'
    copies of those lanes (+-step).
    low = (lower level's sticky lane, lower mode): its power block (owned by this level) needs room. Below an
    attach-lane sticky ('s2') one side lane must stay free of this level's lanes and of the lower level's, with
    none of this level's hoppers beside it (it would power them while spent); below a human sticky ('hs') its
    lane (where the block hangs) takes no loop hopper."""
    my, mz = mg
    inb = lambda l: -my <= l[0] < a + my and -mz <= l[1] < b + mz
    lanes = [(y, z) for y in range(-1 - my, a + 1 + my) for z in range(-1 - mz, b + 1 + mz) if inb((y, z))]
    bl = set(below); out = []
    qbad = set(forbid) | {(l[0] + sg * step[0], l[1] + sg * step[1]) for l in forbid for sg in (1, -1)}
    # (nor beside the lower level's redstone blocks, own tower or the neighbours': the cover would touch them)
    qbad |= {v for l in lowR for sg in (0, 1, -1) for v in nb((l[0] + sg * step[0], l[1] + sg * step[1]))}
    nbl = {v for l in bl for v in nb(l)}
    colw = set(forbid) - bl - set(lowR)   # the lower level's column / connector lanes near its top
    hmc = sorted(l for l in lanes if l not in bl and l in nbl and l not in forbid) if side else None
    for st in ([None] if mode == 'top' else sorted(bl)):
        for Hm in itertools.combinations(hmc if side else sorted(bl - {st}), m):
            s2opts = [None] if mode != 's2' else [l for l in nb(st) if l not in bl and l not in Hm and inb(l)]
            for s2 in s2opts:
                offl = [l for l in lanes if l not in bl and l != st and l != s2 and l not in Hm and l not in forbid
                        and not (low is not None and low[1] == 'hs' and l == low[0]) and not (side and l in nbl)]
                for Hs in itertools.combinations(offl, s):
                    H = list(Hm) + list(Hs); Hset = set(H)
                    # loop covers: lanes beside the loop hoppers, not over the lower plate, free of this level
                    # (not beside a hopper the lower level carries: the cover would drag it; not beside a human
                    # sticky: the lower level's pulled cell sits at x = -2 there)
                    nbHm = {v for h in Hm for v in nb(h)} | (set(nb(st)) if mode == 'hs' else set())
                    qc = sorted({v for h in Hs for v in nb(h) if v not in Hset and v not in bl and v != st and v != s2
                                 and inb(v) and v not in qbad and v not in nbHm and not (side and v in nbl)})
                    Qs = [()] if not Hs else []
                    for nq in range(1, len(Hs) + 1):
                        Qs = [Q for Q in itertools.combinations(qc, nq) if all(any(q in nb(h) for q in Q) for h in Hs)]
                        if Qs: break
                    if not Qs: continue
                    # cover options for corner links (the loop neighbour is rotated; build picks the nearest)
                    qcc = sorted({v for h in Hs for v in nb(h) if v not in Hset and v not in bl and v != st and v != s2
                                  and inb(v) and v not in forbid and v not in nbHm})
                    Qcs = [()] if not Hs else []
                    for nq in range(1, len(Hs) + 1):
                        Qcs = [Q for Q in itertools.combinations(qcc, nq) if all(any(q in nb(h) for q in Q) for h in Hs)]
                        if Qcs: break
                    cand = [l for l in lanes if l not in Hset and l != st and l != s2 and l != free
                            and any(h in nb(l) for h in H) and not (side and l in bl)]
                    fr = [free] if free is not None and free not in Hset else []
                    found = []
                    for nr in range(0, len(H) + 1):
                        found = [R for R in itertools.combinations(cand, nr)
                                 if all(any(r in nb(h) for r in list(R) + fr) for h in H)
                                 and (mode != 'hs' or any(l in nb(st) for l in H + list(R)))]
                        if found: break
                    for R in found:
                        # the neighbouring towers (same layout, +-step): no shared lanes, no RB beside their hoppers
                        own = Hset | set(R) | {l for l in (st, s2) if l is not None}
                        # (periodic=False: every link is a corner, the straight-step copies do not exist)
                        sh = lambda S: {(l[0] + sg * step[0], l[1] + sg * step[1]) for l in S for sg in (1, -1)} if periodic else set()
                        nH, nAll = sh(Hset), sh(own)
                        if own & nAll or any(r in nb(h) for r in R for h in nH): continue
                        glue = Hset | set(R) | ({s2} if s2 is not None else set())
                        nhw = nH | sh(set(R)) | (sh({st}) if st is not None else set())
                        if any(v in nhw for l in glue for v in nb(l)): continue      # own glue beside their hardware
                        if any(n in bl or any(v in bl for v in nb(n)) for n in nH): continue   # their hoppers by our lower plate
                        if low is not None and low[1] == 's2':
                            used = own | bl
                            nbl = sh(bl) | nAll
                            # (the block rises up to 2 into the lower plate layer: no lower plate lane beside it)
                            if not any(p not in used and p not in nbl and not any(h in nb(p) for h in Hset | nH)
                                       and not any(v in bl for v in nb(p)) for p in nb(low[0])): continue
                        for Q in Qs:
                            if set(Q) & set(R): continue   # the loop neighbour rises up to 2 relative to this level
                            # prefer a straight loop column: the loop neighbour's column lane q - step beside its cluster
                            # the loop neighbour's connector: from its cluster (same lanes, +step) to the cover
                            clus = set(H) | set(R)
                            far = sum(min(abs(q[0] - step[0] - c[0]) + abs(q[1] - step[1] - c[1]) for c in clus) - 1
                                      for q in Q)
                            # the plate (fronts of hoppers, RBs, attach lane) in one piece: every extra piece costs
                            # a routed join (2-3 cells, more when the sticky or neighbours are in the way)
                            pl = set(H) | set(R) | ({s2} if s2 is not None else set())
                            if side and pieces(pl) > 1: continue   # glue stays in the plate layer: one piece
                            cost = len(R) + 2 * len(Q) + far + (3 * (pieces(pl) - 1) if side else 0)
                            if side and low is not None and low[0] is not None:
                                # the lower sticky's power block hangs in its lane just below this level's plate:
                                # keep that lane on (or beside) the plate so its attach cell is short
                                dl = min(abs(low[0][0] - c[0]) + abs(low[0][1] - c[1]) for c in pl)
                                cost += 2 * dl
                            if side: cost += 2 * len(set(R) & colw)   # an RB over the lower column makes it detour
                            out.append(dict(st=st, s2=s2, Hm=list(Hm), Hs=list(Hs), R=list(R), Q=list(Q), cost=cost,
                                            Qc=[list(q) for q in Qcs if not set(q) & set(R)]))
                            if len(out) >= cap: break
    out.sort(key=lambda d: d['cost'])
    return out


_BTL = {}
CP_ABOVE = 5   # levels with more hoppers use stack_cp.level_cp


def back_top_lanes(k, vmod, step, cv, xoff):
    """lanes (module frame) where a routed straight back body has cells at x >= -1 (plate, RBs, hoppers, column)"""
    import sqbuild
    key = (k, repr(vmod), step, cv, tuple(xoff or ()))
    if key in _BTL: return _BTL[key]
    r = tower2.build(k, 1, 0, (), back=(vmod, step), cv=cv, xoff=xoff)
    route_all(r)
    X = 1 if r.T.L >= 8 else 0
    x0 = r.place[X][0]
    out = set()
    for g in r.glue[X]:
        loc = sqbuild.to_local(r.place[X], (g[0] - x0, g[1], g[2]))
        if loc[0] >= -1: out.add(loc[1:])
    out |= {tuple(c[1:]) for c in vmod['R']} | {tuple(c) for c in vmod['P']}
    _BTL[key] = frozenset(out)
    return _BTL[key]


def corner_cover(lay, place, L, lowtop=frozenset(), lowR=frozenset()):
    """{tower i: cover lanes} for the corner links (tower i's loop neighbour i+1 is on the next side, rotated):
    among the layout's valid cover choices, the one nearest to the neighbour's cluster (in tower i's frame)"""
    import sqbuild
    if not lay['Hs'] or not lay.get('Qc'): return {}
    m = L // 4; out = {}
    clus = lay['Hm'] + lay['Hs'] + lay['R']
    for i in range(L):
        if i % m != m - 1: continue
        W = (i + 1) % L
        wl = [sqbuild.to_local(place[i], sqbuild.to_world(place[W], (0,) + tuple(c)))[1:] for c in clus]
        far = lambda Q: sum(min(abs(q[0] - c[0]) + abs(q[1] - c[1]) for c in wl) for q in Q)
        # the cover belongs to W: in W's frame it must avoid W's lower level near its top and its RBs' sides
        bad = {v for l in lowR for v in nb(l)} | set(lowtop)
        okq = lambda Q: all(sqbuild.to_local(place[W], sqbuild.to_world(place[i], (0,) + tuple(q)))[1:] not in bad
                            for q in Q)
        cands = [Q for Q in [lay['Q']] + lay['Qc'] if okq(Q)]
        if not cands: return None
        best = min(cands, key=far)
        if best != lay['Q']: out[i] = best
    return out


def build(k, back, params, choice, cv, xoff=None, mg=(0, 1), opts_cache=None, upto=None, gap=4):
    """back = (module, step) with k-1 hoppers; params = [(m, s), ...] for levels 1..M+1 (last = front);
    choice = layout index per level. Returns a Ring3 (unrouted, unpowered) or None.
    upto: build only levels 1..upto (a partial stack, for pruning: higher levels only add cells)."""
    vmod, step = back
    h = len(params)
    assert len(vmod['P']) == k - 1 and h >= 2
    for j, (m, s) in enumerate(params, 1):
        assert m + s + (1 if j < h - 1 else 0) == k, (j, m, s)
    a, b = vmod['size']
    L = square.ring_size(k)
    T0 = Timing(k, L)
    place = square.square_layout(L, a, b, step, cv)
    if xoff: place = [(p[0] + xoff[i],) + tuple(p[1:]) for i, p in enumerate(place)]
    below = [tuple(c[1:]) for c in vmod['PLATE']]
    forbid = back_top_lanes(k, vmod, step, cv, xoff)
    lowR = frozenset(tuple(c[1:]) for c in vmod['R'])
    tops, lowRs = [], []
    hb = h if upto is None else upto
    lays = []
    for j in range(1, hb + 1):
        m, s = params[j - 1]
        side = gap == 3
        mode = 'top' if j == h else 's2' if j == 1 and not side else 'hs'
        free = lays[-1]['st'] if mode == 'top' and lays and not side else None
        low = (lays[-1]['st'], 's2' if j == 2 and not side else 'hs') if lays else None
        per = L // 4 > 1
        key = (m, s, tuple(sorted(below)), a, b, step, mode, mg, free, forbid, low, per, lowR, side)
        tops.append(forbid); lowRs.append(lowR)
        if opts_cache is not None and key in opts_cache: g = opts_cache[key]
        elif m + s > CP_ABOVE and not side:   # enumeration explodes: CP-SAT layouts (best first)
            import stack_cp
            g = stack_cp.level_cp(m, s, below, a, b, step, mode, mg, free, forbid=forbid, low=low, periodic=per,
                                  lowR=lowR)
            if opts_cache is not None: opts_cache[key] = g
        else:
            g = level_opts(m, s, below, a, b, step, mode, mg, free, forbid=forbid, low=low, periodic=per, lowR=lowR,
                           side=side)
            if opts_cache is not None: opts_cache[key] = g
        if len(g) <= choice[j - 1]: return None
        lay = g[choice[j - 1]]
        lays.append(lay)
        H = lay['Hm'] + lay['Hs']
        below = H + lay['R'] + ([lay['s2']] if mode == 's2' else [])
        forbid = frozenset(below) | {l for l in (lay['st'], lay['s2']) if l is not None}
        lowR = frozenset(lay['R'])
    S = T0.S
    rests, nxt, loop = list(T0.rest), [T0.nxt(i) for i in range(L)], [None] * L
    for j in range(1, hb + 1):
        rests += [(T0.rest[i] - 2 * j) % S for i in range(L)]
        nxt += [(j - 1) * L + i for i in range(L)]
        loop += [j * L + T0.nxt(i) for i in range(L)]
    T = Timing2(k, rests, nxt)
    mods = [vmod] * L; places = list(place); mats = ['slime' if i % 2 == 0 else 'honey' for i in range(L)]
    for j in range(1, hb + 1):
        lay = lays[j - 1]; st, s2 = lay['st'], lay['s2']
        H = lay['Hm'] + lay['Hs']; R = lay['R']
        side = gap == 3
        mode = 'top' if j == h else 's2' if j == 1 and not side else 'hs'
        lowpl = {tuple(c[1:]) for c in mods[(j - 1) * L]['PLATE'] if c[0] == 1}   # the lower plate lanes (x = 1)
        qcorner = corner_cover(lay, place, L, tops[j - 1], lowRs[j - 1])
        if qcorner is None: return None
        for i in range(L):
            X, Y = j * L + i, (j - 1) * L + i
            Q = qcorner.get(i, lay['Q'])
            D = T.shift(X, T.rest[X]) - T.shift(Y, T.rest[X])
            x0 = places[Y][0] + gap - D
            plate = [(1,) + tuple(c) for c in H + R]
            rig = []
            if mode == 's2':
                plate += [(0,) + tuple(s2), (1,) + tuple(s2)]
                rig = [dict(pos=(0,) + tuple(st), dir=-1, victim=Y)]
            elif mode == 'hs':
                rig = [dict(pos=(1,) + tuple(st), dir=-1, victim=Y)]
                if not side: mods[Y] = dict(mods[Y], PLATE=list(mods[Y]['PLATE']) + [(2,) + tuple(st)])
            mods.append(dict(P=[tuple(c) for c in H], PC=['B'] * len(lay['Hm']) + ['L'] * len(lay['Hs']),
                             R=[(0,) + tuple(c) for c in R], PLATE=plate,
                             CONT=([(-2,) + next(n for n in nb(c) if n in lowpl) for c in lay['Hm']] if side else
                                   [(-3,) + tuple(c) for c in lay['Hm']]), CONTL=[(-2,) + tuple(q) for q in Q],
                             size=(a, b), RIG=rig))
            places.append((x0,) + place[i][1:])
            mats.append('honey' if (i + j) % 2 else 'slime')
    r = Ring3(T, mods, places, mats, loop)
    if gap == 3:   # levels 3 apart: glue above a body's plate layer would push the hoppers of the level above
        r.xcap = {X: 1 for X in range(T.L) if X < hb * L}
    r.lays, r.h, r.L0, r.power_top, r.params = lays, hb, L, hb == h, params
    return r


def add_power(r):
    """tower2.add_power_greedy for stacks: per sticky (level j < h, powered by level j+1 of the same tower), the
    first block cell / attach cell that adds no collision and no power problem around it. Neighbourhoods are the
    neighbouring towers (all levels); when the ring's sides are exact copies only side 0 is solved and its choices
    are copied to the other sides."""
    import sqbuild
    T = r.T; L = r.L0; h = r.h; m = L // 4
    tw = sym_towers(r); sym = len(tw) < L
    side0 = [i for i in tw if i < m] if sym else tw
    nl = T.L // L
    def near_of(i): return sorted({((i + d) % L) + jj * L for d in (-1, 0, 1) for jj in range(nl)})
    def place(src, loc, att):
        mod = dict(r.mods[src]); mod['R'] = list(mod['R']) + [loc]; r.mods[src] = mod
        a_ = r.mw(src, add(loc, att), 0, src)
        r.extra[src] = set(r.extra[src]) | {a_}; r.glue[src] = r.glue[src] | {a_}
    for j in range(1, h):
        for i in side0:
            tgt, src = j * L + i, (j + 1) * L + i
            st = T.rest[tgt]
            sp = r.mw(tgt, r.mods[tgt]['RIG'][0]['pos'], st)
            near = near_of(i)
            occ = r.world(st, bodies=near)
            done = None
            for d in ((1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                w = add(sp, d)
                if occ.get(w): continue
                cx = w[0] - r.place[src][0] - T.shift(src, st)
                loc = sqbuild.to_local(r.place[src], (cx, w[1], w[2]))
                for att in ((1, 0, 0), (-1, 0, 0)) + tuple((0,) + d2 for d2 in N4):
                    old = (r.mods[src], set(r.extra[src]), set(r.glue[src]))
                    place(src, loc, att)
                    r.__dict__.pop('_hw', None)
                    bad = collisions(r, near) or [p for p in power_problems(r, near)
                                                  if p[2] == src or (p[3] == tgt and 'unpowered' in p[1])]
                    if not bad:
                        r.invalidate()
                        bad = [b for b in r.check([tgt, src]) if f'drags {src} RB' in b[2] or f"({src}, 'RB'" in b[2]
                               or f'touches {src} RB' in b[2]]
                    if not bad: done = (loc, att); break
                    r.mods[src], r.extra[src], r.glue[src] = old
                    r.__dict__.pop('_hw', None)
                if done: break
            if not done: return None
            if sym:
                for q in (1, 2, 3): place((j + 1) * L + i + q * m, *done)
                if i == m - 1: pass
    r.__dict__.pop('_hw', None); r.invalidate()
    return r


def unpowered_hoppers(r):
    """hoppers with no redstone block of their own body beside them (same x, side lane) - they never fire"""
    out = []
    for X in range(r.T.L):
        R = {tuple(c) for c in r.mods[X]['R']}
        for j in range(len(r.mods[X]['P'])):
            h, py, pz = r.lev(X, j)
            if not any((h, py + d[0], pz + d[1]) in R for d in N4): out.append((X, j))
    return out


def finish(r, bound=None):
    """power, route and check a built stack; returns (ring or None, reason). bound: give up ('worse') as soon as
    the predicted PL before routing (routing only adds cells) reaches it."""
    if r is None: return None, 'layout'
    if collisions(r): return None, 'collide'
    if add_power(r) is None: return None, 'power'
    if collisions(r) or power_problems(r) or unpowered_hoppers(r): return None, 'power2'
    if bound is not None and predicted(r) >= bound: return None, 'worse'
    try: route_all(r)
    except RuntimeError: return None, 'route'
    if bound is not None and predicted(r) >= bound: return None, 'worse'
    L = r.L0
    if r.check(subset=[jj * L + i for i in sym_towers(r) for jj in range(r.T.L // L)]): return None, 'check'
    bad = r.check()
    if bad: return None, 'check ' + bad[0][2][:40]
    try: r.flyer(1)
    except AssertionError: return None, 'export'
    return r, 'ok'


def predicted(r):
    import families
    return families.predicted_pl(r)


def sym_towers(r):
    """towers whose bodies represent the whole ring when its four sides are exact rotated copies (same timing and
    x offsets on every side: 2m = 0 mod S and m a multiple of the base ring): side 0 and its first corner; else all"""
    L = r.L0; m = L // 4
    if L >= 8 and (2 * m) % r.T.S == 0 and m % bodies_for(r.T.k) == 0: return list(range(m + 1)) + [L - 1]
    return list(range(L))


def partial_ok(r, j):
    """no collision, and every unrouted glue cell (plates, covers) of levels j-1 and j passes the checker
    (on the representative towers and their neighbours)"""
    L = r.L0; nl = r.T.L // L
    tw = sym_towers(r)
    near = sorted({((i + d) % L) + jj * L for i in tw for d in (-1, 0, 1) for jj in range(nl)})
    if collisions(r, near): return False
    ws = r.worlds(near)
    for jj in (j - 1, j):
        if jj < 0: continue
        for i in tw:
            X = jj * L + i
            for g in r.glue[X]:
                if not r.cell_ok(X, g, ws): return False
    return True


def sim_pl(r, k, slack=2):
    """the lowest PL in [predicted, predicted + slack] at which the ring flies (1 seed, 1000 blocks), or None:
    a safety net for model gaps (a push 1 larger than the load model, a merge the checker misses)"""
    import os, simk, tempfile
    p = os.path.join(tempfile.gettempdir(), f'stack_sim_{os.getpid()}.flyer')
    pl = predicted(r); r.flyer(pl + slack).save(p)
    for q in range(pl, pl + slack + 1):
        ok, out = simk.flies(p, k, q)
        if 'pass=true' in out: return q
    return None


def construct(k, back, params, cv, xoff=None, nlay=8, mg=(0, 1), deadline=None, stats=None, max_leaves=40, sim=True,
              gap=4):
    """depth-first over the level layouts (cheapest first per level), pruning partial stacks that already fail;
    every surviving leaf is powered, routed and checked; returns the best (predicted PL, choice, ring) or None"""
    cache = {}; h = len(params)
    best = [None]; leaves = [0]
    def tally(w):
        if stats is not None: stats[w] = stats.get(w, 0) + 1
    def rec(prefix):
        j = len(prefix) + 1
        for c in range(nlay):
            if (deadline and time.time() > deadline) or leaves[0] >= max_leaves: return
            ch = prefix + (c,)
            try: r = build(k, back, params, ch, cv, xoff, mg, cache, upto=j, gap=gap)
            except (AssertionError, RuntimeError): tally('err'); continue
            if r is None: return
            if not partial_ok(r, j): tally(f'prune{j}'); continue
            if j < h: rec(ch); continue
            leaves[0] += 1
            try: rr, why = finish(build(k, back, params, ch, cv, xoff, mg, cache, gap=gap), best[0] and best[0][0])
            except (AssertionError, RuntimeError) as e: rr, why = None, 'err'
            p = predicted(rr) if rr is not None else None
            if rr is not None and sim:
                p = sim_pl(rr, k)
                if p is None: rr, why = None, 'sim'
            tally(why.split()[0])
            if rr is None: continue
            if best[0] is None or p < best[0][0]: best[0] = (p, ch, rr)
    rec(())
    return best[0]


def all_params(k, M):
    """every uniform parameter list for M middle levels + front"""
    h = M + 1
    rng = [range(0, k - (1 if j < h - 1 else 0) + 1) for j in range(1, h + 1)]
    for ms in itertools.product(*rng):
        yield [(m, k - m - (1 if j < h - 1 else 0)) for j, m in enumerate(ms, 1)]


if __name__ == '__main__':
    import bank_links
    k = int(sys.argv[1])
    params = [tuple(map(int, t.split(','))) for t in sys.argv[2].split(';')]
    nlay = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    e = bank_links.links(k - 1)[0]
    L = square.ring_size(k)
    xo = tower2.balanced_xoff(k, L, bodies_for(k) - 1)
    st = {}
    t = time.time()
    res = construct(k, (e['mod'], e['step']), params, (5, -2), xo, nlay, stats=st)
    print('time', round(time.time() - t, 1), st)
    if res:
        p, lc, r = res
        print('pred', p, lc, [(l['Hm'], l['Hs'], l['R'], l['Q']) for l in r.lays])


def back_candidates(k, keep=6, span=7, lat=0, minstep=2, box=3):
    """rule-built back links (link0.links, n = k-1 hoppers) as plain back rings with balanced frame offsets:
    [(back max, back sum, mod, step, cv)] cheapest first, one corner per link (the cheapest)."""
    import link0
    out = []
    for mod, step, c in link0.links(k - 1, box=box, lat=lat, minstep=minstep):
        ev = link0.evaluate(k, mod, step, span)
        if ev: out.append((ev[0], ev[1], mod, step, ev[2]))
    out.sort(key=lambda t: t[:2])
    return out[:keep]


def back_corners(k, mod, step, span=7, keep=4):
    """corner offsets whose plain back ring passes every check, cheapest first"""
    import link0
    res = []
    for cv in itertools.product(range(-3, span), repeat=2):
        try: r = link0.back_ring(k, mod, step, cv, bodies_for(k) - 1)
        except (AssertionError, RuntimeError): continue
        if r is not None: res.append((max(r.size()), sum(r.size()), cv))
    return [cv for _, _, cv in sorted(res)[:keep]]


def loads(r):
    """per body (glue + RBs, carried hoppers, own rigid pistons)"""
    T = r.T; car = [0] * T.L
    for U in range(T.L):
        for j in range(len(r.mods[U]['P'])):
            W = r.carrier(U, j)
            if W is not None: car[W] += 1
    sz = r.size()
    return [(sz[X], car[X], len(r.mods[X].get('RIG', []))) for X in range(T.L)]


def recipe(k, back_spec, cv, params, choice, mg=(0, 1), phase=None):
    """everything needed to rebuild a stack without searching (JSON-friendly)"""
    return dict(k=k, back=back_spec, cv=list(cv), params=[list(p) for p in params], choice=list(choice), mg=list(mg),
                phase=phase)


def from_recipe(rec):
    """rebuild a stack from a recipe: build (layout choices replayed), power, route, check (~1 s)"""
    import stack_scan
    k = rec['k']; e = stack_scan.back_entry(k, rec['back'])
    L = square.ring_size(k)
    xo = tower2.balanced_xoff(k, L, bodies_for(k) - 1 if rec.get('phase') is None else rec['phase'])
    r, why = finish(build(k, (e['mod'], e['step']), [tuple(p) for p in rec['params']], tuple(rec['choice']),
                          tuple(rec['cv']), xo, tuple(rec.get('mg', (0, 1)))))
    return r
