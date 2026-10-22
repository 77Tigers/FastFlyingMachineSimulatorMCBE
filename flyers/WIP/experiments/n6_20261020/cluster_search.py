"""Enumerate pusher clusters (2 RB + 6 P in a small yz grid) and score plate + predecessor cover + exit.
Rules (U-frame, x relative to U's RB plane, at U-local 0):
  cover cell kinds: lateral at x=-2 in a non-P non-R column next to a P column, or directly behind at x=-3;
  allowed X cells: x<=-3 anywhere; x=-2 in non-P non-R columns; x=-1 in columns not P/R/R-adjacent;
  exit: a cell at x in {-2,-1} in a free column (not P, R, P-adjacent, R-adjacent), from which X can rise."""
import itertools, sys
from ortools.sat.python import cp_model
N4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def nb(c): return [(c[0] + a, c[1] + b) for a, b in N4]


def clusters(G=4):
    cells = [(y, z) for y in range(G) for z in range(G)]
    seen = set()
    for R in itertools.combinations(cells, 2):
        if R[1] in nb(R[0]): continue
        adj = {c for r in R for c in nb(r)} - set(R)
        for P in itertools.combinations(sorted(adj), 6):
            plate = set(P) | set(R)
            st = [P[0]]; vis = set()
            while st:
                u = st.pop()
                if u in vis: continue
                vis.add(u); st += [v for v in nb(u) if v in plate]
            if len(vis) != 8: continue
            key = canon(P, R)
            if key in seen: continue
            seen.add(key); yield P, R


def canon(P, R):
    best = None
    for f in range(8):
        def t(c):
            y, z = c
            for _ in range(f % 4): y, z = -z, y
            if f >= 4: z = -z
            return (y, z)
        pp = sorted(t(c) for c in P); rr = sorted(t(c) for c in R)
        oy = min(c[0] for c in pp + rr); oz = min(c[1] for c in pp + rr)
        k = (tuple((a - oy, b - oz) for a, b in pp), tuple((a - oy, b - oz) for a, b in rr))
        if best is None or k < best: best = k
    return best


EXIT2 = False


def cover_cost(P, R, tl=5, workers=4, exit_col=None):
    P, R = set(P), set(R)
    Padj = {c for p in P for c in nb(p)} - P - R
    Radj = {c for r in R for c in nb(r)} - P - R
    ys = [c[0] for c in P | R]; zs = [c[1] for c in P | R]
    cols = [(y, z) for y in range(min(ys) - 3, max(ys) + 4) for z in range(min(zs) - 3, max(zs) + 4)]
    allowed = {}
    for c in cols:
        for x in (-4, -3, -2, -1):
            if x <= -3: ok = True
            elif x == -2: ok = c not in P and c not in R
            else: ok = c not in P and c not in R and c not in Radj
            if ok: allowed[(x,) + c] = True
    free = {c for c in cols if c not in P and c not in R and c not in Padj and c not in Radj}
    if EXIT2:   # exit column must have a free neighbour (room for the next body's RB + front beside the rise)
        free = {c for c in free if any(n in free for n in nb(c))}
    cand = list(allowed); idx = {c: i for i, c in enumerate(cand)}
    m = cp_model.CpModel(); v = [m.NewBoolVar('') for _ in cand]
    for p in P:
        lits = [v[idx[(-2,) + q]] for q in nb(p) if (-2,) + q in idx] + [v[idx[(-3,) + p]]]
        m.AddBoolOr(lits)
    ex = [v[idx[c]] for c in cand if c[0] in (-2, -1) and c[1:] in free]
    m.AddBoolOr(ex)
    # connectivity by depth labels rooted at a chosen exit-capable cell
    root = [m.NewBoolVar('') for _ in cand]
    m.AddExactlyOne(root)
    for i, c in enumerate(cand):
        if not (c[0] in (-2, -1) and c[1:] in free) or (exit_col is not None and c[1:] != tuple(exit_col)): m.Add(root[i] == 0)
        m.AddImplication(root[i], v[i])
    dep = [m.NewIntVar(0, len(cand), '') for _ in cand]
    D6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for i, c in enumerate(cand):
        par = []
        for d in D6:
            n = (c[0] + d[0], c[1] + d[1], c[2] + d[2])
            if n in idx:
                j = idx[n]; b = m.NewBoolVar('')
                m.AddImplication(b, v[j]); m.Add(dep[i] >= dep[j] + 1).OnlyEnforceIf(b); par.append(b)
        m.AddBoolOr(par + [v[i].Not(), root[i]])
        m.Add(dep[i] == 0).OnlyEnforceIf(root[i])
    m.Minimize(sum(v))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_search_workers = workers
    st = sv.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    return int(sv.ObjectiveValue()), sv.StatusName(st), sorted(c for i, c in enumerate(cand) if sv.Value(v[i]))


if __name__ == '__main__':
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    out = []
    cl = list(clusters(G)); print(len(cl), 'clusters', flush=True)
    for P, R in cl:
        r = cover_cost(P, R)
        if r: out.append((r[0], r[1], P, R, r[2]))
    out.sort()
    for o in out[:12]: print(o[0], o[1], 'P', o[2], 'R', o[3], o[4])


def free_cols(P, R, rad=3):
    P, R = set(P), set(R)
    Padj = {c for p in P for c in nb(p)} - P - R
    Radj = {c for r in R for c in nb(r)} - P - R
    ys = [c[0] for c in P | R]; zs = [c[1] for c in P | R]
    return [(y, z) for y in range(min(ys) - rad, max(ys) + rad + 1) for z in range(min(zs) - rad, max(zs) + rad + 1)
            if (y, z) not in P | R | Padj | Radj]


def exit_variants(P, R, slack=1, tl=5, workers=4):
    base = cover_cost(P, R, tl=tl, workers=workers)
    if not base: return []
    out = []
    for f in free_cols(P, R, rad=2):
        r = cover_cost(P, R, tl=tl, workers=workers, exit_col=f)
        if r and r[0] <= base[0] + slack: out.append((r[0], f, r[2]))
    return sorted(out)
