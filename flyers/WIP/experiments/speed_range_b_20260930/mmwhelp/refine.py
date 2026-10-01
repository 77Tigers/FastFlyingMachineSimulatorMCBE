"""Rip-up/repair hill climb at the abstract-contract level (no simulation), objective = estimated worst action load.

State: per-body glue sets (non-mandatory part is mutable).  Move: delete a random neighbourhood of one body's
optional cells, re-cover uncovered (piston,slot) recovery needs with legal contacts of that body, re-route.
usage: refine.py START.json OUTPREFIX SECONDS SEED [MAXWORSE]
"""
import sys, json, random, time, heapq, collections
import model, est, lazy
from gen2 import dist1
m = model.m; ns = model.ns; S = m.S; DISP = m.DISP
MAND = None
from fastflyer import Flyer, Block, Kind


def load_json(path):
    d = json.load(open(path))
    global MAND
    MAND = [set(map(tuple, x)) for x in d['mandatory']] if 'mandatory' in d else None
    ss = [set(map(tuple, s)) for s in d['segments']]
    ps = [(tuple(p), dp, f, t, st) for p, dp, f, t, st in d['pistons']]
    src = [(tuple(p), o, ob, dr) for p, o, ob, dr in d['sources']]
    return ss, ps, src


def mandatory_of(ss, ps, src):
    import milp_body
    return milp_body.mandatory_sets(ss, ps, src)


def cost_of(ss, ps, src):
    w, det = est.est_load(ss, ps, src)
    return (w, sum(len(s) for s in ss), sorted((len(ss[i]) + sum(1 for x in src if x[1] == i) + max(v[2] for k, v in det.items() if k[0] == i)) for i in range(3))[::-1])


def body_loads(ss, ps, src):
    w, det = est.est_load(ss, ps, src)
    return [len(ss[i]) + sum(1 for x in src if x[1] == i) + max(v[2] for k, v in det.items() if k[0] == i) for i in range(3)]


def repair(i, ss, ps, src, mand, rng, radius_kill):
    """remove optional cells near a random point of body i, re-cover and re-route; return new set or None"""
    tmp = [set(s) for s in ss]
    body = set(tmp[i])
    opt = sorted(body - mand[i])
    if not opt:
        return None
    mode = rng.random()
    if mode < 0.5:
        c = rng.choice(opt)
        kill = {p for p in opt if sum(abs(a - b) for a, b in zip(p, c)) <= radius_kill}
    elif mode < 0.8:
        kill = {p for p in opt if rng.random() < 0.3}
    else:
        kill = set(opt)
    tmp[i] = body - kill
    legal = ns['make_legal'](tmp, ps, src)
    if not callable(legal):
        return None
    # recovery needs not covered by any body
    def covered():
        cov = set()
        for k in range(3):
            for c in tmp[k]:
                cov |= lazy.cover_set(k, c, ps)
        return cov
    need_all = {(j, t) for j, (pp, dp, f, tg, st) in enumerate(ps) for t in lazy.recovery(f)}
    cov = covered()
    guard = 0
    while need_all - cov:
        guard += 1
        if guard > 60:
            return None
        unc = sorted(need_all - cov)
        j, t0 = rng.choice(unc)
        pp, dp, f, tg, st = ps[j]
        opts = []
        for t in [u for (jj, u) in unc if jj == j]:
            for b in range(3):
                if b != i or not S[i][t]:
                    continue
                for d in m.D[2:]:
                    p = m.shift(m.add(pp, d), dp[t] - DISP[i][t])
                    if p in tmp[i] or not legal(p, i):
                        continue
                    cv = lazy.cover_set(i, p, ps) & set(unc)
                    if not cv:
                        continue
                    distance = min(sum(abs(a - bb) for a, bb in zip(p, v)) for v in tmp[i])
                    opts.append((-len(cv), distance + rng.random() * 3, p))
        if not opts:
            return None
        opts.sort()
        p = opts[0][2] if rng.random() < 0.7 else rng.choice(opts[:3])[2]
        tmp[i].add(p)
        legal.cache_clear()
        cov = covered()
    # connect
    cap = 60
    while len(m.conn(tmp[i])) < len(tmp[i]):
        legal.cache_clear()
        reached = m.conn(tmp[i]); targets = tmp[i] - reached
        pq = [(0, rng.random(), p) for p in reached]; heapq.heapify(pq)
        dist = {p: 0 for p in reached}; prev = {}; end = None
        while pq:
            cost, _, p = heapq.heappop(pq)
            if cost != dist[p]:
                continue
            if p in targets:
                end = p; break
            if cost > cap - len(tmp[i]):
                continue
            for d in rng.sample(m.D, 6):
                v = m.add(p, d)
                if not (-8 <= v[0] <= 9 and -6 <= v[1] <= 14 and -6 <= v[2] <= 12):
                    continue
                if v not in tmp[i] and not legal(v, i):
                    continue
                nc = cost + int(v not in tmp[i])
                if nc < dist.get(v, 10000):
                    dist[v] = nc; prev[v] = p; heapq.heappush(pq, (nc, rng.random(), v))
        if end is None:
            return None
        while end not in reached:
            tmp[i].add(end); end = prev[end]
    return tmp[i]


def valid(ss, ps, src):
    legal = ns['make_legal'](ss, ps, src)
    if not callable(legal):
        return False
    for i in range(3):
        if any(not legal(p, i) for p in ss[i]):
            return False
        if len(m.conn(ss[i])) != len(ss[i]):
            return False
    return True


def save(ss, ps, src, prefix):
    json.dump(dict(segments=[sorted(s) for s in ss], pistons=ps, sources=src, counts=[len(s) for s in ss], mandatory=[sorted(x) for x in (MAND or mandatory_of(ss, ps, src))]), open(prefix + '.json', 'w'))
    f = Flyer(rng_state=5, push_limit=1000)
    for p, owner, observer, direction in src:
        f._cells[p] = Block.observer(direction, powered=bool(m.S[owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)
    for pp, dp, phase, target, sticky in ps:
        state = 2 if (0 - phase) % 6 == 1 else 0
        f._cells[pp] = Block.piston(0, state=state)
        if state:
            f._cells[m.shift(pp, 1)] = Block(Kind.PISTON_ARM)
    for i, s in enumerate(ss):
        for p in s:
            f._cells[p] = Block(m.K[i])
    f.save(prefix + '.flyer')


def main():
    start, prefix, secs, seed = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
    maxworse = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    rng = random.Random(seed)
    ss, ps, src = load_json(start)
    mand = MAND if MAND is not None else mandatory_of(ss, ps, src)
    cur = cost_of(ss, ps, src); best = cur
    print('start', cur, flush=True)
    t_end = time.time() + secs; it = 0; acc = 0
    while time.time() < t_end:
        it += 1
        bl = body_loads(ss, ps, src)
        i = bl.index(max(bl)) if rng.random() < 0.7 else rng.randrange(3)
        if rng.random() < 0.3:
            cands = [k for k in range(3) if bl[k] == max(bl)]
            i = rng.choice(cands)
        new = repair(i, ss, ps, src, mand, rng, rng.choice((2, 3, 4, 6)))
        if new is None:
            continue
        cand = [set(s) for s in ss]; cand[i] = new
        c = cost_of(cand, ps, src)
        if c[:2] > (cur[0], cur[1] + maxworse) or not valid(cand, ps, src):
            continue
        if c[:2] <= (cur[0], cur[1] + maxworse):
            if c[:2] != cur[:2] or c != cur:
                acc += 1
            ss = cand; cur = c
            if c[:2] < best[:2]:
                best = c
                save(ss, ps, src, prefix + '_best')
                print('it', it, 'best', best, [len(s) for s in ss], flush=True)
        if it % 50 == 0:
            print('it', it, 'cur', cur, 'acc', acc, flush=True)
    print('final best', best)


if __name__ == '__main__':
    main()
