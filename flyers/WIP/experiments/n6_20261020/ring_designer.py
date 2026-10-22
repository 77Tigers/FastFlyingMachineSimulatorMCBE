"""N6 four-body all-push ring designer: module placement + safe connector routing + kinematic checks.

Global cycle: 8 slots (16 ticks), every block advances 6. Bodies A,B,C,D rest at {0,1},{2,3},{4,5},{6,7};
W(X) = next body. Module X (frame: X's redstone blocks at x=0, X at its local slot k = s - rest(X)):
  R      X's redstone blocks at x=0
  P      six +X pushers: ready x=0, extended x=-1 (arm at 0), spent x=-2 (or -1 at k=1)
  PLATE  X glue cells (x,y,z), normally x=1 in front of P and R
  CONT   W(X) glue cells (x,y,z) given at X-local slot 0; they move with W (+1 at k=1, +2 at k=2, +1 at k=3)
Each body X's glue = PLATE of module X + CONT of module PREV(X) + routed connector.
Any ready pusher may fire (race); the checker uses the union of all positions a pusher column can hold.
"""
import sys, pathlib, itertools, heapq
from collections import defaultdict
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))

ORDER = ['A', 'B', 'C', 'D']
REST = {'A': 0, 'B': 2, 'C': 4, 'D': 6}
NEXT = {X: ORDER[(i + 1) % 4] for i, X in enumerate(ORDER)}
PREV = {v: k for k, v in NEXT.items()}
MAT = {'A': 'slime', 'B': 'honey', 'C': 'slime', 'D': 'honey'}
STRICT = False
D6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def moves(X, s): return (s % 8) not in (REST[X], REST[X] + 1)
def shift(X, s): return sum(1 for t in range(s) if moves(X, t))
def local(X, s): return (s - REST[X]) % 8
DELTA = {0: 0, 1: 1, 2: 2, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0}   # W(X) minus X since X-local slot 0


def pusher_options(k):
    """possible (dx, state, role) of one pusher column at local slot k (union over firing orders)"""
    if k == 1: return [(-1, 0, 'spent')]
    if k == 0: return [(-2, 0, 'spent'), (-1, 2, 'ext')]
    if k == 2: return [(0, 0, 'ready')]
    if k == 3: return [(0, 0, 'ready'), (-1, 2, 'ext')]
    return [(0, 0, 'ready'), (-1, 2, 'ext'), (-2, 0, 'spent')]


def pusher_canon(f, k):
    if 2 <= k <= 7:
        if k <= f: return 0, 0
        if k == f + 1: return -1, 2
        return -2, 0
    if k == 0: return (-1, 2) if f == 7 else (-2, 0)
    return -1, 0


SYMS = [lambda y, z: (y, z), lambda y, z: (-z, y), lambda y, z: (-y, -z), lambda y, z: (z, -y),
        lambda y, z: (y, -z), lambda y, z: (-y, z), lambda y, z: (z, y), lambda y, z: (-z, -y)]


class Ring:
    def __init__(self, mod, place, extra=None):
        """mod: dict(R=[(y,z)], P=[(y,z)]*6, PLATE=[(x,y,z)], CONT=[(x,y,z)]) shared by all modules.
        place: X -> (x0, (oy, oz), sym index). extra: X -> extra glue cells for body X (body frame)."""
        self.mods = dict(mod) if 'R' not in mod else {X: mod for X in ORDER}   # per-body modules
        self.mod, self.place = self.mods[ORDER[0]], place
        self.extra = extra or {}
        self.glue = {X: set() for X in ORDER}       # body frame (world at global slot 0)
        self.contacts = {X: set() for X in ORDER}
        self.plates = {X: set() for X in ORDER}
        for X in ORDER:
            for c in self.mods[X]['PLATE']:
                self.plates[X].add(self.mw(X, c, 0, X))
            U = PREV[X]
            for c in self.mods[U]['CONT']:
                self.contacts[X].add(self.cw(U, c))
            self.glue[X] = self.plates[X] | self.contacts[X] | set(self.extra.get(X, ()))

    # module-frame cell (x,y,z) of module V at global slot s -> world
    def mw(self, V, c, s, body=None):
        x0, (oy, oz), si = self.place[V]
        y, z = SYMS[si](c[1], c[2])
        w = (x0 + shift(V, s) + c[0], oy + y, oz + z)
        if body is not None: w = (w[0] - shift(body, s), w[1], w[2])
        return w

    def cw(self, V, c):
        """contact cell c (V-frame at V-local 0) of W(V) -> W body frame; asserts rigidity"""
        W = NEXT[V]; out = set()
        for s in range(8):
            k = local(V, s)
            w = self.mw(V, (c[0] + DELTA[k], c[1], c[2]), s)
            out.add((w[0] - shift(W, s), w[1], w[2]))
        assert len(out) == 1, out
        return out.pop()

    # --- world state per slot: cell -> list of (owner, kind, info)
    def world(self, s, conn=True, canon=False):
        occ = defaultdict(list)
        for X in ORDER:
            k = local(X, s)
            for r in self.mods[X]['R']:
                occ[self.mw(X, (0,) + tuple(r), s)].append((X, 'RB', None))
            for j, p in enumerate(self.mods[X]['P']):
                opts = [pusher_canon(j + 2, k) + (None,)] if canon else pusher_options(k)
                for dx, st, role in opts:
                    occ[self.mw(X, (dx,) + tuple(p), s)].append((X, 'P', (j, st, role, k)))
                    if st == 2: occ[self.mw(X, (dx + 1,) + tuple(p), s)].append((X, 'arm', j))
            for g in (self.glue[X] if conn else self.plates[X] | self.contacts[X]):
                occ[(g[0] + shift(X, s), g[1], g[2])].append((X, 'g', None))
        return occ

    # --- safety of a glue cell g (body frame) for body X against everything else
    def cell_ok(self, X, g, worlds, why=False):
        for s in range(8):
            occ = worlds[s]
            w = (g[0] + shift(X, s), g[1], g[2])
            mX = moves(X, s)
            for o in occ.get(w, []):
                if o[0] != X or o[1] != 'g':
                    return (False, f's{s} overlaps {o}') if why else False
            for d in D6:
                n = add(w, d)
                for q in occ.get(n, []):
                    Q, kind, info = q
                    if Q == X:
                        # own glue next to an own spent pusher that the next body carries: leaf race (+1 load)
                        if STRICT and kind == 'P' and mX and info[1] == 0 and info[2] == 'spent' and moves(NEXT[X], s):
                            return (False, f's{s} own spent pusher leaf') if why else False
                        continue
                    mQ = moves(Q, s)
                    if kind == 'g':
                        if MAT[Q] == MAT[X]: return (False, f's{s} same material {Q} at {n}') if why else False
                        if d == (1, 0, 0) and mX: return (False, f's{s} pushes {Q} glue') if why else False
                        if d == (-1, 0, 0) and mQ: return (False, f's{s} pushed by {Q} glue') if why else False
                        continue
                    if not mX: continue   # stationary glue does not drag
                    if kind == 'arm': continue
                    if kind == 'RB': return (False, f's{s} drags {Q} RB') if why else False
                    j, st, role, k = info
                    if st == 2: continue
                    if role == 'spent' and NEXT[Q] == X: continue      # designed carriage
                    return (False, f's{s} drags {Q} pusher {role}@{n}') if why else False
            if mX:   # destination must not hold a foreign block that is not part of this move
                dst = add(w, (1, 0, 0))
                for q in occ.get(dst, []):
                    if q[0] == X: continue
                    if q[1] == 'P' and q[2][2] == 'spent' and NEXT[q[0]] == X: continue
                    return (False, f's{s} moves into {q}') if why else False
            back = add(w, (-1, 0, 0))   # a foreign mover directly behind must not move into this cell
            for q in occ.get(back, []):
                Q = q[0]
                if Q == X or not moves(Q, s): continue
                if q[1] == 'g': return (False, f's{s} {Q} glue moves into it') if why else False
                if q[1] == 'P' and q[2][1] == 0 and not mX:
                    return (False, f's{s} {Q} pusher moves into it') if why else False
        return (True, '') if why else True

    def route(self, X, avoid_extra=(), maxlen=40, bounds=None):
        """connect contacts of X to its plate with a minimal safe glue path set (greedy Steiner)."""
        worlds = [self.world(s, conn=True) for s in range(8)]
        tree = set(self.plates[X])
        targets = [c for c in self.contacts[X] if c not in tree]
        comps = []
        seen = set()
        for c in sorted(self.contacts[X]):   # connected components of contacts
            if c in seen: continue
            comp, st = set(), [c]
            while st:
                u = st.pop()
                if u in comp: continue
                comp.add(u)
                for d in D6:
                    v = add(u, d)
                    if v in self.contacts[X] and v not in comp: st.append(v)
            seen |= comp; comps.append(comp)
        added = set()
        okcache = {}

        def ok(c):
            if c not in okcache: okcache[c] = self.cell_ok(X, c, worlds)
            return okcache[c]
        for comp in sorted(comps, key=lambda cc: min(sum(abs(a - b) for a, b in zip(u, v)) for u in cc for v in tree)):
            if any(add(u, d) in tree for u in comp for d in D6) or comp & tree:
                tree |= comp; continue
            # BFS from comp to tree
            prev = {u: None for u in comp}
            q = list(comp); hit = None; depth = {u: 0 for u in comp}
            while q and hit is None:
                nq = []
                for u in q:
                    for d in D6:
                        v = add(u, d)
                        if v in prev: continue
                        if v in tree: hit = u; break
                        if bounds and not all(lo <= a <= hi for a, (lo, hi) in zip(v, bounds)): continue
                        if depth[u] + 1 > maxlen or not ok(v): continue
                        prev[v] = u; depth[v] = depth[u] + 1; nq.append(v)
                    if hit is not None: break
                q = nq
            if hit is None: raise RuntimeError(f'{X}: cannot route component {sorted(comp)}')
            u = hit
            while u is not None and u not in comp:
                added.add(u); u = prev[u]
            tree |= comp | added
            # new cells change the world: refresh
            self.glue[X] = self.plates[X] | self.contacts[X] | added | set(self.extra.get(X, ()))
            worlds = [self.world(s, conn=True) for s in range(8)]
            okcache.clear()
        self.glue[X] = self.plates[X] | self.contacts[X] | added | set(self.extra.get(X, ()))
        return added

    def check(self):
        worlds = [self.world(s) for s in range(8)]
        bad = []
        for X in ORDER:
            for g in sorted(self.glue[X]):
                ok, why = self.cell_ok(X, g, worlds, why=True)
                if not ok:
                    # contacts adjacent to designed spent pushers are fine; others report
                    bad.append((X, g, why))
        # connectivity
        for X in ORDER:
            G = self.glue[X]; st = [next(iter(G))]; seen = set()
            while st:
                u = st.pop()
                if u in seen: continue
                seen.add(u); st += [add(u, d) for d in D6 if add(u, d) in G]
            if len(seen) != len(G): bad.append((X, None, f'disconnected {len(seen)}/{len(G)}'))
        # every hardware block attached: RBs adjacent to own glue, pushers covered when they must move
        for s in range(8):
            occ = worlds[s]
            for X in ORDER:
                k = local(X, s)
                for r in self.mods[X]['R']:
                    w = self.mw(X, (0,) + tuple(r), s)
                    if moves(X, s) and not any(any(o[0] == X and o[1] == 'g' for o in occ.get(add(w, d), [])) for d in D6):
                        bad.append((X, w, f's{s} RB not attached'))
                for j, p in enumerate(self.mods[X]['P']):
                    for dx, st, role in pusher_options(k):
                        if st == 2: continue
                        w = self.mw(X, (dx,) + tuple(p), s)
                        if role == 'ready':
                            need = [X] if moves(X, s) else []
                        else:
                            need = [NEXT[X]] if moves(NEXT[X], s) else []
                            if role == 'spent' and k == 0 and dx == -1: need = []
                        for Y in need:
                            if not any(any(o[0] == Y and o[1] == 'g' for o in occ.get(add(w, d), [])) for d in D6):
                                bad.append((X, w, f's{s} {role} pusher {j} not carried by {Y}'))
        return bad

    def size(self):
        return {X: len(self.glue[X]) for X in ORDER}

    def flyer(self, pl):
        from fastflyer import Flyer, Block, Kind
        fl = Flyer(push_limit=pl)
        occ = self.world(0, canon=True)
        mats = {'slime': Kind.SLIME, 'honey': Kind.HONEY}
        for c, lst in occ.items():
            assert len(lst) == 1, (c, lst)
            X, kind, info = lst[0]
            if kind == 'g': fl.set(c, Block(mats[MAT[X]]))
            elif kind == 'RB': fl.set(c, Block(Kind.REDSTONE_BLOCK))
            elif kind == 'arm': fl.set(c, Block(Kind.PISTON_ARM))
            else: fl.set(c, Block.piston(0, state=info[1]))
        return fl


# ---------------- layouts
V1 = dict(R=[(0, 0), (0, 2)], P=[(0, -1), (1, 0), (0, 1), (1, 2), (0, 3), (-1, 0)])
V1['PLATE'] = [(1,) + c for c in V1['P'] + V1['R']]
V1['CONT'] = [(-3,) + c for c in V1['P'] + V1['R']]          # back plate (the PL31 build)

if __name__ == '__main__':
    place = {'A': (0, (0, 0), 0), 'B': (0, (0, 7), 0), 'C': (-1, (-5, 7), 0), 'D': (-1, (-5, 0), 0)}
    ring = Ring(V1, place)
    for X in ORDER: print(X, 'route', len(ring.route(X)))
    print(ring.size(), ring.check()[:10])

V2 = dict(V1); V2['CONT'] = [(-2, 1, 1), (-2, -1, -1), (-2, 1, 3)]                 # lateral contacts
V3 = dict(R=[(0, 0), (2, 2)], P=[(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)])   # pinwheel
V3['PLATE'] = [(1,) + c for c in V3['P'] + V3['R']] + [(1, 0, 2)]
V3['CONT'] = [(-2, 1, 1), (-2, 3, 3)]


# ---------------- optimal body glue (CP-SAT): plate + coverage of predecessor's spent pushers + connected
def body_opt(ring, X, margin=3, tl=20, workers=4, keep_plate=True):
    from ortools.sat.python import cp_model
    U = PREV[X]
    others = {Y: ring.glue[Y] for Y in ORDER}
    ring.glue[X] = set(ring.plates[X])            # route against everything else
    worlds = [ring.world(s) for s in range(8)]
    # coverage targets: U's pusher column cells at U-x -2 (U-local 0) expressed in X body frame
    sU = next(s for s in range(8) if local(U, s) == 0)
    targets = []
    for p in ring.mods[U]['P']:
        w = ring.mw(U, (-2,) + tuple(p), sU)
        targets.append((w[0] - shift(X, sU), w[1], w[2]))
    pts = list(ring.plates[X]) + targets
    lo = [min(c[i] for c in pts) - margin for i in range(3)]; hi = [max(c[i] for c in pts) + margin for i in range(3)]
    cand = [c for c in itertools.product(*[range(lo[i], hi[i] + 1) for i in range(3)])
            if c in ring.plates[X] or ring.cell_ok(X, c, worlds)]
    cs = set(cand)
    m = cp_model.CpModel()
    v = {c: m.NewBoolVar('') for c in cand}
    for c in ring.plates[X]: m.Add(v[c] == 1)
    for t in targets:
        nb = [add(t, d) for d in D6 if d != (1, 0, 0)]
        lits = [v[n] for n in nb if n in cs]
        if not lits: return None
        m.AddBoolOr(lits)
    # connectivity: single-commodity flow from root plate cell
    root = sorted(ring.plates[X])[0]; N = len(cand)
    f = {}
    for c in cand:
        for d in D6:
            n = add(c, d)
            if n in cs: f[c, n] = m.NewIntVar(0, N, '')
    for c in cand:
        inflow = sum(f[n, c] for d in D6 if (n := add(c, d)) in cs)
        outflow = sum(f[c, n] for d in D6 if (n := add(c, d)) in cs)
        if c == root: m.Add(outflow - inflow == sum(v.values()) - 1)
        else: m.Add(inflow - outflow == v[c])
        for d in D6:
            n = add(c, d)
            if n in cs: m.Add(f[c, n] <= N * v[c]); m.Add(f[c, n] <= N * v[n])
    cur = others[X]
    for c in cand: m.AddHint(v[c], 1 if c in cur else 0)
    if all(c in cs for c in cur): m.Add(sum(v.values()) <= len(cur))
    m.Minimize(sum(v.values()))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_search_workers = workers
    st = sv.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        ring.glue[X] = others[X]; return None
    new = {c for c in cand if sv.Value(v[c])}
    ring.glue[X] = new if len(new) <= len(cur) else cur
    return len(ring.glue[X]), sv.StatusName(st)


def optimise(ring, rounds=2, **kw):
    for r in range(rounds):
        for X in ORDER:
            res = body_opt(ring, X, **kw)
            if res is None: return None
    return ring.size()

V4 = dict(V3); V4['CONT'] = [(-2, 1, 1), (-3, 1, 1), (-3, 1, 2), (-3, 2, 2), (-3, 2, 3), (-3, 3, 2)]
V4['PLATE'] = [(1,) + c for c in V3['P'] + V3['R']] + [(1, 1, 1)]
V5 = dict(R=[(0, 0), (0, 3)], P=[(-1, 0), (1, 0), (0, 1), (0, 2), (-1, 3), (1, 3)])   # two T's
V5['PLATE'] = [(1,) + c for c in V5['P'] + V5['R']]
V5['CONT'] = [(-2, 1, 1), (-2, 1, 2), (-2, -1, 1), (-2, -1, 2), (-3, 1, 1), (-3, 0, 1), (-3, -1, 1)]


def route_all(ring, rounds=3, maxlen=14):
    for X in ORDER: ring.route(X, maxlen=maxlen)
    for r in range(rounds - 1):
        improved = False
        for X in sorted(ORDER, key=lambda Y: -len(ring.glue[Y])):
            old = set(ring.glue[X])
            ring.glue[X] = ring.plates[X] | ring.contacts[X] | set(ring.extra.get(X, ()))
            try:
                ring.route(X, maxlen=maxlen)
            except RuntimeError:
                ring.glue[X] = old; continue
            if len(ring.glue[X]) > len(old): ring.glue[X] = old
            elif len(ring.glue[X]) < len(old): improved = True
        if not improved: break
    return ring.size()


def hard_conflicts(ring, first=False):
    """hardware/plate overlaps between owners and wrong power, over all 8 slots (union of pusher options)."""
    bad = []
    for s in range(8):
        occ = ring.world(s)
        for c, lst in occ.items():
            owners = {o[0] for o in lst}
            if len(owners) > 1:
                bad.append((s, c, 'overlap', sorted(owners)))
                if first: return bad
        for c, lst in occ.items():
            for X, kind, info in lst:
                if kind != 'P' or info[1] == 2: continue
                front = add(c, (1, 0, 0))
                powered = False
                for d in D6:
                    n = add(c, d)
                    if n == front: continue
                    for q in occ.get(n, []):
                        if q[1] == 'RB':
                            if q[0] != X or info[2] != 'ready':
                                bad.append((s, c, 'stray power', q[0], X, info[2]))
                                if first: return bad
                            powered = True
    return bad


def spent_targets(ring, X):
    """X-body-frame cells of PREV(X)'s spent pusher columns at PREV-local slot 0 (x = -2)."""
    U = PREV[X]
    sU = next(s for s in range(8) if local(U, s) == 0)
    out = []
    for p in ring.mods[U]['P']:
        w = ring.mw(U, (-2,) + tuple(p), sU)
        out.append((w[0] - shift(X, sU), w[1], w[2]))
    return out


def route_cover(ring, X, maxlen=12):
    """X glue = plate + greedy shortest safe paths until every predecessor spent column is carried."""
    ring.glue[X] = set(ring.plates[X]) | set(ring.extra.get(X, ()))
    worlds = [ring.world(s) for s in range(8)]
    okc = {}

    def ok(c):
        if c not in okc: okc[c] = ring.cell_ok(X, c, worlds)
        return okc[c]
    tg = spent_targets(ring, X)
    carriers = {t: {add(t, d) for d in D6 if d != (1, 0, 0)} for t in tg}
    while True:
        G = ring.glue[X]
        unc = [t for t in tg if not (carriers[t] & G)]
        if not unc: break
        goal = {}
        for t in unc:
            for c in carriers[t]: goal.setdefault(c, []).append(t)
        prev = {u: None for u in G}; q = list(G); hit = None; depth = 0
        while q and hit is None and depth <= maxlen:
            nq = []
            for u in q:
                for d in D6:
                    v = add(u, d)
                    if v in prev or not ok(v): continue
                    prev[v] = u
                    if v in goal: hit = v; break
                    nq.append(v)
                if hit is not None: break
            q = nq; depth += 1
        if hit is None: raise RuntimeError(f'{X}: cannot cover {unc}')
        u = hit; new = set()
        while u is not None and u not in G:
            new.add(u); u = prev[u]
        ring.glue[X] = G | new
        worlds = [ring.world(s) for s in range(8)]; okc.clear()
    return len(ring.glue[X])


def route_cover_all(ring, rounds=3):
    for X in ORDER: route_cover(ring, X)
    for r in range(rounds - 1):
        for X in sorted(ORDER, key=lambda Y: -len(ring.glue[Y])):
            old = set(ring.glue[X])
            try: route_cover(ring, X)
            except RuntimeError: ring.glue[X] = old; continue
            if len(ring.glue[X]) > len(old): ring.glue[X] = old
    return ring.size()

V4c = dict(V4); V4c['CONT'] = []          # contacts chosen by route_cover
V1c = dict(V1); V1c['CONT'] = []
V5c = dict(V5); V5c['CONT'] = []

V6 = dict(R=[(0, 0), (0, 2)], P=[(-1, 0), (-1, 2), (0, -1), (0, 1), (1, 0), (1, 2)])   # cover+exit 8
V6['PLATE'] = [(1,) + c for c in V6['P'] + V6['R']]
V6['CONT'] = [(-3, -1, 1), (-3, 0, -1), (-3, 0, 0), (-3, 0, 1), (-3, 1, 1), (-2, -2, 1), (-2, -1, 1), (-2, 1, 1)]
V6c = dict(V6); V6c['CONT'] = []


def rb_cells(ring, X):
    """body-frame cells of X's redstone blocks"""
    out = []
    for r in ring.mods[X]['R']:
        w = ring.mw(X, (0,) + tuple(r), 0)
        out.append((w[0] - shift(X, 0), w[1], w[2]))
    return out


def route2(ring, X, maxlen=14):
    """greedy Steiner: connect all components of plate+contacts+extra, and attach every RB to X glue."""
    base = set(ring.plates[X]) | set(ring.contacts[X]) | set(ring.extra.get(X, ()))
    ring.glue[X] = set(base)
    worlds = [ring.world(s) for s in range(8)]
    okc = {}

    def ok(c):
        if c not in okc: okc[c] = ring.cell_ok(X, c, worlds)
        return okc[c]

    def comps(G):
        out, seen = [], set()
        for c in sorted(G):
            if c in seen: continue
            comp, st = set(), [c]
            while st:
                u = st.pop()
                if u in comp: continue
                comp.add(u); st += [add(u, d) for d in D6 if add(u, d) in G and add(u, d) not in comp]
            seen |= comp; out.append(comp)
        return out
    rbs = rb_cells(ring, X)
    while True:
        G = ring.glue[X]
        cs = comps(G)
        tree = max(cs, key=len)
        goals = []      # each goal: set of cells that satisfy it when reached/added
        for c in cs:
            if c is not tree: goals.append(('comp', {add(u, d) for u in c for d in D6} | c))
        for r in rbs:
            nbr = {add(r, d) for d in D6}
            if not (nbr & G): goals.append(('rb', nbr))
            elif not (nbr & tree) and not any(nbr & c for c in cs if c is tree): pass
        if not goals: break
        goalcells = {}
        for gi, (kind, cells) in enumerate(goals):
            for c in cells: goalcells.setdefault(c, []).append(gi)
        prev = {u: None for u in tree}; q = list(tree); hit = None; depth = 0
        # reaching a goal: tree cell adjacent/inside goal set
        for u in tree:
            if u in goalcells: hit = u; break
        while q and hit is None and depth <= maxlen:
            nq = []
            for u in q:
                for d in D6:
                    v = add(u, d)
                    if v in prev: continue
                    if v in G and v not in tree:      # touching another component directly
                        prev[v] = u; hit = v; break
                    if not ok(v): continue
                    prev[v] = u
                    if v in goalcells: hit = v; break
                    nq.append(v)
                if hit is not None: break
            q = nq; depth += 1
        if hit is None: raise RuntimeError(f'{X}: route2 failed, goals {len(goals)}')
        u = hit; new = set()
        while u is not None and u not in tree:
            if u not in G: new.add(u)
            u = prev[u]
        if not new and hit in G: pass
        ring.glue[X] = G | new
        if not new and hit in tree:
            # goal satisfied by tree cell already (rb adjacency) -> nothing to add; avoid infinite loop
            break
        worlds = [ring.world(s) for s in range(8)]; okc.clear()
    return len(ring.glue[X])


def route2_all(ring, rounds=3):
    for X in ORDER: route2(ring, X)
    for r in range(rounds - 1):
        for X in sorted(ORDER, key=lambda Y: -len(ring.glue[Y])):
            old = set(ring.glue[X])
            try: route2(ring, X)
            except RuntimeError: ring.glue[X] = old; continue
            if len(ring.glue[X]) > len(old): ring.glue[X] = old
    return ring.size()


V8 = dict(V6); V8['PLATE'] = [c for c in V6['PLATE'] if c != (1, 0, 2)]

# ring cluster, 3 RBs, predecessor cover = 2x2 block in the hole (exit (2,2) rises through it)
V9 = dict(R=[(0, 0), (0, 3), (3, 0)], P=[(0, 1), (0, 2), (1, 0), (1, 3), (2, 0), (3, 1)])
V9['PLATE'] = [(1,) + c for c in V9['P'] + V9['R']]
V9['CONT'] = [(-2, 1, 1), (-2, 1, 2), (-2, 2, 1), (-2, 2, 2)]

# V9 with the predecessor cover lifted: 3 lateral contacts + bridge at -1, rise starts in (2,2) at x=0,
# so the exit column carries no glue at -2 (next body's pusher may sit beside it: direct plate contact).
V9b = dict(V9); V9b['CONT'] = [(-2, 1, 1), (-2, 1, 2), (-2, 2, 1), (-1, 1, 2), (-1, 2, 2)]


def set_bodies(n):
    """switch the global ring to n bodies (multiple of 4); phases repeat 0,2,4,6; materials alternate."""
    names = [chr(ord('A') + i) for i in range(n)]
    ORDER[:] = names
    REST.clear(); REST.update({X: (2 * i) % 8 for i, X in enumerate(names)})
    NEXT.clear(); NEXT.update({X: names[(i + 1) % n] for i, X in enumerate(names)})
    PREV.clear(); PREV.update({v: k for k, v in NEXT.items()})
    MAT.clear(); MAT.update({X: ('slime', 'honey')[i % 2] for i, X in enumerate(names)})
