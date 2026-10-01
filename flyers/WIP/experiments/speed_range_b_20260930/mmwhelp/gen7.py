"""Rider-aware variant of overnight_20260930/mmw_planar.py build().

Same lifecycle contract (three mmw bodies, four coplanar ports each, nine-cell cross, per-port owned source,
per-piston recovery contacts).  Changes (generation only, no simulator/format change):
  * every (piston, slot) recovery need is assigned to exactly one carrier body;
  * a cell of body i may touch a moving piston at slot t only if that (piston,slot) is assigned to i (strict) -
    this removes incidental double adjacency that raised the worst-case action load;
  * per (body, slot) rider count is capped (default 4) so foreign hands are split between the two other bodies;
  * optional random preference for splitting.
Returns (flyer, data) like build(), or (None, reason).
"""
import random, heapq, collections
import model
mp = model.mp
m = model.m
ns = model.ns
S = m.S; DISP = m.DISP; D = m.D
from fastflyer import Flyer, Block, Kind


def dist1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) == 1


def build2(seed, centers, cap=99, strict=False, share_rs=False, share_obs=False, cost_cap=50, ranges=((-6, 7), (-5, 12), (-5, 10)), fronts=(-1, 0, 1), rots=None, front_choice=None, lane_perm=None, stop_after_mandatory=False, template=False):
    rng = random.Random(seed)
    ss = [set() for _ in range(3)]
    point_G = []
    obs_f = []
    ps = []
    sources = []
    for i, phase in enumerate((0, 2, 1)):
        cy, cz = centers[i]
        front = rng.choice(fronts) if front_choice is None else front_choice[i]
        q = rng.randrange(4) if rots is None else rots[i]

        def point(p, front=front, q=q, cy=cy, cz=cz):
            x, y, z = p
            for _ in range(q):
                y, z = -z, y
            return x + front, y + cy, z + cz
        LANES = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if lane_perm == 'rand':
            while True:
                perm = rng.sample(LANES, 4)
                add = lambda a, b: (a[0] + b[0], a[1] + b[1])
                ok = True
                if share_rs and (perm[0][0] + perm[2][0] == 0 and perm[0][1] + perm[2][1] == 0):
                    ok = False
                if share_obs and (perm[1][0] + perm[3][0] == 0 and perm[1][1] + perm[3][1] == 0):
                    ok = False
                if ok:
                    break
        elif lane_perm is not None:
            perm = lane_perm[i]
        else:
            perm = LANES
        ports = [(0,) + perm[0], (1,) + perm[1], (3,) + perm[2], (4,) + perm[3]]
        cross = [(0, 0)] + list(perm)
        if share_rs:
            cross.append((perm[0][0] + perm[2][0], perm[0][1] + perm[2][1]))
        else:
            cross += [(2 * perm[0][0], 2 * perm[0][1]), (2 * perm[2][0], 2 * perm[2][1])]
        gd = (perm[1][0] + perm[3][0], perm[1][1] + perm[3][1])
        if share_obs == 'diag':
            cross.append(gd)
        elif not share_obs:
            cross += [(2 * perm[1][0], 2 * perm[1][1]), (2 * perm[3][0], 2 * perm[3][1])]
        for y, z in cross:
            ss[i].add(point((0, y, z)))
        if share_obs == 'diag':
            ss[i].add(point((-1, gd[0], gd[1])))
            point_G.append(point((-1, gd[0], gd[1])))
        elif share_obs:
            ss[i].add(point((-1, 0, 0)))
            point_G.append(point((-1, 0, 0)))
        else:
            point_G.append(point((-1, 0, 0)))
        for f, y, z in ports:
            dp = [sum((t - f) % 6 not in (0, 1) for t in range(s)) for s in range(6)]
            base = -1 if f < 2 else -2
            newdp = [4 * ((phase + t) // 6) + dp[(phase + t) % 6] - dp[phase] for t in range(6)]
            ps.append((point((base + dp[phase] - m.DISP[0][phase], y, z)), newdp, (f - phase) % 6, i, False))
            obs_f.append(f in (1, 4))
            out = point((0, -y, -z)); origin = point((0, 0, 0))
            direction = m.D.index(tuple(a - b for a, b in zip(out, origin)))
            if share_rs and f in (0, 3):
                if f == 0:
                    sources.append((point((-1, perm[0][0] + perm[2][0], perm[0][1] + perm[2][1])), i, False, direction))
            elif share_obs and f in (1, 4):
                if f == 1:
                    sources.append((point((-2, gd[0], gd[1])) if share_obs == 'diag' else point((-2, 0, 0)), i, True, 0))
            else:
                sources.append((point((-1, 2 * y, 2 * z)), i, f in (1, 4), direction))
    mand0 = [sorted(x) for x in ss]
    legal = ns['make_legal'](ss, ps, sources)
    if not callable(legal):
        return None, legal[1]
    if any(not legal(p, i) for i, s in enumerate(ss) for p in s):
        return None, 'mandatory'
    if share_obs:
        for i in range(3):
            G = point_G[i]
            want = {(j, ps[j][2]) for j in range(len(ps)) if ps[j][3] == i and obs_f[j]}
            powered = set()
            for t in range(6):
                if not S[i][(t - 1) % 6]:
                    continue
                g = m.shift(G, DISP[i][t])
                for j, (pp, dp, f, tg, st) in enumerate(ps):
                    b = m.shift(pp, dp[t])
                    if dist1(g, b) and g != m.shift(b, 1):
                        powered.add((j, t))
            if powered != want:
                return None, 'hardpower'
    if stop_after_mandatory:
        return 'mand_ok', None
    rec = [[t for t in range(6) if (t - f) % 6 not in (0, 1)] for (pp, dp, f, tg, st) in ps]
    A = {}
    cnt = collections.Counter()

    def adj_pairs(p, i):
        out = []
        for t in range(6):
            if not S[i][t]:
                continue
            c = m.shift(p, DISP[i][t])
            for j, (pp, dp, f, tg, st) in enumerate(ps):
                if t in rec[j] and dist1(c, m.shift(pp, dp[t])):
                    out.append((j, t))
        return out

    def okadj(p, i, extra=None):
        add = collections.Counter()
        for (j, t) in adj_pairs(p, i):
            a = A.get((j, t))
            if a is None:
                add[t] += 1
            elif a != i and strict:
                return False
        for t, n in add.items():
            if cnt[(i, t)] + n > cap:
                return False
        return True

    def commit(p, i):
        for (j, t) in adj_pairs(p, i):
            if (j, t) not in A:
                A[(j, t)] = i
                cnt[(i, t)] += 1
    for i, s in enumerate(ss):
        for p in s:
            commit(p, i)
    if template:
        import itertools as _it
        KINDS = (('beside', 0), ('front', 1), ('back', -1))
        def tcombos(pp, dp, f, maxn):
            R = [t for t in range(6) if (t - f) % 6 not in (0, 1)]
            allo = []
            for X in range(3):
                for cx in range(-8, 9):
                    for kind, dl in KINDS:
                        cov = frozenset(t for t in R if S[X][t] and (cx + DISP[X][t]) == (pp[0] + dp[t] + dl))
                        if cov:
                            allo.append((X, cx - pp[0], kind, cov))
            out = []
            for n in range(2, maxn + 1):
                for combo in _it.combinations(allo, n):
                    cov = set(); per = collections.defaultdict(set)
                    for X, off, kind, c in combo:
                        cov |= c; per[X] |= c
                    if cov != set(R):
                        continue
                    if sum(1 for t in R if sum(1 for X in per if t in per[X]) > 1) == 0:
                        out.append(combo)
            return out
        TC = {}
        for j in rng.sample(range(len(ps)), len(ps)):
            pp, dp, f, tg, st = ps[j]
            key = (pp[0], tuple(dp), f)
            if key not in TC:
                TC[key] = tcombos(pp, dp, f, 3)
            combos = list(TC[key]); rng.shuffle(combos)
            combos.sort(key=lambda c: len(c))
            placed = False
            for combo in combos[:40]:
                choice = []
                ok = True
                for X, off, kind, cov in combo:
                    cx = pp[0] + off
                    if kind == 'beside':
                        ps_ = [(cx, pp[1] + d[1], pp[2] + d[2]) for d in m.D[2:]]
                    else:
                        ps_ = [(cx, pp[1], pp[2])]
                    cands = []
                    for p in ps_:
                        if p in ss[X]:
                            cands = [(-1, 0, p)]; break
                        if any(p in ss[k] for k in range(3)):
                            continue
                        if not legal(p, X):
                            continue
                        distance = min(sum(abs(a - b) for a, b in zip(p, v)) for v in ss[X])
                        cands.append((0, distance + rng.random(), p))
                    if not cands:
                        ok = False; break
                    choice.append((X, min(cands)[2]))
                if ok:
                    for X, p in choice:
                        if p not in ss[X]:
                            ss[X].add(p); legal.cache_clear()
                    placed = True
                    break
            if not placed:
                return None, 'templatecell'
    # recovery coverage
    order = [] if template else rng.sample(ps, len(ps))
    for pp, dp, f, target, sticky in order:
        j = next(k for k, x in enumerate(ps) if x[0] == pp)
        while True:
            unassigned = {t for t in rec[j] if (j, t) not in A}
            if not unassigned:
                break
            opts = []
            for t in unassigned:
                for i in range(3):
                    if not S[i][t]:
                        continue
                    for d in m.D[2:]:
                        p = m.shift(m.add(pp, d), dp[t] - DISP[i][t])
                        if not legal(p, i):
                            continue
                        if p in ss[i]:
                            continue
                        if not okadj(p, i):
                            continue
                        cover = {u for u in unassigned if S[i][u] and dist1(m.shift(p, DISP[i][u]), m.shift(pp, dp[u]))}
                        if t not in cover:
                            continue
                        distance = min(sum(abs(a - b) for a, b in zip(p, v)) for v in ss[i])
                        opts.append((-len(cover), p not in ss[i], distance, rng.random(), p, i, cover))
            if not opts:
                return None, 'pickup'
            *_, p, i, cover = min(opts)
            ss[i].add(p)
            commit(p, i)
            legal.cache_clear()
    # connect bodies
    for i in rng.sample(range(3), 3):
        while len(m.conn(ss[i])) < len(ss[i]):
            legal.cache_clear()
            reached = m.conn(ss[i]); targets = ss[i] - reached
            pq = [(0, rng.random(), p) for p in reached]; heapq.heapify(pq)
            dist = {p: 0 for p in reached}; prev = {}; end = None
            while pq:
                cost, _, p = heapq.heappop(pq)
                if cost != dist[p]:
                    continue
                if p in targets:
                    end = p; break
                if cost > cost_cap - len(ss[i]):
                    continue
                for d in rng.sample(m.D, 6):
                    v = m.add(p, d)
                    if not (ranges[0][0] <= v[0] <= ranges[0][1] and ranges[1][0] <= v[1] <= ranges[1][1] and ranges[2][0] <= v[2] <= ranges[2][1]):
                        continue
                    if v not in ss[i]:
                        if not legal(v, i) or not okadj(v, i):
                            continue
                    nc = cost + int(v not in ss[i])
                    if nc < dist.get(v, 10000):
                        dist[v] = nc; prev[v] = p; heapq.heappush(pq, (nc, rng.random(), v))
            if end is None:
                return None, 'route'
            while end not in reached:
                ss[i].add(end); commit(end, i); end = prev[end]
            if len(ss[i]) > cost_cap:
                return None, 'cap'
    f = Flyer(rng_state=5, push_limit=1000)
    for p, owner, observer, direction in sources:
        f._cells[p] = Block.observer(direction, powered=bool(m.S[owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)
    for pp, dp, phase, target, sticky in ps:
        state = 2 if (0 - phase) % 6 == 1 else 0
        f._cells[pp] = Block.piston(0, state=state)
        if state:
            f._cells[m.shift(pp, 1)] = Block(Kind.PISTON_ARM)
    for i, s in enumerate(ss):
        for p in s:
            assert p not in f._cells
            f._cells[p] = Block(m.K[i])
    return (f, dict(segments=[sorted(s) for s in ss], pistons=ps, sources=sources, counts=list(map(len, ss)), mandatory=mand0)), None
