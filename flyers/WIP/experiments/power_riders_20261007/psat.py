"""[power_riders_20261007 copy of rigid_sat_20261004/satflyer.py]  Changes: riders may be ANY single block kind
(P, S = hand-off pistons; R, D<d>, O<d> = POWER RIDERS) via kinds_by_seg; a rider's obstruction pushes into co-moving
leaves are now charged to the rider's carrier (the original ignored rider leaf loads); leafrod=True also lets rods be
dragged/pushed leaves (verified by fixture.py cases C/D).  Non-piston riders get no 'extended piston' escape: any
moving glue that touches them must be their carrier (or a co-moving leaf drag, counted).

Exact CP-SAT search for rigid-segment 2.5 bps flyers (8-tick cycle = 4 slots of 2 ticks).

Every segment is a rigid set of blocks that moves +1 X in exactly the slots of its word (two of the four slots);
every piston rides its own segment. The solver places blocks for ALL segments in a world box (slot-0 frame) and
decides who pushes / pulls whom. Rules mirror rigid_chain_20261003/rigid.py check() (see RESEARCH_LOG piston guide),
with one stricter rule: among firing pistons only the INITIATING pusher may touch the moved segment's glue (another
firing piston on the same carrier could be dragged before it fires = race).

Kinds: 'g' glue (segment material), 'P' pusher +X, 'S' sticky -X, 'R' redstone block,
       'D<d>' lightning rod facing d, 'O<d>' observer facing d (d: 0 +X, 1 -X, 2 +Y, 3 -Y, 4 +Z, 5 -Z).
Timing: a piston fires at its segment's fire slot k (segment still at k, k+1) and is extended at k+1.
  pusher at k: front cell = glue of a segment moving at k (push).  sticky: extends at k, pulls at k+1 the glue
  two cells ahead (-X) of a segment moving at k+1.  Power must be present exactly at k.
Power: redstone/rod soft-power the 6 neighbours; rods (always) and observers (only in the slot after their segment
  moved) hard-power the glue they face, which powers its 6 neighbours; an observer facing a piston powers it.
  A piston ignores a source in its own front cell.
Races (random piston order): no mover may move into any occupied cell; a mover's glue must not touch a foreign
  block unless it is opposite-material glue, an extended (ret-phase) piston, the initiating pusher, or (leaf=True)
  a non-glue, non-rod, non-firing block of another segment moving in the same slot (counted in the load).
  leaf=True also allows a mover to push such a co-moving leaf ahead as an obstruction (its destination must be empty;
  counted in the load) -- verified in the real simulator by leafpush_test.py.

usage (CLI): python satflyer.py WORDS L XR YR ZR [--leaf] [--kinds g,P,S,R] [--time 600] [--workers 16] [--out DIR]
  WORDS e.g. mmww,wwmm,mmww,wwmm ; XR e.g. m3:6 = -3..6 inclusive (m = minus)
"""
import sys, pathlib, time, os, itertools, pickle, argparse
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from ortools.sat.python import cp_model

D6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
E, W = (1, 0, 0), (-1, 0, 0)
WORDS = {'mmww': (0, 1), 'wwmm': (2, 3), 'wmmw': (1, 2), 'mwwm': (0, 3), 'mwmw': (0, 2), 'wmwm': (1, 3)}


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sx(a, dx): return (a[0] + dx, a[1], a[2])
def wpos(word, t): return sum(1 for m in word if m < t)


def fire_slot(word):
    for k in range(4):
        if k not in word and (k + 1) % 4 not in word: return k
    return None


def phase(word, t):
    k = fire_slot(word)
    if k is None: return 'idle'
    if t % 4 == k: return 'fire'
    if t % 4 == (k + 1) % 4: return 'ret'
    return 'idle'


def neg(l):
    if l is True: return False
    if l is False: return True
    return l.Not()


class Infeasible(Exception):
    pass


class FlyerSAT:
    def __init__(self, words, box, L, kinds=('g', 'P', 'S', 'R'), leaf=False, maxglue=6, anchor=None,
                 open_segs=(), fixed=None, names=None, boxes=None, maxsize=None, skip=(), merges=(), must=None,
                 automerge=False, mergeable=None, riders=(), kinds_by_seg=None, leafrod=False):
        """box: shared candidate cells (slot-0 world frame); boxes: optional per-segment candidate cells (overrides).
        fixed: list per segment of (cells dict world->kind, mat) or None (free); a fixed segment's box = its cells.
        maxsize: optional per-segment cap on block count (list) in addition to the load cap L."""
        self.m = m = cp_model.CpModel()
        self.words = [WORDS[w] if isinstance(w, str) else tuple(w) for w in words]
        self.n = n = len(self.words)
        self.names = names or [f's{i}' for i in range(n)]
        self.kinds = list(kinds); self.leaf = leaf; self.leafrod = leafrod; self.L = L; self.maxglue = maxglue
        # riders: single-piston segments with no glue (hand-off pistons); each move rides exactly one carrier
        self.riders = {self.names.index(x) if isinstance(x, str) else x for x in riders}
        # automerge: the solver may merge any co-moving pair of non-riders (restricted to `mergeable` pairs if given)
        self.automerge = automerge
        self.kinds_by_seg = {self.names.index(k) if isinstance(k, str) else k: list(v) for k, v in (kinds_by_seg or {}).items()}
        self.mergeable = None if mergeable is None else {tuple(self.names.index(x) if isinstance(x, str) else x for x in p) for p in mergeable}
        # open_segs: {index: flags} or a plain set (= all flags). flags: 'pow' (no power checks), 'powmiss' (power may
        # come from outside: skip 'must be powered', keep 'no extra power'), 'Ptarget'/'Starget' (pusher/sticky targets
        # are outside), 'cause_le1' (<=1 cause per move), 'ext_push'/'ext_pull' (first/second move caused outside: 0 here)
        if isinstance(open_segs, dict): self.oflags = {k: set(v) for k, v in open_segs.items()}
        else: self.oflags = {k: {'pow', 'Ptarget', 'Starget', 'cause_le1'} for k in open_segs}
        self.open = set(self.oflags)
        self.boxes = []
        for s in range(n):
            if fixed is not None and fixed[s] is not None: b = list(fixed[s][0])
            elif boxes is not None and boxes[s] is not None: b = list(boxes[s])
            else: b = list(box)
            self.boxes.append(b)
        self.boxsets = [set(b) for b in self.boxes]
        self.fixedset = {s for s in range(n) if fixed is not None and fixed[s] is not None}
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
        if fixed is not None:
            self.fix(fixed)
        if not self.fixedset:
            m.Add(self.mat[0] == 0)
        if anchor is not None: m.Add(self.X[0, anchor, 'g'] == 1)
        for s_, cells in (must or {}).items():     # required blocks of a free segment: {seg: {cell: kind}}
            si = self.names.index(s_) if isinstance(s_, str) else s_
            for c, k in cells.items(): m.Add(self.X[si, c, k] == 1)
        self.maxsize = maxsize
        # merges: [(slot, [seg, seg])]: those co-moving segments move as ONE group in that slot (one cause; the
        # receiver must carry the partner by obstruction (a block right behind the partner's glue) or by same-material
        # glue contact; load = sum). Deterministic single action, e.g. a double push/pull end cap.
        self.merges = [(t, [self.names.index(x) if isinstance(x, str) else x for x in g]) for t, g in merges]
        self.skip = set(skip)   # debug: rule families to leave out ('power','targets','cause','move','adh','conn')
        self.sh = [[wpos(self.words[s], t) for t in range(4)] for s in range(n)]
        self.ph = [[phase(self.words[s], t) for t in range(4)] for s in range(n)]
        self.build()

    # ---------- helpers
    def kinds_of(self, s):
        if s in self.kinds_by_seg:
            return self.kinds_by_seg[s]
        if s in self.riders:
            return [k for k in self.kinds if k in ('P', 'S')]
        if fire_slot(self.words[s]) is None:
            return [k for k in self.kinds if k not in ('P', 'S')]
        return self.kinds

    def x(self, s, u, k): return self.X.get((s, u, k), False)
    def occ(self, s, u): return self.OCC.get((s, u), False)
    def loc(self, s, v, t): return (v[0] - self.sh[s][t], v[1], v[2])

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
        """fixed: list per segment of (cells dict world->kind, mat) or None (free)."""
        for s, f in enumerate(fixed):
            if f is None: continue
            cells, mat = f
            for u in self.boxes[s]:
                for k in self.kinds_of(s):
                    self.m.Add(self.X[s, u, k] == (1 if cells.get(u) == k else 0))
            if mat is not None: self.m.Add(self.mat[s] == (1 if mat == 'honey' else 0))

    # ---------- constraints
    def build(self):
        m, n, X = self.m, self.n, self.X
        sh, ph = self.sh, self.ph
        B = self.boxes
        R = self.riders
        self.leafvars = {}
        self.softcause = {}
        self.mg = {}      # (t, a, b) a<b non-riders -> merge literal (True if planned)
        self.rc = {}      # (t, r, j) rider r carried by non-rider j
        for t in range(4):
            mov = [s for s in range(n) if t in self.words[s]]
            movset = set(mov)
            nr = [s for s in mov if s not in R]
            # ---- merge / carry literals
            planned = {tuple(sorted(g)) for tt, g in self.merges if tt == t}
            for a, b in planned: assert a in movset and b in movset, (t, a, b)
            for i, a in enumerate(nr):
                for b in nr[i + 1:]:
                    if (a, b) in planned: self.mg[t, a, b] = True
                    elif self.automerge and not any(a in p or b in p for p in planned):
                        if self.mergeable is None or (a, b) in self.mergeable or (b, a) in self.mergeable:
                            self.mg[t, a, b] = m.NewBoolVar(f'mg{t}_{a}_{b}')
            for a in nr:
                ls = [v for (tt, x_, y_), v in self.mg.items() if tt == t and a in (x_, y_) and v is not True]
                if len(ls) > 1: m.AddAtMostOne(ls)
            for r in [s for s in mov if s in R]:
                ls = []
                for j in nr:
                    v = m.NewBoolVar(f'rc{t}_{r}_{j}'); self.rc[t, r, j] = v; ls.append(v)
                if not ls: raise Infeasible('rider with no carrier')
                m.AddExactlyOne(ls)

            def esc(a, b, t=t):
                """literal that excuses an a-b interaction in slot t (merged pair / rider carried), else False."""
                if a in R and b in R: return False
                if a in R: return self.rc.get((t, a, b), False)
                if b in R: return self.rc.get((t, b, a), False)
                return self.mg.get((t, min(a, b), max(a, b)), False)

            world = {}
            for s in range(n):
                for u in B[s]:
                    world.setdefault(sx(u, sh[s][t]), []).append((s, u))
            arms = {}
            for s in range(n):
                if ph[s][t] != 'ret': continue
                for u in B[s]:
                    v = sx(u, sh[s][t])
                    for k, d in (('P', E), ('S', W)):
                        l = self.x(s, u, k)
                        if l is not False: arms.setdefault(add(v, d), []).append(l)
            for v, lst in world.items():
                lits = [self.OCC[s, u] for s, u in lst] + arms.get(v, [])
                if len(lits) > 1: m.AddAtMostOne(lits)
            for v, al in arms.items():
                if v not in world and len(al) > 1: m.AddAtMostOne(al)
            # ---- power
            soft = {}; hotsrc = {}; obs_p = {}
            for s in range(n):
                pulsing = ((t - 1) % 4) in self.words[s]
                for u in B[s]:
                    v = sx(u, sh[s][t])
                    for k in self.kinds_of(s):
                        if k == 'R' or k[0] == 'D':
                            soft.setdefault(v, []).append(X[s, u, k])
                        if k[0] in 'DO' and len(k) == 2:
                            if k[0] == 'O' and not pulsing: continue
                            f = add(v, D6[int(k[1])])
                            hotsrc.setdefault(f, []).append(X[s, u, k])
                            if k[0] == 'O': obs_p.setdefault(f, []).append((X[s, u, k], v))
            hot = {}
            for f, srcs in hotsrc.items():
                gl = [X[o, self.loc(o, f, t), 'g'] for o in range(n) if (o, self.loc(o, f, t), 'g') in X]
                if gl: hot[f] = self.AND(self.OR(srcs), self.OR(gl))
            for s in range(n):
                fl = self.oflags.get(s, ())
                if 'pow' in fl or 'power' in self.skip: continue
                for u in B[s]:
                    v = sx(u, sh[s][t])
                    for k, fd in (('P', E), ('S', W)):
                        xp = self.x(s, u, k)
                        if xp is False: continue
                        front = add(v, fd)
                        srcs = []
                        for d in D6:
                            nb = add(v, d)
                            if nb == front: continue
                            srcs += soft.get(nb, [])
                            if nb in hot: srcs.append(hot[nb])
                        srcs += [ol for ol, ov in obs_p.get(v, []) if ov != front]
                        if ph[s][t] == 'fire':
                            if 'powmiss' not in fl: self.clause([neg(xp)] + srcs)
                        else:
                            for l in srcs: self.forbid(xp, l)
            # ---- piston actions
            for s in range(n):
                if 'targets' in self.skip: break
                if ph[s][t] == 'fire':
                    for u in B[s]:
                        v = sx(u, sh[s][t])
                        xp = self.x(s, u, 'P')
                        if xp is not False and 'Ptarget' not in self.oflags.get(s, ()):
                            f = add(v, E)
                            self.clause([neg(xp)] + [self.x(o, self.loc(o, f, t), 'g') for o in mov if o != s])
                        xs = self.x(s, u, 'S')
                        if xs is not False:
                            f = add(v, W)
                            for o in range(n): self.forbid(xs, self.occ(o, self.loc(o, f, t)))
                            for al in arms.get(f, []): self.forbid(xs, al)
                            for j in mov: self.forbid(xs, self.occ(j, self.loc(j, add(f, W), t)))
                if ph[s][t] == 'ret' and 'Starget' not in self.oflags.get(s, ()):
                    for u in B[s]:
                        xs = self.x(s, u, 'S')
                        if xs is False: continue
                        tc = add(sx(u, sh[s][t]), (-2, 0, 0))
                        self.clause([neg(xs)] + [self.x(o, self.loc(o, tc, t), 'g') for o in mov if o != s])
            # ---- causes: every non-rider mover gets exactly one cause unless merged (then one per pair)
            recv = {}; csum = {}
            for j in nr:
                pj = []
                for u in B[j]:
                    gj = X[j, u, 'g']
                    w = sx(u, sh[j][t])
                    for s in range(n):
                        if s == j: continue
                        if ph[s][t] == 'fire':
                            l = self.x(s, self.loc(s, add(w, W), t), 'P')
                            if l is not False: pj.append(self.AND(gj, l))
                        elif ph[s][t] == 'ret':
                            l = self.x(s, self.loc(s, add(w, (2, 0, 0)), t), 'S')
                            if l is not False: pj.append(self.AND(gj, l))
                pj = [p for p in pj if p is not False]
                csum[j] = sum(pj); recv[j] = self.OR(pj)
                if pj: m.Add(csum[j] <= 1)
            if 'cause' not in self.skip:
                for j in nr:
                    fl = self.oflags.get(j, ())
                    first = (t == min(self.words[j]))
                    mls = [v for (tt, x_, y_), v in self.mg.items() if tt == t and j in (x_, y_)]
                    if any(v is True for v in mls): continue                     # planned merge: handled per pair below
                    merged = self.OR(mls)
                    if ('ext_push' in fl and first) or ('ext_pull' in fl and not first):
                        m.Add(csum[j] == 0); continue
                    if 'cause_le1' in fl: continue
                    if 'softcause' in self.skip:
                        b = m.NewBoolVar(f'cause_{j}_{t}'); self.softcause[j, t] = b
                        m.Add(csum[j] == 1).OnlyEnforceIf(b); continue
                    if merged is False: m.Add(csum[j] == 1)
                    else: m.Add(csum[j] == 1).OnlyEnforceIf(neg(merged))
                for (tt, a, b), v in list(self.mg.items()):
                    if tt != t: continue
                    if v is True: m.Add(csum[a] + csum[b] == 1)
                    else: m.Add(csum[a] + csum[b] == 1).OnlyEnforceIf(v)
                    for r_, o_ in ((a, b), (b, a)):
                        bl = []
                        for u in B[r_]:
                            dw = sx(u, sh[r_][t] + 1)
                            l = self.x(o_, self.loc(o_, dw, t), 'g')
                            if l is not False: bl.append(self.AND(self.OCC[r_, u], l))
                            for d in D6:
                                l = self.x(o_, self.loc(o_, add(sx(u, sh[r_][t]), d), t), 'g')
                                if l is not False: bl.append(self.AND(X[r_, u, 'g'], l, self.mateq[r_, o_]))
                        bind = self.OR(bl)
                        # merged and r_ receives the cause -> r_ must carry o_ (obstruction or same-material glue)
                        self.clause(([] if v is True else [neg(v)]) + [neg(recv[r_]), bind])
            # rider binding: carrier's glue touches the rider, or a carrier block is right behind it
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
            # ---- movement into occupied cells
            for j in (mov if 'move' not in self.skip else []):
                for u in B[j]:
                    d = sx(u, sh[j][t] + 1)
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
                            if k == 'g' or (k[0] == 'D' and not self.leafrod):
                                self.clause([neg(self.OCC[j, u]), neg(xo), e]); continue
                            for l2 in blk: self.clause([neg(self.OCC[j, u]), neg(xo), neg(l2), e])
                            self.leafvars.setdefault((j, t, o, lo), []).append((self.OCC[j, u], xo, e))
            # ---- adhesion of moving glue
            for j in (mov if 'adh' not in self.skip else []):
                if j in R: continue
                for u in B[j]:
                    gj = X[j, u, 'g']
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
                                elif k in ('P', 'S'):
                                    if ph[o][t] == 'ret': continue
                                    if ph[o][t] == 'fire':
                                        if k == 'P':
                                            init = self.x(j, self.loc(j, add(nb, E), t), 'g')
                                            self.forbid(gj, xo, neg(init))
                                        else:
                                            self.forbid(gj, xo)
                                        continue
                                    if self.leaf and o in movset:
                                        self.leafvars.setdefault((j, t, o, uo), []).append((gj, xo, e)); continue
                                    self.clause([neg(gj), neg(xo), e])
                                else:
                                    if self.leaf and o in movset and (k[0] != 'D' or self.leafrod):
                                        self.leafvars.setdefault((j, t, o, uo), []).append((gj, xo, e)); continue
                                    self.clause([neg(gj), neg(xo), e])
        # ---- connectivity (glue tree rooted at one glue cell) + attachment; riders = exactly one piston, no glue
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
        # ---- loads: group = non-rider (or merged pair) + riders it carries + dragged/pushed leaves
        self.size = [sum(self.OCC[s, u] for u in B[s]) for s in range(n)]
        if self.maxsize is not None:
            for s in range(n):
                if self.maxsize[s] is not None: m.Add(self.size[s] <= self.maxsize[s])
        self.loadexpr = {}
        for t in range(4):
            nr = [s for s in range(n) if t in self.words[s] and s not in R]
            base = {}
            for j in nr:
                byleaf = {}
                for (jj, tt, o, uo), prs in self.leafvars.items():
                    if jj == j and tt == t: byleaf.setdefault((o, uo), []).extend(prs)
                extra = []
                for prs in byleaf.values():
                    lv = self.OR([self.AND(a, b, neg(e)) for a, b, e in prs])
                    if lv is not False: extra.append(lv)
                for (jj, tt, o, uo), prs in self.leafvars.items():      # leaves pushed by a rider this carrier carries
                    if tt != t or jj not in R: continue
                    rcv = self.rc.get((t, jj, j))
                    if rcv is None: continue
                    lv = self.OR([self.AND(a, b, neg(e), rcv) for a, b, e in prs])
                    if lv is not False: extra.append(lv)
                base[j] = self.size[j] + sum(v for (tt, r, jj), v in self.rc.items() if tt == t and jj == j) + sum(extra)
            for j in nr:
                mls = [v for (tt, a, b), v in self.mg.items() if tt == t and j in (a, b)]
                if any(v is True for v in mls): continue
                merged = self.OR(mls)
                self.loadexpr[j, t] = base[j]
                if self.L is None or j in self.open: continue
                if merged is False: m.Add(base[j] <= self.L)
                else: m.Add(base[j] <= self.L).OnlyEnforceIf(neg(merged))
            for (tt, a, b), v in self.mg.items():
                if tt != t: continue
                self.loadexpr[(a, b), t] = base[a] + base[b]
                if self.L is None: continue
                if v is True: m.Add(base[a] + base[b] <= self.L)
                else: m.Add(base[a] + base[b] <= self.L).OnlyEnforceIf(v)

    def hint(self, sol):
        """Warm start from a solution [(name, word, cells, mat)] (cells may use kinds like ('O',2)); unknown names skipped."""
        by = {nm: (cells, mat) for nm, w, cells, mat in sol}
        for s in range(self.n):
            if self.names[s] not in by or s in self.fixedset: continue
            cells, mat = by[self.names[s]]
            cs = {c: (k if isinstance(k, str) else f'{k[0]}{k[1]}') for c, k in cells.items()}
            for u in self.boxes[s]:
                for k in self.kinds_of(s):
                    self.m.AddHint(self.X[s, u, k], 1 if cs.get(u) == k else 0)
            if mat is not None: self.m.AddHint(self.mat[s], 1 if mat == 'honey' else 0)

    # ---------- solve / extract
    def solve(self, time_limit=600, workers=16, log=False, objective=None, hint=None):
        if objective == 'maxload':
            z = self.m.NewIntVar(0, 50, 'maxload')
            for e in self.loadexpr.values(): self.m.Add(z >= e)
            self.m.Minimize(z)
        elif objective == 'blocks':
            self.m.Minimize(sum(self.size))
        elif objective == 'softcause':
            self.m.Maximize(sum(self.softcause.values()))
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
                    if sv.Value(self.X[s, u, k]):
                        cells[u] = k if len(k) == 1 else (k[0], int(k[1]))
            mat = 'honey' if sv.Value(self.mat[s]) else 'slime'
            segs.append((self.names[s], self.words[s], cells, mat))
        return segs


def to_rigid(sol):
    import rigid
    return [rigid.Seg(nm, w, (0, 0, 0), cells, mat) for nm, w, cells, mat in sol]


def show(sol):
    out = []
    for nm, w, cells, mat in sol:
        out.append(f'{nm} word={w} {mat} n={len(cells)}: ' + ' '.join(f'{c}{k}' for c, k in sorted(cells.items())))
    return '\n'.join(out)


def parse_range(s):
    a, b = s.replace('m', '-').split(':'); return range(int(a), int(b) + 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('words'); ap.add_argument('L', type=int)
    ap.add_argument('xr'); ap.add_argument('yr'); ap.add_argument('zr')
    ap.add_argument('--leaf', action='store_true')
    ap.add_argument('--kinds', default='g,P,S,R')
    ap.add_argument('--time', type=float, default=600)
    ap.add_argument('--workers', type=int, default=16)
    ap.add_argument('--maxglue', type=int, default=6)
    ap.add_argument('--out', default=None)
    ap.add_argument('--log', action='store_true')
    a = ap.parse_args()
    box = list(itertools.product(parse_range(a.xr), parse_range(a.yr), parse_range(a.zr)))
    anchor = (0, 0, 0) if (0, 0, 0) in box else None
    t0 = time.time()
    M = FlyerSAT(a.words.split(','), box, a.L, kinds=a.kinds.split(','), leaf=a.leaf, maxglue=a.maxglue, anchor=anchor)
    print(f'built in {time.time() - t0:.1f}s', flush=True)
    st, dt = M.solve(a.time, a.workers, log=a.log)
    print('status', st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract()
        print(show(sol))
        import rigid
        os.environ.setdefault('LEAF', '1' if a.leaf else '')
        rigid.LEAF = a.leaf
        segs = to_rigid(sol)
        print('rigid.check:', rigid.check(segs), 'loads:', rigid.loads(segs))
        if a.out:
            od = pathlib.Path(a.out); od.mkdir(parents=True, exist_ok=True)
            tag = f"{a.words.replace(',', '_')}_L{a.L}_{int(time.time())}"
            pickle.dump(sol, open(od / f'{tag}.pkl', 'wb'))
            rigid.to_flyer(segs, a.L).save(str(od / f'{tag}.flyer'))
            print('saved', od / f'{tag}.flyer')
