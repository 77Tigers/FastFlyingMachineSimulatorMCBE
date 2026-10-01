"""Faster World for A/B generators: per-slot occupancy maps, glue colouring, greedy Steiner routing."""
import sys
from pathlib import Path
from collections import deque
sys.path.insert(0, str(Path(__file__).resolve().parent))
from abgen333 import nb, piston_traj
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind


class World:
    def __init__(self, lay, req, pist, sources, glue=None):
        self.lay = lay; self.req = req; self.pist = pist; self.sources = sources
        L = lay.L
        for p in pist: p['traj'] = piston_traj(lay, p)
        self.items = [dict() for _ in range(L)]
        for i, p in enumerate(pist):
            for k in range(L):
                self.items[k][(p['traj'][k], p['yz'][0], p['yz'][1])] = ('pist', i)
            f = p['f']; k1 = (f + 1) % L
            dx = 1 if p['kind'] == 'P' else -1
            self.items[k1][(p['traj'][k1] + dx, p['yz'][0], p['yz'][1])] = ('arm', i)
            if p['kind'] == 'Q':
                self.items[f].setdefault((p['traj'][f] - 1, p['yz'][0], p['yz'][1]), ('armclr', i))
        for j, sd in enumerate(sources):
            b = sd['body']
            for k in range(L):
                c = sd['cell']
                self.items[k][(c[0] + lay.off(b, k), c[1], c[2])] = ('src', j, b)
                if sd['kind'] == 'obs':
                    t = sd['target']
                    self.items[k][(t[0] + lay.off(b, k), t[1], t[2])] = ('glazed', j, b)
        self.glue = glue or {b: ('h' if b[0] == 'A' else 's') for b in lay.bodies}
        self.cells = {b: set() for b in lay.bodies}
        self.occ = [dict() for _ in range(L)]
        for b in lay.bodies:
            self.add(b, req[b])

    def add(self, b, cells):
        for c in cells:
            self.cells[b].add(c)
            for k in range(self.lay.L):
                self.occ[k][(c[0] + self.lay.off(b, k), c[1], c[2])] = b

    def wcell(self, b, c, k):
        return (c[0] + self.lay.off(b, k), c[1], c[2])

    def forbidden(self, b, c):
        lay = self.lay; L = lay.L
        for k in range(L):
            w = (c[0] + lay.off(b, k), c[1], c[2])
            if w in self.items[k]: return 'item'
            o = self.occ[k].get(w)
            if o is not None and o != b: return 'overlap'
            mv = lay.moves(b, k)
            if mv:
                fit = self.items[k].get((w[0] + 1, w[1], w[2]))
                if fit is not None and not (fit[0] in ('src', 'glazed') and fit[2] == b) and not (fit[0] == 'arm' and self.pist[fit[1]]['kind'] == 'Q' and self.pist[fit[1]]['victim'] == b) and not (fit[0] == 'pist' and k not in (self.pist[fit[1]]['f'] % L, (self.pist[fit[1]]['f'] + 1) % L)): return 'front'
            for n in nb(w):
                it = self.items[k].get(n)
                if it is not None:
                    if it[0] == 'src' and it[2] != b and mv: return 'srcadj'
                    if it[0] == 'pist' and mv:
                        p = self.pist[it[1]]
                        if p['f'] == k and not (p['kind'] == 'P' and p['victim'] == b): return 'exthaz'
                o = self.occ[k].get(n)
                if o is not None and o != b:
                    if self.glue[o] == self.glue[b]: return 'sameglue'
                    if n[1] == w[1] and n[2] == w[2] and mv and lay.moves(o, k): return 'obstruct'
        return None

    def route(self, b, rnd, pad=3, limit_nodes=60000):
        terms = list(self.req[b])
        bad = [(t, self.forbidden(b, t)) for t in terms]
        bad = [x for x in bad if x[1]]
        if bad: return None, bad
        allc = [c for bb in self.lay.bodies for c in self.cells[bb]] + [(p['traj'][0], p['yz'][0], p['yz'][1]) for p in self.pist]
        lo = [min(c[a] for c in allc) - pad for a in range(3)]
        hi = [max(c[a] for c in allc) + pad for a in range(3)]
        tree = {terms[0]}
        rest = set(terms[1:])
        cache = {}

        def ok(c):
            r = cache.get(c)
            if r is None:
                r = all(lo[a] <= c[a] <= hi[a] for a in range(3)) and self.forbidden(b, c) is None
                cache[c] = r
            return r
        while rest:
            prev = {x: None for x in tree}
            dq = deque(tree)
            hit = None
            while dq:
                v = dq.popleft()
                if v in rest: hit = v; break
                ns = nb(v); rnd.shuffle(ns)
                for w in ns:
                    if w in prev: continue
                    if w in rest or ok(w):
                        prev[w] = v; dq.append(w)
                if len(prev) > limit_nodes: break
            if hit is None: return None, [('unreachable', list(rest)[:3])]
            v = hit; path = []
            while v is not None and v not in tree:
                path.append(v); tree.add(v); v = prev[v]
            rest -= tree
            self.add(b, path)
        return tree, []

    def flyer(self, limit=60, rng=5):
        lay = self.lay; L = lay.L
        f = Flyer(rng_state=rng, push_limit=limit)
        for b in lay.bodies:
            for c in self.cells[b]:
                f.set(c, Block(Kind.HONEY if self.glue[b] == 'h' else Kind.SLIME))
        for i, p in enumerate(self.pist):
            st = 2 if (p['f'] + 1) % L == 0 else 0
            c = (p['traj'][0], p['yz'][0], p['yz'][1])
            f.set(c, Block.piston(0 if p['kind'] == 'P' else 1, sticky=(p['kind'] == 'Q'), state=st))
            if st:
                dx = 1 if p['kind'] == 'P' else -1
                f.set((c[0] + dx, c[1], c[2]), Block(Kind.PISTON_ARM))
        for j, sd in enumerate(self.sources):
            if sd['kind'] == 'obs':
                f.set(sd['cell'], Block.observer(0, powered=lay.moves(sd['body'], L - 1)))
                f.set(sd['target'], Block(Kind.GLAZED_TERRACOTTA))
            else:
                f.set(sd['cell'], Block(Kind.REDSTONE_BLOCK))
        return f


def color_glue(lay, req, rnd):
    """2-colour bodies so that bodies whose required cells touch (any slot) differ. None if impossible."""
    L = lay.L
    occ = [dict() for _ in range(L)]
    for b in lay.bodies:
        for c in req[b]:
            for k in range(L):
                occ[k][(c[0] + lay.off(b, k), c[1], c[2])] = b
    edges = set()
    for k in range(L):
        for w, b in occ[k].items():
            for n in nb(w):
                o = occ[k].get(n)
                if o is not None and o != b: edges.add(frozenset((b, o)))
    col = {}
    bodies = list(lay.bodies); rnd.shuffle(bodies)
    for s in bodies:
        if s in col: continue
        col[s] = rnd.choice('hs')
        st = [s]
        while st:
            u = st.pop()
            for e in edges:
                if u in e:
                    v = next(iter(e - {u}))
                    want = 's' if col[u] == 'h' else 'h'
                    if v not in col: col[v] = want; st.append(v)
                    elif col[v] != want: return None, edges
    return col, edges
