"""Randomised builder for pull-twice mmwmmw flyers (agent F).

Per body V (frame: lx along X, (u,v) in the transverse plane, mapped by one of 8 symmetries):
  glue template: c1 (0,0,0) [A pull / P push], c2 (0,1,1) [B pull / Q push], (0,1,0), (1,1,0), C=(2,1,0),
                 H=(-1,1,0) [hard-powered by own observer -> fires P at w+2 and Q at w+5], C'=(-2,1,0)
  pistons: A sticky lane (0,0) ahead, P normal lane (0,0) behind, B sticky lane (1,1) ahead, Q normal lane (1,1) behind
  observer O next to H facing H.
  Foreign needs: A at w+3, Q at w+3, B at w, P at w -> carried by X or Z (both move then).
  Redstone for A (fires w) and B (fires w+3) rides X (moves w and w+3, waits w-1 and w+2).
"""
import random, heapq, json, sys, itertools
from pathlib import Path
from model import Design, Item, add, sx, nb, DIRS, E, Wd
from sched import S, DISP, W, REL, FIRE, STICKY, piston_x, fire, X_of, Z_of, carrier_kind

SYMS = [lambda u, v: (u, v), lambda u, v: (-u, v), lambda u, v: (u, -v), lambda u, v: (-u, -v),
        lambda u, v: (v, u), lambda u, v: (-v, u), lambda u, v: (v, -u), lambda u, v: (-v, -u)]
TEMPLATE = [(0, 0, 0), (0, 1, 1), (0, 1, 0), (1, 1, 0), (2, 1, 0), (-1, 1, 0), (-2, 1, 0)]
HLOC = (-1, 1, 0)
OOPTS = [((-1, 2, 0), (-1, 0)), ((-1, 1, -1), (0, 1))]   # observer local pos, facing (du,dv) toward H
LANES = dict(A=(0, 0), P=(0, 0), B=(1, 1), Q=(1, 1))


def dir_index(d):
    return DIRS.index(d)


class Builder:
    def __init__(self, rng, gtypes, places, oopt):
        self.rng = rng
        self.d = Design(gtypes)
        self.places = places      # per body: (sym index, (x0,y0,z0))
        self.oopt = oopt
        self.pidx = {}            # (v,k) -> item idx

    def w(self, b, lx, u, v):
        si, (x0, y0, z0) = self.places[b]
        a, c = SYMS[si](u, v)
        return (x0 + lx, y0 + a, z0 + c)

    def setup(self):
        d = self.d
        # pistons first (carry designations for own slots)
        for v in range(3):
            for k in 'ABPQ':
                u, vv = LANES[k]
                base = self.w(v, 0, u, vv)
                pos = [sx(base, piston_x(v, k, t)) for t in range(6)]
                mv = [piston_x(v, k, t + 1) - piston_x(v, k, t) == 1 if t < 5 else piston_x(v, k, 0) + 4 - piston_x(v, k, 5) == 1 for t in range(6)]
                it = Item('piston', pos, mv, name=f'{k}{v}', f=fire(v, k), face=-1 if STICKY[k] else 1, sticky=STICKY[k], victim=v)
                idx = len(d.items)
                for t in range(6):
                    if carrier_kind(v, k, t) == 'V':
                        d.carry[(idx, t)] = v
                d.add_item(it)
                self.pidx[(v, k)] = idx
        for v in range(3):
            for lx, u, vv in TEMPLATE:
                d.add_item(d.glue(v, self.w(v, lx, u, vv)))
            (lx, u, vv), (du, dv) = OOPTS[self.oopt[v]]
            p0 = self.w(v, lx, u, vv)
            q0 = self.w(v, lx, u + du, vv + dv)
            odir = dir_index(tuple(b - a for a, b in zip(p0, q0)))
            pos = [sx(p0, DISP[v][t]) for t in range(6)]
            d.add_item(Item('obs', pos, [bool(S[v][t]) for t in range(6)], body=v, odir=odir, name=f'O{v}'))
        errs = d.all_errors()
        errs = [e for e in errs if e[0] not in ('uncovered', 'nocarrier', 'power')]
        return errs

    def foreign(self, mode):
        """assign foreign carriers. mode: per (v,slot) choose which piston goes to X."""
        d = self.d
        self.needs = []
        for v in range(3):
            X, Z = X_of(v), Z_of(v)
            w = W[v]
            for t, pair in ((w % 6, ('B', 'P')), ((w + 3) % 6, ('A', 'Q'))):
                # pushers must go to Z: X also moves next slot, when the pusher sits behind V's contact cell
                first = True if mode != 'rand' else self.rng.random() < 0.5
                kx, kz = pair if first else pair[::-1]
                for k, c in ((kx, X), (kz, Z)):
                    i = self.pidx[(v, k)]
                    d.carry[(i, t)] = c
                    self.needs.append((i, t, c))

    def cell_ok(self, p0, b):
        it = self.d.glue(b, p0)
        return not self.d.item_errors(it, None, self.armc)

    def place_rs(self):
        d = self.d
        self.armc = [d.arm_ext(t) for t in range(6)]
        self.holders = {b: [] for b in range(3)}
        for v in range(3):
            X = X_of(v)
            cands = {}
            for k, t in (('A', W[v]), ('B', (W[v] + 3) % 6)):
                i = self.pidx[(v, k)]
                kp = d.items[i].pos[t]
                front = sx(kp, -1)
                cs = set()
                for q in nb(kp):
                    if q == front:
                        continue
                    cs.add(sx(q, -DISP[X][t]))
                cands[k] = cs
            opts = [[c] for c in cands['A'] & cands['B']]
            singles = [[a, b] for a in cands['A'] for b in cands['B'] if a != b]
            self.rng.shuffle(opts); self.rng.shuffle(singles)
            placed = False
            for combo in opts + singles[:60]:
                added = []
                ok = True
                for c in combo:
                    pos = [sx(c, DISP[X][t]) for t in range(6)]
                    it = Item('rs', pos, [bool(S[X][t]) for t in range(6)], body=X, name=f'R{X}for{v}')
                    if d.item_errors(it, None, self.armc):
                        ok = False; break
                    added.append(d.add_item(it))
                if ok:
                    pe = [e for e in d.power_errors() if e[1][0] in 'AB']
                    # only check stickies here; P/Q via H checked later too
                    pe = d.power_errors()
                    if not any(e for e in pe if not self._expected_missing(e)):
                        # holder options
                        hs = []
                        for a in added:
                            hopts = [sx(q, -DISP[X][0]) for q in nb(d.items[a].pos[0])]
                            hopts = [h for h in hopts if self.cell_ok(h, X)]
                            if not hopts:
                                ok = False
                            hs.append(hopts)
                        if ok:
                            self.holders[X] += hs
                            placed = True
                            break
                for a in reversed(added):
                    self._pop(a)
            if not placed:
                return False
        return True

    def _expected_missing(self, e):
        # power errors that are "missing power" for pistons whose source is not yet placed
        _, name, t, got = e
        if got:
            return False
        k, v = name[0], int(name[1:])
        if k in 'AB':
            # missing only if this body's R not placed yet
            return not any(it.cat == 'rs' and it.name.endswith(f'for{v}') for it in self.d.items)
        return False

    def _pop(self, idx):
        d = self.d
        assert idx == len(d.items) - 1
        it = d.items.pop()
        for t in range(6):
            if d.occ[t].get(it.pos[t]) == idx:
                del d.occ[t][it.pos[t]]

    def body_cells(self, b):
        return {it.pos[0] for it in self.d.items if it.cat == 'glue' and it.body == b}

    def add_glue(self, b, p0):
        self.d.add_item(self.d.glue(b, p0))

    def place_carries(self):
        d = self.d
        for i, t, c in self.rng.sample(self.needs, len(self.needs)):
            kp = d.items[i].pos[t]
            # already covered?
            if any(q in d.occ[t] and d.occ[t][q] >= 0 and d.items[d.occ[t][q]].cat == 'glue' and d.items[d.occ[t][q]].body == c for q in nb(kp)):
                continue
            mine = self.body_cells(c)
            opts = []
            for q in nb(kp):
                p0 = sx(q, -DISP[c][t])
                if p0 in mine or not self.cell_ok(p0, c):
                    continue
                dist = min(sum(abs(a - b) for a, b in zip(p0, m)) for m in mine)
                opts.append((dist, self.rng.random(), p0))
            if not opts:
                return False
            opts.sort()
            j = getattr(self, 'jitter', 0)
            pick = opts[0] if not j else min(opts, key=lambda o: o[0] + j * self.rng.random())
            self.add_glue(c, pick[2])
        return True

    def route(self, cap):
        d = self.d
        for b in self.rng.sample(range(3), 3):
            # holders: choose cheapest holder per R lazily: add best holder now
            for hopts in self.holders[b]:
                mine = self.body_cells(b)
                if any(h in mine for h in hopts):
                    continue
                hopts = [h for h in hopts if self.cell_ok(h, b)]
                if not hopts:
                    return 'holder'
                hopts.sort(key=lambda h: (min(sum(abs(a - c) for a, c in zip(h, m)) for m in mine), self.rng.random()))
                self.add_glue(b, hopts[0])
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
                        self.add_glue(b, p)
                    p = prev.get(p)
        return None


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


def rand_place(rng, spread=4, xspread=2):
    gt = rng.choice([('S', 'H', 'S'), ('S', 'S', 'H'), ('H', 'S', 'S')])
    places = [(rng.randrange(8), (0, 0, 0))]
    for b in (1, 2):
        places.append((rng.randrange(8), (rng.randint(-xspread, xspread), rng.randint(-spread, spread), rng.randint(-spread, spread))))
    oopt = [rng.randrange(2) for _ in range(3)]
    return gt, places, oopt


def build(seed, spread=4, xspread=2, cap=12, place=None, jitter=0):
    rng = random.Random(seed)
    if place is None:
        place = rand_place(rng, spread, xspread)
    gt, places, oopt = place
    B = Builder(rng, gt, places, oopt)
    B.jitter = jitter
    errs = B.setup()
    if errs:
        return None, 'template', errs[:3]
    B.foreign('fixed')
    B.armc = [B.d.arm_ext(t) for t in range(6)]
    if not B.place_rs():
        return None, 'rs', None
    if not B.place_carries():
        return None, 'carry', None
    r = B.route(cap)
    if r:
        return None, r, None
    errs = B.d.all_errors()
    if errs:
        return None, 'final', errs[:5]
    return B, 'ok', dict(gtypes=gt, places=places, oopt=oopt)


if __name__ == '__main__':
    import collections
    out = Path(sys.argv[1]); out.mkdir(exist_ok=True, parents=True)
    n0, n1 = int(sys.argv[2]), int(sys.argv[3])
    maxload = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    stats = collections.Counter(); rows = []
    for seed in range(n0, n1):
        B, why, info = build(seed)
        stats[why] += 1
        if B is None:
            if why == 'final':
                print(seed, info)
            continue
        L = B.d.max_load()
        if L > maxload:
            stats['overload'] += 1; continue
        name = f's{seed:06d}_L{L}'
        f = B.d.to_flyer(limit=L)
        f.translate(20, 20, 20)
        f.save(out / f'{name}.flyer')
        rows.append(dict(name=name, load=L, info=info, glue=[len(B.body_cells(b)) for b in range(3)]))
        print(name, L, [len(B.body_cells(b)) for b in range(3)], flush=True)
    print(dict(stats))
    (out / f'manifest_{n0}_{n1}.json').write_text(json.dumps(rows, indent=1))


def route2(self, cap=10, order=None):
    """group-Steiner routing: each need = set of legal carry cells; R holders = legal neighbours."""
    d = self.d
    bodies = order or self.rng.sample(range(3), 3)
    for b in bodies:
        # groups for b
        groups = []
        for i, t, c in self.needs:
            if c != b:
                continue
            kp = d.items[i].pos[t]
            groups.append(('need', [sx(q, -DISP[b][t]) for q in nb(kp)]))
        for it in d.items:
            if it.cat == 'rs' and it.body == b:
                groups.append(('hold', list(nb(it.pos[0]))))
        while True:
            cells = self.body_cells(b)
            open_g = [g for g in groups if not any(c in cells for c in g[1])]
            if not open_g:
                break
            targets = {}
            for gi, g in enumerate(open_g):
                for c in g[1]:
                    targets.setdefault(c, []).append(gi)
            pq = [(0, self.rng.random(), p) for p in cells]
            heapq.heapify(pq)
            dist = {p: 0 for p in cells}; prev = {}; end = None
            okc = {}
            while pq:
                cost, _, p = heapq.heappop(pq)
                if cost != dist[p]:
                    continue
                if p in targets and p not in cells:
                    end = p; break
                if cost >= cap:
                    continue
                for q in nb(p):
                    if q in cells:
                        continue
                    if q not in okc:
                        okc[q] = self.cell_ok(q, b)
                    if not okc[q]:
                        continue
                    nc = cost + 1 + self.rng.random() * getattr(self, 'jitter', 0) * 0.3
                    if nc < dist.get(q, 1e9):
                        dist[q] = nc; prev[q] = p; heapq.heappush(pq, (nc, self.rng.random(), q))
            if end is None:
                return 'route'
            path = []
            p = end
            while p not in cells:
                path.append(p); p = prev[p]
            for p in reversed(path):
                if not self.cell_ok(p, b):
                    return 'route_late'
                self.add_glue(b, p)
    return None


Builder.route2 = route2


def build2(seed, place, jitter=0.0, cap=10):
    rng = random.Random(seed)
    gt, places, oopt = place
    B = Builder(rng, gt, places, oopt)
    B.jitter = jitter
    errs = B.setup()
    if errs:
        return None, 'template', errs[:3]
    B.foreign('fixed')
    B.armc = [B.d.arm_ext(t) for t in range(6)]
    if not B.place_rs():
        return None, 'rs', None
    r = B.route2(cap)
    if r:
        return None, r, None
    errs = B.d.all_errors()
    if errs:
        return None, 'final', errs[:5]
    return B, 'ok', dict(gtypes=gt, places=places, oopt=oopt)


def strip_body(d, B, b):
    """new Design without the non-template glue of body b"""
    import model
    tmpl = {B.w(b, *c) for c in TEMPLATE}
    keep = [i for i, it in enumerate(d.items) if not (it.cat == 'glue' and it.body == b and it.pos[0] not in tmpl)]
    nd = model.Design(d.gtypes)
    remap = {}
    for i in keep:
        remap[i] = len(nd.items); nd.items.append(d.items[i])
    for (i, t), c in d.carry.items():
        if i in remap:
            nd.carry[(remap[i], t)] = c
    for i, it in enumerate(nd.items):
        for t in range(6):
            nd.occ[t][it.pos[t]] = i
        if it.cat == 'piston':
            t = (it.f + 1) % 6
            nd.occ[t][sx(it.pos[t], it.face)] = -1 - i
    # needs indices: pistons are first items and never removed, so indices unchanged
    return nd


def improve(B, rounds=3, tries=4, rng=None):
    """rip-up & reroute each body; keeps the best (max load, total glue)."""
    import model
    rng = rng or random.Random(0)
    def score(d):
        return (d.max_load(), sum(1 for it in d.items if it.cat == 'glue'))
    best = model.trim(B.d, rng)
    bs = score(best)
    for _ in range(rounds):
        for b in rng.sample(range(3), 3):
            for _t in range(tries):
                B.d = strip_body(best, B, b)
                B.armc = [B.d.arm_ext(t) for t in range(6)]
                B.jitter = 1.5
                if B.route2(10, order=[b]):
                    continue
                if B.d.all_errors():
                    continue
                cand = model.trim(B.d, rng)
                s = score(cand)
                if s < bs:
                    best, bs = cand, s
    B.d = best
    return best
