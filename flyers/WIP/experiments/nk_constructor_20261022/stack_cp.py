"""CP-SAT version of stack.level_opts for any hopper count (the enumeration explodes beyond k ~ 8).
Same lane roles and rules as level_opts (see its docstring): Hm on the lower plate lanes, Hs off them (not in
`forbid`), one sticky lane st on the lower plate (not for the front), an attach lane s2 beside it (level 1), RB
lanes R beside every hopper (or the free lane), loop covers Q beside the loop hoppers; the neighbouring towers are
the same layout shifted by +-step (no shared lanes, no RB beside their hoppers, no own glue beside their hardware,
their hoppers not on / beside our lower plate); below an attach-lane sticky one side lane stays free for its
power block. Objective: RB lanes + 2 * covers + cover distance to the loop neighbour's cluster (approximated by
its lanes) + plate pieces that touch no other plate lane. Solutions are enumerated best first with no-good cuts.
level_cp(...) -> list of dicts like level_opts."""
from ortools.sat.python import cp_model

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


def level_cp(m, s, below, a, b, step, mode, mg=(0, 1), free=None, forbid=frozenset(), low=None, nsol=8, secs=2.0,
             periodic=True):
    my, mz = mg
    inb = lambda l: -my <= l[0] < a + my and -mz <= l[1] < b + mz
    U = [(y, z) for y in range(-1 - my, a + 1 + my) for z in range(-1 - mz, b + 1 + mz) if inb((y, z))]
    Us = set(U); bl = set(below)
    sh = lambda l, sg: (l[0] + sg * step[0], l[1] + sg * step[1])
    md = cp_model.CpModel()
    B = lambda: md.NewBoolVar('')
    z0 = md.NewConstant(0)
    hm = {l: B() for l in U if l in bl}
    hs = {l: B() for l in U if l not in bl and l not in forbid and not (low and low[1] == 'hs' and l == low[0])}
    r = {l: B() for l in U if l != free}
    st = {l: B() for l in U if l in bl} if mode != 'top' else {}
    s2 = {l: B() for l in U if l not in bl} if mode == 's2' else {}
    qbad = set(forbid) | {sh(l, sg) for l in forbid for sg in (1, -1)}
    q = {l: B() for l in U if l not in bl and l not in qbad}
    g = lambda d, l: d.get(l, z0)
    H = lambda l: [x for x in (hm.get(l), hs.get(l)) if x is not None]
    own = lambda l: [x for x in (hm.get(l), hs.get(l), r.get(l), st.get(l), s2.get(l)) if x is not None]
    for l in U:
        md.Add(sum(own(l)) + g(q, l) <= 1)
    md.Add(sum(hm.values()) == m); md.Add(sum(hs.values()) == s)
    if mode != 'top': md.AddExactlyOne(st.values())
    if mode == 's2':
        md.AddExactlyOne(s2.values())
        for l, v in s2.items(): md.Add(v <= sum(g(st, n) for n in nb(l)))
    # every hopper has a redstone block (or the free lane) beside it
    for l in U:
        hv = H(l)
        if not hv: continue
        if free is not None and free in nb(l): continue
        md.Add(sum(hv) <= sum(g(r, n) for n in nb(l)))
    # RB only beside own hoppers (useful); human sticky held by a hopper / RB neighbour
    for l, v in r.items(): md.Add(v <= sum(x for n in nb(l) for x in H(n)))
    if mode == 'hs':
        for l, v in st.items(): md.Add(v <= sum(x for n in nb(l) for x in H(n) + ([r[n]] if n in r else [])))
    # loop covers
    for l, v in hs.items(): md.Add(v <= sum(g(q, n) for n in nb(l)))
    for l, v in q.items():
        md.Add(v <= sum(g(hs, n) for n in nb(l)))
        for n in nb(l):
            if n in hm: md.Add(v + hm[n] <= 1)
            if mode == 'hs' and n in st: md.Add(v + st[n] <= 1)
        if l in r: md.Add(v + r[l] <= 1)
    # neighbouring towers (the same layout shifted by +-step; none when every link is a corner)
    for l in (U if periodic else []):
        for sg in (1, -1):
            l2 = sh(l, sg)
            if l2 in Us:
                for x in own(l):
                    for y in own(l2): md.Add(x + y <= 1)
            # our RB beside their hopper / our glue beside their hardware
            for n in nb(l):
                n2 = sh(n, -sg)        # their lane n is our lane n2 in their frame
                if n2 not in Us: continue
                if l in r:
                    for y in H(n2): md.Add(r[l] + y <= 1)
                glue = [x for x in (hm.get(l), hs.get(l), r.get(l), s2.get(l)) if x is not None]
                hw = H(n2) + ([r[n2]] if n2 in r else []) + ([st[n2]] if n2 in st else [])
                for x in glue:
                    for y in hw: md.Add(x + y <= 1)
        # their hoppers on / beside our lower plate
        for sg in (1, -1):
            t = sh(l, sg)
            if t in bl or any(v in bl for v in nb(t)):
                for x in H(l): md.Add(x == 0)
    # room for the power block of an attach-lane sticky below
    if low is not None and low[1] == 's2':
        ps = [p for p in nb(low[0]) if p not in bl and not (periodic and any(sh(p, sg) in bl for sg in (1, -1)))]
        pv = {p: B() for p in ps}
        if not pv: return []
        md.Add(sum(pv.values()) >= 1)
        for p, v in pv.items():
            for x in own(p): md.Add(v + x <= 1)
            for sg in ((1, -1) if periodic else ()):
                for x in own(sh(p, sg)): md.Add(v + x <= 1)
            for n in nb(p):
                for x in H(n): md.Add(v + x <= 1)
                for sg in ((1, -1) if periodic else ()):
                    for x in H(sh(n, sg)): md.Add(v + x <= 1)
    # objective
    far = []
    for l, v in q.items():
        d = min((abs(l[0] - step[0] - c[0]) + abs(l[1] - step[1] - c[1]) for c in U), default=0)
        far.append(v * max(0, d - 1))
    plate = {l: md.NewBoolVar('') for l in U}
    for l in U: md.Add(plate[l] == sum(x for x in (hm.get(l), hs.get(l), r.get(l), s2.get(l)) if x is not None))
    lone = []
    for l in U:
        y = B(); md.Add(sum(plate[n] for n in nb(l) if n in plate) >= 1).OnlyEnforceIf([plate[l], y.Not()])
        lone.append(y)
    md.Minimize(2 * sum(r.values()) + 4 * sum(q.values()) + 2 * sum(far) + sum(lone))
    out = []
    keyvars = list(hm.values()) + list(hs.values()) + list(r.values()) + list(st.values()) + list(s2.values()) + list(q.values())
    solver = cp_model.CpSolver(); solver.parameters.num_workers = 1; solver.parameters.max_time_in_seconds = secs
    for _ in range(nsol):
        res = solver.Solve(md)
        if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE): break
        val = lambda d: [l for l, v in d.items() if solver.Value(v)]
        Q = val(q)
        out.append(dict(st=(val(st) or [None])[0], s2=(val(s2) or [None])[0], Hm=val(hm), Hs=val(hs), R=val(r), Q=Q,
                        cost=solver.ObjectiveValue(), Qc=[Q]))
        md.AddBoolOr([v.Not() if solver.Value(v) else v for v in keyvars])
    return out
