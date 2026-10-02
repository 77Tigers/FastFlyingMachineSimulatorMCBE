"""Layered role model for 3 bps (5-slot) flyers with arbitrary per-body words (agent J2, 2026-10-02).

Generalises j_mmwmw/rider_floor.py (rings of one rotated word) to any set of bodies with any 5-slot words.
Every move (body V, slot s) is driven by one piston: push (normal, fires s, frozen s,s+1, REL(s)=-1) or pull
(sticky, fires s-1, frozen s-1,s, REL(s)=2).  The piston moves in its 3 non-frozen slots and must be touched by
>=1 moving body in each of them (that body carries it: +1 load on that move).  Static hazard rules exactly as in
rider_floor.py.  Glued stickies are counted as riders here (subtract them from glue when comparing to a ledger).

The ILP picks, per move, push or pull (or a fixed kind) and per (piston, body) an adjacency timeline, minimising
  W_REAR * max rear load + W_ALL * max load + sum of loads, where load = glue + riders.
Relaxation: no geometry (any body may touch any piston).  Use it to rank STRUCTURES (words + kinds), not layouts.

python layered.py            -> validation on tm_smol + mmwmw-rear structures
"""
import itertools, sys
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

L = 5


def moves(w):
    return [1 if c == 'm' else 0 for c in w]


def trajectory(vm, kind, s):
    if kind == 'pull':
        f = (s - 1) % L; frozen = {f, s}; rel_s = 2
    else:
        f = s; frozen = {s, (s + 1) % L}; rel_s = -1
    pm = [0 if t in frozen else 1 for t in range(L)]
    rel = [None] * L; rel[s] = rel_s; t = s
    for _ in range(L):
        rel[(t + 1) % L] = rel[t] + pm[t] - vm[t]; t = (t + 1) % L
    if rel[s] != rel_s:
        return None
    for t in range(L):
        if kind == 'pull' and rel[t] < 1: return None
        if kind == 'push' and rel[t] > -1: return None
    for t in range(L):  # static infeasibility (rider_floor rule)
        if abs(rel[t]) == 1 and vm[t] and t not in frozen and not pm[t]:
            return None
    return f, frozen, pm, rel


def options(vm, mvd, is_v, kind, f, frozen, pm, rel):
    out = []
    for bits in itertools.product((0, 1), repeat=L):
        ok = True
        for t in range(L):
            if mvd[t] == pm[t] and bits[(t + 1) % L] != bits[t]: ok = False; break
        if not ok: continue
        if bits[f] and mvd[f] and not (kind == 'push' and is_v): continue
        bad = False
        for t in range(L):
            if abs(rel[t]) == 1:
                if is_v and not bits[t]: bad = True; break
                if (not is_v) and vm[t] and mvd[t] and bits[t] and (pm[t] or t == f): bad = True; break
            if t == f and kind == 'push' and (not is_v) and mvd[t] and bits[t]: bad = True; break
        if bad: continue
        out.append(bits)
    return out


def solve(bodies, kinds=None, rear=(), W_REAR=1000, W_ALL=30, cap=None, time_limit=60, allow=None, K=None, base=11,
          excess=False, ref_kinds=None, ref_allow=None, c_kind=5, c_edge=2):
    """bodies: dict name -> (word, glue).  kinds: dict (name,slot)->'push'/'pull' to fix, else free.
    allow: optional dict piston-target-name -> set of body names allowed to touch its pistons (adjacency limit)."""
    names = list(bodies)
    mv = {n: moves(bodies[n][0]) for n in names}
    var = []  # (piston key, body, bits) ; plus kind vars
    kvars = []  # (V, s, kind, traj)
    for V in names:
        for s in range(L):
            if not mv[V][s]: continue
            for kind in ('push', 'pull'):
                if kinds and (V, s) in kinds and kinds[(V, s)] != kind: continue
                tr = trajectory(mv[V], kind, s)
                if tr is None: continue
                kvars.append((V, s, kind, tr))
    nk = len(kvars)
    rows = []  # (coeff dict, lo, hi)
    for i, (V, s, kind, (f, frozen, pm, rel)) in enumerate(kvars):
        for d in names:
            al = allow.get((V, kind), allow.get(V, set())) if allow is not None else None
            if allow is not None and d != V and d not in al:
                ops = [b for b in options(mv[V], mv[d], d == V, kind, f, frozen, pm, rel) if not any(b)]
            else:
                ops = options(mv[V], mv[d], d == V, kind, f, frozen, pm, rel)
            idx0 = len(var)
            for b in ops: var.append((i, d, b))
            rows.append(({nk + j: 1 for j in range(idx0, len(var))} | {i: -1}, 0, 0))
    # exactly one kind per move
    for V in names:
        for s in range(L):
            if not mv[V][s]: continue
            ids = [i for i, k in enumerate(kvars) if k[0] == V and k[1] == s]
            if not ids: return None
            rows.append(({i: 1 for i in ids}, 1, 1))
    # carrier coverage
    for i, (V, s, kind, (f, frozen, pm, rel)) in enumerate(kvars):
        for t in range(L):
            if not pm[t]: continue
            c = {nk + j: 1 for j, (ii, d, b) in enumerate(var) if ii == i and mv[d][t] and b[t]}
            c[i] = c.get(i, 0) - 1
            rows.append((c, 0, np.inf))
    nv0 = nk + len(var)
    zkeys = []
    if K is not None:
        zkeys = [(V, d) for V in names for d in names if d != V]
    zid = {k: nv0 + j for j, k in enumerate(zkeys)}
    if K is not None:
        for j, (i, d, b) in enumerate(var):
            V = kvars[i][0]
            if d != V and any(b): rows.append(({nk + j: 1, zid[(V, d)]: -1}, -np.inf, 0))
        for V in names:
            rows.append(({zid[(V, d)]: 1 for d in names if d != V}, 0, K))
    nv = nv0 + len(zkeys)
    # load variables per (body, moving slot) and maxima
    lmoves = [(n, t) for n in names for t in range(L) if mv[n][t]]
    lid = {m: nv + j for j, m in enumerate(lmoves)}
    MR, MA = nv + len(lmoves), nv + len(lmoves) + 1
    eid = {m: MA + 1 + j for j, m in enumerate(lmoves)}
    N = MA + 1 + len(lmoves)
    for (n, t) in lmoves:
        c = {nk + j: 1 for j, (i, d, b) in enumerate(var) if d == n and b[t] and kvars[i][3][2][t]}
        c[lid[(n, t)]] = -1
        rows.append((c, -bodies[n][1], -bodies[n][1]))  # load = glue + riders
        rows.append(({MA: 1, lid[(n, t)]: -1}, 0, np.inf))
        if n in rear: rows.append(({MR: 1, lid[(n, t)]: -1}, 0, np.inf))
        if cap is not None: rows.append(({lid[(n, t)]: 1}, -np.inf, cap))
        rows.append(({eid[(n, t)]: 1, lid[(n, t)]: -1}, -base, np.inf))  # excess >= load - base
    A = np.zeros((len(rows), N)); lo = np.zeros(len(rows)); hi = np.zeros(len(rows))
    for r, (c, a, b) in enumerate(rows):
        for k, v in c.items(): A[r, k] += v
        lo[r], hi[r] = a, b
    obj = np.zeros(N); obj[MR] = W_REAR; obj[MA] = W_ALL
    for m in lmoves: obj[lid[m]] = 1
    if excess:  # minimise sum of excess over base (rear weighted), loads only tie-break
        obj[MR] = obj[MA] = 0
        for m in lmoves:
            obj[lid[m]] = 0.01
            obj[eid[m]] = W_REAR if m[0] in rear else W_ALL
    integ = np.zeros(N); integ[:nv] = 1
    if ref_kinds:
        for i, (V, s_, kind, _) in enumerate(kvars):
            if ref_kinds.get((V, s_)) != kind: obj[i] += c_kind
    if ref_allow and K is not None:
        for (V, d), j in zid.items():
            if d not in ref_allow.get(V, set()): obj[j] += c_edge
    ub = np.full(N, np.inf); ub[:nv] = 1
    for m in lmoves: ub[eid[m]] = np.inf
    res = milp(obj, constraints=LinearConstraint(A, lo, hi), integrality=integ, bounds=Bounds(0, ub),
               options={'time_limit': time_limit})
    if res.x is None: return None
    x = res.x
    loads = {m: int(round(x[lid[m]])) for m in lmoves}
    chosen = [kvars[i][:3] for i in range(nk) if x[i] > .5]
    carry = {}
    for j, (i, d, b) in enumerate(var):
        if x[nk + j] > .5 and any(b[t] and kvars[i][3][2][t] and mv[d][t] for t in range(L)):
            carry.setdefault(kvars[i][:3], []).append((d, ''.join(map(str, b))))
    touch = {V: sorted(d for (VV, d) in zkeys if VV == V and x[zid[(VV, d)]] > .5) for V in names} if K else {}
    return dict(touch=touch, status=res.status, loads=loads, kinds=chosen, carry=carry,
                max_rear=max([v for (n, t), v in loads.items() if n in rear], default=0),
                max_all=max(loads.values()))


def report(r, bodies, rear, lim=12):
    if r is None: print('  INFEASIBLE'); return
    n12r = sum(1 for (n, t), v in r['loads'].items() if n in rear and v >= lim)
    n12 = sum(1 for v in r['loads'].values() if v >= lim)
    print(f"  status {r['status']} max_rear {r['max_rear']} max_all {r['max_all']} rear>={lim}: {n12r} all>={lim}: {n12}")
    for n in bodies:
        ks = ' '.join(f"s{s}{'P' if k == 'pull' else 'p'}" for (V, s, k) in sorted(r['kinds']) if V == n)
        ls = ' '.join(f"{r['loads'][(n, t)]}" for t in range(L) if (n, t) in r['loads'])
        print(f"   {n:4s} {bodies[n][0]} g{bodies[n][1]:2d} {ks:16s} loads {ls}{'  REAR' if n in rear else ''}")


TM = {  # tm_smol: word, glue minus glued stickies (stickies counted as riders by the model)
    'B9': ('mwwmm', 7), 'B10': ('wmmmw', 9), 'B11': ('mmwwm', 9), 'B15': ('mmmww', 10), 'B18': ('wwmmm', 7),
    'B19': ('wmmmw', 7), 'B24': ('mmmww', 8), 'B29': ('mmwwm', 8), 'B35': ('mwwmm', 8), 'B36': ('wwmmm', 7),
    'B37': ('wmmmw', 7), 'B41': ('mmmww', 7), 'B45': ('mmwwm', 7)}
TM_REAR = ('B9', 'B10', 'B11', 'B15', 'B18')
TM_PULLS = {('B9', 0), ('B29', 1), ('B35', 0), ('B15', 2), ('B10', 3), ('B18', 4)}

if __name__ == '__main__':
    kinds = {(n, s): ('pull' if (n, s) in TM_PULLS else 'push') for n in TM for s in range(L) if TM[n][0][s] == 'm'}
    print('tm_smol, fixed kinds (validation; ledger: rear max 12, 8 rear 12s, 12 total):')
    report(solve(TM, kinds, TM_REAR), TM, TM_REAR)
    print('tm_smol words, free kinds:')
    report(solve(TM, None, TM_REAR), TM, TM_REAR)

TM_ALLOW = {'B9': {'B15', 'B19'}, 'B10': {'B9', 'B29'}, 'B11': {'B10'}, 'B15': {'B18', 'B35'}, 'B18': {'B11', 'B24'},
            'B19': {'B9'}, 'B24': {'B18'}, 'B29': {'B19', 'B36'}, 'B35': {'B24', 'B37'}, 'B36': {'B29'},
            'B37': {'B35'}, 'B41': {'B36'}, 'B45': {'B37'}}  # ledger carriers + pullers (foreign only)

if __name__ == '__main__' and 'allow' in sys.argv:
    print('tm_smol fixed kinds, real carrier graph:')
    report(solve(TM, kinds, TM_REAR, allow=TM_ALLOW), TM, TM_REAR)
    print('tm_smol free kinds, real carrier graph:')
    report(solve(TM, None, TM_REAR, allow=TM_ALLOW), TM, TM_REAR)

if __name__ == '__main__' and 'excess' in sys.argv:
    print('tm_smol fixed kinds, real graph, excess objective (cap 12):')
    report(solve(TM, kinds, TM_REAR, allow=TM_ALLOW, cap=12, excess=True), TM, TM_REAR)
    print('tm_smol words, free kinds, real graph, excess (cap 12):')
    report(solve(TM, None, TM_REAR, allow=TM_ALLOW, cap=12, excess=True), TM, TM_REAR)
    print('tm_smol words, free kinds, any graph K=2, excess (cap 12):')
    r = solve(TM, None, TM_REAR, K=2, cap=12, excess=True, time_limit=120); report(r, TM, TM_REAR); print(r and r['touch'])


def boxes_of(path):
    import re
    boxes = {}
    for line in open(path):
        m = re.match(r'\s*(B\d+): n=\d+ .*box x(\d+)-(\d+) y(\d+)-(\d+) z(\d+)-(\d+)', line)
        if m: boxes[m.group(1)] = [int(v) for v in m.groups()[1:]]
    return boxes


def directed_graph(path, gap=2, names=None):
    bx = boxes_of(path); NG = near_graph(path, gap); out = {}
    for V in (names or bx):
        out[(V, 'pull')] = {d for d in NG[V] if bx[d][1] >= bx[V][1]}   # toucher reaches as far forward
        out[(V, 'push')] = {d for d in NG[V] if bx[d][0] <= bx[V][1] - 1}  # toucher not entirely in front
    return out


def near_graph(path, gap=2):
    import re
    boxes = {}
    for line in open(path):
        m = re.match(r'\s*(B\d+): n=\d+ .*box x(\d+)-(\d+) y(\d+)-(\d+) z(\d+)-(\d+)', line)
        if m: boxes[m.group(1)] = [int(v) for v in m.groups()[1:]]
    def dist(a, b):
        return max(max(a[2*i] - b[2*i+1], b[2*i] - a[2*i+1], 0) for i in range(3))
    return {V: {d for d in boxes if d != V and dist(boxes[V], boxes[d]) <= gap} for V in boxes}

if __name__ == '__main__' and 'near' in sys.argv:
    gap = int(sys.argv[sys.argv.index('near') + 1])
    NG = {k: v for k, v in near_graph('../base.bodytrack.txt', gap).items() if k in TM}
    print('near graph gap', gap, {k: sorted(v) for k, v in NG.items()})
    print('  real graph within near graph:', all(TM_ALLOW[k] <= NG[k] for k in TM))
    r = solve(TM, None, TM_REAR, allow=NG, K=2, cap=12, excess=True, time_limit=120); report(r, TM, TM_REAR); print(r and r['touch'])

if __name__ == '__main__' and 'whatif' in sys.argv:
    NG = {k: v for k, v in near_graph('../base.bodytrack.txt', 2).items() if k in TM}
    def run(label, bodies):
        r = solve(bodies, None, TM_REAR, allow=NG, K=2, cap=12, excess=True, time_limit=120)
        if r is None: print(label, 'INFEASIBLE'); return
        n12r = sum(1 for (n, t), v in r['loads'].items() if n in TM_REAR and v >= 12)
        n12 = sum(1 for v in r['loads'].values() if v >= 12)
        print(f'{label:34s} rear12 {n12r} all12 {n12} pulls {sum(1 for k in r["kinds"] if k[2]=="pull")}')
        return r
    run('base (B15 g10)', TM)
    T = dict(TM); T['B15'] = ('mmmww', 9); run('B15 g9', T)
    for w in ('mmwmw', 'mwmmw', 'wmmwm', 'mwmwm', 'wmwmm'):
        T2 = dict(T); T2['B9'] = (w, 7); run(f'B15 g9, B9 {w}', T2)

if __name__ == '__main__' and 'minimal' in sys.argv:
    NG = {k: v for k, v in near_graph('../base.bodytrack.txt', 2).items() if k in TM}
    g15 = int(sys.argv[sys.argv.index('minimal') + 1])
    T = dict(TM); T['B15'] = ('mmmww', g15)
    for ck in (5, 50, 300):
        r = solve(T, None, TM_REAR, allow=NG, K=2, cap=12, excess=True, time_limit=120,
                  ref_kinds=kinds, ref_allow=TM_ALLOW, c_kind=ck, c_edge=ck // 2 or 1)
        n12r = sum(1 for (n, t), v in r['loads'].items() if n in TM_REAR and v >= 12)
        n12 = sum(1 for v in r['loads'].values() if v >= 12)
        flips = [k for k in r['kinds'] if kinds[(k[0], k[1])] != k[2]]
        edges = [(V, d) for V, ds in r['touch'].items() for d in ds if d not in TM_ALLOW[V]]
        drop = [(V, d) for V in TM for d in TM_ALLOW[V] if d not in r['touch'][V]]
        print(f'B15 g{g15} cost {ck}: rear12 {n12r} all12 {n12} flips {flips} new edges {edges} dropped {drop}')

if __name__ == '__main__' and 'directed' in sys.argv:
    DG = directed_graph('../base.bodytrack.txt', 2, TM)
    for (V, k) in list(DG): DG[(V, k)] |= TM_ALLOW[V]
    bad = [(V, k, d) for (V, s_), k in kinds.items() for d in TM_ALLOW[V] if False]
    for g15 in (10, 9):
        T = dict(TM); T['B15'] = ('mmmww', g15)
        r = solve(T, None, TM_REAR, allow=DG, K=2, cap=12, excess=True, time_limit=120,
                  ref_kinds=kinds, ref_allow=TM_ALLOW, c_kind=50, c_edge=25)
        if r is None: print('g', g15, 'INFEASIBLE'); continue
        n12r = sum(1 for (n, t), v in r['loads'].items() if n in TM_REAR and v >= 12)
        n12 = sum(1 for v in r['loads'].values() if v >= 12)
        flips = [k for k in r['kinds'] if kinds[(k[0], k[1])] != k[2]]
        edges = [(V, d) for V, ds in r['touch'].items() for d in ds if d not in TM_ALLOW[V]]
        drop = [(V, d) for V in TM for d in TM_ALLOW[V] if d not in r['touch'][V]]
        print(f'B15 g{g15}: rear12 {n12r} all12 {n12} flips {flips} new edges {edges} dropped {drop}')
        report(r, T, TM_REAR)
    # is the real tm_smol consistent with the directed rule?
    r0 = solve(TM, kinds, TM_REAR, allow=DG, cap=12, excess=True)
    print('real kinds under directed graph:', 'INFEASIBLE' if r0 is None else (r0['max_rear'], r0['max_all']))

if __name__ == '__main__' and 'subsets' in sys.argv:
    DG = directed_graph('../base.bodytrack.txt', 2, TM)
    for (V, k) in list(DG): DG[(V, k)] |= TM_ALLOW[V]
    FL = [('B11', 1), ('B19', 3), ('B24', 2), ('B36', 4), ('B37', 3)]
    g15 = int(sys.argv[sys.argv.index('subsets') + 1])
    T = dict(TM); T['B15'] = ('mmmww', g15)
    for m in range(32):
        sub = [FL[i] for i in range(5) if m >> i & 1]
        kk = dict(kinds)
        for f_ in sub: kk[f_] = 'pull'
        r = solve(T, kk, TM_REAR, allow=DG, K=2, cap=12, excess=True, time_limit=60, ref_allow=TM_ALLOW, c_edge=25)
        if r is None: print(len(sub), sub, 'INFEASIBLE'); continue
        n12r = sum(1 for (n, t), v in r['loads'].items() if n in TM_REAR and v >= 12)
        n12 = sum(1 for v in r['loads'].values() if v >= 12)
        print(len(sub), f'rear12 {n12r} all12 {n12}', [f'{a}s{b}' for a, b in sub])
