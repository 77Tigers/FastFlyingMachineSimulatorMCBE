"""Randomised builder for pull-first lifecycles (agent G).

A lifecycle spec (see specs.py) gives: schedule S (N bodies x L slots), per body the reference slot w[b]
(relative slot r = (t - w[b]) % L), and per victim a list of piston kinds:
  name, sticky, fire (relative slot), REL (piston x - lane glue x at start of each relative slot),
  lane key, carriers {relative slot: body offset} (0 = own victim).
Power: each piston kind lists candidate source bodies (offset) for a redstone block that touches the
piston only at the fire slot start (validated by the model's exact power check).
"""
import random, heapq, sys, json, collections
from pathlib import Path
from pmodel import Design, Item, Sched, add, sx, nb, DIRS, trim, connected_ok

SYMS = [lambda u, v: (u, v), lambda u, v: (-u, v), lambda u, v: (u, -v), lambda u, v: (-u, -v),
        lambda u, v: (v, u), lambda u, v: (-v, u), lambda u, v: (v, -u), lambda u, v: (-v, -u)]


def conn(s):
    s = set(s)
    if not s:
        return set()
    st = [next(iter(s))]; seen = {st[0]}
    while st:
        p = st.pop()
        for q in nb(p):
            if q in s and q not in seen:
                seen.add(q); st.append(q)
    return seen


class Builder:
    def __init__(self, spec, rng, gtypes, places, tmpl):
        self.spec = spec
        self.sch = Sched(spec['S'])
        self.rng = rng
        self.d = Design(self.sch, gtypes)
        self.places = places          # per body (sym, (x0,y0,z0))
        self.tmpl = tmpl              # per body: dict lane -> (lx,u,v), extra cells list
        self.pidx = {}

    def w(self, b, lx, u, v):
        si, (x0, y0, z0) = self.places[b]
        a, c = SYMS[si](u, v)
        return (x0 + lx, y0 + a, z0 + c)

    def setup(self, bodies=None):
        d = self.d; sp = self.spec; L = self.sch.L; N = self.sch.N
        bodies = list(range(N)) if bodies is None else bodies
        for v in bodies:
            wv = sp['w'][v]
            for k in sp['pistons']:
                lx, u, vv = self.tmpl[v]['lanes'][k['lane']]
                base = self.w(v, lx, u, vv)
                pos = [sx(base, self.sch.DISP[v][t] + k['REL'][(t - wv) % L]) for t in range(L)]
                nxt = lambda t: pos[t + 1][0] if t + 1 < L else pos[0][0] + self.sch.ADV
                mv = [nxt(t) - pos[t][0] == 1 for t in range(L)]
                f = (wv + k['fire']) % L
                assert not mv[f] and not mv[(f + 1) % L], (k['name'], mv, f)
                assert sum(mv) == self.sch.ADV
                it = Item('piston', pos, mv, name=f"{k['name']}{v}", f=f, face=-1 if k['sticky'] else 1,
                          sticky=k['sticky'], victim=v)
                idx = len(d.items)
                for r, off in k['carriers'].items():
                    d.carry[(idx, (wv + r) % L)] = (v + off) % N
                d.add_item(it)
                self.pidx[(v, k['name'])] = idx
        for v in bodies:
            cells = set(self.tmpl[v]['lanes'].values()) | set(self.tmpl[v].get('extra', []))
            for c in cells:
                d.add_item(d.glue(v, self.w(v, *c)))
        errs = d.all_errors()
        errs = [e for e in errs if e[0] not in ('uncovered', 'nocarrier', 'power')]
        return errs

    def cell_ok(self, p0, b):
        it = self.d.glue(b, p0)
        return not self.d.item_errors(it, None, self.armc)

    def body_cells(self, b):
        return {it.pos[0] for it in self.d.items if it.cat == 'glue' and it.body == b}

    def place_power(self):
        """assign each piston a source (kind, body offset); cover groups with redstones / observers."""
        d = self.d; sp = self.spec; L = self.sch.L; N = self.sch.N
        self.armc = [d.arm_ext(t) for t in range(L)]
        self.holders = {b: [] for b in range(N)}
        groups = collections.defaultdict(list)
        for v in range(N):
            for k in sp['pistons']:
                kind, off = self.rng.choice(k['power'])
                i = self.pidx[(v, k['name'])]
                groups[(kind, (v + off) % N, d.items[i].f)].append(i)
        keys = list(groups)
        self.rng.shuffle(keys)
        for key in keys:
            kind, Y, f = key
            ok = {'rs': self._cover_rs, 'obs': self._cover_obs, 'og': self._cover_og}[kind](Y, groups[key])
            if not ok:
                return False
            self.armc = [d.arm_ext(t) for t in range(L)]
        return True

    def _pcands(self, Y, i):
        d = self.d
        kp = d.items[i]; t = kp.f
        front = sx(kp.pos[t], kp.face)
        return {sx(q, -self.sch.DISP[Y][t]) for q in nb(kp.pos[t]) if q != front}

    def _cover_rs(self, Y, pist):
        d = self.d
        cands = {i: self._pcands(Y, i) for i in pist}
        remaining = set(pist)
        allc = set().union(*cands.values())
        while remaining:
            ok = False
            for c in sorted(allc, key=lambda c: (-sum(c in cands[i] for i in remaining), self.rng.random())):
                if not any(c in cands[i] for i in remaining):
                    break
                it = d.src('rs', Y, c, name=f'R{Y}')
                if d.item_errors(it, None, self.armc):
                    continue
                d.add_item(it)
                if [e for e in d.power_errors() if e[3]]:
                    d.pop_last(); continue
                hopts = [sx(q, -self.sch.DISP[Y][0]) for q in nb(it.pos[0])]
                hopts = [h for h in hopts if self.cell_ok(h, Y)]
                if not hopts:
                    d.pop_last(); continue
                self.holders[Y].append(hopts)
                remaining -= {i for i in remaining if c in cands[i]}
                ok = True
                break
            if not ok:
                return False
        return True

    def _cover_obs(self, Y, pist):
        """observer O on body Y facing a glue cell H of Y (H touches pistons), or facing a piston directly."""
        d = self.d
        cands = {i: self._pcands(Y, i) for i in pist}
        remaining = set(pist)
        mine = self.body_cells(Y)
        while remaining:
            opts = []
            # H options
            allc = set().union(*(cands[i] for i in remaining))
            for H in allc:
                cov = {i for i in remaining if H in cands[i]}
                for dd in range(6):
                    O = add(H, tuple(-x for x in DIRS[dd]))
                    opts.append((len(cov) - (0 if H in mine else 0.5), self.rng.random(), 'H', H, O, dd, cov))
            # direct options: observer adjacent to piston facing it
            for i in remaining:
                for O in cands[i]:
                    kp = d.items[i]; t = kp.f
                    Ot = sx(O, self.sch.DISP[Y][t])
                    dd = DIRS.index(tuple(a - b for a, b in zip(kp.pos[t], Ot)))
                    opts.append((1 - 0.7, self.rng.random(), 'D', None, O, dd, {i}))
            opts.sort(key=lambda o: (-o[0], o[1]))
            ok = False
            for sc, _, typ, H, O, dd, cov in opts[:400]:
                n0 = len(d.items)
                if typ == 'H' and H not in self.body_cells(Y):
                    if not self.cell_ok(H, Y):
                        continue
                    d.add_item(d.glue(Y, H))
                it = d.src('obs', Y, O, odir=dd, name=f'O{Y}')
                if d.item_errors(it, None, self.armc):
                    while len(d.items) > n0: d.pop_last()
                    continue
                d.add_item(it)
                pe = d.power_errors()
                bad = [e for e in pe if e[3]]
                if bad:
                    while len(d.items) > n0: d.pop_last()
                    continue
                if typ == 'D':
                    hopts = [sx(q, -self.sch.DISP[Y][0]) for q in nb(it.pos[0])]
                    hopts = [h for h in hopts if self.cell_ok(h, Y)]
                    if not hopts:
                        while len(d.items) > n0: d.pop_last()
                        continue
                    self.holders[Y].append(hopts)
                # check H glue itself is legal vs everything (already) and that cov pistons are now powered
                pw = set()
                for i in cov:
                    if not any(e[1] == d.items[i].name and e[2] == d.items[i].f for e in pe):
                        pw.add(i)
                if not pw:
                    while len(d.items) > n0: d.pop_last()
                    continue
                remaining -= pw
                ok = True
                break
            if not ok:
                return False
        return True

    def rs_feasible(self, Y, pist):
        d = self.d
        self.armc = [d.arm_ext(t) for t in range(self.sch.L)]
        common = set.intersection(*[self._pcands(Y, i) for i in pist])
        for c in common:
            it = d.src('rs', Y, c)
            if d.item_errors(it, None, self.armc):
                continue
            d.add_item(it)
            ok = not [e for e in d.power_errors() if e[3]]
            d.pop_last()
            if ok:
                return True
        return False

    def og_feasible(self, Y, pist):
        d = self.d
        self.armc = [d.arm_ext(t) for t in range(self.sch.L)]
        common = set.intersection(*[self._pcands(Y, i) for i in pist])
        for G in common:
            it = d.src('obs', Y, sx(G, -1), odir=0)
            if d.item_errors(it, None, self.armc):
                continue
            n0 = len(d.items)
            d.add_item(it)
            gz = d.src('glz', Y, G)
            ok = not d.item_errors(gz, None, self.armc)
            if ok:
                d.add_item(gz)
                ok = not [e for e in d.power_errors() if e[3]]
            while len(d.items) > n0: d.pop_last()
            if ok:
                return True
        return False

    def _cover_og(self, Y, pist):
        """observer O (faces +X) pushing glazed G; G hard-powered one slot after Y moves; G touches pistons."""
        d = self.d
        cands = {i: self._pcands(Y, i) for i in pist}
        remaining = set(pist)
        while remaining:
            allc = set().union(*(cands[i] for i in remaining))
            opts = sorted(allc, key=lambda c: (-sum(c in cands[i] for i in remaining), self.rng.random()))
            ok = False
            for G in opts:
                cov = {i for i in remaining if G in cands[i]}
                if not cov:
                    break
                n0 = len(d.items)
                O = sx(G, -1)
                it = d.src('obs', Y, O, odir=0, name=f'O{Y}')
                if d.item_errors(it, None, self.armc):
                    continue
                d.add_item(it)
                gz = d.src('glz', Y, G, name=f'G{Y}')
                if d.item_errors(gz, None, self.armc):
                    while len(d.items) > n0: d.pop_last()
                    continue
                d.add_item(gz)
                pe = d.power_errors()
                if [e for e in pe if e[3]]:
                    while len(d.items) > n0: d.pop_last()
                    continue
                pw = {i for i in cov if not any(e[1] == d.items[i].name and e[2] == d.items[i].f for e in pe)}
                hopts = [sx(q, -self.sch.DISP[Y][0]) for q in nb(it.pos[0]) if q != gz.pos[0]]
                hopts = [h for h in hopts if self.cell_ok(h, Y)]
                if not pw or not hopts:
                    while len(d.items) > n0: d.pop_last()
                    continue
                self.holders[Y].append(hopts)
                remaining -= pw
                ok = True
                break
            if not ok:
                return False
        return True

    def place_carries(self, only=None):
        d = self.d; L = self.sch.L
        if not hasattr(self, 'armc'):
            self.armc = [d.arm_ext(t) for t in range(L)]
        needs = []
        for (i, t), c in d.carry.items():
            if c != d.items[i].victim and (only is None or d.items[i].name[0] in only):
                needs.append((i, t, c))
        for i, t, c in self.rng.sample(needs, len(needs)):
            kp = d.items[i].pos[t]
            if any(q in d.occ[t] and d.occ[t][q] >= 0 and d.items[d.occ[t][q]].cat == 'glue' and d.items[d.occ[t][q]].body == c for q in nb(kp)):
                continue
            mine = self.body_cells(c)
            opts = []
            for q in nb(kp):
                p0 = sx(q, -self.sch.DISP[c][t])
                if p0 in mine or not self.cell_ok(p0, c):
                    continue
                dist = min(sum(abs(a - b) for a, b in zip(p0, m)) for m in mine)
                opts.append((dist, self.rng.random(), p0))
            if not opts:
                return False
            j = getattr(self, 'jitter', 0)
            pick = min(opts) if not j else min(opts, key=lambda o: o[0] + j * self.rng.random())
            d.add_item(d.glue(c, pick[2]))
        return True

    def route(self, cap):
        d = self.d; N = self.sch.N
        for b in self.rng.sample(range(N), N):
            for hopts in self.holders[b]:
                mine = self.body_cells(b)
                if any(h in mine for h in hopts):
                    continue
                hopts = [h for h in hopts if self.cell_ok(h, b)]
                if not hopts:
                    return 'holder'
                hopts.sort(key=lambda h: (min(sum(abs(a - c) for a, c in zip(h, m)) for m in mine), self.rng.random()))
                d.add_item(d.glue(b, hopts[0]))
            while True:
                cells = self.body_cells(b)
                comp = conn(cells)
                if len(comp) == len(cells):
                    break
                targets = cells - comp
                pq = [(0, self.rng.random(), p) for p in comp]
                heapq.heapify(pq)
                dist = {p: 0 for p in comp}; prev = {}; end = None
                lo = [min(p[k] for p in cells) - 3 for k in range(3)]
                hi = [max(p[k] for p in cells) + 3 for k in range(3)]
                okc = {}
                while pq:
                    cost, _, p = heapq.heappop(pq)
                    if cost != dist[p]:
                        continue
                    if p in targets:
                        end = p; break
                    if cost >= cap:
                        continue
                    for q in nb(p):
                        if not all(lo[k] <= q[k] <= hi[k] for k in range(3)):
                            continue
                        if q not in cells:
                            if q not in okc:
                                okc[q] = self.cell_ok(q, b)
                            if not okc[q]:
                                continue
                        nc = cost + (0 if q in cells else 1)
                        if nc < dist.get(q, 1e9):
                            dist[q] = nc; prev[q] = p; heapq.heappush(pq, (nc, self.rng.random(), q))
                if end is None:
                    return 'route'
                p = prev.get(end)
                while p is not None and p not in comp:
                    if p not in cells:
                        d.add_item(d.glue(b, p))
                    p = prev.get(p)
        return None


def rand_place(spec, rng, spread=3, xspread=2):
    N = len(spec['S'])
    gt = tuple(rng.choice('SH') for _ in range(N))
    places = [(rng.randrange(8), (0, 0, 0))]
    for b in range(1, N):
        places.append((rng.randrange(8), (rng.randint(-xspread, xspread), rng.randint(-spread, spread), rng.randint(-spread, spread))))
    tmpl = [rng.choice(spec['templates']) for _ in range(N)]
    return gt, places, tmpl


def relations(spec):
    """(victim offset 0 piston name, relative slot, body offset) pairs that must touch."""
    rel = []
    for k in spec['pistons']:
        for r, off in k['carriers'].items():
            if off:
                rel.append((k['name'], r, off))
        for kind, off in k['power']:
            rel.append((k['name'], k['fire'], off))
    return rel


def inc_place(spec, rng, spread=4, xspread=2, temp=1.0, gt=None):
    N = len(spec['S']); L = len(spec['S'][0])
    gt = gt or tuple(rng.choice('SH') for _ in range(N))
    if 'tmpl_ok' in spec:
        while True:
            tmpl = [rng.choice(spec['templates']) for _ in range(N)]
            if spec['tmpl_ok'](tmpl):
                break
    else:
        tmpl = [rng.choice(spec['templates']) for _ in range(N)]
    places = [None] * N
    places[0] = (rng.randrange(8), (0, 0, 0))
    rels = relations(spec)
    order = list(range(1, N))
    rng.shuffle(order)
    done = [0]
    import math
    for b in order:
        cands = []
        if 'xchain' in spec:
            xs = [spec['xchain'](tmpl)[b]]
        else:
            xs = range(-xspread, xspread + 1)
        offs = [(x, y, z) for x in xs for y in range(-spread, spread + 1) for z in range(-spread, spread + 1)]
        rng.shuffle(offs)
        for si in range(8):
            for off in offs[:200]:
                pl = list(places); pl[b] = (si, off)
                B = Builder(spec, rng, gt, pl, tmpl)
                if B.setup(done + [b]):
                    continue
                d = B.d; sc = 0
                for v in done + [b]:
                    for kn, r, o in rels:
                        y = (v + o) % N
                        if y not in done + [b] or (v != b and y != b):
                            continue
                        i = B.pidx[(v, kn)]; t = (spec['w'][v] + r) % L
                        kp = d.items[i].pos[t]
                        cells = [it.pos[t] for it in d.items if it.cat == 'glue' and it.body == y]
                        sc += min(sum(abs(a - c) for a, c in zip(kp, q)) for q in cells) - 1
                        if kn in spec.get('carry_first', '') and r in [rr for k in spec['pistons'] if k['name'] == kn for rr, oo in k['carriers'].items() if oo == o]:
                            B.armc = [d.arm_ext(tt) for tt in range(L)]
                            if not any(not d.item_errors(d.glue(y, sx(q, -B.sch.DISP[y][t])), None, B.armc) for q in nb(kp)):
                                sc += 15
                for k1, o1, k2, o2, wgt in spec.get('share', []):
                    for v in done + [b]:
                        v2 = (v + o2) % N
                        if v2 not in done + [b]:
                            continue
                        i1 = d.items[B.pidx[(v, k1)]]; i2 = d.items[B.pidx[(v2, k2)]]
                        t = i1.f
                        dd = sum(abs(a - c) for a, c in zip(i1.pos[t], i2.pos[t]))
                        if dd != 2:
                            sc += wgt * abs(dd - 2); continue
                        Y = v  # source body = victim of k1 (P_y on own body)
                        if not B.og_feasible(Y, [B.pidx[(v, k1)], B.pidx[(v2, k2)]]):
                            sc += wgt
                if 'rsgroups' in spec:
                    pl_ = done + [b]
                    for Y in range(N):
                        mem = [((Y + o) % N, kn) for kn, o in spec['rsgroups']]
                        if Y not in pl_ or any(v not in pl_ for v, _ in mem):
                            continue
                        if b != Y and all(v != b for v, _ in mem):
                            continue
                        ps = [B.pidx[m] for m in mem]
                        t = d.items[ps[0]].f
                        dd = max(sum(abs(a - c) for a, c in zip(d.items[p].pos[t], d.items[q].pos[t])) for p in ps for q in ps)
                        if dd > 2:
                            sc += 20 * (dd - 2); continue
                        if not B.rs_feasible(Y, ps):
                            sc += 20
                    # partial groups: pairwise closeness among placed members
                    for Y in range(N):
                        mem = [((Y + o) % N, kn) for kn, o in spec['rsgroups']]
                        pm = [m for m in mem if m[0] in pl_]
                        if len(pm) == len(mem) and Y in pl_:
                            continue
                        if not any(v == b for v, _ in pm) or len(pm) < 2:
                            continue
                        ps = [B.pidx[m] for m in pm]
                        t = d.items[ps[0]].f
                        dd = max(sum(abs(a - c) for a, c in zip(d.items[p].pos[t], d.items[q].pos[t])) for p in ps for q in ps)
                        sc += 20 * max(0, dd - 2)
                cands.append((sc, rng.random(), si, off))
        if not cands:
            return None
        cands.sort()
        ws = [math.exp(-(c[0] - cands[0][0]) / temp) for c in cands]
        pick = rng.choices(cands, weights=ws)[0]
        places[b] = (pick[2], pick[3])
        done.append(b)
    return gt, places, tmpl


def build(spec, seed, place=None, spread=3, xspread=2, cap=10, jitter=0):
    rng = random.Random(seed)
    if place is None:
        place = rand_place(spec, rng, spread, xspread)
    gt, places, tmpl = place
    B = Builder(spec, rng, gt, places, tmpl)
    B.jitter = jitter
    errs = B.setup()
    if errs:
        return None, 'template', errs[:3]
    first = B.spec.get('carry_first')
    if first:
        B.armc = [B.d.arm_ext(t) for t in range(B.sch.L)]
        if not B.place_carries(only=first):
            return None, 'carry1', None
    if not B.place_power():
        return None, 'power', None
    n0 = len(B.d.items)
    for attempt in range(12):
        while len(B.d.items) > n0:
            B.d.pop_last()
        B.jitter = jitter if attempt == 0 else 1.5
        if not B.place_carries():
            r = 'carry'; continue
        r = B.route(cap)
        if not r:
            break
    if r:
        return None, r, None
    errs = B.d.all_errors()
    if errs:
        return None, 'final', errs[:5]
    return B, 'ok', place
