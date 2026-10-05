"""Rigid-segment flyer model, slot-level checker and exporter (2.5 bps, 8-tick cycle, 4 slots of 2 ticks).

A segment is a rigid set of cells that moves +1 X in exactly the slots of its word (2 of 4 slots).
Every piston rides its own segment rigidly. Kinds (local cell -> code):
  'g' glue (segment material), 'P' pusher facing +X, 'S' sticky facing -X,
  'R' redstone block, ('D',d) lightning rod facing d, ('O',d) observer facing d.
Directions: 0 +X, 1 -X, 2 +Y, 3 -Y, 4 +Z, 5 -Z.

Timing rules (see RESEARCH_LOG piston guide): a pusher fires at slot k with its segment still at k,k+1 and
retracts at k+1; a sticky extends at e with its segment still at e,e+1 and pulls (two cells ahead) at e+1.
For a segment whose word has consecutive moves (m, m+1) the only legal slot is k = e = m+2.

check(segs) returns None if the abstract model is consistent, else a short reason string.
to_flyer(segs, limit) exports the slot-0 start state (pistons that are extended at slot 0 get state 2 + arm).
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind

D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
E, W_ = (1,0,0), (-1,0,0)

class Seg:
    def __init__(self, name, word, origin, cells, mat='slime', rider=False, fire=None):
        self.name, self.word, self.origin, self.cells, self.mat = name, tuple(word), origin, dict(cells), mat
        self.rider, self.fire = rider, fire
        assert len(self.word) == 2
    def pos(self, t):  # moves completed before slot t (t may be 0..4)
        return sum(1 for m in self.word if m < t)
    def moves(self, t): return (t % 4) in self.word
    def fire_slot(self):
        if self.fire is not None: return self.fire
        for k in range(4):
            if not self.moves(k) and not self.moves(k+1): return k
        return None
    def at(self, t):
        o = self.origin; dx = self.pos(t)
        return {(o[0]+c[0]+dx, o[1]+c[1], o[2]+c[2]): k for c, k in self.cells.items()}

def kind_of(k): return k if isinstance(k, str) else k[0]
def dirv(d): return D6[d]

def piston_phase(seg, t):
    """'fire' at k (pusher extends / sticky extends), 'ret' at k+1 (extended at slot start), else 'idle'."""
    k = seg.fire_slot()
    if k is None: return None
    if t % 4 == k: return 'fire'
    if t % 4 == (k+1) % 4: return 'ret'
    return 'idle'

import os as _os
LEAF = bool(_os.environ.get('LEAF'))

def leaf_ok(segs, oi, n, ok, o, t, occ, movers, j):
    """Glue of mover j touches a NON-glue block n of segment o that also moves this slot (by its own cause).
    Either order gives the same result: if j goes first it drags the block +1 (where it was going anyway);
    if o goes first the block is moving, hence immovable and skipped by adhesion. Requirements: o moves now,
    the block is not a firing piston, and its destination is empty at slot start (or j's own cell)."""
    if oi not in movers or oi == j or o.rider: return False
    if ok == 'g' or ok == 'D': return False
    if ok in 'PS' and piston_phase(o, t) == 'fire': return False
    d = add(n, E)
    if d in occ and occ[d][0] != j: return False
    return True

LEAFPUSH = bool(_os.environ.get('LEAFPUSH'))

def leafpush_ok(segs, occ, arms, movers, j, d):
    """(rigid_sat_20261004, verified by leafpush_test.py) mover j moves a block into cell d holding a NON-glue, non-rod
    block of a segment o that also moves this slot by its own cause: if j goes first it pushes the leaf +1 as an
    obstruction (where it was going anyway), if o goes first the cell is freed. Needs d+E empty; counts in j's load."""
    oi, ok = occ[d][0], kind_of(occ[d][1])
    if oi not in movers or oi == j or segs[oi].rider or ok in ('g', 'D'): return False
    d2 = add(d, E)
    return d2 not in occ and d2 not in arms

def check(segs, verbose=False, ignore=()):
    names = [s.name for s in segs]
    for s in segs:
        if s.rider: continue
        has_p = any(kind_of(k) in 'PS' for k in s.cells.values())
        if has_p and s.fire_slot() is None: return f'{s.name}: no rigid fire slot'
        # connectivity: every non-glue block next to own glue; glue connected
        glue = [c for c, k in s.cells.items() if k == 'g']
        if not glue: return f'{s.name}: no glue'
        seen = {glue[0]}; st = [glue[0]]
        while st:
            c = st.pop()
            for d in D6:
                n = add(c, d)
                if n in s.cells and s.cells[n] == 'g' and n not in seen: seen.add(n); st.append(n)
        if len(seen) != len(glue): return f'{s.name}: glue disconnected'
        for c, k in s.cells.items():
            if k != 'g' and not any(add(c, d) in seen for d in D6): return f'{s.name}: {k} at {c} not attached'
    for t in range(4):
        occ = {}
        for i, s in enumerate(segs):
            for c, k in s.at(t).items():
                if c in occ: return f't{t}: overlap {c} {names[occ[c][0]]}/{s.name}'
                occ[c] = (i, k)
        arms = {}
        for i, s in enumerate(segs):
            if piston_phase(s, t) == 'ret':
                for c, k in s.at(t).items():
                    kk = kind_of(k)
                    if kk == 'P': a = add(c, E)
                    elif kk == 'S': a = add(c, W_)
                    else: continue
                    if a in occ or a in arms: return f't{t}: arm of {s.name} at {a} blocked'
                    arms[a] = (i, kk)
        movers = {i for i, s in enumerate(segs) if s.moves(t)}
        cause = {i: [] for i in movers}
        # power
        hot = set(); soft = set()
        for i, s in enumerate(segs):
            pulsing = s.moves(t-1)
            for c, k in s.at(t).items():
                kk = kind_of(k)
                if kk == 'R':
                    for d in D6: soft.add((add(c, d), c))
                elif kk == 'D':
                    for d in D6: soft.add((add(c, d), c))
                    f = add(c, dirv(k[1]))
                    if f in occ and occ[f][1] == 'g': hot.add(f)
                elif kk == 'O' and pulsing:
                    f = add(c, dirv(k[1]))
                    if f in occ:
                        if occ[f][1] == 'g': hot.add(f)
                        elif kind_of(occ[f][1]) in 'PS': soft.add((f, c))
        for h in hot:
            for d in D6: soft.add((add(h, d), h))
        powered_src = {}
        for (p, src) in soft:
            powered_src.setdefault(p, set()).add(src)
        for i, s in enumerate(segs):
            ph = piston_phase(s, t)
            for c, k in s.at(t).items():
                kk = kind_of(k)
                if kk not in 'PS': continue
                front = add(c, E if kk == 'P' else W_)
                srcs = {x for x in powered_src.get(c, ()) if x != front}
                pw = bool(srcs)
                want = (ph == 'fire')
                if pw != want and s.name not in ignore: return f't{t}: {s.name} {kk}@{c} power {"missing" if want else "extra"}'
                if ph == 'fire':
                    if kk == 'P' and s.name in ignore and front not in occ: continue
                    if kk == 'S' and s.name in ignore and add(front, W_) not in occ: continue
                    if kk == 'P':
                        v = occ.get(front)
                        if not v or v[1] != 'g' or v[0] == i: return f't{t}: {s.name} pusher front {front} not foreign glue'
                        if v[0] not in movers: return f't{t}: {s.name} pushes {names[v[0]]} which should not move'
                        cause[v[0]].append(('push', i))
                    else:
                        if front in occ or front in arms: return f't{t}: {s.name} sticky ext blocked {front}'
                        for j in movers:
                            if j != i and any(add(cc, E) == front for cc in segs[j].at(t)):
                                return f't{t}: {s.name} sticky arm cell entered by {names[j]}'
                if ph == 'ret' and kk == 'S':
                    tgt = add(front, W_)
                    if s.name in ignore and tgt not in occ: continue
                    v = occ.get(tgt)
                    if not v or v[1] != 'g' or v[0] == i: return f't{t}: {s.name} sticky pull target {tgt} not foreign glue'
                    if v[0] not in movers: return f't{t}: {s.name} pulls {names[v[0]]} which should not move'
                    cause[v[0]].append(('pull', i))
        riders_of = {}
        for r in movers:
            if not segs[r].rider: continue
            rc = list(segs[r].at(t))[0]
            if piston_phase(segs[r], t) != 'idle': return f't{t}: rider {segs[r].name} busy while moving'
            for j in movers:
                if j == r or segs[j].rider: continue
                cj = segs[j].at(t)
                if any(add(c, E) == rc for c in cj) or any(k == 'g' and any(add(c, d) == rc for d in D6) for c, k in cj.items()):
                    cause[r].append(('ride', j)); riders_of.setdefault(j, set()).add(r)
        for j in movers:
            if names[j] in ignore:
                if len(cause[j]) > 1: return f't{t}: {names[j]} has causes {cause[j]}'
                if not cause[j]: cause[j] = [('ext', -1)]
                continue
            if len(cause[j]) != 1: return f't{t}: {names[j]} has causes {cause[j]}'
        # movement collisions and adhesion
        pulled_arm = {}
        for j in movers:
            typ, a = cause[j][0]
            if typ == 'pull' and a >= 0:
                for c, k in segs[a].at(t).items():
                    if kind_of(k) == 'S': pulled_arm[add(c, W_)] = j
        for j in movers:
            s = segs[j]; cells = dict(s.at(t))
            if s.rider:
                typ, a = cause[j][0]
                if typ == 'ride':
                    c = list(cells)[0]; d = add(c, E)
                    if d in occ and occ[d][0] != a: return f't{t}: rider {s.name} moves into {names[occ[d][0]]}'
                    continue
            for r in riders_of.get(j, ()):
                cells.update(segs[r].at(t))
            for c, k in cells.items():
                d = add(c, E)
                if d not in cells:
                    if d in arms:
                        if pulled_arm.get(d) != j: return f't{t}: {s.name} moves into arm {d}'
                    elif d in occ:
                        if LEAFPUSH and leafpush_ok(segs, occ, arms, movers, j, d): continue
                        return f't{t}: {s.name} moves into {names[occ[d][0]]} at {d}'
                if k == 'g':
                    for dd in D6:
                        n = add(c, dd)
                        if n in cells: continue
                        if n in arms: continue
                        v = occ.get(n)
                        if not v: continue
                        if v[0] in riders_of.get(j, ()): continue
                        o = segs[v[0]]; ok = kind_of(v[1])
                        if ok == 'g' and o.mat != s.mat: continue
                        if ok in 'PS' and piston_phase(o, t) == 'ret': continue
                        typ, a = cause[j][0]
                        if v[0] == a and ok in 'PS' and piston_phase(o, t) == 'fire':
                            continue   # the initiating piston is immovable for its own move (any face)
                        if LEAF and leaf_ok(segs, v[0], n, ok, o, t, occ, movers, j):
                            continue   # order-independent leaf race (see leaf_ok)
                        return f't{t}: {s.name} glue {c} sticks to {names[v[0]]} {v[1]} at {n}'
            # also the cell behind a moving glue cell must not be another mover's sticky front etc. (covered)
    return None

def loads(segs):
    """Max action load per slot: mover cells + riders it carries (call after check() passes)."""
    best = 0
    for t in range(4):
        for j, s in enumerate(segs):
            if not s.moves(t) or s.rider: continue
            cj = s.at(t); n = len(cj)
            for r in segs:
                if r.rider and r.moves(t):
                    rc = list(r.at(t))[0]
                    if any(add(c, E) == rc for c in cj) or any(k == 'g' and any(add(c, d) == rc for d in D6) for c, k in cj.items()):
                        n += 1
            if LEAF:   # leaves of co-moving segments dragged (or, LEAFPUSH, pushed) when this one goes first
                glue_nb = {add(c, d) for c, k in cj.items() if k == 'g' for d in D6}
                if LEAFPUSH: glue_nb |= {add(c, E) for c in cj}
                for o in segs:
                    if o is s or o.rider or not o.moves(t): continue
                    for c, k in o.at(t).items():
                        if kind_of(k) not in ('g', 'D') and c in glue_nb: n += 1
            best = max(best, n)
    return best

def to_flyer(segs, limit):
    f = Flyer(); f.push_limit = limit
    mats = {'slime': Kind.SLIME, 'honey': Kind.HONEY}
    for s in segs:
        ph = piston_phase(s, 0)
        for c, k in s.at(0).items():
            kk = kind_of(k)
            if kk == 'g': b = Block(mats[s.mat])
            elif kk == 'R': b = Block(Kind.REDSTONE_BLOCK)
            elif kk == 'D': b = Block.rod(k[1])
            elif kk == 'O': b = Block.observer(k[1], powered=s.moves(3))   # pulse pending from the move in the previous slot
            elif kk in 'PS':
                ext = (ph == 'ret')
                b = Block.piston(0 if kk == 'P' else 1, sticky=(kk == 'S'), state=2 if ext else 0)
                if ext:
                    a = add(c, E if kk == 'P' else W_)
                    f.set(a, Block(Kind.PISTON_ARM))
            f.set(c, b)
    return f

def reserved_cells(segs, me, glue=True):
    """Cells (in segment `me`'s slot-0 frame) that `me` must not occupy: any other segment's block at any slot
    (incl. the moment it moves in), piston arms when present, and (glue=True) cells next to another segment's
    movable piston at a slot where `me` moves but does not carry that piston (approximate: riders excluded)."""
    def P(s, t): return 2 if t == 4 else s.pos(t)
    res = set()
    for o in segs:
        if o is me: continue
        for t in range(4):
            for tt in (t, t + 1):
                sh = (o.origin[0] + P(o, tt)) - (me.origin[0] + P(me, tt))
                dy = o.origin[1] - me.origin[1]; dz = o.origin[2] - me.origin[2]
                for c, k in o.cells.items():
                    res.add((c[0] + sh, c[1] + dy, c[2] + dz))
            ph = piston_phase(o, t)
            if ph == 'ret' or (ph == 'fire'):
                sh = (o.origin[0] + P(o, t)) - (me.origin[0] + P(me, t))
                dy = o.origin[1] - me.origin[1]; dz = o.origin[2] - me.origin[2]
                for c, k in o.cells.items():
                    kk = kind_of(k)
                    if kk == 'P' and ph == 'ret': res.add((c[0] + sh + 1, c[1] + dy, c[2] + dz))
                    if kk == 'S': res.add((c[0] + sh - 1, c[1] + dy, c[2] + dz))
        if glue:
            for t in range(4):
                if not me.moves(t): continue
                sh = (o.origin[0] + P(o, t)) - (me.origin[0] + P(me, t))
                dy = o.origin[1] - me.origin[1]; dz = o.origin[2] - me.origin[2]
                ph = piston_phase(o, t)
                for c, k in o.cells.items():
                    kk = kind_of(k)
                    if kk == 'g' and o.mat != me.mat: continue
                    if LEAF and kk not in ('g', 'D') and o.moves(t) and not o.rider and not (kk in 'PS' and ph == 'fire'):
                        continue   # leaf race allowed (checker verifies the destination)
                    if kk in 'PS':
                        if ph == 'ret': continue
                        if o.rider and o.moves(t): continue
                    elif o.rider: continue
                    oc = (c[0] + sh, c[1] + dy, c[2] + dz)
                    if kk == 'P' and ph == 'fire' and add(oc, (1, 0, 0)) in me.cells: continue  # it pushes me: initiator
                    for d in D6:
                        if kk == 'P' and ph == 'fire' and d == (1, 0, 0): continue   # pusher's own target cell
                        res.add(add(oc, d))
    return res

def glue_path(seg, goals, segs, rng, maxlen=3, extra_block=()):
    """BFS from seg's glue to any goal cell (seg frame) through free cells; adds glue; returns cells added or None."""
    from collections import deque
    res = reserved_cells(segs, seg) | set(extra_block)
    start = [c for c, k in seg.cells.items() if k == 'g']
    goals = [g for g in goals if g not in res and g not in seg.cells or (g in seg.cells and seg.cells[g] == 'g')]
    if any(g in start for g in goals): return []
    prev = {c: None for c in start}; depth = {c: 0 for c in start}; q = deque(start)
    while q:
        c = q.popleft()
        if c in goals and c not in start:
            path = []; z = c
            while z not in start: path.append(z); z = prev[z]
            for z in path: seg.cells[z] = 'g'
            return path
        if depth[c] >= maxlen: continue
        ds = list(D6); rng.shuffle(ds)
        for d in ds:
            m = add(c, d)
            if m in prev or m in res or m in seg.cells: continue
            prev[m] = c; depth[m] = depth[c] + 1; q.append(m)
    return None

def unique_offset(o, s, k):
    rel = [o.pos(t) - s.pos(t) for t in range(4)]
    return rel.count(rel[k]) == 1

def power_fix(segs, rng, tries=6, maxlen=2):
    """Repeatedly run check; on 'power missing' for a piston, add a redstone block on another (non-rider) segment
    with a unique offset at that piston's fire slot, attached by a short glue path. Returns final check result."""
    import re as _re
    for _ in range(tries):
        r = check(segs)
        if r is None or 'power missing' not in r: return r
        m = _re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        if not m: return r
        t = int(m.group(1)); name = m.group(2); pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        s = [x for x in segs if x.name == name][0]
        front = add(pw, E if m.group(3) == 'P' else W_)
        cands = [add(pw, d) for d in D6 if add(pw, d) != front]
        rng.shuffle(cands)
        placed = False
        others = [o for o in segs if not o.rider and o is not s and unique_offset(o, s, t)]
        rng.shuffle(others)
        for c in cands:
            for o in others:
                lc = (c[0] - o.origin[0] - o.pos(t), c[1] - o.origin[1], c[2] - o.origin[2])
                if lc in o.cells or lc in reserved_cells(segs, o, glue=False): continue
                o.cells[lc] = 'R'
                if any(add(lc, d) in o.cells and o.cells[add(lc, d)] == 'g' for d in D6) or \
                   glue_path(o, [add(lc, d) for d in D6], segs, rng, maxlen=maxlen) is not None:
                    placed = True; break
                del o.cells[lc]
            if placed: break
        if not placed: return r
    return check(segs)
