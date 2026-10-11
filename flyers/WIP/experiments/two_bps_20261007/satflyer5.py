"""Exact CP-SAT model of rigid-segment flyers with an NS-slot cycle (slot = 2 ticks) and PER-PISTON fire slots.

Generalisation of rigid_sat_20261004/satflyer.py (which is the NS=4, one-fire-slot-per-segment case).
NS=4 -> 2.5 bps (every segment moves twice per 8 ticks); NS=5 -> 2 bps (twice per 10 ticks).

Words: tuple of the slots in which a segment moves +1 X (any number of moves; all segments of one flyer must move
equally often for a rigid flyer). Kinds:
  'g' glue (segment material), 'R' redstone block, 'D<d>' rod facing d, 'O<d>' observer facing d
  (d: 0 +X, 1 -X, 2 +Y, 3 -Y, 4 +Z, 5 -Z),
  'P<f>' pusher (+X) with fire slot f, 'S<f>' sticky (-X) with fire slot f; suffix 'h' = power held 2 slots.
Piston timing (hold h = 1 or 2): powered exactly at slots f .. f+h-1, extends at f (pusher pushes the glue in
  front, which must belong to a segment moving at f), extended at slot start f+1 .. f+h, retracts at f+h (sticky
  pulls the glue two cells ahead (-X), which must belong to a segment moving at f+h). Carrier still at f .. f+h.
  Legal fire slots of a segment = those with its word free at f .. f+h.
Power: redstone/rod soft-power the 6 neighbours; rods (always) and observers (only in the slot after their own
  segment moved) hard-power the glue they face, which powers its 6 neighbours; an observer facing a piston powers it.
  A piston ignores a source / hot block in its own front cell. Power must be absent at every non-powered slot.
Races: as satflyer (see that docstring); plus: nothing may move into an extended pusher's arm, and only the pulled
  glue may move into a retracting sticky's arm.
Riders (single-piston segments without glue that ride a carrier on every move) and merged moves as in satflyer.
"""
import sys, pathlib, time, os, itertools, pickle, argparse
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from ortools.sat.python import cp_model

D6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
E, W = (1, 0, 0), (-1, 0, 0)


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sx(a, dx): return (a[0] + dx, a[1], a[2])
def wpos(word, t): return sum(1 for m in word if m < t)


def pinfo(k):
    """piston kind -> (type 'P'/'S', fire slot, hold) else None"""
    if k[0] in 'PS':
        return k[0], int(k[1]), (2 if k.endswith('h') else 1)
    return None


def kphase(k, t, NS):
    """'fire' (power, extends), 'hold' (extended and powered), 'ret' (extended at slot start, retracts/pulls), 'idle'"""
    _, f, h = pinfo(k)
    d = (t - f) % NS
    if d == 0: return 'fire'
    if d < h: return 'hold'
    if d == h: return 'ret'
    return 'idle'


def fire_slots(word, NS, h=1):
    return [f for f in range(NS) if all((f + i) % NS not in word for i in range(h + 1))]


def piston_kinds(word, NS, holds=(1,)):
    out = []
    for h in holds:
        for f in fire_slots(word, NS, h):
            for t in 'PS':
                out.append(f'{t}{f}' + ('h' if h == 2 else ''))
    return out


def neg(l):
    if l is True: return False
    if l is False: return True
    return l.Not()


class Infeasible(Exception):
    pass


class FlyerSAT:
    def __init__(self, words, box, L, NS=5, kinds=('g', 'R'), leaf=True, maxglue=6, anchor=None,
                 open_segs=(), fixed=None, names=None, boxes=None, maxsize=None, skip=(), merges=(), must=None,
                 riders=(), kinds_by_seg=None, holds=(1,), pistons=True, forbid_cells=None):
        """kinds: non-piston kinds allowed (piston kinds with all legal fire slots are added automatically when
        pistons=True; kinds_by_seg overrides the full list for a segment). box: shared candidate cells (slot-0 world
        frame); boxes: per-segment overrides. fixed: per segment (cells dict world->kind, mat) or None."""
        self.m = m = cp_model.CpModel()
        self.NS = NS
        self.words = [tuple(w) for w in words]
        self.n = n = len(self.words)
        self.names = names or [f's{i}' for i in range(n)]
        self.basekinds = [k for k in kinds if pinfo(k) is None]
        self.holds = holds; self.pistons = pistons
        self.leaf = leaf; self.L = L; self.maxglue = maxglue
        self.riders = {self.names.index(x) if isinstance(x, str) else x for x in riders}
        self.kinds_by_seg = {self.names.index(k) if isinstance(k, str) else k: list(v) for k, v in (kinds_by_seg or {}).items()}
        if isinstance(open_segs, dict): self.oflags = {(self.names.index(k) if isinstance(k, str) else k): set(v) for k, v in open_segs.items()}
        else: self.oflags = {(self.names.index(k) if isinstance(k, str) else k): {'pow', 'Ptarget', 'Starget', 'cause_le1'} for k in open_segs}
        self.open = set(self.oflags)
        self.fixedset = {s for s in range(n) if fixed is not None and fixed[s] is not None}
        if fixed is not None:
            for s in self.fixedset:   # fixed segments: their kinds must be available
                ks = set(self.kinds_of(s))
                for c, k in fixed[s][0].items():
                    if k not in ks:
                        raise Infeasible(f'{self.names[s]}: kind {k} not allowed (word {self.words[s]})')
        self.boxes = []
        for s in range(n):
            if s in self.fixedset: b = list(fixed[s][0])
            elif boxes is not None and boxes[s] is not None: b = list(boxes[s])
            else: b = list(box)
            if forbid_cells and s not in self.fixedset: b = [u for u in b if u not in forbid_cells.get(s, ())]
            self.boxes.append(b)
        self.boxsets = [set(b) for b in self.boxes]
        self.X = {}; self.OCC = {}
        for s in range(n):
            ks = self.kinds_of(s)
            for u in self.boxes[s]:
                vs = []
                for k in ks:
                    v = m.NewBoolVar(f'x{s}_{u}_{k}'); self.X[s, u, k] = v; vs.append(v)
                o = m.NewBoolVar(f'o{s}_{u}'); self.OCC[s, u] = o
                m.Add(sum(vs) == o)
        self.mat = [m.NewBoolVar(f'mat{s}') for s in range(n)]
        self.mateq = {}
        for a in range(n):
            for b in range(a + 1, n):
                e = m.NewBoolVar('')
                m.Add(self.mat[a] == self.mat[b]).OnlyEnforceIf(e)
                m.Add(self.mat[a] != self.mat[b]).OnlyEnforceIf(e.Not())
                self.mateq[a, b] = self.mateq[b, a] = e
        if fixed is not None: self.fix(fixed)
        if not self.fixedset: m.Add(self.mat[0] == 0)
        if anchor is not None: m.Add(self.X[0, anchor, 'g'] == 1)
        for s_, cells in (must or {}).items():
            si = self.names.index(s_) if isinstance(s_, str) else s_
            for c, k in cells.items(): m.Add(self.X[si, c, k] == 1)
        self.maxsize = maxsize
        self.merges = [(t, [self.names.index(x) if isinstance(x, str) else x for x in g]) for t, g in merges]
        self.skip = set(skip)
        self.sh = [[wpos(self.words[s], t) for t in range(NS)] for s in range(n)]
        self.build()

    # ---------- helpers
    def kinds_of(self, s):
        if s in self.kinds_by_seg: return self.kinds_by_seg[s]
        pk = piston_kinds(self.words[s], self.NS, self.holds) if self.pistons else []
        if s in self.riders: return pk
        return self.basekinds + pk

    def pk_of(self, s): return [k for k in self.kinds_of(s) if pinfo(k) is not None]
    def x(self, s, u, k): return self.X.get((s, u, k), False)
    def occ(self, s, u): return self.OCC.get((s, u), False)
    def loc(self, s, v, t): return (v[0] - self.sh[s][t], v[1], v[2])
    def moves(self, s, t): return (t % self.NS) in self.words[s]

    def clause(self, lits):
        out = []
        for l in lits:
            if l is True: return
            if l is False: continue
            out.append(l)
        if not out: raise Infeasible('empty clause')
        self.m.AddBoolOr(out)

    def forbid(self, *lits): self.clause([neg(l) for l in lits])

    def AND(self, *lits):
        ls = []
        for l in lits:
            if l is False: return False
            if l is True: continue
            ls.append(l)
        if not ls: return True
        if len(ls) == 1: return ls[0]
        b = self.m.NewBoolVar('')
        for l in ls: self.m.AddImplication(b, l)
        self.m.AddBoolOr([neg(l) for l in ls] + [b])
        return b

    def OR(self, lits):
        ls = []
        for l in lits:
            if l is True: return True
            if l is False: continue
            ls.append(l)
        if not ls: return False
        if len(ls) == 1: return ls[0]
        b = self.m.NewBoolVar('')
        for l in ls: self.m.AddImplication(l, b)
        self.m.AddBoolOr(ls + [b.Not()])
        return b

    def fix(self, fixed):
        for s, f in enumerate(fixed):
            if f is None: continue
            cells, mat = f
            for u in self.boxes[s]:
                for k in self.kinds_of(s):
                    self.m.Add(self.X[s, u, k] == (1 if cells.get(u) == k else 0))
            if mat is not None: self.m.Add(self.mat[s] == (1 if mat == 'honey' else 0))

    # ---------- constraints
    def build(self):
        m, n, X, NS = self.m, self.n, self.X, self.NS
        sh = self.sh
        B = self.boxes
        R = self.riders
        self.leafvars = {}
        self.softcause = {}
        self.mg = {}
        self.rc = {}
        for t in range(NS):
            mov = [s for s in range(n) if self.moves(s, t)]
            movset = set(mov)
            nr = [s for s in mov if s not in R]
            planned = {tuple(sorted(g)) for tt, g in self.merges if tt == t}
            for a, b in planned: assert a in movset and b in movset, (t, a, b)
            for i, a in enumerate(nr):
                for b in nr[i + 1:]:
                    if (a, b) in planned: self.mg[t, a, b] = True
            for r in [s for s in mov if s in R]:
                ls = []
                for j in nr:
                    v = m.NewBoolVar(f'rc{t}_{r}_{j}'); self.rc[t, r, j] = v; ls.append(v)
                if not ls: raise Infeasible('rider with no carrier')
                m.AddExactlyOne(ls)

            def esc(a, b, t=t):
                if a in R and b in R: return False
                if a in R: return self.rc.get((t, a, b), False)
                if b in R: return self.rc.get((t, b, a), False)
                return self.mg.get((t, min(a, b), max(a, b)), False)

            world = {}
            for s in range(n):
                for u in B[s]:
                    world.setdefault(sx(u, sh[s][t]), []).append((s, u))
            arms = {}; parms = {}; sarms_ret = {}
            for s in range(n):
                for k in self.pk_of(s):
                    p = kphase(k, t, NS)
                    if p not in ('hold', 'ret'): continue
                    typ = k[0]
                    for u in B[s]:
                        v = sx(u, sh[s][t]); l = X[s, u, k]
                        a = add(v, E if typ == 'P' else W)
                        arms.setdefault(a, []).append(l)
                        if typ == 'P' or p == 'hold': parms.setdefault(a, []).append(l)
                        else: sarms_ret.setdefault(a, []).append(l)
            for v, lst in world.items():
                lits = [self.OCC[s, u] for s, u in lst] + arms.get(v, [])
                if len(lits) > 1: m.AddAtMostOne(lits)
            for v, al in arms.items():
                if v not in world and len(al) > 1: m.AddAtMostOne(al)
            # ---- power
            soft = {}; hotsrc = {}; obs_p = {}
            for s in range(n):
                pulsing = self.moves(s, t - 1)
                for u in B[s]:
                    v = sx(u, sh[s][t])
                    for k in self.kinds_of(s):
                        if k == 'R' or k[0] == 'D':
                            soft.setdefault(v, []).append(X[s, u, k])
                        if k[0] in 'DO':
                            if k[0] == 'O' and not pulsing: continue
                            f = add(v, D6[int(k[1])])
                            hotsrc.setdefault(f, []).append(X[s, u, k])
                            if k[0] == 'O': obs_p.setdefault(f, []).append((X[s, u, k], v))
            hot = {}
            for f, srcs in hotsrc.items():
                gl = [X[o, self.loc(o, f, t), 'g'] for o in range(n) if (o, self.loc(o, f, t), 'g') in X]
                if gl: hot[f] = self.AND(self.OR(srcs), self.OR(gl))
            self.hot_t = getattr(self, 'hot_t', {}); self.hot_t[t] = hot
            for s in range(n):
                fl = self.oflags.get(s, ())
                if 'pow' in fl or 'power' in self.skip: continue
                for k in self.pk_of(s):
                    p = kphase(k, t, NS)
                    need = p in ('fire', 'hold')
                    fd = E if k[0] == 'P' else W
                    for u in B[s]:
                        xp = X[s, u, k]
                        v = sx(u, sh[s][t])
                        front = add(v, fd)
                        srcs = []
                        for d in D6:
                            nb = add(v, d)
                            if nb == front: continue
                            srcs += soft.get(nb, [])
                            if nb in hot: srcs.append(hot[nb])
                        srcs += [ol for ol, ov in obs_p.get(v, []) if ov != front]
                        if need:
                            if 'powmiss' not in fl: self.clause([neg(xp)] + srcs)
                        else:
                            for l in srcs: self.forbid(xp, l)
            # ---- piston actions
            for s in range(n):
                if 'targets' in self.skip: break
                for k in self.pk_of(s):
                    p = kphase(k, t, NS)
                    for u in B[s]:
                        xp = X[s, u, k]
                        v = sx(u, sh[s][t])
                        if p == 'fire' and k[0] == 'P' and 'Ptarget' not in self.oflags.get(s, ()):
                            f = add(v, E)
                            self.clause([neg(xp)] + [self.x(o, self.loc(o, f, t), 'g') for o in mov if o != s])
                        if p == 'fire' and k[0] == 'S':
                            f = add(v, W)
                            for o in range(n): self.forbid(xp, self.occ(o, self.loc(o, f, t)))
                            for al in arms.get(f, []): self.forbid(xp, al)
                            for j in mov: self.forbid(xp, self.occ(j, self.loc(j, add(f, W), t)))
                        if p == 'ret' and k[0] == 'S' and 'Starget' not in self.oflags.get(s, ()):
                            tc = add(v, (-2, 0, 0))
                            self.clause([neg(xp)] + [self.x(o, self.loc(o, tc, t), 'g') for o in mov if o != s])
            # ---- causes
            recv = {}; csum = {}
            self.cause_lits = getattr(self, 'cause_lits', {})
            for j in nr:
                pj = []
                for u in B[j]:
                    gj = X[j, u, 'g'] if (j, u, 'g') in X else False
                    if gj is False: continue
                    w = sx(u, sh[j][t])
                    for s in range(n):
                        if s == j: continue
                        for k in self.pk_of(s):
                            p = kphase(k, t, NS)
                            if p == 'fire' and k[0] == 'P':
                                l = self.x(s, self.loc(s, add(w, W), t), k)
                            elif p == 'ret' and k[0] == 'S':
                                l = self.x(s, self.loc(s, add(w, (2, 0, 0)), t), k)
                            else: continue
                            if l is not False:
                                a_ = self.AND(gj, l); pj.append(a_)
                                self.cause_lits.setdefault((j, t), []).append((a_, s, k))
                pj = [p for p in pj if p is not False]
                csum[j] = sum(pj); recv[j] = self.OR(pj)
                if pj: m.Add(csum[j] <= 1)
            if 'cause' not in self.skip:
                for j in nr:
                    fl = self.oflags.get(j, ())
                    first = (t == min(self.words[j]))
                    mls = [v for (tt, x_, y_), v in self.mg.items() if tt == t and j in (x_, y_)]
                    if any(v is True for v in mls): continue
                    if ('ext_push' in fl and first) or ('ext_pull' in fl and not first):
                        m.Add(csum[j] == 0); continue
                    if 'ext_' + str(t) in fl:
                        m.Add(csum[j] == 0); continue
                    if 'cause_le1' in fl: continue
                    if 'softcause' in self.skip:
                        b = m.NewBoolVar(f'cause_{j}_{t}'); self.softcause[j, t] = b
                        m.Add(csum[j] == 1).OnlyEnforceIf(b); continue
                    m.Add(csum[j] == 1)
                for (tt, a, b), v in list(self.mg.items()):
                    if tt != t: continue
                    m.Add(csum[a] + csum[b] == 1)
                    for r_, o_ in ((a, b), (b, a)):
                        bl = []
                        for u in B[r_]:
                            dw = sx(u, sh[r_][t] + 1)
                            l = self.x(o_, self.loc(o_, dw, t), 'g')
                            if l is not False: bl.append(self.AND(self.OCC[r_, u], l))
                            for d in D6:
                                l = self.x(o_, self.loc(o_, add(sx(u, sh[r_][t]), d), t), 'g')
                                if l is not False and (r_, u, 'g') in X:
                                    bl.append(self.AND(X[r_, u, 'g'], l, self.mateq[r_, o_]))
                        bind = self.OR(bl)
                        self.clause([neg(recv[r_]), bind])
            for (tt, r, j), v in list(self.rc.items()):
                if tt != t: continue
                bl = []
                for u in B[r]:
                    w = sx(u, sh[r][t])
                    for d in D6:
                        l = self.x(j, self.loc(j, add(w, d), t), 'g')
                        if l is not False: bl.append(self.AND(self.OCC[r, u], l))
                    l = self.occ(j, self.loc(j, add(w, W), t))
                    if l is not False: bl.append(self.AND(self.OCC[r, u], l))
                self.clause([neg(v), self.OR(bl)])
            # ---- movement into occupied cells / arms
            for j in (mov if 'move' not in self.skip else []):
                for u in B[j]:
                    d = sx(u, sh[j][t] + 1)
                    for al in parms.get(d, []): self.forbid(self.OCC[j, u], al)
                    for al in sarms_ret.get(d, []):
                        self.forbid(self.OCC[j, u], al, neg(self.x(j, u, 'g')))
                    for o in range(n):
                        if o == j: continue
                        lo = self.loc(o, d, t)
                        if lo not in self.boxsets[o]: continue
                        if o not in movset:
                            self.forbid(self.OCC[j, u], self.OCC[o, lo]); continue
                        e = esc(j, o)
                        if not self.leaf:
                            self.clause([neg(self.OCC[j, u]), neg(self.OCC[o, lo]), e]); continue
                        d2 = add(d, E)
                        blk = [self.occ(q, self.loc(q, d2, t)) for q in range(n)] + arms.get(d2, [])
                        for k in self.kinds_of(o):
                            xo = X[o, lo, k]
                            if k == 'g' or k[0] == 'D':
                                self.clause([neg(self.OCC[j, u]), neg(xo), e]); continue
                            for l2 in blk: self.clause([neg(self.OCC[j, u]), neg(xo), neg(l2), e])
                            self.leafvars.setdefault((j, t, o, lo), []).append((self.OCC[j, u], xo, e))
            # ---- adhesion of moving glue
            for j in (mov if ('adh' not in self.skip and f'adh{t}' not in self.skip) else []):
                if j in R: continue
                for u in B[j]:
                    gj = self.x(j, u, 'g')
                    if gj is False: continue
                    v = sx(u, sh[j][t])
                    for d in D6:
                        nb = add(v, d)
                        for o in range(n):
                            if o == j: continue
                            uo = self.loc(o, nb, t)
                            if uo not in self.boxsets[o]: continue
                            e = esc(j, o) if o in movset else False
                            for k in self.kinds_of(o):
                                xo = X[o, uo, k]
                                if k == 'g':
                                    self.clause([neg(gj), neg(xo), neg(self.mateq[j, o]), e])
                                elif pinfo(k) is not None:
                                    p = kphase(k, t, NS)
                                    if p in ('hold', 'ret'): continue
                                    if p == 'fire':
                                        if k[0] == 'P':
                                            init = self.x(j, self.loc(j, add(nb, E), t), 'g')
                                            self.forbid(gj, xo, neg(init))
                                        else:
                                            self.forbid(gj, xo)
                                        continue
                                    if self.leaf and o in movset:
                                        self.leafvars.setdefault((j, t, o, uo), []).append((gj, xo, e)); continue
                                    self.clause([neg(gj), neg(xo), e])
                                else:
                                    if self.leaf and o in movset and k[0] != 'D':
                                        self.leafvars.setdefault((j, t, o, uo), []).append((gj, xo, e)); continue
                                    self.clause([neg(gj), neg(xo), e])
        # ---- connectivity + attachment
        for s in (range(n) if 'conn' not in self.skip else []):
            if s in R:
                m.Add(sum(self.OCC[s, u] for u in B[s]) == 1); continue
            root = {u: m.NewBoolVar('') for u in B[s]}
            m.AddExactlyOne(root.values())
            dist = {u: m.NewIntVar(0, max(self.maxglue, len(B[s])) if s in self.fixedset else self.maxglue, '') for u in B[s]}
            for u in B[s]:
                g = X[s, u, 'g']
                m.AddImplication(root[u], g)
                m.Add(dist[u] == 0).OnlyEnforceIf(root[u])
                pars = []
                nbs = [add(u, d) for d in D6 if add(u, d) in self.boxsets[s]]
                for nb in nbs:
                    p = m.NewBoolVar('')
                    m.AddImplication(p, X[s, nb, 'g'])
                    m.Add(dist[nb] + 1 <= dist[u]).OnlyEnforceIf(p)
                    pars.append(p)
                m.AddBoolOr(pars + [root[u], g.Not()])
                for k in self.kinds_of(s):
                    if k == 'g': continue
                    m.AddBoolOr([X[s, u, k].Not()] + [X[s, nb, 'g'] for nb in nbs])
            if s not in self.fixedset: m.Add(sum(X[s, u, 'g'] for u in B[s]) <= self.maxglue)
        # ---- loads
        self.size = [sum(self.OCC[s, u] for u in B[s]) for s in range(n)]
        if self.maxsize is not None:
            for s in range(n):
                if self.maxsize[s] is not None: m.Add(self.size[s] <= self.maxsize[s])
        self.loadexpr = {}
        for t in range(NS):
            nr = [s for s in range(n) if self.moves(s, t) and s not in R]
            base = {}
            for j in nr:
                byleaf = {}
                for (jj, tt, o, uo), prs in self.leafvars.items():
                    if jj == j and tt == t: byleaf.setdefault((o, uo), []).extend(prs)
                extra = []
                for prs in byleaf.values():
                    lv = self.OR([self.AND(a, b, neg(e)) for a, b, e in prs])
                    if lv is not False: extra.append(lv)
                base[j] = self.size[j] + sum(v for (tt, r, jj), v in self.rc.items() if tt == t and jj == j) + sum(extra)
            for j in nr:
                mls = [v for (tt, a, b), v in self.mg.items() if tt == t and j in (a, b)]
                if any(v is True for v in mls): continue
                self.loadexpr[j, t] = base[j]
                if self.L is None or j in self.open: continue
                m.Add(base[j] <= self.L)
            for (tt, a, b), v in self.mg.items():
                if tt != t: continue
                self.loadexpr[(a, b), t] = base[a] + base[b]
                if self.L is None: continue
                m.Add(base[a] + base[b] <= self.L)

    def hint(self, sol):
        by = {nm: (cells, mat) for nm, w, cells, mat in sol}
        for s in range(self.n):
            if self.names[s] not in by or s in self.fixedset: continue
            cells, mat = by[self.names[s]]
            for u in self.boxes[s]:
                for k in self.kinds_of(s):
                    self.m.AddHint(self.X[s, u, k], 1 if cells.get(u) == k else 0)
            if mat is not None: self.m.AddHint(self.mat[s], 1 if mat == 'honey' else 0)

    def solve(self, time_limit=600, workers=6, log=False, objective=None, assumptions=None):
        if objective == 'maxload':
            z = self.m.NewIntVar(0, 60, 'maxload')
            for e in self.loadexpr.values(): self.m.Add(z >= e)
            self.m.Minimize(z)
        elif objective == 'blocks':
            self.m.Minimize(sum(self.size))
        elif objective == 'softcause':
            self.m.Maximize(sum(self.softcause.values()))
        elif objective is not None:
            self.m.Minimize(objective)
        if assumptions: self.m.AddAssumptions(assumptions)
        sv = cp_model.CpSolver()
        sv.parameters.max_time_in_seconds = time_limit
        sv.parameters.num_search_workers = workers
        sv.parameters.log_search_progress = log
        t0 = time.time()
        st = sv.Solve(self.m)
        self.solver = sv
        return sv.StatusName(st), time.time() - t0

    def extract(self):
        sv = self.solver
        segs = []
        for s in range(self.n):
            cells = {}
            for u in self.boxes[s]:
                for k in self.kinds_of(s):
                    if sv.Value(self.X[s, u, k]): cells[u] = k
            mat = 'honey' if sv.Value(self.mat[s]) else 'slime'
            segs.append((self.names[s], self.words[s], cells, mat))
        return segs

    def loads(self):
        sv = self.solver
        return {(self.names[j] if isinstance(j, int) else '+'.join(self.names[x] for x in j), t): sv.Value(e)
                for (j, t), e in self.loadexpr.items()}

    def causes(self):
        sv = self.solver; out = []
        for (j, t), lst in self.cause_lits.items():
            for l, s, k in lst:
                if sv.Value(l): out.append((t, self.names[j], 'push' if k[0] == 'P' else 'pull', self.names[s], k))
        for (t, r, j), v in self.rc.items():
            if sv.Value(v): out.append((t, self.names[r], 'ride', self.names[j], ''))
        return sorted(out)


# ---------------------------------------------------------------- export / helpers
def to_flyer(sol, limit, NS):
    from fastflyer import Flyer, Block, Kind
    f = Flyer(); f.push_limit = limit
    mats = {'slime': Kind.SLIME, 'honey': Kind.HONEY}
    for nm, word, cells, mat in sol:
        for c, k in cells.items():
            if k == 'g': b = Block(mats[mat])
            elif k == 'R': b = Block(Kind.REDSTONE_BLOCK)
            elif k[0] == 'D': b = Block.rod(int(k[1]))
            elif k[0] == 'O': b = Block.observer(int(k[1]), powered=((NS - 1) in word))
            elif pinfo(k):
                typ, fs, h = pinfo(k)
                ph = kphase(k, 0, NS)
                ext = ph in ('hold', 'ret')
                b = Block.piston(0 if typ == 'P' else 1, sticky=(typ == 'S'), state=2 if ext else 0)
                if ext:
                    a = add(c, E if typ == 'P' else W)
                    f.set(a, Block(Kind.PISTON_ARM))
            else: raise ValueError(k)
            f.set(c, b)
    return f


def convert4(sol):
    """old satflyer (NS=4) solution -> per-piston-fire-slot kinds."""
    out = []
    for nm, w, cells, mat in sol:
        fs = fire_slots(w, 4)
        c2 = {}
        for c, k in cells.items():
            ks = k if isinstance(k, str) else f'{k[0]}{k[1]}'
            if ks in ('P', 'S'): ks = f'{ks}{fs[0]}'
            c2[c] = ks
        out.append((nm, tuple(w), c2, mat))
    return out


def show(sol):
    out = []
    for nm, w, cells, mat in sol:
        out.append(f'{nm} word={w} {mat} n={len(cells)}: ' + ' '.join(f'{c}{k}' for c, k in sorted(cells.items())))
    return '\n'.join(out)


def check_fixed(sol, NS, L=None, riders=(), merges=(), workers=4, tl=120, leaf=True):
    fixed = [(c, m) for nm, w, c, m in sol]
    kinds = sorted({k for _, _, c, _ in sol for k in c.values() if pinfo(k) is None} | {'g', 'R'})
    M = FlyerSAT([w for _, w, _, _ in sol], None, L, NS=NS, kinds=kinds, leaf=leaf, maxglue=30, fixed=fixed,
                 names=[nm for nm, *_ in sol], riders=riders, merges=merges, holds=(1, 2))
    st, dt = M.solve(tl, workers)
    return st, M
