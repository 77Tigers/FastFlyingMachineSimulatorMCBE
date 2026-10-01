"""Place & route A/B generator: each piston module is committed together with the glue paths that
connect its new cells to their bodies (fixed glue colouring per seed)."""
import sys, random
from pathlib import Path
from collections import deque
sys.path.insert(0, str(Path(__file__).resolve().parent))
from abgen333 import nb
from abgen_g import Lay2, lifecycle
from abinc import Inc, module_options, _cost
from abworld import World
from abcheck import check
from abrules import carried_front_conflict


class IncR(Inc):
    def __init__(self, lay, glue):
        super().__init__(lay)
        self.glue = glue

    def forb(self, b, c):
        lay = self.lay
        for k in range(lay.L):
            w = (c[0] + lay.off(b, k), c[1], c[2])
            if w in self.items[k]: return True
            o = self.occ[k].get(w)
            if o is not None and o != b: return True
            mv = lay.moves(b, k)
            if mv and carried_front_conflict(lay, b, w, k, (self.occ[k],), (self.items[k],)): return True
            if mv:
                fit = self.items[k].get((w[0] + 1, w[1], w[2]))
                if fit is not None and not (fit[0] in ('src', 'glazed') and fit[2] == b) and not (fit[0] == 'arm' and fit[1]['kind'] == 'Q' and fit[1]['victim'] == b) and not (fit[0] == 'pist' and k not in (fit[1]['f'] % lay.L, (fit[1]['f'] + 1) % lay.L)): return True
            for n in nb(w):
                it = self.items[k].get(n)
                if it is not None:
                    if it[0] == 'src' and it[2] != b and mv: return True
                    if it[0] == 'pist' and mv:
                        p = it[1]
                        if p['f'] == k and not (p['kind'] == 'P' and p['victim'] == b): return True
                o = self.occ[k].get(n)
                if o is not None and o != b:
                    if self.glue[o] == self.glue[b]: return True
                    if n[1] == w[1] and n[2] == w[2] and mv and lay.moves(o, k): return True
        return False

    def snapshot(self):
        return ({b: dict(v) for b, v in self.req.items()}, [dict(o) for o in self.occ],
                [dict(i) for i in self.items], list(self.pist), list(self.sources), set(self.edges))

    def restore(self, s):
        self.req, self.occ, self.items, self.pist, self.sources, self.edges = s

    def path_to(self, b, start, targets, maxnodes=3000):
        """BFS from start cells over own-new cells / allowed cells until reaching targets."""
        own = self.req[b]
        prev = {c: None for c in start}
        dq = deque(start)
        while dq:
            v = dq.popleft()
            for w in nb(v):
                if w in prev: continue
                if w in targets:
                    path = []; u = v
                    while u is not None and u not in start:
                        path.append(u); u = prev[u]
                    return path
                if w in own:
                    prev[w] = v; dq.append(w); continue
                if self.forb(b, w):
                    prev[w] = False; continue
                prev[w] = v; dq.append(w)
                if len(prev) > maxnodes: return None
        return None

    def trial_route(self, cells, pist, sources):
        ok, edges = self.trial(cells, pist, sources)
        if not ok: return None
        if any(self.glue[a] == self.glue[b] for e in edges for a, b in [tuple(e)]): return None
        snap = self.snapshot()
        before = {b: set(snap[0][b]) for b in snap[0]}
        self.commit(cells, pist, sources, edges)
        byb = {}
        for b, c in cells: byb.setdefault(b, []).append(c)
        added = []; okr = True
        for b, cs in byb.items():
            pend = list(dict.fromkeys(cs))
            conn = set(before[b]) if before[b] else {pend[0]}
            while pend:
                c = pend.pop(0)
                if c in conn: continue
                path = self.path_to(b, [c], conn)
                if path is None: okr = False; break
                for q in path + [c]:
                    if q not in self.req[b]:
                        self.req[b][q] = 1
                        for k in range(self.lay.L): self.occ[k][(q[0] + self.lay.off(b, k), q[1], q[2])] = b
                        added.append((b, q))
                    conn.add(q)
                conn.add(c)
            if not okr: break
        if okr:
            okr = partial_ok(self)
        self.restore(snap)
        if not okr: return None
        return added, edges


def module_reuse(lay, p, gy, gz, xi, src_side, rnd, maxopt=60):
    import itertools
    from abgen_g import choose_contacts
    from abgen333 import piston_traj
    SIDES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    f = p['f']; v = p['victim']
    pp = dict(kind=p['kind'], f=f, victim=v, yz=(gy, gz), xi=xi)
    pp['traj'] = piston_traj(lay, pp)
    face = [(v, (xi + 1 - lay.off(v, f), gy, gz))] if p['kind'] == 'P' else [(v, (xi - 2 - lay.off(v, f + 1), gy, gz))]
    rest = [sd for sd in SIDES if sd != src_side]
    out = []
    for combo in choose_contacts(lay, p, rnd):
        if len(combo) > 3: continue
        for perm in itertools.permutations(rest, len(combo)):
            cells = list(face)
            for (b, r), sd in zip(combo, perm):
                cells.append((b, (xi + r - lay.off(b, f), gy + sd[0], gz + sd[1])))
            out.append((cells, [pp], []))
    rnd.shuffle(out)
    return out[:maxopt]


def est_load(inc):
    lay = inc.lay; L = lay.L
    src = {b: 0 for b in lay.bodies}
    for sd in inc.sources:
        src[sd['body']] += 2 if sd['kind'] == 'obs' else 1
    best = 0
    for k in range(L):
        car = {b: set() for b in lay.bodies}
        for i, p in enumerate(inc.pist):
            if k in (p['f'] % L, (p['f'] + 1) % L): continue
            w = (p['traj'][k], p['yz'][0], p['yz'][1])
            for n in nb(w):
                o = inc.occ[k].get(n)
                if o is not None and lay.moves(o, k): car[o].add(i)
        for b in lay.bodies:
            if lay.moves(b, k):
                best = max(best, len(inc.req[b]) + src[b] + len(car[b]))
    return best


class _View:
    pass


def partial_ok(inc):
    v = _View()
    v.lay = inc.lay; v.glue = inc.glue
    v.cells = {b: set(inc.req[b]) for b in inc.lay.bodies}
    v.pist = inc.pist; v.sources = inc.sources
    v.wcell = lambda b, c, k: (c[0] + inc.lay.off(b, k), c[1], c[2])
    for p in check(v):
        if p[1] in ('uncarried', 'frozenmoved'): continue
        if len(p) > 2 and p[0] == 'disconnected': continue
        if p[0] == 'disconnected': continue
        return False
    return True


def place_route(lay, seed, glue, npos=40, nopt=40, keep=8, win=3, stack=0):
    rnd = random.Random(seed)
    P = lifecycle(lay)
    for p in P:
        p['xi0'] = round(sum(lay.off(b, p['f']) for b in lay.bodies) / len(lay.bodies))
    order = list(range(len(P))); rnd.shuffle(order)
    inc = IncR(lay, glue)
    used = set()
    for i in order:
        p = P[i]
        if not inc.pist:
            poss = [(0, 0)]
        else:
            ys = [q['yz'][0] for q in inc.pist]; zs = [q['yz'][1] for q in inc.pist]
            poss = [(y, z) for y in range(min(ys) - win, max(ys) + win + 1) for z in range(min(zs) - win, max(zs) + win + 1) if stack or (y, z) not in used]

            def near(yz):
                d = [abs(c[1] - yz[0]) + abs(c[2] - yz[1]) for b in [p['victim']] + p['anchors'] for c in inc.req[b]]
                return min(d) if d else 0
            poss.sort(key=lambda yz: (near(yz), rnd.random()))
            poss = poss[:npos]
        cands = []
        for (gy, gz) in poss:
            for dxi in ((0, -1, 1) if not stack else (0, -1, 1, -2, 2, -3, 3)):
                p['xi'] = p['xi0'] + dxi
                for cells, pist, src in module_options(lay, p, gy, gz, rnd, maxopt=nopt):
                    ok, edges = inc.trial(cells, pist, src)
                    if not ok: continue
                    if any(glue[a] == glue[b] for e in edges for a, b in [tuple(e)]): continue
                    cands.append((_cost(inc, cells) + 0.01 * rnd.random(), cells, pist, src, (gy, gz)))
        # reuse existing triggers: piston placed beside an existing source of a suitable body/kind/phase
        from abgen_g import power_options
        SIDES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for sd in list(inc.sources):
            for (kind, b, r) in power_options(lay, p):
                if kind != sd['kind'] or b != sd['body']: continue
                sc = sd['cell'] if kind == 'rs' else sd['target']
                xi = sc[0] - r + lay.off(b, p['f'])
                for side in SIDES:
                    gy, gz = sc[1] - side[0], sc[2] - side[1]
                    if (gy, gz) in used and not stack: continue
                    for cells, pist, src in module_reuse(lay, p, gy, gz, xi, side, rnd):
                        ok, edges = inc.trial(cells, pist, src)
                        if not ok: continue
                        if any(glue[a] == glue[b2] for e in edges for a, b2 in [tuple(e)]): continue
                        cands.append((_cost(inc, cells) - 3 + 0.01 * rnd.random(), cells, pist, src, (gy, gz)))
        cands.sort(key=lambda t: t[0])
        best = None
        for c0, cells, pist, src, yz in cands[:keep]:
            r = inc.trial_route(cells, pist, src)
            if r is None: continue
            added, edges = r
            snap = inc.snapshot()
            inc.commit(cells + added, pist, src, edges)
            tot = (est_load(inc), len(cells) + len(added))
            inc.restore(snap)
            if best is None or tot < best[0]: best = (tot, cells, pist, src, edges, added, yz)
        if best is None: return None, ('place', i, len(cands))
        _, cells, pist, src, edges, added, yz = best
        inc.commit(cells + added, pist, src, edges); used.add(yz)
        if not hasattr(inc, 'terms'): inc.terms = {b: set() for b in lay.bodies}
        for b, c in cells: inc.terms[b].add(c)
    return inc, None


def valid_colorings(lay):
    import itertools
    P = lifecycle(lay)
    for p in P: p['xi'] = round(sum(lay.off(b, p['f']) for b in lay.bodies) / len(lay.bodies))
    rnd = random.Random(0)
    opts = [module_options(lay, p, 0, 0, rnd, maxopt=400) for p in P]
    good = []
    for bits in itertools.product('hs', repeat=len(lay.bodies)):
        glue = dict(zip(lay.bodies, bits))
        okall = True
        for i, p in enumerate(P):
            inc = IncR(lay, glue); found = False
            for cells, pist, src in opts[i]:
                ok, edges = inc.trial(cells, pist, src)
                if ok and not any(glue[a] == glue[b] for e in edges for a, b in [tuple(e)]): found = True; break
            if not found: okall = False; break
        if okall: good.append(glue)
    return good


def generate3(Aw, Bw, outdir, seeds, **kw):
    lay = Lay2(Aw, Bw)
    outdir = Path(outdir); outdir.mkdir(exist_ok=True)
    good = []
    cols = valid_colorings(lay)
    print('valid colourings', len(cols), flush=True)
    for seed in seeds:
        rnd = random.Random(seed * 7 + 1)
        glue = cols[seed % len(cols)]
        inc, err = place_route(lay, seed, glue, **kw)
        if err: print('seed', seed, err, flush=True); continue
        req = {b: dict(inc.req[b]) for b in lay.bodies}
        pist = [dict(kind=p['kind'], f=p['f'], victim=p['victim'], yz=p['yz'], xi=p['xi']) for p in inc.pist]
        wd = World(lay, req, pist, inc.sources, glue=glue)
        pr = check(wd)
        if pr:
            print('seed', seed, 'check', len(pr), pr[:2], flush=True); continue
        f = wd.flyer(limit=250)
        nglue = {b: len(wd.cells[b]) for b in lay.bodies}
        f.save(outdir / ('s%05d.flyer' % seed)); good.append((seed, max(nglue.values()), nglue))
        print('seed', seed, 'maxglue', max(nglue.values()), nglue, flush=True)
    return good


if __name__ == '__main__':
    Aw = sys.argv[1].split(','); Bw = sys.argv[2].split(',')
    kw = {}
    for a in sys.argv[6:]:
        k, v = a.split('='); kw[k] = int(v)
    generate3(Aw, Bw, sys.argv[3], range(int(sys.argv[4]), int(sys.argv[5])), **kw)
