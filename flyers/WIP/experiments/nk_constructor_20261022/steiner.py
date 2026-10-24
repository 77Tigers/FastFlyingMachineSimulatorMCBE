"""Exact connector for one body (CP-SAT Steiner tree over the cells nk's checker allows for that body, with every
other body as it is): python steiner.py K [BODY]. Compares with the greedy router's connector."""
import sys, json, time
from ortools.sat.python import cp_model
from nk import D6, add


def comps(cells):
    cells = set(cells); out = []; seen = set()
    for c in sorted(cells):
        if c in seen: continue
        st = [c]; comp = set()
        while st:
            u = st.pop()
            if u in comp: continue
            comp.add(u); st += [add(u, d) for d in D6 if add(u, d) in cells]
        seen |= comp; out.append(comp)
    return out


def exact_connector(r, X, margin=2, secs=20.0, workers=16, hint=None):
    """minimum set of extra cells joining X's plates, contacts and extras (other bodies fixed)"""
    old = r.glue[X]
    term = set(r.plates[X]) | set(r.contacts[X]) | set(r.extra[X])
    r.glue[X] = set(term); r.invalidate()
    ws = r.worlds()
    lo = [min(c[i] for c in term) - margin for i in range(3)]; hi = [max(c[i] for c in term) + margin for i in range(3)]
    cand = [(x, y, z) for x in range(lo[0], hi[0] + 1) for y in range(lo[1], hi[1] + 1) for z in range(lo[2], hi[2] + 1)
            if (x, y, z) not in term]
    ok = [c for c in cand if r.cell_ok(X, c, ws)]
    m = cp_model.CpModel()
    nodes = list(term) + ok; idx = set(nodes)
    v = {c: (m.NewConstant(1) if c in term else m.NewBoolVar('')) for c in nodes}
    tcomp = comps(term)
    root = next(iter(tcomp[0]))
    # flow: root sends one unit to every other terminal component (to one representative cell)
    sinks = [next(iter(cc)) for cc in tcomp[1:]]
    n = len(sinks)
    f = {}
    for c in nodes:
        for d in D6:
            u = add(c, d)
            if u in idx:
                f[c, u] = m.NewIntVar(0, n, '')
                if c not in term: m.Add(f[c, u] == 0).OnlyEnforceIf(v[c].Not())
                if u not in term: m.Add(f[c, u] == 0).OnlyEnforceIf(v[u].Not())
    for c in nodes:
        out = sum(f[c, u] for u in (add(c, d) for d in D6) if (c, u) in f)
        inn = sum(f[u, c] for u in (add(c, d) for d in D6) if (u, c) in f)
        m.Add(out - inn == (n if c == root else -1 if c in sinks else 0))
    m.Minimize(sum(v[c] for c in ok))
    if hint is not None:
        for c in ok: m.AddHint(v[c], c in hint)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = secs; s.parameters.num_workers = workers
    st = s.Solve(m)
    r.glue[X] = old; r.invalidate()
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    return {c for c in ok if s.Value(v[c])}, st == cp_model.OPTIMAL, len(ok), s.BestObjectiveBound()


if __name__ == '__main__':
    import families as F
    k = int(sys.argv[1]); X = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    r = F.build(k, json.load(open('bits.json'))[str(k)])
    cur = r.glue[X] - r.plates[X] - r.contacts[X] - set(r.extra[X])
    t = time.time(); res = exact_connector(r, X, secs=float(sys.argv[3]) if len(sys.argv) > 3 else 20.0, hint=cur)
    print('k', k, 'body', X, 'router connector', len(cur), 'exact', res and (len(res[0]), res[1], 'bound', res[3], 'candidates', res[2]),
          round(time.time() - t, 1))
