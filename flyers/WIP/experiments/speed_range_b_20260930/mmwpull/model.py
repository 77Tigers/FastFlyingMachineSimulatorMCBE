"""Space-time item model + legality checker for the pull-twice mmwmmw (agent F).

Items have positions at the start of slots t=0..5 (pos[6] = pos[0] + 4 in x) and a per-slot move flag.
Rules (derived from SIMULATION.md + tonight's verified hazards):
  occupancy, move destinations, arm cells, same-type glue merging, strict adhesion designation,
  order hazard (moving glue touching a piston that fires in that slot), foreign sources,
  exact power (each piston powered at slot start iff it is its fire slot).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from fastflyer import Flyer, Block, Kind
from sched import S, DISP, W, REL, FIRE, STICKY, piston_x, fire, X_of, Z_of

DIRS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
E, Wd, U, D, Sd, N = range(6)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sx(a, d):
    return (a[0] + d, a[1], a[2])


def nb(p):
    return [add(p, d) for d in DIRS]


class Item:
    __slots__ = ('cat', 'body', 'gtype', 'pos', 'mv', 'name', 'f', 'face', 'sticky', 'odir', 'victim')

    def __init__(self, cat, pos, mv, body=None, gtype=None, name='', f=None, face=0, sticky=False, odir=None, victim=None):
        self.cat = cat; self.pos = pos; self.mv = mv; self.body = body; self.gtype = gtype; self.name = name
        self.f = f; self.face = face; self.sticky = sticky; self.odir = odir; self.victim = victim


def body_traj(p0, b):
    return [sx(p0, DISP[b][t]) for t in range(6)], [bool(S[b][t]) for t in range(6)]


class Design:
    def __init__(self, gtypes):
        self.items = []
        self.gtypes = gtypes
        self.carry = {}           # (piston item index, t) -> body
        self.occ = [dict() for _ in range(6)]     # slot-start occupancy pos -> item idx (incl arms as -1-idx)
        self.H = {}               # body -> hard-powered glue item idx

    # ---------------------------------------------------------------- construction
    def glue(self, b, p0):
        pos, mv = body_traj(p0, b)
        return Item('glue', pos, mv, body=b, gtype=self.gtypes[b])

    def add_item(self, it):
        idx = len(self.items)
        self.items.append(it)
        for t in range(6):
            self.occ[t][it.pos[t]] = idx
        if it.cat == 'piston':
            t = (it.f + 1) % 6
            self.occ[t][sx(it.pos[t], it.face)] = -1 - idx
        return idx

    def group(self, idx, t):
        it = self.items[idx]
        if it.cat == 'piston':
            return self.carry.get((idx, t))
        return it.body

    # ---------------------------------------------------------------- checks
    def arm_ext(self, t):
        """cells into which arms extend during slot t: {cell: piston idx}"""
        out = {}
        for i, it in enumerate(self.items):
            if it.cat == 'piston' and it.f == t:
                out[sx(it.pos[t], it.face)] = i
        return out

    def item_errors(self, it, idx=None, arm_cache=None):
        """errors involving item `it` (both directions). idx=None means not yet added."""
        errs = []
        for t in range(6):
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
                        if not (k.sticky and (k.f + 1) % 6 == t and k.victim == mine):
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
                # someone moving into me
                o = self.occ[t].get(sx(p, -1))
                if o is not None and o >= 0 and o != idx and self.items[o].mv[t]:
                    errs.append(('hit_by_mover', t, p))
            # adjacency
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
                        elif (other.f + 1) % 6 == t:
                            pass
                        elif oi is None or self.carry.get((oi, t)) != g.body:
                            # extra (race) carrier: harmless iff the piston's destination is empty
                            dk = sx(other.pos[t], 1)
                            if dk in self.occ[t] or dk in (arm_cache[t] if arm_cache else self.arm_ext(t)) or (gi is None and dk == it.pos[t]):
                                errs.append(('undesignated_carry', t, p))
                    else:  # source / observer
                        if other.body != g.body:
                            errs.append(('touch_source', t, p))
        if it.cat == 'glue':
            # observers facing this cell (hard power) other than own H
            for o in self.items:
                if o.cat == 'obs' and o.body != it.body:
                    for t in range(6):
                        if add(o.pos[t], DIRS[o.odir]) == it.pos[t]:
                            errs.append(('obs_face', t, it.pos[t]))
        return errs

    def items_group(self, it, idx, t):
        if it.cat == 'piston':
            return self.carry.get((idx, t)) if idx is not None else None
        return it.body

    def coverage_errors(self):
        errs = []
        for i, it in enumerate(self.items):
            if it.cat != 'piston':
                continue
            if it.sticky:
                t = (it.f + 1) % 6; c = sx(it.pos[t], 2 * it.face)
            else:
                t = it.f; c = sx(it.pos[t], it.face)
            o = self.occ[t].get(c)
            if o is None or o < 0 or self.items[o].cat != 'glue' or self.items[o].body != it.victim:
                errs.append(('nocontact', it.name, t))
            for t in range(6):
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
        """set of piston idx powered at the power stage at start of slot t."""
        out = set()
        hard = set()
        for o in self.items:
            if o.cat == 'obs' and S[o.body][(t - 1) % 6]:
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
                elif ob.cat == 'obs' and S[ob.body][(t - 1) % 6] and add(ob.pos[t], DIRS[ob.odir]) == k.pos[t]:
                    out.add(i)
                elif q in hard and ob.cat == 'glue':
                    out.add(i)
        return out

    def power_errors(self):
        errs = []
        for t in range(6):
            pw = self.powered(t)
            for i, k in enumerate(self.items):
                if k.cat == 'piston' and ((i in pw) != (k.f == t)):
                    errs.append(('power', k.name, t, i in pw))
        return errs

    def all_errors(self):
        errs = []
        cache = [self.arm_ext(t) for t in range(6)]
        for i, it in enumerate(self.items):
            errs += [(it.name or it.cat,) + e for e in self.item_errors(it, i, cache)]
        return errs + self.coverage_errors() + self.power_errors()

    # ---------------------------------------------------------------- loads
    def loads(self):
        out = {}
        for b in range(3):
            g = sum(1 for it in self.items if it.cat == 'glue' and it.body == b)
            s = sum(1 for it in self.items if it.cat in ('rs', 'obs') and it.body == b)
            for t in range(6):
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

    # ---------------------------------------------------------------- output
    def to_flyer(self, limit=1000, rng=5):
        f = Flyer(rng_state=rng, push_limit=limit)
        for it in self.items:
            p = it.pos[0]
            if it.cat == 'glue':
                f.set(p, Block(Kind.SLIME if it.gtype == 'S' else Kind.HONEY))
            elif it.cat == 'rs':
                f.set(p, Block(Kind.REDSTONE_BLOCK))
            elif it.cat == 'obs':
                f.set(p, Block.observer(it.odir, powered=bool(S[it.body][5])))
            elif it.cat == 'piston':
                st = 2 if it.f == 5 else 0
                f.set(p, Block.piston(E if it.face == 1 else Wd, sticky=it.sticky, state=st))
                if st:
                    f.set(sx(p, it.face), Block(Kind.PISTON_ARM))
        return f


def remove_item(d, idx):
    """rebuild design without item idx (carry keys remapped)."""
    nd = Design(d.gtypes)
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
        for t in range(6):
            nd.occ[t][it.pos[t]] = i
        if it.cat == 'piston':
            t = (it.f + 1) % 6
            nd.occ[t][sx(it.pos[t], it.face)] = -1 - i
    return nd


def connected_ok(d):
    for b in range(3):
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
    """greedy removal of glue cells while the design stays legal; returns new design."""
    import random
    rng = rng or random.Random(0)
    changed = True
    while changed:
        changed = False
        order = [i for i, it in enumerate(d.items) if it.cat == 'glue']
        rng.shuffle(order)
        for i in order:
            nd = remove_item(d, i)
            if connected_ok(nd) and not nd.all_errors():
                d = nd; changed = True
                break
    return d
