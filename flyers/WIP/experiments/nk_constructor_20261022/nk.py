"""N_k push ring core (generalised from n6_20261020/ring_designer.py).

Cycle: S = k+2 slots (2 ticks each), every body moves k slots, rests 2.
Bodies 0..L-1; body i rests at slots r_i, r_i+1 with r_i = 2i mod S.  Even k: L = S/2 (one rests per slot);
odd k: L = S (two rest per slot).  NEXT(i) = i+1 rests 2 slots after i and carries i's spent pushers.

Module frame of body V (x along flight, lanes (y,z)):
  R      V's redstone blocks (x, y, z)            (usually x = 0)
  P      V's k hopping +X pushers, lanes (y, z) [+ optional level h]: ready at x=h, extended base h-1, spent h-2
  PLATE  V glue cells
  CONT   NEXT(V) glue cells given in V's frame at V-local slot 0 (they move with NEXT(V))
"""
import itertools, heapq
from collections import defaultdict

D6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
SYMS = [lambda y, z: (y, z), lambda y, z: (-z, y), lambda y, z: (-y, -z), lambda y, z: (z, -y),
        lambda y, z: (y, -z), lambda y, z: (-y, z), lambda y, z: (z, y), lambda y, z: (-z, -y)]


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def bodies_for(k):
    S = k + 2
    return S // 2 if S % 2 == 0 else S


class Timing:
    def __init__(self, k, L=None):
        self.k, self.S = k, k + 2
        self.L = L or bodies_for(k)
        self.rest = [(2 * i) % self.S for i in range(self.L)]
        self._shift = [[0] * (2 * self.S + 1) for _ in range(self.L)]
        for i in range(self.L):
            for s in range(2 * self.S):
                self._shift[i][s + 1] = self._shift[i][s] + (1 if self.moves(i, s) else 0)

    def nxt(self, i): return (i + 1) % self.L
    def prv(self, i): return (i - 1) % self.L
    def local(self, i, s): return (s - self.rest[i]) % self.S
    def moves(self, i, s): return self.local(i, s) not in (0, 1)
    def shift(self, i, s): return self._shift[i][s]

    @staticmethod
    def delta(m):  # NEXT(V) minus V since V-local slot 0, at the start of V-local slot m
        return {0: 0, 1: 1, 2: 2, 3: 1}.get(m, 0)

    def pusher_options(self, m):
        """(dx, state, role) a pusher can be in at the start of V-local slot m (union over firing orders)"""
        if m == 0: return [(-2, 0, 'spent'), (-1, 2, 'ext')]
        if m == 1: return [(-1, 0, 'spent')]
        if m == 2: return [(0, 0, 'ready')]
        if m == 3: return [(0, 0, 'ready'), (-1, 2, 'ext')]
        return [(0, 0, 'ready'), (-1, 2, 'ext'), (-2, 0, 'spent')]

    def pusher_canon(self, f, m):
        """pusher firing at local slot f (2..S-1): (dx, state) at the start of local slot m"""
        if m >= 2:
            if m <= f: return 0, 0
            if m == f + 1: return -1, 2
            return -2, 0
        if m == 0: return (-1, 2) if f == self.S - 1 else (-2, 0)
        return -1, 0


class Ring:
    """mods: list of per-body module dicts; place: list of (x0, (oy, oz), sym) per body (world at global slot 0).
    extra: per-body extra glue cells (body frame).  mat: per-body 'slime'/'honey'."""

    def __init__(self, T, mods, place, mat=None, extra=None):
        self.T, self.mods, self.place = T, mods, place
        L = T.L
        self.mat = mat or ['slime' if i % 2 == 0 else 'honey' for i in range(L)]
        self.extra = extra or [set() for _ in range(L)]
        self.plates, self.contacts = [set() for _ in range(L)], [set() for _ in range(L)]
        for X in range(L):
            for c in mods[X]['PLATE']: self.plates[X].add(self.mw(X, c, 0, X))
            U = T.prv(X)
            for c in mods[U]['CONT']: self.contacts[X].add(self.cw(U, c))
        self.glue = [self.plates[X] | self.contacts[X] | set(self.extra[X]) for X in range(L)]

    def lev(self, X, j):
        p = self.mods[X]['P'][j]
        return (p[2], p[0], p[1]) if len(p) == 3 else (0, p[0], p[1])   # (h, y, z)

    def mw(self, V, c, s, body=None):
        x0, (oy, oz), si = self.place[V]
        y, z = SYMS[si](c[1], c[2])
        w = (x0 + self.T.shift(V, s) + c[0], oy + y, oz + z)
        if body is not None: w = (w[0] - self.T.shift(body, s), w[1], w[2])
        return w

    def cw(self, V, c, verify=False):
        """contact cell c (V frame, at V-local slot 0) of NEXT(V) -> NEXT(V)'s body frame (rigid by construction)."""
        T = self.T; W = T.nxt(V); out = set()
        for s in (range(T.S) if verify else [T.rest[V]]):
            m = T.local(V, s)
            w = self.mw(V, (c[0] + T.delta(m), c[1], c[2]), s)
            out.add((w[0] - T.shift(W, s), w[1], w[2]))
        assert len(out) == 1, out
        return out.pop()

    def yz_box(self, X):
        pts = [self.mw(X, r, 0) for r in self.mods[X]['R']] + [self.mw(X, (0, p[0], p[1]), 0) for p in self.mods[X]['P']]
        pts += list(self.glue[X])
        return (min(p[1] for p in pts), max(p[1] for p in pts), min(p[2] for p in pts), max(p[2] for p in pts))

    def near(self, X, margin=3):
        b = self.yz_box(X)
        out = []
        for Y in range(self.T.L):
            c = self.yz_box(Y)
            if c[0] <= b[1] + margin and b[0] <= c[1] + margin and c[2] <= b[3] + margin and b[2] <= c[3] + margin: out.append(Y)
        return out

    def hw(self, X, s, canon=False):
        """hardware (RB, pusher, arm) entries of body X at slot s; cached (glue is added separately)."""
        key = (X, s, canon)
        cache = self.__dict__.setdefault('_hw', {})
        if key in cache: return cache[key]
        T = self.T; out = []; m = T.local(X, s)
        for r in self.mods[X]['R']:
            out.append((self.mw(X, r, s), (X, 'RB', None)))
        for j in range(len(self.mods[X]['P'])):
            h, py, pz = self.lev(X, j)
            opts = [T.pusher_canon(j + 2, m) + (None,)] if canon else T.pusher_options(m)
            for dx, st, role in opts:
                out.append((self.mw(X, (h + dx, py, pz), s), (X, 'P', (j, st, role, m))))
                if st == 2: out.append((self.mw(X, (h + dx + 1, py, pz), s), (X, 'arm', j)))
        cache[key] = out
        return out

    def world(self, s, canon=False, bodies=None):
        T = self.T; occ = defaultdict(list)
        for X in (range(T.L) if bodies is None else bodies):
            for c, e in self.hw(X, s, canon): occ[c].append(e)
            sh = T.shift(X, s); ent = (X, 'g', None)
            for g in self.glue[X]:
                occ[(g[0] + sh, g[1], g[2])].append(ent)
        return occ

    def worlds(self, bodies=None): return [self.world(s, bodies=bodies) for s in range(self.T.S)]

    def cached_worlds(self):
        """all-body occupancy per slot, kept up to date by route(); call invalidate() after editing glue by hand."""
        if getattr(self, '_ws', None) is None: self._ws = self.worlds(getattr(self, 'active', None))
        return self._ws

    def invalidate(self): self._ws = None

    def _add_glue_to_cache(self, X, cells):
        if getattr(self, '_ws', None) is None: return
        act = getattr(self, 'active', None)
        if act is not None and X not in act: return
        ent = (X, 'g', None)
        for s, occ in enumerate(self._ws):
            sh = self.T.shift(X, s)
            for g in cells: occ[(g[0] + sh, g[1], g[2])].append(ent)

    STRICT = True

    def cell_ok(self, X, g, worlds, why=False, strict=None):
        if strict is None: strict = self.STRICT
        T = self.T
        def bad(msg): return (False, msg) if why else False
        for s in range(T.S):
            occ = worlds[s]
            w = (g[0] + T.shift(X, s), g[1], g[2])
            mX = T.moves(X, s)
            for o in occ.get(w, []):
                if o[0] != X or o[1] != 'g': return bad(f's{s} overlaps {o}')
            for d in D6:
                n = add(w, d)
                for q in occ.get(n, []):
                    Q, kind, info = q
                    if Q == X:
                        if strict and kind == 'P' and mX and info[1] == 0 and info[2] == 'spent' and T.moves(T.nxt(X), s):
                            return bad(f's{s} own spent pusher leaf')
                        continue
                    mQ = T.moves(Q, s)
                    if kind == 'g':
                        if self.mat[Q] == self.mat[X]: return bad(f's{s} same material {Q} at {n}')
                        if d == (1, 0, 0) and mX: return bad(f's{s} pushes {Q} glue')
                        if d == (-1, 0, 0) and mQ: return bad(f's{s} pushed by {Q} glue')
                        continue
                    if not mX: continue
                    if kind == 'arm': continue
                    if kind == 'RB':
                        if mQ: continue          # leaf race with a co-moving owner (+1 load)
                        return bad(f's{s} drags {Q} RB')
                    j, st, role, m = info
                    if st == 2: continue
                    if role == 'spent' and T.nxt(Q) == X: continue
                    return bad(f's{s} drags {Q} pusher {role}@{n}')
            if mX:
                dst = add(w, (1, 0, 0))
                for q in occ.get(dst, []):
                    if q[0] == X: continue
                    if q[1] == 'P' and q[2][2] == 'spent' and T.nxt(q[0]) == X: continue
                    return bad(f's{s} moves into {q}')
            back = add(w, (-1, 0, 0))
            for q in occ.get(back, []):
                Q = q[0]
                if Q == X or not T.moves(Q, s): continue
                if q[1] == 'g': return bad(f's{s} {Q} glue moves into it')
                if q[1] == 'P' and q[2][1] == 0 and not mX: return bad(f's{s} {Q} pusher moves into it')
        return (True, '') if why else True

    def check(self, subset=None):
        T = self.T; badl = []
        if subset is None: subset = list(range(T.L)); ws = self.worlds()
        else:
            near = sorted({Y for X in subset for Y in self.near(X, margin=4)}); ws = self.worlds(near)
        for X in subset:
            for g in sorted(self.glue[X]):
                ok, why = self.cell_ok(X, g, ws, why=True)
                if not ok: badl.append((X, g, why))
            G = self.glue[X]; st = [next(iter(G))]; seen = set()
            while st:
                u = st.pop()
                if u in seen: continue
                seen.add(u); st += [add(u, d) for d in D6 if add(u, d) in G]
            if len(seen) != len(G): badl.append((X, None, f'disconnected {len(seen)}/{len(G)}'))
        for s in range(T.S):
            occ = ws[s]
            for X in subset:
                m = T.local(X, s)
                for r in self.mods[X]['R']:
                    w = self.mw(X, r, s)
                    if T.moves(X, s) and not any(o[0] == X and o[1] == 'g' for d in D6 for o in occ.get(add(w, d), [])):
                        badl.append((X, w, f's{s} RB not attached'))
                for j in range(len(self.mods[X]['P'])):
                    h, py, pz = self.lev(X, j)
                    for dx, st, role in T.pusher_options(m):
                        if st == 2: continue
                        w = self.mw(X, (h + dx, py, pz), s)
                        if role == 'ready': need = [X] if T.moves(X, s) else []
                        else:
                            need = [T.nxt(X)] if T.moves(T.nxt(X), s) else []
                            if m == 0 and dx == -1: need = []
                        for Y in need:
                            if not any(o[0] == Y and o[1] == 'g' for d in D6 for o in occ.get(add(w, d), [])):
                                badl.append((X, w, f's{s} {role} pusher {j} not carried by {Y}'))
        return badl

    def route(self, X, maxlen=60, strict=None, maxbox=4):
        """connect X's contact components and extras to its plate (greedy BFS Steiner)."""
        T = self.T
        tree = set(self.plates[X])
        rest = set(self.contacts[X]) | set(self.extra[X])
        comps, seen = [], set()
        for c in sorted(rest):
            if c in seen: continue
            comp, st = set(), [c]
            while st:
                u = st.pop()
                if u in comp: continue
                comp.add(u); st += [add(u, d) for d in D6 if add(u, d) in rest and add(u, d) not in comp]
            seen |= comp; comps.append(comp)
        added = set()
        new0 = (tree | rest) - self.glue[X]
        self.glue[X] = tree | rest
        ws = self.cached_worlds(); self._add_glue_to_cache(X, new0); cache = {}

        def ok(c):
            if c not in cache: cache[c] = self.cell_ok(X, c, ws, strict=strict)
            return cache[c]
        while comps:
            comps.sort(key=lambda cc: min(sum(abs(a - b) for a, b in zip(u, v)) for u in cc for v in tree))
            comp = comps.pop(0)
            if comp & tree or any(add(u, d) in tree for u in comp for d in D6):
                tree |= comp; continue
            tl = list(tree)
            def hh(v): return min(abs(v[0] - t[0]) + abs(v[1] - t[1]) + abs(v[2] - t[2]) for t in tl) - 1
            prev = {u: None for u in comp}; gd = {u: 0 for u in comp}
            pq = [(hh(u), 0, u) for u in comp]; heapq.heapify(pq); hit = None
            while pq:
                f, g0, u = heapq.heappop(pq)
                if g0 > gd.get(u, 1 << 30): continue
                if any(add(u, d) in tree for d in D6): hit = u; break
                if g0 >= maxlen: continue
                for d in D6:
                    v = add(u, d)
                    if v in tree or (v in gd and gd[v] <= g0 + 1) or not ok(v): continue
                    gd[v] = g0 + 1; prev[v] = u
                    heapq.heappush(pq, (g0 + 1 + hh(v), g0 + 1, v))
            if hit is None: raise RuntimeError(f'body {X}: cannot route {sorted(comp)[:4]}')
            u = hit
            while u is not None and u not in comp:
                added.add(u); u = prev[u]
            tree |= comp | added
            self.glue[X] = tree | rest
        self._add_glue_to_cache(X, added)
        return added

    def flyer(self, pl):
        from fastflyer import Flyer, Block, Kind
        fl = Flyer(push_limit=pl)
        mats = {'slime': Kind.SLIME, 'honey': Kind.HONEY}
        for c, lst in self.world(0, canon=True).items():
            assert len(lst) == 1, (c, lst)
            X, kind, info = lst[0]
            if kind == 'g': fl.set(c, Block(mats[self.mat[X]]))
            elif kind == 'RB': fl.set(c, Block(Kind.REDSTONE_BLOCK))
            elif kind == 'arm': fl.set(c, Block(Kind.PISTON_ARM))
            else: fl.set(c, Block.piston(0, state=info[1]))
        return fl

    def size(self):
        return [len(self.glue[X]) + len(self.mods[X]['R']) for X in range(self.T.L)]
