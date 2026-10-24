"""Non-uniform stacks: geometry for a stack_topo suggestion (per back position a list of segments with numbers
(m, s, dn, pw), plus the offsets of the links into each position). Levels are 4 apart (stack.build gap=4 rules).
The back ring is built and routed on its own first and then frozen (the back is sacred: towers never add back
cells). Layouts are chosen per class (side position when the four sides are copies, else per body), level by
level, filtered against the real neighbouring layouts (lane rules) and checked against the real neighbours
(collisions + cell rules on the partial stack), depth-first with a node budget.
Segment (i, j) over back body i: m hoppers stand on (i, j-1)'s plate, s loop hoppers are carried by the next
tower's segment (i+1, j) (its cover cells beside them); dn = its sticky pulls (i, j-1) (level 1: attach-lane
sticky on the hopper layer pulling the back's existing plate cell; higher: human sticky in the plate layer pulling
an extra cell of the segment below); pw = who powers the sticky: 'a' the segment above, 'p' the previous tower's
segment (i-1, j). Every back body must be pulled (one back module).
python stack_nu.py K BACK CV TOWERS LINKS_IN
   TOWERS: positions separated by '/', segments by ';', a segment = m,s,dn,pw (e.g. '2,0,1,a;3,0,1,p')"""
import sys, time
import square, tower2, sqbuild, stack, stack_topo
from nk import add
from nk2 import Timing2, power_problems
from terrace import collisions
from tower import route_all
from stack import Ring3, level_opts, N4

GAP = 4
DEBUG = False
PERIODIC = True   # level_opts also assumes the neighbours are copies (a heuristic filter; real neighbours are checked)


def _nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


class Plan:
    """bodies and timing: back bodies 0..L-1, then segments; idx[(i, j)] = body of segment j over back body i.
    chosen: only the (class, level) pairs placed so far (a partial stack)."""

    def __init__(self, k, towers, sym, chosen=None):
        self.k = k; L = square.ring_size(k); self.L = L
        n = len(towers); self.n, self.sym, self.towers = n, sym, towers
        self.cls = [i % n for i in range(L)] if sym else list(range(L))
        T0 = stack_topo.Timing(k, L); S = T0.S
        self.idx = {(i, 0): i for i in range(L)}
        rests, nxt = list(T0.rest), [T0.nxt(i) for i in range(L)]
        for i in range(L):
            for j in range(1, len(towers[self.cls[i]]) + 1):
                if chosen is not None and (self.cls[i], j) not in chosen: continue
                self.idx[(i, j)] = len(rests)
                rests.append((T0.rest[i] - 2 * j) % S)
                nxt.append(self.idx[(i, j - 1)])
        self.T = Timing2(k, rests, nxt)
        self.where = {X: ij for ij, X in self.idx.items()}

    def seg(self, i, j):
        tw = self.towers[self.cls[i % self.L]]
        return tw[j - 1] if 1 <= j <= len(tw) else None

    def loop(self, X):
        i, j = self.where[X]
        return self.idx.get(((i + 1) % self.L, j)) if j >= 1 else None

    def power_src(self, i, j):
        g = self.seg(i, j)
        return self.idx.get((i, j + 1)) if g[3] == 'a' else self.idx.get(((i - 1) % self.L, j))


def back_ring(k, back, cv, links_in):
    n = len(links_in)
    lk = [links_in[(q + 1) % n] for q in range(n)]   # link q -> q+1 is the link into q+1
    r = tower2.build(k, 1, 0, (), back=back, cv=cv, xoff=stack_topo.xoff_for(k, lk))
    if r is None or collisions(r): return None
    route_all(r)
    if r.check() or power_problems(r): return None
    return r


def lanes_of(r, X, x_min=None):
    """lanes (X's module frame) where X has glue, optionally only cells at module x >= x_min"""
    x0 = r.place[X][0]; out = set()
    for g in r.glue[X]:
        loc = sqbuild.to_local(r.place[X], (g[0] - x0, g[1], g[2]))
        if x_min is None or loc[0] >= x_min: out.add(loc[1:])
    return out


def compatible(lay, bl, other, obl, sh):
    """stack.level_opts' neighbour rules against a real neighbouring layout `other` (its lanes shifted by sh into
    this frame; obl its lower plate lanes): no shared lanes, no RB beside the other's hoppers, no glue beside the
    other's hardware, no hopper on or beside the other's lower plate (both ways)"""
    S = lambda ls: {(l[0] + sh[0], l[1] + sh[1]) for l in ls if l is not None}
    I = lambda ls: {l for l in ls if l is not None}
    def parts(L_, f):
        return f(L_['Hm'] + L_['Hs']), f(L_['R']), f([L_['st']]), f([L_.get('s2')])
    H1, R1, st1, s21 = parts(lay, I); H2, R2, st2, s22 = parts(other, S)
    if (H1 | R1 | st1 | s21) & (H2 | R2 | st2 | s22): return False
    for Ha, Ra, s2a, Hb, Rb, stb in ((H1, R1, s21, H2, R2, st2), (H2, R2, s22, H1, R1, st1)):
        if any(v in Hb for r_ in Ra for v in _nb(r_)): return False
        hw = Hb | Rb | stb
        if any(v in hw for g in Ha | Ra | s2a for v in _nb(g)): return False
    blo = S(obl); bl = set(bl)
    if any(h in blo or any(v in blo for v in _nb(h)) for h in H1): return False
    if any(h in bl or any(v in bl for v in _nb(h)) for h in H2): return False
    return True


def assemble(plan, br, vmod, lays, Qs, pw=None):
    """Ring3 for the plan (its present segments). lays[(class, level)] = layout; Qs[(class, level)] = the cover
    lanes actually used (corner links pick other covers); pw[(class, level)] = (loc, att): the power block of that
    segment's sticky (owned by its power source, which must be present)"""
    k, L, T = plan.k, plan.L, plan.T
    nbod = T.L
    mods = [vmod] * L + [None] * (nbod - L)
    places = list(br.place) + [None] * (nbod - L)
    mats = list(br.mat) + [None] * (nbod - L)
    a, b = vmod['size']
    for X in range(L, nbod):
        i, j = plan.where[X]
        c = plan.cls[i]; Y = plan.idx[(i, j - 1)]
        lay = lays[(c, j)]; g = plan.seg(i, j)
        D = T.shift(X, T.rest[X]) - T.shift(Y, T.rest[X])
        x0 = places[Y][0] + GAP - D
        H = lay['Hm'] + lay['Hs']; R = lay['R']
        plate = [(1,) + tuple(h) for h in H + R]
        rig = []
        if g[2] and j == 1:      # attach-lane sticky on the hopper layer, pulls the back's existing plate cell
            plate += [(0,) + tuple(lay['s2']), (1,) + tuple(lay['s2'])]
            rig = [dict(pos=(0,) + tuple(lay['st']), dir=-1, victim=Y)]
        elif g[2]:               # human sticky in the plate layer, pulls an extra cell of the segment below
            rig = [dict(pos=(1,) + tuple(lay['st']), dir=-1, victim=Y)]
        mods[X] = dict(P=[tuple(h) for h in H], PC=['B'] * len(lay['Hm']) + ['L'] * len(lay['Hs']),
                       R=[(0,) + tuple(h) for h in R], PLATE=plate, CONT=[(-3,) + tuple(h) for h in lay['Hm']],
                       CONTL=[(-2,) + tuple(q) for q in Qs.get((c, j), lay['Q'])], size=(a, b), RIG=rig)
        places[X] = (x0,) + tuple(br.place[i][1:])
        mats[X] = 'honey' if (i + j) % 2 else 'slime'
    for X in range(L, nbod):     # the pulled cells of human stickies
        i, j = plan.where[X]
        up = plan.idx.get((i, j + 1))
        if up is not None and plan.seg(i, j + 1)[2]:
            st = lays[(plan.cls[i], j + 1)]['st']
            mods[X] = dict(mods[X], PLATE=list(mods[X]['PLATE']) + [(2,) + tuple(st)])
    loop = [None] * nbod
    for X in range(L, nbod):
        W = plan.loop(X)
        if W is not None and mods[X]['CONTL']: loop[X] = W
        elif mods[X]['CONTL']: mods[X] = dict(mods[X], CONTL=[])   # neighbour not placed yet
    r = Ring3(T, mods, places, mats, loop)
    for X in range(L):   # the frozen back
        r.extra[X] = set(br.glue[X]); r.glue[X] = r.glue[X] | r.extra[X]
    r.plan = plan
    for X in range(L, nbod):
        i, j = plan.where[X]
        key = (plan.cls[i], j)
        if pw and key in pw:
            src = plan.power_src(i, j)
            if src is not None: _place_power(r, src, *pw[key])
    return r


def rep_bodies(plan):
    """bodies whose checks represent the ring: side 0 (+ the first body of side 1, the last of side 3) and towers"""
    if not plan.sym: return list(range(plan.T.L))
    m = plan.L // 4
    return [X for X, (i, j) in plan.where.items() if i <= m or i == plan.L - 1]


def near_bodies(plan, Xs, d=1):
    ii = {plan.where[X][0] for X in Xs}
    return sorted({Y for Y, (i2, _) in plan.where.items()
                   if any(min((i2 - i) % plan.L, (i - i2) % plan.L) <= d for i in ii)})


def partial_ok(r, Xs):
    """no collisions near Xs; every unrouted glue cell of Xs, the segments below them and the neighbouring towers'
    segments at these levels passes the cell rules"""
    plan = r.plan
    near = near_bodies(plan, Xs, 2)
    if collisions(r, near): return False
    ws = r.worlds(near)
    chk = set()
    for X in Xs:   # Xs, the segments below them, and the neighbouring towers' segments at these levels
        i, j = plan.where[X]
        chk |= {X, plan.idx[(i, j - 1)]}
        chk |= {Y for Y in near_bodies(plan, [X], 1) if plan.where[Y][1] in (j - 1, j)}
    for Y in chk:
        for g in r.glue[Y]:
            if not r.cell_ok(Y, g, ws): return False
    return True


def _place_power(r, src, loc, att):
    mod = dict(r.mods[src]); mod['R'] = list(mod['R']) + [loc]; r.mods[src] = mod
    a_ = r.mw(src, add(loc, att), 0, src)
    r.extra[src] = set(r.extra[src]) | {a_}; r.glue[src] = r.glue[src] | {a_}
    r.__dict__.pop('_hw', None); r.invalidate()


def power_options(r, tgt, src, limit=6):
    """placements (loc in src's frame, attach direction) of a redstone block owned by src beside tgt's sticky at
    tgt's local slot 0 that add no collision, no power problem and no cell-rule failure nearby (r is unchanged)"""
    plan = r.plan; T = r.T
    st = T.rest[tgt]
    sp = r.mw(tgt, r.mods[tgt]['RIG'][0]['pos'], st)
    near = near_bodies(plan, [tgt, src], 1)
    occ = r.world(st, bodies=near)
    out = []
    for d in ((1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        w = add(sp, d)
        if occ.get(w): continue
        cx = w[0] - r.place[src][0] - T.shift(src, st)
        loc = sqbuild.to_local(r.place[src], (cx, w[1], w[2]))
        for att in ((1, 0, 0), (-1, 0, 0)) + tuple((0,) + d2 for d2 in N4):
            old = (r.mods[src], set(r.extra[src]), set(r.glue[src]))
            _place_power(r, src, loc, att)
            bad = collisions(r, near) or [p for p in power_problems(r, near)
                                          if p[2] == src or (p[3] == tgt and 'unpowered' in p[1])]
            if not bad:
                # (the new block and attach cell against every nearby body's glue, and theirs against it)
                bad = [b for b in r.check(near) if b[1] is not None and 'not carried' not in b[2]
                       and 'not attached' not in b[2] and (b[0] == src or f'{src} RB' in b[2]
                                                            or f"({src}, 'RB'" in b[2])]
            if DEBUG and bad: print('  power', tgt, src, d, att, str(bad[0])[:110])
            r.mods[src], r.extra[src], r.glue[src] = old
            r.__dict__.pop('_hw', None); r.invalidate()
            if not bad:
                # routing estimate: the attach cell's distance to src's plate
                a_ = r.mw(src, add(loc, att), 0, src)
                dist = min(sum(abs(u - v) for u, v in zip(a_, g)) for g in r.plates[src])
                out.append((dist, loc, att))
                if len(out) >= limit: break
                break
        if len(out) >= limit: break
    out.sort()
    return [(loc, att) for _, loc, att in out]


def route_levels(r):
    """tower.route_all in the order the search placed the segments (level by level, ring order), so the routes
    estimated during the search are the ones that get built"""
    plan = r.plan; D = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for X in sorted(range(r.T.L), key=lambda X: (plan.where[X][1], plan.where[X][0])):
        full = set(r.plates[X]); comps = []; seen = set()
        for c in full:
            if c in seen: continue
            st = [c]; comp = set()
            while st:
                u = st.pop()
                if u in comp: continue
                comp.add(u); st += [add(u, d) for d in D if add(u, d) in full]
            seen |= comp; comps.append(comp)
        tree = max(comps, key=len)
        r.plates[X] = tree; r.extra[X] = set(r.extra[X]) | (full - tree)
        r.route(X); r.plates[X] = full
    return r


def finish(r, bound=None):
    if r is None: return None, 'layout'
    if collisions(r): return None, 'collide'
    if collisions(r) or power_problems(r) or stack.unpowered_hoppers(r): return None, 'power2'
    if bound is not None and stack.predicted(r) >= bound: return None, 'worse'
    try: route_levels(r)
    except RuntimeError: return None, 'route'
    if bound is not None and stack.predicted(r) >= bound: return None, 'worse'
    bad = r.check(subset=rep_bodies(r.plan))
    if bad: return None, 'check ' + str(bad[0])[:90]
    bad = r.check()
    if bad: return None, 'check ' + bad[0][2][:40]
    try: r.flyer(1)
    except AssertionError: return None, 'export'
    return r, 'ok'


def corner_q(br, plan, lays, c, j, lay):
    """cover lanes for class c's loop hoppers when its loop neighbour is across a corner (rotated): among the
    layout's cover choices, the one nearest the neighbour's cluster in this frame (cf. stack.corner_cover)"""
    if not lay['Hs']: return lay['Q']
    i = c; W = (i + 1) % plan.L; cw = plan.cls[W]
    ol = lays.get((cw, j))
    if ol is None: return lay['Q']
    clus = ol['Hm'] + ol['Hs'] + ol['R']
    wl = [sqbuild.to_local(br.place[i], sqbuild.to_world(br.place[W], (0,) + tuple(q)))[1:] for q in clus]
    far = lambda Q: sum(min(abs(q[0] - w[0]) + abs(q[1] - w[1]) for w in wl) for q in Q)
    cands = [lay['Q']] + [list(q) for q in lay.get('Qc', [])]
    return min(cands, key=far)


def construct(k, back, cv, towers, links_in, nlay=4, max_leaves=6, max_nodes=400, deadline=None, stats=None,
              verbose=False, mg=(0, 1)):
    """layouts class by class, level by level (cheapest first), depth-first with partial checks against the real
    neighbours; leaves are powered, routed and checked; returns (predicted PL, lays, ring) of the best leaf"""
    vmod, step = back
    n, sym = stack_topo.positions(k)
    assert len(towers) == n and len(links_in) == n
    full = Plan(k, towers, sym)
    br = back_ring(k, back, cv, links_in)
    if br is None: return None
    a, b = vmod['size']
    order = [(c, j) for j in range(1, 9) for c in range(n) if j <= len(towers[c])]
    best = [None]; nodes = [0]; leaves = [0]

    def tally(w):
        if stats is not None: stats[w] = stats.get(w, 0) + 1

    def lower_lanes(lays, c, j):
        if j == 1: return [tuple(x[1:]) for x in vmod['PLATE']]
        l2 = lays[(c, j - 1)]; return l2['Hm'] + l2['Hs'] + l2['R'] + ([l2['s2']] if l2.get('s2') else [])

    def opts_for(lays, c, j):
        g = towers[c][j - 1]
        below = lower_lanes(lays, c, j)
        if j == 1:
            forbid = frozenset(lanes_of(br, c, -1)) | {tuple(x) for x in vmod['P']}
            lowR = frozenset(tuple(x[1:]) for x in vmod['R']); low = None
        else:
            ll = lays[(c, j - 1)]
            forbid = frozenset(below) | {l for l in (ll['st'], ll.get('s2')) if l is not None}
            lowR = frozenset(ll['R'])
            gl = towers[c][j - 2]
            low = (ll['st'], 's2' if j == 2 else 'hs') if gl[2] and gl[3] == 'a' else None
        mode = 's2' if g[2] and j == 1 else 'hs' if g[2] else 'top'
        ll = lays.get((c, j - 1))
        gl = towers[c][j - 2] if j > 1 else None
        free = ll['st'] if mode == 'top' and gl and gl[2] and gl[3] == 'a' else None
        m, s = g[0], g[1]
        if m + s > stack.CP_ABOVE:
            import stack_cp
            opts = stack_cp.level_cp(m, s, below, a, b, step, mode, mg, free, forbid=forbid, low=low,
                                     periodic=PERIODIC, lowR=lowR)
        else:
            opts = level_opts(m, s, below, a, b, step, mode, mg, free, forbid=forbid, low=low,
                              periodic=PERIODIC, lowR=lowR)
        # the straight neighbours already placed at this level (their lanes shifted by -step / +step)
        nbrs = []
        if sym:
            if c > 0 and (c - 1, j) in lays:
                nbrs.append((lays[(c - 1, j)], lower_lanes(lays, c - 1, j), (-step[0], -step[1])))
            if c + 1 < n and (c + 1, j) in lays:
                nbrs.append((lays[(c + 1, j)], lower_lanes(lays, c + 1, j), step))
        return [lay for lay in opts if all(compatible(lay, below, o, ob, sh) for o, ob, sh in nbrs)]

    def rec(lays, Qs, pw, pos):
        if (deadline and time.time() > deadline) or nodes[0] >= max_nodes or leaves[0] >= max_leaves: return
        if pos == len(order):
            leaves[0] += 1
            try: rr, why = finish(assemble(full, br, vmod, lays, Qs, pw), best[0] and best[0][0])
            except (AssertionError, RuntimeError) as ex: rr, why = None, 'err ' + str(ex)[:40]
            tally(why.split()[0])
            if verbose: print('leaf', why, flush=True)
            if rr is not None:
                p = stack.predicted(rr)
                if best[0] is None or p < best[0][0]: best[0] = (p, dict(lays), rr)
            return
        c, j = order[pos]
        sub = Plan(k, towers, sym, set(lays) | {(c, j)})
        cands = []
        for lay in opts_for(lays, c, j):
            if len(cands) >= 2 * nlay: break
            nodes[0] += 1
            if nodes[0] >= max_nodes: break
            lays2 = dict(lays); lays2[(c, j)] = lay
            Qs2 = dict(Qs)
            if stack_topo.corner_link(k, c) and lay['Hs']: Qs2[(c, j)] = corner_q(br, sub, lays2, c, j, lay)
            try: r = assemble(sub, br, vmod, lays2, Qs2, pw)
            except (AssertionError, RuntimeError, KeyError): tally('err'); continue
            if not partial_ok(r, [sub.idx[(c, j)]]): tally(f'prune{j}'); continue
            # the stickies whose power source and host are now both placed: power them now (prune if impossible)
            jobs = []
            if j > 1 and towers[c][j - 2][2] and towers[c][j - 2][3] == 'a': jobs.append((c, j - 1))
            if towers[c][j - 1][2] and towers[c][j - 1][3] == 'p' and ((c - 1) % n, j) in lays2: jobs.append((c, j))
            cn = (c + 1) % n
            if cn != c and (cn, j) in lays2 and towers[cn][j - 1][2] and towers[cn][j - 1][3] == 'p':
                jobs.append((cn, j))
            pw2 = dict(pw); ok = True
            for cc, jj in jobs:
                tgt = sub.idx[(cc, jj)]; src = sub.power_src(cc, jj)
                po = power_options(r, tgt, src)
                if not po: ok = False; break
                pw2[(cc, jj)] = po[0]
                r = assemble(sub, br, vmod, lays2, Qs2, pw2)
            if not ok: tally(f'power{j}'); continue
            # rank: routed loads of this segment and the one below (now complete but for the pulled cell above)
            X = sub.idx[(c, j)]; Y = sub.idx[(c, j - 1)]
            try:
                for B in ((Y, X) if j > 1 else (X,)): r.route(B)
            except RuntimeError: tally(f'route{j}'); continue
            ld = stack.loads(r)
            est = max(sum(ld[B]) for B in (Y, X))
            if best[0] is not None and est >= best[0][0]: tally(f'bound{j}'); continue
            cands.append((est, lay['cost'], len(cands), lays2, Qs2, pw2))
        cands.sort(key=lambda t: t[:3])
        for est, _, _, lays2, Qs2, pw2 in cands[:nlay]:
            if best[0] is not None and est >= best[0][0]: break
            rec(lays2, Qs2, pw2, pos + 1)

    rec({}, {}, {}, 0)
    return best[0]


def parse_towers(s):
    out = []
    for pos in s.split('/'):
        tw = []
        for g in [x for x in pos.split(';') if x]:
            m, s_, d, pw = g.split(',')
            tw.append((int(m), int(s_), int(d), pw if pw in ('a', 'p') else None))
        out.append(tw)
    return out


if __name__ == '__main__':
    import stack_scan
    k = int(sys.argv[1]); bi = sys.argv[2]; cv = tuple(map(int, sys.argv[3].split(',')))
    towers = parse_towers(sys.argv[4]); links_in = [int(v) for v in sys.argv[5].split(',')]
    e = stack_scan.back_entry(k, bi)
    st = {}; t = time.time()
    import os
    res = construct(k, (e['mod'], e['step']), cv, towers, links_in, stats=st, verbose=bool(os.environ.get('V')),
                    nlay=int(os.environ.get('NLAY', 4)), max_leaves=int(os.environ.get('LEAVES', 6)),
                    max_nodes=int(os.environ.get('NODES', 400)),
                    mg=tuple(map(int, os.environ.get('MG', '0,1').split(','))))
    print('time', round(time.time() - t, 1), st)
    if res:
        p, lays, r = res
        ld = stack.loads(r)
        print('predicted', p, 'loads', {r.plan.where[X]: sum(ld[X]) for X in rep_bodies(r.plan)
                                        if r.plan.where[X][0] < r.plan.n})
        sim = stack.sim_pl(r, k)
        print('sim', sim)
        name = f'out/stack/nu_n{k:02d}_pl{sim or p}.flyer'
        r.flyer(sim or p).save(name); print(name)
