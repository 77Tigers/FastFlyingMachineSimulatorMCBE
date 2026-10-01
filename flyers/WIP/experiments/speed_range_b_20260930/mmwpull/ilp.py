"""Exact routing ILP for a fixed placement (agent F).

python ilp.py PLACE_JSON [rs_seed] [out.flyer]
Fixed: templates, pistons, observers, redstone blocks (placed by gen with rs_seed).
Variables: x[b,c] candidate glue cells, y[b,t,k] rider indicators, flow f on arcs, L.
min 1000*L + sum x   s.t. coverage groups, holders, pairwise conflicts, connectivity (single-commodity flow), loads <= L.
Solution is re-validated by model.all_errors(); violating pairs/triples are cut and re-solved.
"""
import sys, json, random, itertools, time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
import gen, model
from model import nb, sx, Item
from sched import S, DISP


def base_design(place, rs_seed):
    rng = random.Random(rs_seed)
    gt, places, oopt = place
    B = gen.Builder(rng, gt, places, oopt)
    if B.setup():
        return None
    B.foreign('fixed')
    B.armc = [B.d.arm_ext(t) for t in range(6)]
    if not B.place_rs():
        return None
    return B


def solve(place, rs_seed=0, margin=2, time_limit=120, verbose=True, radius=2, Lmax=200, free=False):
    B = base_design(place, rs_seed)
    if B is None:
        return None, 'base'
    d0 = B.d
    if free:
        keepl = {(0, 0, 0), (0, 1, 1), (-1, 1, 0)}
        drop = set()
        for b in range(3):
            for c in gen.TEMPLATE:
                if c not in keepl:
                    drop.add((b, B.w(b, *c)))
        keep = [i for i, it in enumerate(d0.items) if not (it.cat == 'glue' and (it.body, it.pos[0]) in drop)]
        nd = model.Design(d0.gtypes); remap = {}
        for i in keep:
            remap[i] = len(nd.items); nd.items.append(d0.items[i])
        for (i, t), c in d0.carry.items():
            if i in remap: nd.carry[(remap[i], t)] = c
        for i, it in enumerate(nd.items):
            for t in range(6): nd.occ[t][it.pos[t]] = i
            if it.cat == 'piston':
                t = (it.f + 1) % 6; nd.occ[t][sx(it.pos[t], it.face)] = -1 - i
        B.d = d0 = nd
        B.armc = [d0.arm_ext(t) for t in range(6)]
        B.needs = [(i, t, c) for (i, t), c in d0.carry.items() if d0.items[i].cat == 'piston']
    armc = B.armc
    allp = [it.pos[0] for it in d0.items]
    lo = [min(p[k] for p in allp) - margin for k in range(3)]
    hi = [max(p[k] for p in allp) + margin for k in range(3)]
    tmpl = {b: {it.pos[0] for it in d0.items if it.cat == 'glue' and it.body == b} for b in range(3)}
    nsrc = {b: sum(1 for it in d0.items if it.cat in ('rs', 'obs') and it.body == b) for b in range(3)}
    # candidate region: within R of the body's template or of its group/holder cells
    keyc = {b: set(tmpl[b]) for b in range(3)}
    for (pi, t, cb) in B.needs:
        kp = d0.items[pi].pos[t]
        keyc[cb] |= {sx(q, -DISP[cb][t]) for q in nb(kp)}
    for it in d0.items:
        if it.cat == 'rs':
            keyc[it.body] |= set(nb(it.pos[0]))
    def near_fn(b, c):
        return any(sum(abs(p - q) for p, q in zip(c, k)) <= radius for k in keyc[b])
    # candidates
    cand = []
    for b in range(3):
        for x in range(lo[0], hi[0] + 1):
            for y in range(lo[1], hi[1] + 1):
                for z in range(lo[2], hi[2] + 1):
                    c = (x, y, z)
                    if c in tmpl[b]:
                        continue
                    if near_fn(b, c) and not d0.item_errors(d0.glue(b, c), None, armc):
                        cand.append((b, c))
    nodes = [(b, c, True) for b in range(3) for c in tmpl[b]] + [(b, c, False) for b, c in cand]
    idx = {(b, c): i for i, (b, c, _) in enumerate(nodes)}
    N = len(nodes)
    # riders: (b,t,k) for piston k moving at t touched by node at t while b moves
    pist = [i for i, it in enumerate(d0.items) if it.cat == 'piston']
    ppos = {}
    for k in pist:
        it = d0.items[k]
        for t in range(6):
            if it.mv[t]:
                ppos.setdefault((t, it.pos[t]), []).append(k)
    touch = {}  # node -> set of (t,k)
    for i, (b, c, _) in enumerate(nodes):
        s = set()
        for t in range(6):
            if not S[b][t]:
                continue
            p = sx(c, DISP[b][t])
            for q in nb(p):
                for k in ppos.get((t, q), []):
                    s.add((t, k))
        touch[i] = s
    yvars = sorted({(nodes[i][0], t, k) for i in range(N) for (t, k) in touch[i]})
    yidx = {v: N + j for j, v in enumerate(yvars)}
    # arcs within same body between adjacent nodes
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
    # conflicts between candidate pairs of different bodies (pairwise glue-glue legality)
    conflicts = set()
    by_pos = {}
    for i, (b, c, fixed) in enumerate(nodes):
        if not fixed:
            by_pos.setdefault(c, []).append(i)
    for i, (b, c, fixed) in enumerate(nodes):
        if fixed:
            continue
        dd = model.remove_item(d0, -1) if False else None
        it = d0.glue(b, c)
        ii = d0.add_item(it)
        for dx in range(-4, 5):
            for dy, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (c[0] + dx, c[1] + dy, c[2] + dz)
                for j in by_pos.get(q, []):
                    if j <= i or nodes[j][0] == b:
                        continue
                    if d0.item_errors(d0.glue(nodes[j][0], q), None, armc):
                        conflicts.add((i, j))
        B._pop(ii)
    if verbose:
        print('conflicts', len(conflicts), flush=True)
    rows = []  # (coeffs dict, lo, hi)
    # fixed nodes
    lb = np.zeros(nv); ub = np.ones(nv)
    for i, (b, c, fixed) in enumerate(nodes):
        if fixed:
            lb[i] = 1
    for a in range(nA):
        ub[A0 + a] = N
    lb[Lvar] = 0; ub[Lvar] = Lmax
    # coverage groups
    for (pi, t, cb) in B.needs:
        kp = d0.items[pi].pos[t]
        grp = [idx[(cb, sx(q, -DISP[cb][t]))] for q in nb(kp) if (cb, sx(q, -DISP[cb][t])) in idx]
        if any(nodes[g][2] for g in grp):
            continue
        if not grp:
            return None, 'nogroup'
        rows.append(({g: 1 for g in grp}, 1, np.inf))
    for it in d0.items:
        if it.cat == 'rs':
            grp = [idx[(it.body, q)] for q in nb(it.pos[0]) if (it.body, q) in idx]
            if not grp:
                return None, 'noholder'
            rows.append(({g: 1 for g in grp}, 1, np.inf))
    for (i, j) in conflicts:
        rows.append(({i: 1, j: 1}, -np.inf, 1))
    # riders y >= x for touching nodes
    for i in range(N):
        b = nodes[i][0]
        for (t, k) in touch[i]:
            rows.append(({yidx[(b, t, k)]: 1, i: -1}, 0, np.inf))
    # loads
    for b in range(3):
        for t in range(6):
            if not S[b][t]:
                continue
            co = {i: 1 for i in range(N) if nodes[i][0] == b}
            for (bb, tt, k), j in yidx.items():
                if bb == b and tt == t:
                    co[j] = 1
            co[Lvar] = -1
            rows.append((co, -np.inf, -nsrc[b]))
    # flow: root = first fixed node of each body; inflow - outflow = x_v for non-root; f <= N x
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
        rows.append((co, 0, 0))
    integrality = np.zeros(nv)
    integrality[:N + len(yvars)] = 1
    integrality[Lvar] = 1
    cobj = np.zeros(nv)
    cobj[:N] = 1
    cobj[Lvar] = 1000
    extra_cuts = []
    for it_round in range(8):
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
        # build and validate
        d = d0
        added = []
        for i in chosen:
            b, c, _ = nodes[i]
            added.append(d.add_item(d.glue(b, c)))
        errs = d.all_errors()
        ok = model.connected_ok(d)
        if not errs and ok:
            final = model.Design(d.gtypes)
            final = model.remove_item(d, len(d.items))  # copy
            for a in reversed(added):
                B._pop(a)
            return final, round(xs[Lvar])
        # find offending chosen nodes: any chosen node whose own item check fails -> cut that set
        bad = set()
        for a, i in zip(added, chosen):
            if d.item_errors(d.items[a], a, None):
                bad.add(i)
        for a in reversed(added):
            B._pop(a)
        if not bad:
            return None, 'unexplained:' + str(errs[:3])
        # no-good: not all of the bad nodes together with their nearby chosen nodes
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
    g, p, o = json.load(open(sys.argv[1]))
    place = (tuple(g), [(a, tuple(b)) for a, b in p], o)
    rs_seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    radius = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    Lmax = int(sys.argv[5]) if len(sys.argv) > 5 else 200
    free = len(sys.argv) > 7 and sys.argv[7] == 'free'
    tl = float(sys.argv[6]) if len(sys.argv) > 6 else 300
    d, L = solve(place, rs_seed, radius=radius, Lmax=Lmax, time_limit=tl, free=free)
    print('result', L)
    if d is not None and len(sys.argv) > 3:
        print('glue', [sum(1 for it in d.items if it.cat == 'glue' and it.body == b) for b in range(3)], 'model load', d.max_load())
        f = d.to_flyer(limit=d.max_load()); f.translate(20, 20, 20); f.save(sys.argv[3])
