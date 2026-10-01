"""Routing + flyer assembly for abgen333 layouts (generic over Lay words)."""
import sys, random
from pathlib import Path
from collections import deque
sys.path.insert(0, str(Path(__file__).resolve().parent))
from abgen333 import Lay, build, analyse, nb, piston_traj
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind


class World:
    def __init__(self, lay, req, pist, sources):
        self.lay = lay; self.req = req; self.pist = pist; self.sources = sources
        L = lay.L
        for p in pist: p['traj'] = piston_traj(lay, p)
        # static item occupancy per slot start (pistons, arms, sources)
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
        self.cells = {b: set(req[b]) for b in lay.bodies}
        self.glue = {b: ('h' if b[0] == 'A' else 's') for b in lay.bodies}

    def wcell(self, b, c, k):
        return (c[0] + self.lay.off(b, k), c[1], c[2])

    def forbidden(self, b, c, others=True):
        lay = self.lay; L = lay.L
        for k in range(L):
            w = self.wcell(b, c, k)
            it = self.items[k].get(w)
            if it is not None:
                return 'item'
            mv = lay.moves(b, k)
            for n in nb(w):
                it = self.items[k].get(n)
                if it is None: continue
                if it[0] == 'src' and it[2] != b and mv: return 'srcadj'
                if it[0] == 'pist' and mv:
                    p = self.pist[it[1]]
                    if p['f'] == k and not (p['kind'] == 'P' and p['victim'] == b): return 'exthaz'
        if others:
            for b2 in lay.bodies:
                if b2 == b: continue
                for c2 in self.cells[b2]:
                    if abs(c2[1] - c[1]) + abs(c2[2] - c[2]) > 1: continue
                    for k in range(L):
                        d = (c[0] + lay.off(b, k)) - (c2[0] + lay.off(b2, k))
                        same_line = (c2[1] == c[1] and c2[2] == c[2])
                        if same_line and d == 0: return 'overlap'
                        sg = self.glue[b2] == self.glue[b]
                        if not same_line and d == 0 and sg: return 'sameglue'
                        if same_line and abs(d) == 1 and sg: return 'sameglue'
                        if same_line and abs(d) == 1 and lay.moves(b, k) and lay.moves(b2, k): return 'obstruct'
        return None

    def route(self, b, rnd, pad=3):
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
            if c in cache: return cache[c]
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
            if hit is None: return None, [('unreachable', list(rest)[:3])]
            v = hit
            while v is not None and v not in tree:
                tree.add(v); v = prev[v]
            rest -= tree
        self.cells[b] |= tree
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


def make(params, seed, order=None):
    lay = Lay()
    req, pist, src = build(lay, params)
    probs, _ = analyse(lay, req, pist, src)
    if probs: return None, ('static', probs[:3])
    wd = World(lay, req, pist, src)
    rnd = random.Random(seed)
    bodies = list(lay.bodies)
    if order is None: rnd.shuffle(bodies)
    for b in bodies:
        t, why = wd.route(b, rnd)
        if t is None: return None, (b, why[:3])
    return wd, None


if __name__ == '__main__':
    params = dict(u=[(0, 2), (0, 6), (4, 4)], xi=[0, 1, 1], perm=[(0, 1, 2, 3)] * 3, holder=['B'] * 3, hx=[-1] * 3)
    for seed in range(5):
        wd, err = make(params, seed)
        print(seed, err if err else {b: len(wd.cells[b]) for b in wd.lay.bodies})
