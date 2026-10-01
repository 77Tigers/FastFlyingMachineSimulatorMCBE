"""Incremental, hazard-checked placement of A/B piston modules (generic words, L - D == 2)."""
import sys, itertools, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from abgen333 import nb, piston_traj
from abgen_g import Lay2, lifecycle, choose_contacts, power_options, rel
from abworld import World
from abcheck import check
from abrules import carried_front_conflict

SIDES = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Inc:
    def __init__(self, lay):
        self.lay = lay; L = lay.L
        self.items = [dict() for _ in range(L)]   # world -> tag
        self.occ = [dict() for _ in range(L)]     # world -> body
        self.req = {b: {} for b in lay.bodies}
        self.pist = []; self.sources = []
        self.edges = set()

    # --- trial evaluation ------------------------------------------------
    def trial(self, cells, pist, sources):
        """cells: list of (body, bframe cell). pist: new piston dicts (with traj). sources: new source dicts.
        Returns (ok, new_edges)."""
        lay = self.lay; L = lay.L
        items = [dict() for _ in range(L)]
        for p in pist:
            for k in range(L):
                items[k][(p['traj'][k], p['yz'][0], p['yz'][1])] = ('pist', p)
            f = p['f']; k1 = (f + 1) % L
            dx = 1 if p['kind'] == 'P' else -1
            items[k1][(p['traj'][k1] + dx, p['yz'][0], p['yz'][1])] = ('arm', p)
            if p['kind'] == 'Q':
                items[f].setdefault((p['traj'][f] - 1, p['yz'][0], p['yz'][1]), ('armclr', p))
        for sd in sources:
            b = sd['body']
            for k in range(L):
                c = sd['cell']; items[k][(c[0] + lay.off(b, k), c[1], c[2])] = ('src', sd, b)
                if sd['kind'] == 'obs':
                    t = sd['target']; items[k][(t[0] + lay.off(b, k), t[1], t[2])] = ('glazed', sd, b)
        occ = [dict() for _ in range(L)]
        for b, c in cells:
            for k in range(L):
                w = (c[0] + lay.off(b, k), c[1], c[2])
                if occ[k].get(w, b) != b: return False, None
                occ[k][w] = b
        new_edges = set()
        for k in range(L):
            # item/item and item/cell overlaps
            for w, it in items[k].items():
                if w in self.items[k] or w in self.occ[k] or w in occ[k]: return False, None
            for w, b in occ[k].items():
                if w in self.items[k]: return False, None
                o = self.occ[k].get(w)
                if o is not None and o != b: return False, None
            # hazards: glue (old+new) vs items (old+new)
            def haz(w, b, itemmaps):
                mv = lay.moves(b, k)
                if mv:
                    for im in itemmaps:
                        fit = im.get((w[0] + 1, w[1], w[2]))
                        if fit is not None and not (fit[0] in ('src', 'glazed') and fit[2] == b) and not (fit[0] == 'arm' and fit[1]['kind'] == 'Q' and fit[1]['victim'] == b) and not (fit[0] == 'pist' and k not in (fit[1]['f'] % lay.L, (fit[1]['f'] + 1) % lay.L)): return True
                for n in nb(w):
                    for im in itemmaps:
                        it = im.get(n)
                        if it is None: continue
                        if it[0] == 'src' and it[2] != b and mv: return True
                        if it[0] == 'pist' and mv:
                            p = it[1]
                            if p['f'] == k and not (p['kind'] == 'P' and p['victim'] == b): return True
                return False
            for w, b in occ[k].items():
                if haz(w, b, (self.items[k], items[k])): return False, None
                if lay.moves(b, k) and carried_front_conflict(lay, b, w, k, (occ[k], self.occ[k]), (items[k], self.items[k])): return False, None
            if items[k]:
                for w, b in self.occ[k].items():
                    if lay.moves(b, k) and carried_front_conflict(lay, b, w, k, (occ[k], self.occ[k]), (items[k], self.items[k])): return False, None
            if items[k]:
                for w, b in self.occ[k].items():
                    if haz(w, b, (items[k],)): return False, None
            # glue adjacency edges / obstruction
            for w, b in occ[k].items():
                for n in nb(w):
                    o = occ[k].get(n) or self.occ[k].get(n)
                    if o is None or o == b: continue
                    if n[1] == w[1] and n[2] == w[2] and lay.moves(b, k) and lay.moves(o, k): return False, None
                    new_edges.add(frozenset((b, o)))
        if not self.bipartite(self.edges | new_edges): return False, None
        if not self.power_ok(pist, sources): return False, None
        return True, new_edges

    def _powered(self, sd, k):
        lay = self.lay; b = sd['body']
        if sd['kind'] == 'rs':
            c = sd['cell']
        else:
            if not lay.moves(b, k - 1): return set()
            c = sd['target']
        w = (c[0] + lay.off(b, k), c[1], c[2])
        return set(nb(w))

    def power_ok(self, newp, news):
        L = self.lay.L
        allp = self.pist + list(newp); alls = self.sources + list(news)
        for k in range(L):
            for sd in alls:
                isnew_s = any(sd is x for x in news)
                pc = self._powered(sd, k)
                if not pc: continue
                for p in allp:
                    if not isnew_s and not any(p is x for x in newp): continue
                    if (p['traj'][k], p['yz'][0], p['yz'][1]) in pc and p['f'] != k:
                        return False
        return True

    def bipartite(self, edges):
        col = {}
        adj = {}
        for e in edges:
            a, b = tuple(e); adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
        for s in adj:
            if s in col: continue
            col[s] = 0; st = [s]
            while st:
                u = st.pop()
                for v in adj[u]:
                    if v not in col: col[v] = 1 - col[u]; st.append(v)
                    elif col[v] == col[u]: return False
        return True

    def commit(self, cells, pist, sources, edges):
        lay = self.lay; L = lay.L
        for b, c in cells:
            self.req[b][c] = 1
            for k in range(L): self.occ[k][(c[0] + lay.off(b, k), c[1], c[2])] = b
        for p in pist:
            self.pist.append(p)
            for k in range(L):
                self.items[k][(p['traj'][k], p['yz'][0], p['yz'][1])] = ('pist', p)
            f = p['f']; k1 = (f + 1) % L
            dx = 1 if p['kind'] == 'P' else -1
            self.items[k1][(p['traj'][k1] + dx, p['yz'][0], p['yz'][1])] = ('arm', p)
            if p['kind'] == 'Q':
                self.items[f].setdefault((p['traj'][f] - 1, p['yz'][0], p['yz'][1]), ('armclr', p))
        for sd in sources:
            self.sources.append(sd)
            b = sd['body']
            for k in range(L):
                c = sd['cell']; self.items[k][(c[0] + lay.off(b, k), c[1], c[2])] = ('src', sd, b)
                if sd['kind'] == 'obs':
                    t = sd['target']; self.items[k][(t[0] + lay.off(b, k), t[1], t[2])] = ('glazed', sd, b)
        self.edges |= edges

    def coloring(self, rnd):
        col = {}
        adj = {b: [] for b in self.lay.bodies}
        for e in self.edges:
            a, b = tuple(e); adj[a].append(b); adj[b].append(a)
        for s in self.lay.bodies:
            if s in col: continue
            col[s] = rnd.choice('hs'); st = [s]
            while st:
                u = st.pop()
                for v in adj[u]:
                    if v not in col: col[v] = 'h' if col[u] == 's' else 's'; st.append(v)
        return col


def module_options(lay, p, gy, gz, rnd, maxopt=400):
    """Yield (cells, piston, sources) placements for one piston at grid (gy, gz)."""
    f = p['f']; v = p['victim']; xi = p['xi']
    sols = choose_contacts(lay, p, rnd)
    pw = power_options(lay, p)
    pp = dict(kind=p['kind'], f=f, victim=v, yz=(gy, gz), xi=xi)
    pp['traj'] = piston_traj(lay, pp)
    face = []
    if p['kind'] == 'P':
        face.append((v, (xi + 1 - lay.off(v, f), gy, gz)))
    else:
        face.append((v, (xi - 2 - lay.off(v, f + 1), gy, gz)))
    out = []
    for combo in sols:
        for perm in itertools.permutations(SIDES, len(combo) + 1):
            for pwc in pw:
                cells = list(face)
                for (b, r), s in zip(combo, perm):
                    cells.append((b, (xi + r - lay.off(b, f), gy + s[0], gz + s[1])))
                s = perm[-1]
                kind, b, r = pwc
                line = (gy + s[0], gz + s[1])
                outward = (gy + 2 * s[0], gz + 2 * s[1])
                bx = xi + r - lay.off(b, f)
                if kind == 'rs':
                    src = dict(kind='rs', body=b, cell=(bx, line[0], line[1]), f=f)
                    cells.append((b, (bx, outward[0], outward[1])))
                else:
                    src = dict(kind='obs', body=b, cell=(bx - 1, line[0], line[1]), target=(bx, line[0], line[1]), f=f)
                    cells.append((b, (bx - 1, outward[0], outward[1])))
                out.append((cells, [pp], [src]))
    rnd.shuffle(out)
    return out[:maxopt]


def place_all(lay, seed, grid_w=5, spacing=4):
    rnd = random.Random(seed)
    P = lifecycle(lay)
    for p in P:
        p['xi'] = round(sum(lay.off(b, p['f']) for b in lay.bodies) / len(lay.bodies)) + rnd.choice((-1, 0, 0, 1))
    order = list(range(len(P))); rnd.shuffle(order)
    inc = Inc(lay)
    slots = [((n // grid_w) * spacing, (n % grid_w) * spacing) for n in range(len(P) + 6)]
    free = slots[:]
    for i in order:
        p = P[i]
        placed = False
        cand_slots = free[:]
        rnd.shuffle(cand_slots)
        for (gy, gz) in cand_slots[:6]:
            for cells, pist, src in module_options(lay, p, gy, gz, rnd):
                ok, edges = inc.trial(cells, pist, src)
                if ok:
                    inc.commit(cells, pist, src, edges); placed = True; break
            if placed:
                free.remove((gy, gz)); break
        if not placed: return None, ('place', i)
    return inc, None


def generate(Aw, Bw, outdir, seeds, grid_w=5, spacing=4):
    lay = Lay2(Aw, Bw)
    outdir = Path(outdir); outdir.mkdir(exist_ok=True)
    stats = {}; good = []
    for seed in seeds:
        inc, err = place_all(lay, seed, grid_w, spacing)
        if err: stats['place'] = stats.get('place', 0) + 1; continue
        rnd = random.Random(seed)
        col = inc.coloring(rnd)
        req = {b: dict(inc.req[b]) for b in lay.bodies}
        pist = [dict(kind=p['kind'], f=p['f'], victim=p['victim'], yz=p['yz'], xi=p['xi']) for p in inc.pist]
        wd = World(lay, req, pist, inc.sources, glue=col)
        bad = False
        bodies = list(lay.bodies); rnd.shuffle(bodies)
        for b in bodies:
            t, why = wd.route(b, rnd)
            if t is None:
                k = 'route_' + str(why[0][1] if isinstance(why[0][1], str) else why[0][0]); stats[k] = stats.get(k, 0) + 1; bad = True; break
        if bad: continue
        pr = check(wd)
        if pr:
            stats['check'] = stats.get('check', 0) + 1
            if len(pr) < stats.get('bestn', 999): stats['bestn'] = len(pr); stats['best'] = (seed, pr[:4])
            continue
        f = wd.flyer(limit=100)
        nglue = {b: len(wd.cells[b]) for b in lay.bodies}
        f.save(outdir / ('s%05d.flyer' % seed)); good.append((seed, nglue))
    print('good', len(good), {k: v for k, v in stats.items() if k not in ('best',)})
    print('best', stats.get('best'))
    for g in good[:10]: print(g)
    return good


if __name__ == '__main__':
    Aw = sys.argv[1].split(','); Bw = sys.argv[2].split(',')
    generate(Aw, Bw, sys.argv[3], range(int(sys.argv[4]), int(sys.argv[5])))


def _cost(inc, cells):
    tot = 0
    for b, c in cells:
        ex = inc.req[b]
        if not ex: continue
        tot += min(abs(c[0] - e[0]) + abs(c[1] - e[1]) + abs(c[2] - e[2]) for e in ex)
    return tot


def place_cluster(lay, seed, npos=30, nopt=60, xi_jit=1):
    rnd = random.Random(seed)
    P = lifecycle(lay)
    for p in P:
        p['xi0'] = round(sum(lay.off(b, p['f']) for b in lay.bodies) / len(lay.bodies))
    order = list(range(len(P))); rnd.shuffle(order)
    inc = Inc(lay)
    used = set()
    for n, i in enumerate(order):
        p = P[i]
        best = None
        if not inc.pist:
            poss = [(0, 0)]
        else:
            ys = [q['yz'][0] for q in inc.pist]; zs = [q['yz'][1] for q in inc.pist]
            poss = [(y, z) for y in range(min(ys) - 3, max(ys) + 4) for z in range(min(zs) - 3, max(zs) + 4)
                    if (y, z) not in used]
            # prefer near the bodies involved: sort by distance to existing cells of victim/anchors
            def near(yz):
                bs = [p['victim']] + p['anchors']
                d = []
                for b in bs:
                    for c in inc.req[b]:
                        d.append(abs(c[1] - yz[0]) + abs(c[2] - yz[1]))
                return min(d) if d else 0
            poss.sort(key=lambda yz: (near(yz), rnd.random()))
            poss = poss[:npos]
        for (gy, gz) in poss:
            for dxi in sorted({0, -xi_jit, xi_jit}):
                p['xi'] = p['xi0'] + dxi
                for cells, pist, src in module_options(lay, p, gy, gz, rnd, maxopt=nopt):
                    ok, edges = inc.trial(cells, pist, src)
                    if not ok: continue
                    c = _cost(inc, cells) + 0.01 * rnd.random()
                    if best is None or c < best[0]: best = (c, cells, pist, src, edges, (gy, gz))
        if best is None: return None, ('place', i)
        inc.commit(*best[1:5]); used.add(best[5])
    return inc, None


def generate2(Aw, Bw, outdir, seeds, **kw):
    lay = Lay2(Aw, Bw)
    outdir = Path(outdir); outdir.mkdir(exist_ok=True)
    stats = {}; good = []
    for seed in seeds:
        inc, err = place_cluster(lay, seed, **kw)
        if err: stats['place'] = stats.get('place', 0) + 1; continue
        rnd = random.Random(seed)
        col = inc.coloring(rnd)
        req = {b: dict(inc.req[b]) for b in lay.bodies}
        pist = [dict(kind=p['kind'], f=p['f'], victim=p['victim'], yz=p['yz'], xi=p['xi']) for p in inc.pist]
        wd = World(lay, req, pist, inc.sources, glue=col)
        bad = False
        bodies = sorted(lay.bodies, key=lambda b: -len(req[b]))
        for b in bodies:
            t, why = wd.route(b, rnd)
            if t is None:
                k = 'route'; stats[k] = stats.get(k, 0) + 1; bad = True; break
        if bad: continue
        pr = check(wd)
        if pr:
            stats['check'] = stats.get('check', 0) + 1
            if len(pr) < stats.get('bestn', 999): stats['bestn'] = len(pr); stats['best'] = (seed, pr[:4])
            continue
        f = wd.flyer(limit=250)
        nglue = {b: len(wd.cells[b]) for b in lay.bodies}
        f.save(outdir / ('s%05d.flyer' % seed)); good.append((seed, max(nglue.values()), nglue))
        print('seed', seed, 'maxglue', max(nglue.values()), flush=True)
    print('good', len(good), {k: v for k, v in stats.items() if k not in ('best',)})
    print('best', stats.get('best'))
    return good
