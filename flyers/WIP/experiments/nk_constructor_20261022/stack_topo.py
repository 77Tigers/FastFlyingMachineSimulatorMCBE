"""Topology + offset stage for non-uniform stacks (counts only, no layouts).

Positions p: the back bodies of one side of the square ring when the four sides are exact copies, else every back
body (cyclic; the link p -> p+1 is a corner link at the end of each side). Over each back body stands a list of
segments (levels j = 1, 2, ..., possibly none; the top one is the front). Per segment (p, j):
  m   hoppers carried by the segment below (p, j-1)       (j = 1: by back body p)
  s   hoppers carried by the next tower's segment (p+1, j) (it must exist)
  up  pulled by the segment above (p, j+1) (one pull per cycle)
  dn  its sticky pulls the segment below; the sticky is powered by the segment above or by the previous tower's
      segment (p-1, j) (both rest 2 slots earlier)
  m + s + up = k.  Back body p: k - up hoppers, all carried by back body p+1.
Load = size (glue + RBs) + riders (hoppers it carries) + its sticky.
  back size: f_p(t) measured from plain back rings, t = frame offset of the link into p ("reach"; the offsets sum
  to a fixed total over the ring) [+ DK when not pulled: k hoppers instead of k-1]
  segment size (estimate EST, calibrated on the uniform gap-4 stacks k = 3, 4): plate = hoppers + RB lanes
  (rb = ceil(hoppers / 3)), + rb blocks, + POWER per sticky it powers (block + attach cell), + DN_BACK (attach lane
  of a sticky that pulls the back) + ROUTE when it has a sticky, + PULLED when the segment above pulls it (the
  pulled cell), + cover cells when it carries the previous tower's hoppers (COVER + COVER_H per hopper beyond the
  first, + CORNER across a corner link).
  The hoppers (and sticky) of the segment above stand on a segment's plate lanes: m(above) + dn(above) <= plate
  (hopper + RB lanes, + the attach lane of a level-1 sticky).
CP-SAT: minimise the largest load; then prefer fewer cells and (gently) segments with an empty neighbouring column.
Several suggestions: each found structure is excluded and the model solved again.
python stack_topo.py K BACK CV [NSUG] [HMAX]"""
import sys
import square, tower2
from nk import bodies_for
from tower2 import Timing

VRANGE = range(-3, 2)
EST = dict(POWER=2, DN_BACK=1, ROUTE=2, PULLED=1, COVER=3, COVER_H=1, CORNER=2, DK=2, NUDGE=1)


def link_D(k, L):
    T = Timing(k, L)
    return [T.shift(T.nxt(U), T.rest[U]) - T.shift(U, T.rest[U]) for U in range(L)]


def positions(k):
    """(number of positions, whether sides are copies): side positions if the four sides repeat, else all bodies"""
    L = square.ring_size(k); m = L // 4; S = k + 2
    if L >= 8 and (2 * m) % S == 0 and m % bodies_for(k) == 0: return m, True
    return L, False


def corner_link(k, p):
    n, sym = positions(k)
    if sym: return p == n - 1
    m = square.ring_size(k) // 4
    return p % m == m - 1


def xoff_for(k, t):
    """x shifts giving link q the frame offset t[q % len(t)]"""
    L = square.ring_size(k); D = link_D(k, L)
    tg = [t[q % len(t)] for q in range(L)]
    assert sum(tg) == sum(D), (sum(tg), sum(D))
    e = [0]
    for q in range(L - 1): e.append(e[-1] + tg[q] - D[q])
    return e


def offset_total(k):
    n, _ = positions(k); L = square.ring_size(k)
    return sum(link_D(k, L)) * n // L


def probe_vectors(n, tot, vals=VRANGE):
    """a few offset vectors (sum tot) that together give every position every value on its incoming link"""
    need = {(p, v) for p in range(n) for v in vals}; out = []
    lo, hi = min(vals), max(vals)
    while need:
        p0, v0 = min(need)
        t = [None] * n; t[p0] = v0
        for p in range(n):
            if t[p] is None:
                c = [v for v in vals if (p, v) in need]
                t[p] = c[0] if c else lo
        d = tot - sum(t)
        for p in sorted(range(n), key=lambda p: -((p, t[p]) in need)):
            while d and p != p0 and lo <= t[p] + (1 if d > 0 else -1) <= hi:
                t[p] += 1 if d > 0 else -1; d += -1 if d > 0 else 1
        if d: need.discard((p0, v0)); continue
        out.append(t)
        need -= {(p, t[p]) for p in range(n)}
    return out


def measure_reach(k, back, cv, verbose=False):
    """f[p][v] = size of back body p (glue + RBs, plain back ring, routed) when the link into it has offset v"""
    from terrace import collisions
    from tower import route_all
    from nk2 import power_problems
    vmod, step = back
    n, sym = positions(k); tot = offset_total(k)
    f = [dict() for _ in range(n)]
    for t in probe_vectors(n, tot):
        try:
            r = tower2.build(k, 1, 0, (), back=(vmod, step), cv=cv, xoff=xoff_for(k, t))
            if r is None or collisions(r): continue
            route_all(r)
            if r.check() or power_problems(r): continue
        except (AssertionError, RuntimeError):
            continue
        sz = r.size()
        for p in range(n):
            v = t[(p - 1) % n]
            f[p][v] = max(f[p].get(v, 0), sz[p])
        if verbose: print('probe', t, sz[:n], flush=True)
    return f


def rbs(h): return (h + 2) // 3


def seg_size(h, j, dn, up, powers, carried_s, corner, est=EST):
    return h + 2 * rbs(h) + est['POWER'] * powers + (est['DN_BACK'] if dn and j == 1 else 0) + \
        (est['ROUTE'] if dn else 0) + (est['PULLED'] if up else 0) + \
        ((est['COVER'] + est['COVER_H'] * (carried_s - 1) + (est['CORNER'] if corner else 0)) if carried_s else 0)


def evaluate(k, f, towers, links=None, est=EST):
    """loads of a given structure: towers[p] = [(m, s, dn[, pw]), ...] bottom up; pw = 'a' (sticky powered from
    above) or 'p' (by the previous tower's segment); default: from above when there is a segment above. links: offsets of the links INTO each position (None: the best
    for these riders). Returns (max load, back loads, segment loads, links)."""
    n = len(towers)
    seg = lambda p, j: towers[p % n][j - 1] if 1 <= j <= len(towers[p % n]) else None
    up = lambda p, j: bool(seg(p, j + 1) and seg(p, j + 1)[2])
    for p in range(n):
        for j in range(1, len(towers[p]) + 1):
            m, s, dn = seg(p, j)[:3]
            assert m + s + up(p, j) == k, (p, j, towers[p])
            assert s == 0 or seg(p + 1, j) is not None, ('no neighbour', p, j)
    nh = [k - up(p, 0) for p in range(n)]
    rid0 = [nh[(p - 1) % n] + (seg(p, 1)[0] if seg(p, 1) else 0) for p in range(n)]
    extra = [est['DK'] if nh[p] == k else 0 for p in range(n)]
    if links is None:
        links = _best_links(k, f, [rid0[p] + extra[p] for p in range(n)])
        if links is None: return None
    back = [f[p][links[p]] + extra[p] + rid0[p] for p in range(n)]
    def src(p, j):   # who powers (p, j)'s sticky
        g = seg(p, j)
        pw = g[3] if len(g) > 3 else ('a' if seg(p, j + 1) else 'p')
        return (p, j + 1) if pw == 'a' else ((p - 1) % n, j)
    segs = {}
    for p in range(n):
        for j in range(1, len(towers[p]) + 1):
            m, s, dn = seg(p, j)[:3]
            prev = seg(p - 1, j)
            powers = sum(1 for q, jj in ((p, j - 1), ((p + 1) % n, j))
                         if seg(q, jj) and seg(q, jj)[2] and src(q, jj) == (p, j))
            riders = (seg(p, j + 1)[0] if seg(p, j + 1) else 0) + (prev[1] if prev else 0)
            segs[(p, j)] = seg_size(m + s, j, dn, up(p, j), powers, prev[1] if prev else 0,
                                    corner_link(k, (p - 1) % n), est) + riders + (1 if dn else 0)
    return max(back + list(segs.values())), back, segs, links


def _best_links(k, f, add):
    """offsets of the links into each position minimising max f_p(t_p) + add_p (sum fixed; f increasing)"""
    n = len(f); tot = offset_total(k)
    for P in range(1, 500):
        vm = []
        for p in range(n):
            ok = [v for v in f[p] if f[p][v] + add[p] <= P]
            vm.append(max(ok) if ok else None)
        if any(v is None for v in vm) or sum(vm) < tot: continue
        t = list(vm); d = sum(t) - tot
        while d > 0:
            q = max((p for p in range(n) if t[p] - 1 in f[p]), key=lambda p: f[p][t[p]] + add[p], default=None)
            if q is None: break
            t[q] -= 1; d -= 1
        if d == 0: return t
    return None


def solve(k, f, plate0, hmax=4, nsug=6, slack=1, est=EST, secs=20.0, workers=4, forbid=(), all_pulled=False):
    """CP-SAT over towers (heights 0..hmax, per-segment m, s, dn, sticky power source) and link offsets.
    plate0 = the back module's plate lanes. Returns suggestions [(max load, towers, links into each position)]:
    the best, then others within `slack` of it (each found structure is excluded)."""
    from ortools.sat.python import cp_model
    n = len(f); tot = offset_total(k)
    out = []; nogoods = list(forbid); bestP = None
    J = range(1, hmax + 1)
    for it in range(nsug):
        M = cp_model.CpModel()
        e = {(p, j): M.NewBoolVar('') for p in range(n) for j in J}
        mm = {(p, j): M.NewIntVar(0, k, '') for p in range(n) for j in J}
        ss = {(p, j): M.NewIntVar(0, k, '') for p in range(n) for j in J}
        dn = {(p, j): M.NewBoolVar('') for p in range(n) for j in J}
        pa = {(p, j): M.NewBoolVar('') for p in range(n) for j in J}   # sticky powered from above
        pp = {(p, j): M.NewBoolVar('') for p in range(n) for j in J}   # ... by the previous tower's segment
        nxt = lambda p: (p + 1) % n
        prv = lambda p: (p - 1) % n
        def E(p, j): return 1 if j == 0 else (e[(p, j)] if j <= hmax else 0)
        def UP(p, j): return dn[(p, j + 1)] if j + 1 <= hmax else 0
        rb = {}
        for p in range(n):
            for j in J:
                h = mm[(p, j)] + ss[(p, j)]
                rb[(p, j)] = M.NewIntVar(0, k, '')
                M.Add(3 * rb[(p, j)] >= h); M.Add(3 * rb[(p, j)] <= h + 2)
                if j > 1: M.AddImplication(e[(p, j)], e[(p, j - 1)])
                M.Add(mm[(p, j)] + ss[(p, j)] + UP(p, j) == k * e[(p, j)])
                M.AddImplication(dn[(p, j)], e[(p, j)])
                M.Add(ss[(p, j)] <= k * E(nxt(p), j))
                M.Add(pa[(p, j)] + pp[(p, j)] == dn[(p, j)])
                M.Add(pa[(p, j)] <= E(p, j + 1)); M.Add(pp[(p, j)] <= E(prv(p), j))
        if all_pulled:   # every back body pulled (k-1 hoppers: one back module for the whole ring)
            for p in range(n): M.Add(dn[(p, 1)] == 1)
        for p in range(n):   # the hoppers (and sticky) of the segment above stand on a segment's plate lanes
            M.Add(mm[(p, 1)] + dn[(p, 1)] <= plate0)
            for j in J:
                # (plate lanes: hopper fronts, RB fronts, and the attach lane of a sticky that pulls the back)
                if j < hmax: M.Add(mm[(p, j + 1)] + dn[(p, j + 1)] <=
                                   mm[(p, j)] + ss[(p, j)] + rb[(p, j)] + (dn[(p, j)] if j == 1 else 0))
        tv = {(p, v): M.NewBoolVar('') for p in range(n) for v in f[p]}
        for p in range(n): M.AddExactlyOne(tv[(p, v)] for v in f[p])
        M.Add(sum(v * tv[(p, v)] for p in range(n) for v in f[p]) == tot)
        P = M.NewIntVar(0, 1000, 'P')
        loads = []
        for p in range(n):
            size = sum(f[p][v] * tv[(p, v)] for v in f[p]) + est['DK'] * (1 - dn[(p, 1)])
            ld = size + k - dn[(prv(p), 1)] + mm[(p, 1)]
            M.Add(P >= ld); loads.append(ld)
        for p in range(n):
            for j in J:
                h = mm[(p, j)] + ss[(p, j)]
                cov = M.NewBoolVar('')
                M.Add(ss[(prv(p), j)] >= 1).OnlyEnforceIf(cov); M.Add(ss[(prv(p), j)] == 0).OnlyEnforceIf(cov.Not())
                cc = est['COVER'] - est['COVER_H'] + (est['CORNER'] if corner_link(k, prv(p)) else 0)
                powers = (pa[(p, j - 1)] if j > 1 else 0) + pp[(nxt(p), j)]
                riders = (mm[(p, j + 1)] if j < hmax else 0) + ss[(prv(p), j)]
                ld = h + 2 * rb[(p, j)] + est['POWER'] * powers + (est['DN_BACK'] if j == 1 else 0) * dn[(p, j)] + \
                    est['ROUTE'] * dn[(p, j)] + est['PULLED'] * UP(p, j) + cc * cov + \
                    est['COVER_H'] * ss[(prv(p), j)] + riders + dn[(p, j)]
                M.Add(P >= ld).OnlyEnforceIf(e[(p, j)]); loads.append(ld)
        emp = []   # gentle nudge: segments with an empty neighbouring column at their level
        for p in range(n):
            for j in J:
                b = M.NewBoolVar('')
                M.Add(b <= e[(p, j)]); M.Add(b <= 2 - E(prv(p), j) - E(nxt(p), j))
                emp.append(b)
        if bestP is not None: M.Add(P <= bestP + slack)
        for ng in nogoods:
            lits = []
            for (p, j), (ex, m_, s_, d_) in ng.items():
                for var, val in ((mm[(p, j)], m_), (ss[(p, j)], s_)):
                    b = M.NewBoolVar('')
                    M.Add(var != val).OnlyEnforceIf(b); M.Add(var == val).OnlyEnforceIf(b.Not())
                    lits.append(b)
                lits += [e[(p, j)].Not() if ex else e[(p, j)], dn[(p, j)].Not() if d_ else dn[(p, j)]]
            M.AddBoolOr(lits)
        M.Minimize(1000 * P + sum(loads) - est['NUDGE'] * sum(emp))
        sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = secs; sv.parameters.num_workers = workers
        st = sv.Solve(M)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): break
        Pv = sv.Value(P)
        if bestP is None: bestP = Pv
        towers, ng = [], {}
        for p in range(n):
            tw = []
            for j in J:
                ng[(p, j)] = (sv.Value(e[(p, j)]), sv.Value(mm[(p, j)]), sv.Value(ss[(p, j)]), sv.Value(dn[(p, j)]))
                if sv.Value(e[(p, j)]):
                    pw = 'a' if sv.Value(pa[(p, j)]) else 'p' if sv.Value(pp[(p, j)]) else None
                    tw.append((sv.Value(mm[(p, j)]), sv.Value(ss[(p, j)]), sv.Value(dn[(p, j)]), pw))
            towers.append(tw)
        links = [next(v for v in f[p] if sv.Value(tv[(p, v)])) for p in range(n)]
        nogoods.append(ng)
        out.append((Pv, towers, links))
    return out


def show(k, f, sug):
    for P, towers, links in sug:
        ev = evaluate(k, f, towers, links)
        print(f'P {P} (re-evaluated {ev[0]})  links-in {links}  back loads {ev[1]}')
        for p, tw in enumerate(towers):
            print(f'   p{p}: ' + ('-' if not tw else ' | '.join(
                f'm{g[0]} s{g[1]}{" dn" + g[3] if g[2] else ""} ={ev[2][(p, j)]}' for j, g in enumerate(tw, 1))))


if __name__ == '__main__':
    import stack_scan
    k = int(sys.argv[1]); bi = sys.argv[2]; cv = tuple(map(int, sys.argv[3].split(',')))
    nsug = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    hmax = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    e = stack_scan.back_entry(k, bi)
    n, sym = positions(k)
    print('k', k, 'positions', n, 'sym', sym, 'offset total', offset_total(k), 'raw D', link_D(k, square.ring_size(k))[:n])
    f = measure_reach(k, (e['mod'], e['step']), cv)
    print('f', [dict(sorted(d.items())) for d in f])
    std = [[(k - 1, 0, 1), (k, 0, 1), (k, 0, 0)]] * n
    ev = evaluate(k, f, std)
    print('uniform human topology:', ev[0], 'back', ev[1], 'segments', sorted(set(ev[2].values())), 'links', ev[3])
    import os
    show(k, f, solve(k, f, len(e['mod']['PLATE']), hmax, nsug, all_pulled=bool(int(os.environ.get('ALLP', 0)))))
