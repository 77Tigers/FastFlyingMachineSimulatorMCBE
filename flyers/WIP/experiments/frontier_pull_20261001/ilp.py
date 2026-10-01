"""Exact glue routing ILP for a fixed placement + power (agent G; adapted from agent F's mmwpull/ilp.py).

python ilp.py SPEC PLACE.pkl POWER_SEED OUT.flyer [radius] [Lmax] [time_limit]
Fixed: templates (lane cells), pistons, sources (placed by gen.Builder.place_power with POWER_SEED).
Variables: x[b,c] candidate glue cells, y[b,t,k] rider indicators, flow on arcs, L.
min 1000*L + sum x  s.t. carry coverage, source holders, pairwise conflicts, connectivity, loads <= L.
Solutions are re-validated with pmodel.all_errors(); offending node sets are cut and re-solved.
"""
import sys, json, random, time, pickle
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
import gen, pmodel, specs, os
CF = os.environ.get("ILP_CF", "0") == "1"
from pmodel import nb, sx


def base(spec, place, pseed, carry_first=False):
    B = gen.Builder(spec, random.Random(pseed), *place)
    if B.setup():
        return None
    B.armc = [B.d.arm_ext(t) for t in range(B.sch.L)]
    if carry_first and spec.get('carry_first'):
        if not B.place_carries(only=spec['carry_first']):
            return None
    if not B.place_power():
        return None
    return B


def solve(spec, place, pseed, margin=2, time_limit=120, verbose=True, radius=2, Lmax=200, rounds=10, seed_cells=None):
    B = base(spec, place, pseed, carry_first=CF)
    if B is None:
        return None, 'base'
    sch = B.sch; L = sch.L; NB = sch.N; DISP = sch.DISP; S = sch.S
    d0 = B.d
    armc = [d0.arm_ext(t) for t in range(L)]
    allp = [it.pos[0] for it in d0.items]
    lo = [min(p[k] for p in allp) - margin for k in range(3)]
    hi = [max(p[k] for p in allp) + margin for k in range(3)]
    tmpl = {b: {it.pos[0] for it in d0.items if it.cat == 'glue' and it.body == b} for b in range(NB)}
    nsrc = {b: sum(1 for it in d0.items if it.cat in ('rs', 'obs', 'glz') and it.body == b) for b in range(NB)}
    needs = [(i, t, c) for (i, t), c in d0.carry.items() if c != d0.items[i].victim]
    keyc = {b: set(tmpl[b]) for b in range(NB)}
    for (pi, t, cb) in needs:
        kp = d0.items[pi].pos[t]
        keyc[cb] |= {sx(q, -DISP[cb][t]) for q in nb(kp)}
    for b in range(NB):
        for hopts in B.holders[b]:
            keyc[b] |= set(hopts)
    if seed_cells:
        for b in range(NB):
            keyc[b] |= set(seed_cells[b])

    # corridors: BFS (legal cells, big box) from fixed cells; add shortest paths to every key cell
    from collections import deque
    blo = [lo[k] - 2 for k in range(3)]; bhi = [hi[k] + 2 for k in range(3)]
    corridor = {b: set() for b in range(NB)}
    for b in range(NB):
        memo = {}
        def legal(c):
            if c in tmpl[b]:
                return True
            if not all(blo[k] <= c[k] <= bhi[k] for k in range(3)):
                return False
            if c not in memo:
                memo[c] = not d0.item_errors(d0.glue(b, c), None, armc)
            return memo[c]
        for src in tmpl[b]:
            prev = {src: None}; dq = deque([src])
            while dq:
                p = dq.popleft()
                for q in nb(p):
                    if q not in prev and legal(q):
                        prev[q] = p; dq.append(q)
            for k in list(keyc[b]) + list(tmpl[b]):
                if k in prev:
                    p = k
                    while p is not None:
                        corridor[b].add(p); p = prev[p]
        keyc[b] |= corridor[b]

    def near_fn(b, c):
        return any(sum(abs(p - q) for p, q in zip(c, k)) <= radius for k in keyc[b])
    cand = []
    for b in range(NB):
        for x in range(blo[0], bhi[0] + 1):
            for y in range(blo[1], bhi[1] + 1):
                for z in range(blo[2], bhi[2] + 1):
                    c = (x, y, z)
                    if c in tmpl[b]:
                        continue
                    if near_fn(b, c) and not d0.item_errors(d0.glue(b, c), None, armc):
                        cand.append((b, c))
    nodes = [(b, c, True) for b in range(NB) for c in tmpl[b]] + [(b, c, False) for b, c in cand]
    idx = {(b, c): i for i, (b, c, _) in enumerate(nodes)}
    N = len(nodes)
    pist = [i for i, it in enumerate(d0.items) if it.cat == 'piston']
    ppos = {}
    for k in pist:
        it = d0.items[k]
        for t in range(L):
            if it.mv[t]:
                ppos.setdefault((t, it.pos[t]), []).append(k)
    touch = {}
    for i, (b, c, _) in enumerate(nodes):
        s = set()
        for t in range(L):
            if not S[b][t]:
                continue
            p = sx(c, DISP[b][t])
            for q in nb(p):
                for k in ppos.get((t, q), []):
                    s.add((t, k))
        touch[i] = s
    yvars = sorted({(nodes[i][0], t, k) for i in range(N) for (t, k) in touch[i]})
    yidx = {v: N + j for j, v in enumerate(yvars)}
    arcs = []
    for i, (b, c, _) in enumerate(nodes):
        for q in nb(c):
            j = idx.get((b, q))
            if j is not None:
                arcs.append((i, j))
    A0 = N + len(yvars)
    nA = len(arcs)
    Lvar = A0 + nA
    nv = Lvar + 1
    if verbose:
        print(f'nodes {N} (cand {len(cand)}) riders {len(yvars)} arcs {nA}', flush=True)
    conflicts = set()
    by_pos = {}
    for i, (b, c, fixed) in enumerate(nodes):
        if not fixed:
            by_pos.setdefault(c, []).append(i)
    for i, (b, c, fixed) in enumerate(nodes):
        if fixed:
            continue
        ii = d0.add_item(d0.glue(b, c))
        for dx in range(-4, 5):
            for dy, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (c[0] + dx, c[1] + dy, c[2] + dz)
                for j in by_pos.get(q, []):
                    if j <= i or nodes[j][0] == b:
                        continue
                    if d0.item_errors(d0.glue(nodes[j][0], q), None, armc):
                        conflicts.add((i, j))
        d0.pop_last()
    if verbose:
        print('conflicts', len(conflicts), flush=True)
    rows = []
    lb = np.zeros(nv); ub = np.ones(nv)
    for i, (b, c, fixed) in enumerate(nodes):
        if fixed:
            lb[i] = 1
    for a in range(nA):
        ub[A0 + a] = N
    lb[Lvar] = 0; ub[Lvar] = Lmax
    for (pi, t, cb) in needs:
        kp = d0.items[pi].pos[t]
        grp = [idx[(cb, sx(q, -DISP[cb][t]))] for q in nb(kp) if (cb, sx(q, -DISP[cb][t])) in idx]
        if not grp:
            return None, 'nogroup'
        rows.append(({g: 1 for g in grp}, 1, np.inf))
    for b in range(NB):
        for hopts in B.holders[b]:
            grp = [idx[(b, q)] for q in hopts if (b, q) in idx]
            if not grp:
                return None, 'noholder'
            rows.append(({g: 1 for g in grp}, 1, np.inf))
    for (i, j) in conflicts:
        if os.environ.get('NOCONF') != '1':
            rows.append(({i: 1, j: 1}, -np.inf, 1))
    for i in range(N):
        b = nodes[i][0]
        for (t, k) in touch[i]:
            rows.append(({yidx[(b, t, k)]: 1, i: -1}, 0, np.inf))
    for b in range(NB):
        for t in range(L):
            if not S[b][t]:
                continue
            co = {i: 1 for i in range(N) if nodes[i][0] == b}
            for (bb, tt, k), j in yidx.items():
                if bb == b and tt == t:
                    co[j] = 1
            co[Lvar] = -1
            if os.environ.get('NOLOAD') != '1':
                rows.append((co, -np.inf, -nsrc[b]))
    roots = {}
    for i, (b, c, fixed) in enumerate(nodes):
        if fixed and b not in roots:
            roots[b] = i
    inA = {i: [] for i in range(N)}; outA = {i: [] for i in range(N)}
    for a, (u, v) in enumerate(arcs):
        outA[u].append(a); inA[v].append(a)
        rows.append(({A0 + a: 1, v: -N}, -np.inf, 0))
        rows.append(({A0 + a: 1, u: -N}, -np.inf, 0))
    for v in range(N):
        if v in roots.values():
            continue
        co = {}
        for a in inA[v]:
            co[A0 + a] = co.get(A0 + a, 0) + 1
        for a in outA[v]:
            co[A0 + a] = co.get(A0 + a, 0) - 1
        co[v] = co.get(v, 0) - 1
        if os.environ.get('NOFLOW') != '1':
            rows.append((co, 0, 0))
    if os.environ.get('ILPDBG') == '1':
        reach = set()
        for b, r in roots.items():
            st = [r]; reach.add(r)
            while st:
                u = st.pop()
                for a in outA[u]:
                    v = arcs[a][1]
                    if v not in reach:
                        reach.add(v); st.append(v)
        print('unreachable fixed', [nodes[i] for i in range(N) if nodes[i][2] and i not in reach])
        for (pi, t, cb) in needs:
            kp = d0.items[pi].pos[t]
            grp = [idx[(cb, sx(q, -DISP[cb][t]))] for q in nb(kp) if (cb, sx(q, -DISP[cb][t])) in idx]
            if not any(g in reach for g in grp):
                print('group unreachable', d0.items[pi].name, t, cb, [nodes[g] for g in grp])
        for b in range(NB):
            for hopts in B.holders[b]:
                grp = [idx[(b, q)] for q in hopts if (b, q) in idx]
                if not any(g in reach for g in grp):
                    print('holder unreachable', b, hopts)
    integrality = np.zeros(nv)
    integrality[:N + len(yvars)] = 1
    integrality[Lvar] = 1
    cobj = np.zeros(nv)
    cobj[:N] = 1
    cobj[Lvar] = 1000
    extra_cuts = []
    for it_round in range(rounds):
        allrows = rows + extra_cuts
        M = lil_matrix((len(allrows), nv))
        rlo = np.zeros(len(allrows)); rhi = np.zeros(len(allrows))
        for r, (co, l, h) in enumerate(allrows):
            for j, v in co.items():
                M[r, j] = v
            rlo[r] = l; rhi[r] = h
        t0 = time.time()
        res = milp(cobj, constraints=LinearConstraint(M.tocsr(), rlo, rhi), integrality=integrality,
                   bounds=Bounds(lb, ub), options=dict(time_limit=time_limit, disp=False))
        if res.x is None:
            return None, 'infeasible:' + str(res.message)
        xs = res.x
        chosen = [i for i in range(N) if xs[i] > 0.5 and not nodes[i][2]]
        if verbose:
            print(f'round {it_round} L={round(xs[Lvar])} glue={sum(1 for i in range(N) if xs[i] > 0.5)} status={res.status} t={time.time()-t0:.1f}s', flush=True)
        n0 = len(d0.items)
        added = []
        for i in chosen:
            b, c, _ = nodes[i]
            added.append(d0.add_item(d0.glue(b, c)))
        errs = d0.all_errors()
        ok = pmodel.connected_ok(d0)
        if not errs and ok:
            final = pmodel.rebuild_without(d0, len(d0.items))
            while len(d0.items) > n0:
                d0.pop_last()
            return final, round(xs[Lvar])
        bad = set()
        for a, i in zip(added, chosen):
            if d0.item_errors(d0.items[a], a, None):
                bad.add(i)
        cov = [e for e in errs if e[0] in ('uncovered', 'nocarrier', 'nocontact', 'power', 'glz_nopush')]
        while len(d0.items) > n0:
            d0.pop_last()
        if not bad:
            return None, 'unexplained:' + str(errs[:3]) + ' conn=' + str(ok)
        cut = {i: 1 for i in bad}
        for i in chosen:
            if i in bad:
                continue
            ci = nodes[i][1]
            if any(sum(abs(p - q) for p, q in zip(ci, nodes[j][1])) <= 3 for j in bad):
                cut[i] = 1
        extra_cuts.append((cut, -np.inf, len(cut) - 1))
    return None, 'rounds'


if __name__ == '__main__':
    spec = specs.SPECS[sys.argv[1]]()
    place = pickle.load(open(sys.argv[2], 'rb'))
    pseed = int(sys.argv[3])
    if len(place) == 2:
        place, pseed = place
    out = sys.argv[4]
    radius = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    Lmax = int(sys.argv[6]) if len(sys.argv) > 6 else 200
    tl = float(sys.argv[7]) if len(sys.argv) > 7 else 300
    sc = None
    for r in range(6):
        Bg, why, _ = gen.build(spec, pseed, place=place, cap=14) if r == 0 else (None, None, None)
        if Bg is not None:
            sc = {b: [it.pos[0] for it in Bg.d.items if it.cat == 'glue' and it.body == b] for b in range(Bg.sch.N)}
            print('greedy load', Bg.d.max_load(), Bg.d.glue_counts(), flush=True)
            break
    if sc is None:
        print('no greedy seed; using key cells only', flush=True)
    d, L = solve(spec, place, pseed, radius=radius, Lmax=Lmax, time_limit=tl, seed_cells=sc)
    print('result', L)
    if d is not None:
        print('glue', d.glue_counts(), 'model load', d.max_load())
        f = d.to_flyer(limit=d.max_load()); f.translate(20, 20, 20); f.save(out)
