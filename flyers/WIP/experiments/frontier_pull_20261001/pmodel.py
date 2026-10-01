"""Generalised space-time item model + legality checker (agent G), derived from agent F's
speed_range_b_20260930/mmwpull/model.py (3 bodies, period 6) -> N bodies, period L, any schedule.

A schedule `sch` has: L (slots per cycle), S[b][t] (body b moves in slot t), DISP[b][t].
Items have slot-start positions pos[0..L-1]; pos[L] = pos[0] + ADV.
Rules: occupancy, move destinations, arm cells, same-type glue merging, designated carriers,
order hazard (moving glue touching a piston that fires in that slot), foreign sources,
exact power (each piston powered at slot start iff it is its fire slot).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind

DIRS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
E, Wd, U, D, Sd, N = range(6)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sx(a, d):
    return (a[0] + d, a[1], a[2])


def nb(p):
    return [add(p, d) for d in DIRS]


class Sched:
    def __init__(self, S):
        self.S = [tuple(r) for r in S]
        self.L = len(S[0])
        self.N = len(S)
        self.ADV = sum(S[0])
        assert all(sum(r) == self.ADV for r in S)
        self.DISP = [[sum(r[:t]) for t in range(self.L + 1)] for r in S]


class Item:
    __slots__ = ('cat', 'body', 'gtype', 'pos', 'mv', 'name', 'f', 'face', 'sticky', 'odir', 'victim')

    def __init__(self, cat, pos, mv, body=None, gtype=None, name='', f=None, face=0, sticky=False, odir=None, victim=None):
        self.cat = cat; self.pos = pos; self.mv = mv; self.body = body; self.gtype = gtype; self.name = name
        self.f = f; self.face = face; self.sticky = sticky; self.odir = odir; self.victim = victim


class Design:
    def __init__(self, sch, gtypes):
        self.sch = sch
        self.L = sch.L
        self.items = []
        self.gtypes = gtypes
        self.carry = {}
        self.occ = [dict() for _ in range(self.L)]

    def glue(self, b, p0):
        sch = self.sch
        return Item('glue', [sx(p0, sch.DISP[b][t]) for t in range(self.L)], [bool(sch.S[b][t]) for t in range(self.L)],
                    body=b, gtype=self.gtypes[b])

    def src(self, cat, b, p0, odir=None, name=''):
        sch = self.sch
        return Item(cat, [sx(p0, sch.DISP[b][t]) for t in range(self.L)], [bool(sch.S[b][t]) for t in range(self.L)],
                    body=b, odir=odir, name=name)

    def add_item(self, it):
        idx = len(self.items)
        self.items.append(it)
        for t in range(self.L):
            self.occ[t][it.pos[t]] = idx
        if it.cat == 'piston':
            t = (it.f + 1) % self.L
            self.occ[t][sx(it.pos[t], it.face)] = -1 - idx
        return idx

    def pop_last(self):
        idx = len(self.items) - 1
        it = self.items.pop()
        for t in range(self.L):
            if self.occ[t].get(it.pos[t]) == idx:
                del self.occ[t][it.pos[t]]
        if it.cat == 'piston':
            t = (it.f + 1) % self.L
            c = sx(it.pos[t], it.face)
            if self.occ[t].get(c) == -1 - idx:
                del self.occ[t][c]
        for k in [k for k in self.carry if k[0] == idx]:
            del self.carry[k]

    def group(self, idx, t):
        it = self.items[idx]
        if it.cat == 'piston':
            return self.carry.get((idx, t))
        return it.body

    def arm_ext(self, t):
        out = {}
        for i, it in enumerate(self.items):
            if it.cat == 'piston' and it.f == t:
                out[sx(it.pos[t], it.face)] = i
        return out

    def item_errors(self, it, idx=None, arm_cache=None):
        L = self.L
        errs = []
        for t in range(L):
            p = it.pos[t]
            o = self.occ[t].get(p)
            if o is not None and o != idx:
                errs.append(('occ', t, p)); continue
            ext = arm_cache[t] if arm_cache else self.arm_ext(t)
            mine = self.items_group(it, idx, t)
            if it.mv[t]:
                d = sx(p, 1)
                o = self.occ[t].get(d)
                if o is not None and o != idx:
                    if o < 0:
                        k = self.items[-1 - o]
                        if not (k.sticky and (k.f + 1) % L == t and k.victim == mine):
                            errs.append(('dest_arm', t, d))
                    else:
                        ob = self.items[o]
                        if not ob.mv[t]:
                            errs.append(('dest_static', t, d))
                        elif self.group(o, t) != mine or mine is None:
                            errs.append(('dest_foreign_moving', t, d))
                if d in ext and ext[d] != idx:
                    errs.append(('dest_armext', t, d))
                if p in ext and ext[p] != idx:
                    k = self.items[ext[p]]
                    if k.sticky or k.victim != mine:
                        errs.append(('in_armext', t, p))
                o = self.occ[t].get(sx(p, -1))
                if o is not None and o >= 0 and o != idx and self.items[o].cat != 'piston' and self.items[o].mv[t] and self.items[o].body != mine:
                    errs.append(('behind_foreign_moving', t, p))
                if it.cat == 'glue':
                    o = self.occ[t].get(sx(p, -1))
                    if o is not None and o >= 0 and o != idx and self.items[o].cat == 'piston' and self.items[o].mv[t]:
                        k = self.items[o]
                        if self.carry.get((o, t)) != it.body:
                            errs.append(('front_of_piston', t, p))
                        else:
                            for q in nb(k.pos[t]):
                                oo = self.occ[t].get(q)
                                if oo is not None and oo >= 0 and self.items[oo].cat == 'glue' and self.items[oo].mv[t] and self.items[oo].body != it.body:
                                    errs.append(('front_of_raced_piston', t, p))
            else:
                if p in ext and ext[p] != idx:
                    errs.append(('static_in_armext', t, p))
                o = self.occ[t].get(sx(p, -1))
                if o is not None and o >= 0 and o != idx and self.items[o].mv[t]:
                    errs.append(('hit_by_mover', t, p))
            for q in nb(p):
                o = self.occ[t].get(q)
                if o is None or o == idx or o < 0:
                    continue
                ob = self.items[o]
                if it.cat == 'glue' and ob.cat == 'glue':
                    if ob.body != it.body and ob.gtype == it.gtype:
                        errs.append(('merge', t, p))
                    continue
                for g, gi, other, oi in ((it, idx, ob, o), (ob, o, it, idx)):
                    if g.cat != 'glue' or other.cat == 'glue' or not g.mv[t]:
                        continue
                    if other.cat == 'piston':
                        if other.f == t:
                            if other.sticky or other.victim != g.body:
                                errs.append(('fire_touch', t, p))
                        elif (other.f + 1) % L == t:
                            pass
                        elif oi is None or self.carry.get((oi, t)) != g.body:
                            dk = sx(other.pos[t], 1)
                            if dk in self.occ[t] or dk in (arm_cache[t] if arm_cache else self.arm_ext(t)) or (gi is None and dk == it.pos[t]):
                                errs.append(('undesignated_carry', t, p))
                    elif other.cat != 'glz':
                        if other.body != g.body:
                            errs.append(('touch_source', t, p))
        if it.cat == 'glue':
            for o in self.items:
                if o.cat == 'obs' and o.body != it.body:
                    for t in range(L):
                        if add(o.pos[t], DIRS[o.odir]) == it.pos[t]:
                            errs.append(('obs_face', t, it.pos[t]))
        return errs

    def items_group(self, it, idx, t):
        if it.cat == 'piston':
            return self.carry.get((idx, t)) if idx is not None else None
        return it.body

    def coverage_errors(self):
        L = self.L
        errs = []
        for i, it in enumerate(self.items):
            if it.cat == 'glz':
                for t in range(L):
                    if it.mv[t]:
                        o = self.occ[t].get(sx(it.pos[t], -1))
                        if o is None or o < 0 or self.items[o].cat == 'piston' or self.items[o].body != it.body:
                            errs.append(('glz_nopush', it.name, t))
            if it.cat != 'piston':
                continue
            if it.sticky:
                t = (it.f + 1) % L; c = sx(it.pos[t], 2 * it.face)
            else:
                t = it.f; c = sx(it.pos[t], it.face)
            o = self.occ[t].get(c)
            if o is None or o < 0 or self.items[o].cat != 'glue' or self.items[o].body != it.victim:
                errs.append(('nocontact', it.name, t))
            for t in range(L):
                if not it.mv[t]:
                    continue
                c = self.carry.get((i, t))
                if c is None:
                    errs.append(('nocarrier', it.name, t)); continue
                ok = False
                for q in nb(it.pos[t]) + [sx(it.pos[t], -1)]:
                    o = self.occ[t].get(q)
                    if o is not None and o >= 0 and self.items[o].cat == 'glue' and self.items[o].body == c:
                        ok = True; break
                if not ok:
                    errs.append(('uncovered', it.name, t))
        return errs

    def powered(self, t):
        S = self.sch.S; L = self.L
        out = set()
        hard = set()
        for o in self.items:
            if o.cat == 'obs' and S[o.body][(t - 1) % L]:
                hard.add(add(o.pos[t], DIRS[o.odir]))
        for i, k in enumerate(self.items):
            if k.cat != 'piston':
                continue
            front = sx(k.pos[t], k.face)
            for q in nb(k.pos[t]):
                if q == front:
                    continue
                o = self.occ[t].get(q)
                if o is None or o < 0:
                    continue
                ob = self.items[o]
                if ob.cat == 'rs':
                    out.add(i)
                elif ob.cat == 'obs' and S[ob.body][(t - 1) % L] and add(ob.pos[t], DIRS[ob.odir]) == k.pos[t]:
                    out.add(i)
                elif q in hard and ob.cat in ('glue', 'glz'):
                    out.add(i)
        return out

    def power_errors(self, only=None):
        errs = []
        for t in range(self.L):
            pw = self.powered(t)
            for i, k in enumerate(self.items):
                if k.cat == 'piston' and ((i in pw) != (k.f == t)):
                    errs.append(('power', k.name, t, i in pw))
        return errs

    def all_errors(self):
        errs = []
        cache = [self.arm_ext(t) for t in range(self.L)]
        for i, it in enumerate(self.items):
            errs += [(it.name or it.cat,) + e for e in self.item_errors(it, i, cache)]
        return errs + self.coverage_errors() + self.power_errors()

    def loads(self):
        S = self.sch.S
        out = {}
        for b in range(self.sch.N):
            g = sum(1 for it in self.items if it.cat == 'glue' and it.body == b)
            s = sum(1 for it in self.items if it.cat in ('rs', 'obs', 'glz') and it.body == b)
            for t in range(self.L):
                if S[b][t]:
                    r = 0
                    for i, k in enumerate(self.items):
                        if k.cat != 'piston' or not k.mv[t]:
                            continue
                        hit = False
                        for q in nb(k.pos[t]):
                            o = self.occ[t].get(q)
                            if o is not None and o >= 0 and self.items[o].cat == 'glue' and self.items[o].body == b:
                                hit = True; break
                        r += hit
                    out[(b, t)] = (g, s, r)
        return out

    def max_load(self):
        return max(sum(v) for v in self.loads().values())

    def glue_counts(self):
        return [sum(1 for it in self.items if it.cat == 'glue' and it.body == b) for b in range(self.sch.N)]

    def to_flyer(self, limit=1000, rng=5):
        S = self.sch.S; L = self.L
        f = Flyer(rng_state=rng, push_limit=limit)
        for it in self.items:
            p = it.pos[0]
            if it.cat == 'glue':
                f.set(p, Block(Kind.SLIME if it.gtype == 'S' else Kind.HONEY))
            elif it.cat == 'rs':
                f.set(p, Block(Kind.REDSTONE_BLOCK))
            elif it.cat == 'obs':
                f.set(p, Block.observer(it.odir, powered=bool(S[it.body][L - 1])))
            elif it.cat == 'glz':
                f.set(p, Block(Kind.GLAZED_TERRACOTTA))
            elif it.cat == 'piston':
                st = 2 if it.f == L - 1 else 0
                f.set(p, Block.piston(E if it.face == 1 else Wd, sticky=it.sticky, state=st))
                if st:
                    f.set(sx(p, it.face), Block(Kind.PISTON_ARM))
        return f


def rebuild_without(d, idx):
    nd = Design(d.sch, d.gtypes)
    remap = {}
    for i, it in enumerate(d.items):
        if i == idx:
            continue
        remap[i] = len(nd.items)
        nd.items.append(it)
    for (i, t), c in d.carry.items():
        if i in remap:
            nd.carry[(remap[i], t)] = c
    for i, it in enumerate(nd.items):
        for t in range(d.L):
            nd.occ[t][it.pos[t]] = i
        if it.cat == 'piston':
            t = (it.f + 1) % d.L
            nd.occ[t][sx(it.pos[t], it.face)] = -1 - i
    return nd


def connected_ok(d):
    for b in range(d.sch.N):
        cells = {it.pos[0] for it in d.items if it.cat == 'glue' and it.body == b}
        if not cells:
            return False
        st = [next(iter(cells))]; seen = {st[0]}
        while st:
            p = st.pop()
            for q in nb(p):
                if q in cells and q not in seen:
                    seen.add(q); st.append(q)
        if len(seen) != len(cells):
            return False
        for it in d.items:
            if it.cat in ('rs', 'obs') and it.body == b and not any(q in cells for q in nb(it.pos[0])):
                return False
    return True


def trim(d, rng=None):
    import random
    rng = rng or random.Random(0)
    changed = True
    while changed:
        changed = False
        order = [i for i, it in enumerate(d.items) if it.cat == 'glue']
        rng.shuffle(order)
        for i in order:
            nd = rebuild_without(d, i)
            if connected_ok(nd) and not nd.all_errors():
                d = nd; changed = True
                break
    return d
