"""Joint CP for one straight link of a translation ring: V's module (P, R, plate at x=1) + the next body W's extra
glue E (cover for V's spent pushers + W's connector to its own plate), W = V shifted by `step` in (y,z), same x
(d = 0).  Body cost = plate + R + |E| (by translation every body pays one E).  Hand-derived timing rules (see
README); results are verified with nk.Ring.check and the simulator.
python joint_cp.py K A B SY SZ [SECONDS] [XLO]"""
import sys, json, itertools
from ortools.sat.python import cp_model

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def add(l, s, sign=1): return (l[0] + sign * s[0], l[1] + sign * s[1])


def nbs(l): return [(l[0] + a, l[1] + b) for a, b in N4]


def solve(k, a, b, step, secs=60, workers=4, xlo=-4, margin=2, hint=None, extra_cons=None, fix=None, det=None):
    m = cp_model.CpModel()
    B = lambda: m.NewBoolVar('')
    box = [(y, z) for y in range(a) for z in range(b)]
    Wbox = [add(l, step) for l in box]
    ys = [l[0] for l in box + Wbox]; zs = [l[1] for l in box + Wbox]
    region = [(y, z) for y in range(min(ys) - margin, max(ys) + margin + 1)
              for z in range(min(zs) - margin, max(zs) + margin + 1)]
    Xs = list(range(xlo, 2))
    P = {l: B() for l in box}; R = {l: B() for l in box}; PL = {l: B() for l in box}
    F = m.NewConstant(0)
    def g(d, l): return d.get(l, F)
    PV = lambda l: g(P, l); RV = lambda l: g(R, l); PLV = lambda l: g(PL, l)
    PW = lambda l: g(P, add(l, step, -1)); RW = lambda l: g(R, add(l, step, -1)); PLW = lambda l: g(PL, add(l, step, -1))
    PU = lambda l: g(P, add(l, step)); RU = lambda l: g(R, add(l, step)); PLU = lambda l: g(PL, add(l, step))
    E = {(x, l): B() for x in Xs for l in region}
    ge = lambda x, l: E.get((x, l), F)
    EV = lambda x, l: E.get((x, add(l, step)), F)          # V's own extra glue (its cover for U) in V frame
    for l in box:
        m.Add(P[l] + R[l] <= 1)
        m.AddImplication(P[l], PL[l]); m.AddImplication(R[l], PL[l])
        m.AddBoolOr([g(R, v) for v in nbs(l)] + [P[l].Not()])
    m.Add(sum(P.values()) == k)
    # RB of V never adjacent to W's pusher lanes (powers W's returning pushers); W's RB never adjacent to/under V plate
    for l in region:
        for v in nbs(l):
            m.AddBoolOr([RV(l).Not(), PW(v).Not()])
            m.AddBoolOr([RW(l).Not(), PLV(v).Not()])
        m.AddBoolOr([RW(l).Not(), PLV(l).Not()])
        m.AddBoolOr([PW(l).Not(), PLV(l).Not()])            # overlap
        m.AddBoolOr([PLW(l).Not(), PLV(l).Not()])
        m.AddBoolOr([RW(l).Not(), PV(l).Not(), ])
    for (x, l), e in E.items():
        # R1 overlap with V over time (W cell visits x, x+1, x+2)
        if x > -3:
            m.AddImplication(e, PV(l).Not()); m.AddImplication(e, RV(l).Not())
        if x > -2: m.AddImplication(e, PLV(l).Not())
        # glue-glue with V's own extra glue in the same lane: V cell x' not in {x-1..x+2}
        for xp in (x - 1, x, x + 1, x + 2):
            if (xp, add(l, step)) in E: m.AddBoolOr([e.Not(), EV(xp, l).Not()])
        # R2/R3 drags
        if x == 0:
            for v in nbs(l): m.AddImplication(e, PV(v).Not()); m.AddImplication(e, RV(v).Not())
        if x == -1:
            for v in nbs(l): m.AddImplication(e, RV(v).Not())
        # R4/R5 W's own module (W frame = V frame, d = 0)
        if x == -2:
            for v in nbs(l): m.AddImplication(e, PW(v).Not())
        if x >= -3: m.AddImplication(e, PW(l).Not())
        if x >= 0: m.AddImplication(e, RW(l).Not())
        if x == 1: m.AddImplication(e, PLW(l).Not())
        # same material: U (= V - step) glue never adjacent to W glue; keep E clear of U's module lanes
        for v in [l] + nbs(l):
            m.AddImplication(e, PLU(v).Not()); m.AddImplication(e, PU(v).Not()); m.AddImplication(e, RU(v).Not())
    # cover: each V pusher lane behind (-3) or beside (-2)
    for l in box:
        m.AddBoolOr([P[l].Not(), ge(-3, l)] + [ge(-2, v) for v in nbs(l)])
    # connectivity of W's glue: W plate cells (1, l) with PLW(l) + E cells
    sel = {}
    for nd in E:
        if nd[0] == 1:
            v = B(); m.Add(v == E[nd] + PLW(nd[1])); sel[nd] = v     # exclusive (E(1,l) forbids PLW(l))
        else: sel[nd] = E[nd]
    nodes = list(sel)
    idx = set(nodes)
    adj = {u: [w for w in [(u[0] + 1, u[1]), (u[0] - 1, u[1])] + [(u[0], q) for q in nbs(u[1])] if w in idx] for u in nodes}
    root = {u: B() for u in nodes}
    m.AddExactlyOne(root.values())
    if fix:
        l0 = add(tuple(sorted(map(tuple, fix['PL']))[0]), step)
        m.Add(root[(1, l0)] == 1)
    for u in nodes: m.AddImplication(root[u], sel[u])
    n = len(nodes); f = {}
    tot = m.NewIntVar(0, n, ''); m.Add(tot == sum(sel.values()))
    for u in nodes:
        for w in adj[u]:
            f[u, w] = m.NewIntVar(0, n, '')
            m.Add(f[u, w] == 0).OnlyEnforceIf(sel[u].Not()); m.Add(f[u, w] == 0).OnlyEnforceIf(sel[w].Not())
    for u in nodes:
        sup = m.NewIntVar(0, n, '')
        m.Add(sup == tot).OnlyEnforceIf(root[u]); m.Add(sup == 0).OnlyEnforceIf(root[u].Not())
        m.Add(sum(f[u, w] for w in adj[u]) - sum(f[w, u] for w in adj[u]) == sup - sel[u])
    if fix:
        for name, d in (('P', P), ('R', R), ('PL', PL)):
            hs = set(map(tuple, fix[name]))
            for l in d: m.Add(d[l] == (1 if l in hs else 0))
    if extra_cons: extra_cons(m, P, R, PL, E)
    m.Minimize(sum(PL.values()) + sum(R.values()) + sum(E.values()))
    if hint:
        for name, d in (('P', P), ('R', R), ('PL', PL)):
            hs = set(map(tuple, hint[name]))
            for l in d: m.AddHint(d[l], l in hs)
        if 'E' in hint:
            he = {(e[0], tuple(e[1])) for e in hint['E']}
            for e in E: m.AddHint(E[e], e in he)
    s = cp_model.CpSolver(); s.parameters.num_workers = workers
    if det: s.parameters.max_deterministic_time = det
    else: s.parameters.max_time_in_seconds = secs
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    gl = lambda d: sorted(l for l in d if s.Value(d[l]))
    return dict(cost=int(s.ObjectiveValue()), bound=int(s.BestObjectiveBound()), opt=st == cp_model.OPTIMAL,
                P=gl(P), R=gl(R), PL=gl(PL), E=sorted(e for e in E if s.Value(E[e])), a=a, b=b, step=list(step))


def show(r):
    P, R, PL = set(map(tuple, r['P'])), set(map(tuple, r['R'])), set(map(tuple, r['PL']))
    st = tuple(r['step']); E = {(e[0], tuple(e[1])) for e in r['E']}
    PW = {add(l, st) for l in P}; RW = {add(l, st) for l in R}; PLW = {add(l, st) for l in PL}
    ls = list(P | R | PL | PW | RW | PLW | {e[1] for e in E})
    y0, y1 = min(l[0] for l in ls), max(l[0] for l in ls); z0, z1 = min(l[1] for l in ls), max(l[1] for l in ls)
    out = []
    for z in range(z1, z0 - 1, -1):
        row = ''
        for y in range(y0, y1 + 1):
            l = (y, z)
            ch = 'P' if l in P else 'R' if l in R else 'p' if l in PW else 'r' if l in RW else '.'
            if ch == '.' and l in PL: ch = '_'
            if ch == '.' and l in PLW: ch = '-'
            xs = ''.join(str(-e[0]) if e[0] < 0 else ('+' if e[0] == 1 else '0') for e in sorted(E) if e[1] == l)
            row += ch + xs.ljust(3)
        out.append(row)
    return '\n'.join(out)


if __name__ == '__main__':
    k, a, b, sy, sz = map(int, sys.argv[1:6])
    secs = float(sys.argv[6]) if len(sys.argv) > 6 else 60
    xlo = int(sys.argv[7]) if len(sys.argv) > 7 else -4
    r = solve(k, a, b, (sy, sz), secs, xlo=xlo)
    if r is None: print('none'); sys.exit()
    print('cost', r['cost'], 'bound', r['bound'], 'opt', r['opt'], 'plate', len(r['PL']), 'R', len(r['R']), 'E', len(r['E']))
    print(show(r))
    print(json.dumps(r))
