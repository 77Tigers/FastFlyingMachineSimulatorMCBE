"""Abstract topology enumerator with provable per-move load lower bounds (2026-10-07).

A design = bodies (rigid segments with a 2-slot word) + piston riders + power riders + merges + exactly one cause per
(merge group, slot) + a power plan.  No geometry: only the slot laws (RESEARCH_LOG piston guide / rigid_sat FINDINGS)
and the exact offset patterns that decide which carrier can power which piston.

Slot laws used (all provable from the rules satflyer encodes):
  * rigid pusher firing at k: carrier word {k+2,k+3};  rigid sticky pulling at p: carrier word {p+1,p+2}.
  * pushed at k while the target moves at k-1: the pusher's carrier (it moves at k-1 too) must be MERGED with the target
    at k-1 (otherwise its piston sits right behind the target's glue while both move = race).  Rider pusher: its k-1
    carrier must be the target's merge group.
  * pulled at p while the target moves at p+1: the sticky's carrier must be merged with the target at p+1 (rider
    sticky: its p+1 carrier must be the target's group).
  * one cause (piston) per merge group per slot; every piston causes exactly one move.
  * riders (1 block) are carried at each of their move slots by a body moving then (+1 to that move's load).
Power (exact, by word patterns only): piston host pattern h(t) = pos(host word, t), fire slot k (sticky: extension slot).
  static source (redstone / rod soft power) on carrier Y != host: d(t) = pos_Y(t) - h(t) takes its k-value only at k.
  observer on Y: Y moves at k-1 (pulse at k) and d differs at Y's other pulse slot.
  relays (rod / observer on Y hard-powering glue of body Z next to the piston, Z != Y, Z != host): the PAIR
  (pos_Y - pos_Z, pos_Z - h) must single out k (static) or differ at the other pulse (observer).  Y may be the host.
  power riders (redstone / rod / observer riding carriers, own word) are carriers like any other.
Lower bound per move (group G at slot t):  sum over bodies B in G of
     pistons(B) + [B carries a static-type source] + [B carries an observer] + fixed template extras + glue_lb(B)
  + riders carried by G at t.   glue_lb = 1, or the x-span forced by the push/pull contact equations (stretch ILP).
  Source sharing is allowed without limit (one block per carrier and kind) -> the bound stays provable.
Closed flyers additionally use  max load >= ceil(2 N / P)  (every block moves twice, one action per piston).

EST (heuristic, NOT a bound, used only for ranking): chain bodies keep their template glue 2, one source block per
(carrier, served host), other bodies glue = max(span, ceil(attachments / 3)).

usage:  python topo_enum.py front|twin|rear|closed [L] [max_new_entities] [max_riders]
"""
import sys, itertools, json, time, math
from collections import defaultdict

WORDS = {'mmww': (0, 1), 'wmmw': (1, 2), 'wwmm': (2, 3), 'mwwm': (0, 3), 'mwmw': (0, 2), 'wmwm': (1, 3)}
WNAME = {v: k for k, v in WORDS.items()}
CONSEC = [(0, 1), (1, 2), (2, 3), (0, 3)]


def pos(w, t):
    return sum(1 for m in w if m < t)


def fire_slot(w):
    for k in range(4):
        if k not in w and (k + 1) % 4 not in w: return k
    return None


def word_of(slots): return tuple(sorted(s % 4 for s in slots))


def d_pat(Y, h): return [pos(Y, t) - pos(h, t) for t in range(4)]


def pulses(Y): return sorted({(m + 1) % 4 for m in Y})


def static_ok(Y, h, k):
    d = d_pat(Y, h); return all(d[t] != d[k] for t in range(4) if t != k)


def obs_ok(Y, h, k):
    p = pulses(Y)
    if k not in p: return False
    o = [t for t in p if t != k][0]
    d = d_pat(Y, h); return d[o] != d[k]


def pair(Y, Z, h, t): return (pos(Y, t) - pos(Z, t), pos(Z, t) - pos(h, t))


def relay_static_ok(Y, Z, h, k):
    return all(pair(Y, Z, h, t) != pair(Y, Z, h, k) for t in range(4) if t != k)


def relay_obs_ok(Y, Z, h, k):
    p = pulses(Y)
    if k not in p: return False
    o = [t for t in p if t != k][0]
    return pair(Y, Z, h, o) != pair(Y, Z, h, k)


# ------------------------------------------------------------------ state
class S:
    """mutable state with explicit copy (small)."""
    __slots__ = ('bodies', 'pist', 'riders', 'cause', 'groups', 'power', 'src', 'req', 'ext', 'log', 'nnew', 'nrid')

    def copy(self):
        n = S.__new__(S)
        n.bodies = [dict(b) for b in self.bodies]
        n.pist = list(self.pist)
        n.riders = [dict(r, car=dict(r['car'])) for r in self.riders]
        n.cause = dict(self.cause)
        n.groups = {t: [set(g) for g in gs] for t, gs in self.groups.items()}
        n.power = dict(self.power)
        n.src = {k: dict(v) for k, v in self.src.items()}
        n.req = dict(self.req)
        n.ext = set(self.ext)
        n.log = list(self.log)
        n.nnew = self.nnew; n.nrid = self.nrid
        return n


def new_state():
    s = S.__new__(S)
    s.bodies = []      # {name, w, tmpl(bool), extra(int fixed blocks besides pistons/sources), fixed_src(set modes)}
    s.pist = []        # (hostkind 'B'|'R', host idx, kind 'P'|'S', target body or -1, slot)
    s.riders = []      # {name, w, kind 'P'|'S'|'st'|'ob', car {slot: body}}
    s.cause = {}       # (body, slot) -> piston idx | 'ext'
    s.groups = {t: [] for t in range(4)}   # nontrivial merge groups per slot (sets of bodies)
    s.power = {}       # hostkey -> (carrierkey, mode, relay)   hostkey ('B',i) / ('R',j); carrier ('B',i)/('R',j)/'ext'
    s.src = {}         # carrierkey -> {mode: set(hostkeys)}
    s.req = {}         # (rider j, slot) -> body that must be in the carrier's group
    s.ext = set()      # (body, slot) externally caused moves
    s.log = []
    s.nnew = 0; s.nrid = 0
    return s


def group_of(s, b, t):
    for g in s.groups[t]:
        if b in g: return g
    return {b}


def group_cause(s, b, t):
    for m in group_of(s, b, t):
        if (m, t) in s.cause: return s.cause[m, t]
    return None


def merge(s, a, b, t):
    """union a and b at slot t; False if both groups already have a cause or a/b do not move at t."""
    if t not in s.bodies[a]['w'] or t not in s.bodies[b]['w']: return False
    ga, gb = group_of(s, a, t), group_of(s, b, t)
    if ga is gb or (a in gb): return True
    if group_cause(s, a, t) is not None and group_cause(s, b, t) is not None: return False
    new = set(ga) | set(gb)
    s.groups[t] = [g for g in s.groups[t] if not (g & new)] + [new]
    return True


def add_body(s, name, w, tmpl=False, extra=0, fixed_src=()):
    s.bodies.append({'name': name, 'w': w, 'tmpl': tmpl, 'extra': extra, 'fsrc': tuple(fixed_src)})
    return len(s.bodies) - 1


def host_word(s, hk):
    return s.bodies[hk[1]]['w'] if hk[0] == 'B' else s.riders[hk[1]]['w']


def carrier_word(s, ck):
    return s.bodies[ck[1]]['w'] if ck[0] == 'B' else s.riders[ck[1]]['w']


def npist(s, b):
    return sum(1 for p in s.pist if p[0] == 'B' and p[1] == b)


def blocks_lb(s, b, glue=1):
    B = s.bodies[b]
    modes = set(s.src.get(('B', b), {}).keys()) | set(B['fsrc'])
    return npist(s, b) + len(modes) + B['extra'] + glue


def loads(s, glue=None, est=False):
    """dict (t, frozenset group) -> load lower bound (or estimate)."""
    out = {}
    for t in range(4):
        seen = set()
        for b, B in enumerate(s.bodies):
            if t not in B['w'] or b in seen: continue
            g = group_of(s, b, t); seen |= g
            L = 0
            for m in g:
                gl = s.bodies[m].get('gmin', 1) if glue is None else glue[m]
                L += blocks_est(s, m, gl) if est else blocks_lb(s, m, gl)
            for j, r in enumerate(s.riders):
                if r['car'].get(t) in g: L += 1
            out[t, frozenset(g)] = L
    return out


def blocks_est(s, b, glue):
    B = s.bodies[b]
    nsrc = sum(len(h) for h in s.src.get(('B', b), {}).values()) + len(B['fsrc'])
    if B['tmpl']: g = max(glue, 2)
    else:
        att = npist(s, b) + nsrc + sum(1 for (bb, t), c in s.cause.items() if bb == b and c != 'ext') \
            + sum(1 for r in s.riders for t, c in r['car'].items() if c == b)
        g = max(glue, math.ceil(att / 3), 1)
    return npist(s, b) + nsrc + B['extra'] + g


def maxload(s, **kw):
    L = loads(s, **kw)
    return max(L.values()) if L else 0


# ------------------------------------------------------------------ demands
def demands(s, cfg):
    for b, B in enumerate(s.bodies):
        for t in B['w']:
            if (b, t) in s.ext: continue
            if group_cause(s, b, t) is None:
                # a group containing an ext member counts as caused
                if any((m, t) in s.ext for m in group_of(s, b, t)): continue
                return ('cause', b, t)
    for j, r in enumerate(s.riders):
        for t in r['w']:
            if t not in r['car']: return ('carry', j, t)
    hosts = [('B', b) for b in range(len(s.bodies)) if npist(s, b) > 0] + \
            [('R', j) for j, r in enumerate(s.riders) if r['kind'] in ('P', 'S')]
    for hk in hosts:
        if hk not in s.power: return ('power', hk)
    return None


def add_piston(s, hk, kind, target, slot):
    """append piston + apply slot laws. Returns False if impossible."""
    s.pist.append((hk[0], hk[1], kind, target, slot))
    pi = len(s.pist) - 1
    if target < 0: return True
    if group_cause(s, target, slot) is not None: return False
    s.cause[target, slot] = pi
    Tw = s.bodies[target]['w']
    law = (slot - 1) % 4 if kind == 'P' else (slot + 1) % 4
    if law in Tw:
        if hk[0] == 'B':
            if not merge(s, hk[1], target, law): return False
        else:
            s.req[hk[1], law] = target
    return True


def branches(s, d, cfg):
    out = []
    E, RMAX, MAXP = cfg['E'], cfg['R'], cfg['maxp']
    if d[0] == 'cause':
        _, T, t = d
        for kind in ('P', 'S'):
            w = word_of((t + 2, t + 3)) if kind == 'P' else word_of((t + 1, t + 2))
            # existing body hosts a rigid piston
            for X, B in enumerate(s.bodies):
                if X == T or B['w'] != w or npist(s, X) >= MAXP or B.get('nohost'): continue
                n = s.copy()
                if add_piston(n, ('B', X), kind, T, t):
                    n.log.append(f"{kind}:{B['name']}->{s.bodies[T]['name']}@{t}"); out.append(n)
            if s.nnew < E:
                n = s.copy(); n.nnew += 1
                X = add_body(n, f"B{len(n.bodies)}", w)
                if add_piston(n, ('B', X), kind, T, t):
                    n.log.append(f"new {n.bodies[X]['name']}({WNAME[w]}) {kind}->{s.bodies[T]['name']}@{t}"); out.append(n)
                if s.nrid < RMAX:
                    n = s.copy(); n.nnew += 1; n.nrid += 1
                    n.riders.append({'name': f"r{len(n.riders)}", 'w': w, 'kind': kind, 'car': {}})
                    j = len(n.riders) - 1
                    if add_piston(n, ('R', j), kind, T, t):
                        n.log.append(f"rider {n.riders[j]['name']}({WNAME[w]},{kind})->{s.bodies[T]['name']}@{t}"); out.append(n)
        # optional merge into a caused co-moving group
        if cfg.get('merges', True):
            for Y, B in enumerate(s.bodies):
                if Y == T or t not in B['w'] or group_cause(s, Y, t) is None: continue
                if Y in group_of(s, T, t): continue
                n = s.copy()
                if merge(n, T, Y, t):
                    n.log.append(f"merge {s.bodies[T]['name']}+{B['name']}@{t}"); out.append(n)
    elif d[0] == 'carry':
        _, j, t = d
        need = s.req.get((j, t))
        for C, B in enumerate(s.bodies):
            if t not in B['w']: continue
            if need is not None and C not in group_of(s, need, t): continue
            n = s.copy(); n.riders[j]['car'][t] = C
            n.log.append(f"{s.riders[j]['name']} on {B['name']}@{t}"); out.append(n)
        if need is None and s.nnew < E and cfg.get('carrier_bodies', True):
            for w in WORDS.values():
                if t not in w: continue
                n = s.copy(); n.nnew += 1
                C = add_body(n, f"B{len(n.bodies)}", w)
                n.riders[j]['car'][t] = C
                n.log.append(f"new {n.bodies[C]['name']}({WNAME[w]}) carries {s.riders[j]['name']}@{t}"); out.append(n)
    elif d[0] == 'power':
        _, hk = d
        h = host_word(s, hk); k = fire_slot(h)
        bodies = list(range(len(s.bodies)))
        cars = [('B', b) for b in bodies] + [('R', j) for j, r in enumerate(s.riders) if r['kind'] in ('st', 'ob')]
        for ck in cars:
            Y = carrier_word(s, ck)
            kinds_allowed = ('st', 'ob') if ck[0] == 'B' else (s.riders[ck[1]]['kind'],)
            for mode in kinds_allowed:
                ok = None
                if ck != hk:
                    if mode == 'st' and static_ok(Y, h, k): ok = 'direct'
                    if mode == 'ob' and obs_ok(Y, h, k): ok = 'direct'
                if ok is None:
                    for Z in bodies:
                        if ('B', Z) == ck or ('B', Z) == hk: continue
                        Zw = s.bodies[Z]['w']
                        if (mode == 'st' and relay_static_ok(Y, Zw, h, k)) or (mode == 'ob' and relay_obs_ok(Y, Zw, h, k)):
                            ok = f"relay:{s.bodies[Z]['name']}"; break
                if ok is None: continue
                n = s.copy(); n.power[hk] = (ck, mode, ok)
                n.src.setdefault(ck, {}).setdefault(mode, set()).add(hk)
                n.log.append(f"pow {hname(s, hk)} <- {mode}@{cname(s, ck)} ({ok})"); out.append(n)
        if s.nnew < E and s.nrid < RMAX and cfg.get('power_riders', True):
            for w in WORDS.values():
                for mode in ('st', 'ob'):
                    ok = (mode == 'st' and static_ok(w, h, k)) or (mode == 'ob' and obs_ok(w, h, k))
                    how = 'direct' if ok else 'relay'
                    if not ok:
                        ok = any((mode == 'st' and relay_static_ok(w, s.bodies[Z]['w'], h, k)) or
                                 (mode == 'ob' and relay_obs_ok(w, s.bodies[Z]['w'], h, k))
                                 for Z in bodies if ('B', Z) != hk)
                    if not ok: continue
                    n = s.copy(); n.nnew += 1; n.nrid += 1
                    n.riders.append({'name': f"q{len(n.riders)}", 'w': w, 'kind': mode, 'car': {}})
                    j = len(n.riders) - 1
                    n.power[hk] = (('R', j), mode, how); n.src.setdefault(('R', j), {}).setdefault(mode, set()).add(hk)
                    n.log.append(f"powrider {n.riders[j]['name']}({WNAME[w]},{mode}) -> {hname(s, hk)}"); out.append(n)
    return out


def hname(s, hk): return s.bodies[hk[1]]['name'] if hk[0] == 'B' else s.riders[hk[1]]['name']
def cname(s, ck): return 'EXT' if ck == 'ext' else hname(s, ck)


# ------------------------------------------------------------------ stretch ILP (exact x-potential relaxation)
def stretch_lb(s, L):
    """min over feature x-positions of the max move load with glue = x-span of each body (contacts exact,
    pistons within 1, riders within 2 of carrier glue). Returns (maxload, glue list) or None if > L."""
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    nb = len(s.bodies)
    BIG = 40
    lo = [m.NewIntVar(-BIG, BIG, '') for _ in range(nb)]
    hi = [m.NewIntVar(-BIG, BIG, '') for _ in range(nb)]
    for b in range(nb): m.Add(lo[b] <= hi[b])
    rx = [m.NewIntVar(-BIG, BIG, '') for _ in s.riders]
    m.Add(lo[0] == 0)
    for (hk0, hi_, kind, T, slot) in s.pist:
        hw = s.bodies[hi_]['w'] if hk0 == 'B' else s.riders[hi_]['w']
        if hk0 == 'B':
            xp = m.NewIntVar(-BIG, BIG, '')
            if kind == 'P': m.Add(xp >= lo[hi_]); m.Add(xp <= hi[hi_] + 1)
            else: m.Add(xp >= lo[hi_] - 1); m.Add(xp <= hi[hi_])
        else:
            xp = rx[hi_]
        if T < 0: continue
        c = m.NewIntVar(-BIG, BIG, '')
        m.Add(c >= lo[T]); m.Add(c <= hi[T])
        Tw = s.bodies[T]['w']
        if kind == 'P': m.Add(c + pos(Tw, slot) == xp + pos(hw, slot) + 1)
        else: m.Add(c + pos(Tw, slot) == xp + pos(hw, slot) - 2)
    for j, r in enumerate(s.riders):
        for t, C in r['car'].items():
            Cw = s.bodies[C]['w']
            m.Add(rx[j] + pos(r['w'], t) - pos(Cw, t) >= lo[C] - 2)
            m.Add(rx[j] + pos(r['w'], t) - pos(Cw, t) <= hi[C] + 2)
    # host piston levels (for power adjacency): a rigid host's pistons lie within [lo-1, hi+1]; riders at rx
    def host_level(hk, t):
        v = m.NewIntVar(-BIG, BIG, '')
        if hk[0] == 'B':
            Hw = s.bodies[hk[1]]['w']; m.Add(v - pos(Hw, t) >= lo[hk[1]] - 1); m.Add(v - pos(Hw, t) <= hi[hk[1]] + 1)
        else:
            m.Add(v == rx[hk[1]] + pos(s.riders[hk[1]]['w'], t))
        return v
    # power sources: a source block on carrier Y within 1 of Y's glue, within 1 (direct) / 2 (relay) of the piston
    for hk, (ck, mode, how) in s.power.items():
        if ck == 'ext' or how in ('template', 'chain'): continue
        k = fire_slot(host_word(s, hk))
        hv = host_level(hk, k)
        reach = 1 if how == 'direct' else 2
        if ck[0] == 'B':
            Yw = s.bodies[ck[1]]['w']
            sv_ = m.NewIntVar(-BIG, BIG, '')
            m.Add(sv_ >= lo[ck[1]] - 1); m.Add(sv_ <= hi[ck[1]] + 1)
            m.Add(sv_ + pos(Yw, k) - hv <= reach); m.Add(sv_ + pos(Yw, k) - hv >= -reach)
        else:
            Yw = s.riders[ck[1]]['w']
            m.Add(rx[ck[1]] + pos(Yw, k) - hv <= reach); m.Add(rx[ck[1]] + pos(Yw, k) - hv >= -reach)
    # merges: the receiver carries the partner (block right behind its glue or glue contact): glue levels within 2
    for t in range(4):
        for g in s.groups[t]:
            gl = sorted(g)
            for a, b in zip(gl, gl[1:]):
                ga = m.NewIntVar(-BIG, BIG, ''); gb = m.NewIntVar(-BIG, BIG, '')
                m.Add(ga >= lo[a]); m.Add(ga <= hi[a]); m.Add(gb >= lo[b]); m.Add(gb <= hi[b])
                e = ga + pos(s.bodies[a]['w'], t) - gb - pos(s.bodies[b]['w'], t)
                m.Add(e <= 2); m.Add(e >= -2)
    glue = [hi[b] - lo[b] + 1 for b in range(nb)]
    for b in range(nb):
        if s.bodies[b].get('gmin'): m.Add(glue[b] >= s.bodies[b]['gmin'])
    z = m.NewIntVar(0, 200, 'z')
    for t in range(4):
        seen = set()
        for b, B in enumerate(s.bodies):
            if t not in B['w'] or b in seen: continue
            g = group_of(s, b, t); seen |= g
            expr = sum(blocks_lb(s, mm, 0) + glue[mm] for mm in g) + sum(1 for r in s.riders if r['car'].get(t) in g)
            m.Add(z >= expr)
    m.Minimize(z)
    sv = cp_model.CpSolver(); sv.parameters.num_search_workers = 1; sv.parameters.max_time_in_seconds = 5
    st = sv.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    zv = sv.Value(z) if st == cp_model.OPTIMAL else int(sv.BestObjectiveBound())
    return zv, [sv.Value(hi[b]) - sv.Value(lo[b]) + 1 for b in range(nb)]


# ------------------------------------------------------------------ bases
TGLUE = 2   # assumption: chain middle bodies (K4, K4', K1) keep their 2 template glue (set 1 for the pure bound)


def base_front(twin=False):
    s = new_state()
    # chain 1: K4 (mmww) template: P -> K5@2, S -> K3 (outside) @3, carries R for K3 (fixed), powered by K5's R
    K4 = add_body(s, 'K4', WORDS['mmww'], tmpl=True, fixed_src=('st',))
    K5 = add_body(s, 'K5', WORDS['wwmm'], tmpl=True, fixed_src=('st',))   # template R powers K4's pistons
    s.ext.add((K4, 0))
    add_piston(s, ('B', K4), 'S', -1, 3)          # pulls K3 (outside)
    add_piston(s, ('B', K4), 'P', K5, 2)
    add_piston(s, ('B', K5), 'S', K4, 1)
    s.power[('B', K4)] = (('B', K5), 'st', 'template')
    s.bodies[K4]['nohost'] = True                 # K4 keeps its template pistons only
    s.bodies[K4]['gmin'] = TGLUE
    if twin:
        A = add_body(s, "K4'", WORDS['wwmm'], tmpl=True, fixed_src=('st',))
        B = add_body(s, "K5'", WORDS['mmww'], tmpl=True, fixed_src=('st',))
        s.ext.add((A, 2))
        add_piston(s, ('B', A), 'S', -1, 1)
        add_piston(s, ('B', A), 'P', B, 0)
        add_piston(s, ('B', B), 'S', A, 3)
        s.power[('B', A)] = (('B', B), 'st', 'template')
        s.bodies[A]['nohost'] = True
        s.bodies[A]['gmin'] = TGLUE
    return s


def base_rear():
    s = new_state()
    R0 = add_body(s, 'K0', WORDS['mmww'])                         # first chain body; template R of K1 powers it
    R1 = add_body(s, 'K1', WORDS['wwmm'], tmpl=True, fixed_src=('st',))
    s.ext.add((R1, 3))                                            # K2 pulls K1 (chain continues)
    add_piston(s, ('B', R1), 'P', -1, 0)                          # pushes K2 (outside)
    add_piston(s, ('B', R1), 'S', R0, 1)
    add_piston(s, ('B', R0), 'P', R1, 2)
    s.power[('B', R1)] = ('ext', 'st', 'chain')
    s.power[('B', R0)] = (('B', R1), 'st', 'template')
    s.bodies[R1]['nohost'] = True
    s.bodies[R1]['gmin'] = TGLUE
    return s


def base_closed(w):
    s = new_state()
    add_body(s, 'B0', w)
    return s


# ------------------------------------------------------------------ search
def search(base, cfg, closed=False):
    L = cfg['L']
    res = []; nodes = 0
    stack = [base]
    while stack:
        s = stack.pop(); nodes += 1
        if maxload(s) > L: continue
        d = demands(s, cfg)
        if d is None:
            if closed:
                P = len(s.pist)
                N = sum(blocks_lb(s, b) for b in range(len(s.bodies))) + len(s.riders)
                if P == 0 or math.ceil(2 * N / P) > L: continue
            res.append(s); continue
        stack.extend(branches(s, d, cfg))
    return res, nodes


def describe(s):
    parts = []
    for b, B in enumerate(s.bodies):
        ps = [f"{p[2]}->{s.bodies[p[3]]['name'] if p[3] >= 0 else 'out'}@{p[4]}" for p in s.pist if p[0] == 'B' and p[1] == b]
        src = sorted(s.src.get(('B', b), {}).keys())
        parts.append(f"{B['name']}:{WNAME[B['w']]}[{','.join(ps)}{'|src:' + ''.join(src) if src else ''}]")
    for j, r in enumerate(s.riders):
        tg = [f"{p[2]}->{s.bodies[p[3]]['name']}@{p[4]}" for p in s.pist if p[0] == 'R' and p[1] == j]
        car = ','.join(f"{s.bodies[c]['name']}@{t}" for t, c in sorted(r['car'].items()))
        parts.append(f"{r['name']}:{WNAME[r['w']]}/{r['kind']}[{''.join(tg)} on {car}]")
    mg = [f"{'+'.join(sorted(s.bodies[b]['name'] for b in g))}@{t}" for t in range(4) for g in s.groups[t] if len(g) > 1]
    pw = [f"{hname(s, hk)}<-{v[1]}@{cname(s, v[0])}({v[2]})" for hk, v in s.power.items()]
    return ' '.join(parts) + (' merges:' + ','.join(mg) if mg else '') + ' power:' + ';'.join(pw)


def signature(s):
    """power-agnostic kinematic signature (for grouping)."""
    parts = []
    for b, B in enumerate(s.bodies):
        ps = sorted(f"{p[2]}{s.bodies[p[3]]['name'] if p[3] >= 0 else 'o'}{p[4]}" for p in s.pist if p[0] == 'B' and p[1] == b)
        parts.append(f"{B['name']}:{WNAME[B['w']]}[{','.join(ps)}]")
    for j, r in enumerate(s.riders):
        if r['kind'] not in ('P', 'S'): continue
        tg = [f"{p[2]}{s.bodies[p[3]]['name']}{p[4]}" for p in s.pist if p[0] == 'R' and p[1] == j]
        car = ','.join(f"{s.bodies[c]['name']}{t}" for t, c in sorted(r['car'].items()))
        parts.append(f"{r['name']}:{WNAME[r['w']]}[{''.join(tg)} on {car}]")
    mg = [f"{'+'.join(sorted(s.bodies[b]['name'] for b in g))}@{t}" for t in range(4) for g in s.groups[t] if len(g) > 1]
    return ' '.join(parts) + (' M:' + ','.join(mg) if mg else '')


def run(mode, L=7, E=3, R=2, maxp=3, out=None, merges=True, refine=True):
    cfg = {'L': L, 'E': E, 'R': R, 'maxp': maxp, 'merges': merges}
    t0 = time.time()
    if mode in ('front', 'twin'): bases = [base_front(mode == 'twin')]; closed = False
    elif mode == 'rear': bases = [base_rear()]; closed = False
    else: bases = [base_closed(WORDS['mmww']), base_closed(WORDS['mwmw'])]; closed = True
    allres = []; nodes = 0
    for b in bases:
        r, n = search(b, cfg, closed); allres += r; nodes += n
    rows = []
    for s in allres:
        lb0 = maxload(s)
        lb, glue = lb0, None
        if refine:
            sr = stretch_lb(s, L)
            if sr is None: continue
            lb, glue = sr
            if lb > L: continue
        est = maxload(s, glue=glue, est=True)
        if closed:
            P = len(s.pist); N = sum(blocks_lb(s, b, glue[b] if glue else 1) for b in range(len(s.bodies))) + len(s.riders)
            lb = max(lb, math.ceil(2 * N / P))
            if lb > L: continue
        rows.append({'lb': lb, 'lb0': lb0, 'est': est, 'sig': signature(s), 'desc': describe(s), 'log': s.log,
                     'nent': s.nnew, 'loads': {f"{'+'.join(sorted(s.bodies[b]['name'] for b in g))}@{t}": v
                                               for (t, g), v in loads(s, glue=glue).items()}})
    rows.sort(key=lambda r: (r['est'], r['lb'], r['nent']))
    print(f"{mode}: L={L} E={E} R={R}: {nodes} nodes, {len(allres)} leaves, {len(rows)} with LB<={L}, {time.time() - t0:.1f}s")
    if out:
        json.dump(rows, open(out, 'w'), indent=1)
    return rows


if __name__ == '__main__':
    mode = sys.argv[1]
    L = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    E = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    R = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    rows = run(mode, L, E, R, out=f'runs/enum_{mode}_L{L}_E{E}_R{R}.json')
    sigs = defaultdict(list)
    for r in rows: sigs[r['sig']].append(r)
    print(len(sigs), 'kinematic signatures')
    for sg, rs in sorted(sigs.items(), key=lambda kv: (min(r['est'] for r in kv[1]), min(r['lb'] for r in kv[1])))[:40]:
        b = min(rs, key=lambda r: (r['est'], r['lb']))
        print(f"LB {b['lb']} EST {b['est']} ({len(rs)} power plans) {sg}")
