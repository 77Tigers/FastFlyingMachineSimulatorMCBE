"""Role-level rider-floor model for 5-slot (3 bps) ring lifecycles (agent J-mmwmw, 2026-10-02).

Generalises speed_range_b_20260930/mmwpull/riders.py (F's 6-slot pull-twice) to any 5-slot word and any
push/pull assignment of V's three moves.  Ring: bodies V_e for e in D (subset of Z5), V_e has V's word rotated by
e slots (moves at t iff base[(t-e)%5]=='m').  Every body plays the same lifecycle shifted by e.

Pistons of V (frame V = V_0, slots 0..4):
  pull at s : sticky, fire f=s-1 (extends empty), pulls at s; frozen f, s;  REL(s)=2
  push at s : normal, fire f=s, frozen s, s+1;                            REL(s)=-1
  piston moves in exactly the 3 non-frozen slots (3 moves/cycle).  REL(t+1)=REL(t)+pm(t)-vm(t).
  REL = piston x minus V's contact cell x.   Sticky needs REL>=1, pusher REL<=-1 always.
Adjacency a[d][t] in {0,1}: piston touches (glue of) ring body d at slot-t start.
  continuity: if body d and piston both move or both stay in slot t then a[d][t+1]==a[d][t]
  each piston-moving slot t: >=1 body d with mv_d(t)=1 and a[d][t]=1 (carrier; each costs the carrier 1 rider)
  fire slot f: no moving adjacent body (push: only V allowed, V must... may touch)
  |REL|==1 at t -> V touches at t (forced); if additionally V moves at t and the piston is not frozen: no other
      moving body may touch it (merge/order hazard); if V moves at t and piston not frozen it must move at t.
Load of body V_0 at move slot t = sum over e in D, pistons k of V_e: cnt_k[(0-e)%5][(t-e)%5]  (+ constant sources).
Prints min over piston-pattern choices of the max load (riders only), per lifecycle.
"""
import itertools, sys
import numpy as np

L = 5


def rot_moves(base, e):
    return [1 if base[(t - e) % L] == 'm' else 0 for t in range(L)]


def trajectory(vm, kind, s):
    """returns (fire, frozen set, pm list, REL list) or None"""
    if kind == 'pull':
        f = (s - 1) % L
        frozen = {f, s}
        rel_s = 2
    else:
        f = s
        frozen = {s, (s + 1) % L}
        rel_s = -1
    pm = [0 if t in frozen else 1 for t in range(L)]
    rel = [None] * L
    rel[s] = rel_s
    t = s
    for _ in range(L):
        rel[(t + 1) % L] = rel[t] + pm[t] - vm[t]
        t = (t + 1) % L
    if rel[s] != rel_s:
        return None
    for t in range(L):
        if kind == 'pull' and rel[t] < 1:
            return None
        if kind == 'push' and rel[t] > -1:
            return None
    return f, frozen, pm, rel


def patterns(base, D, kind, s, maxadj=None):
    vm = rot_moves(base, 0)
    tr = trajectory(vm, kind, s)
    if tr is None:
        return None
    f, frozen, pm, rel = tr
    bodies = sorted(D)  # body index d relative to V_0: ring body V_{d}, d in D (V_0 must be in D)
    mv = {d: rot_moves(base, d) for d in bodies}
    # per-body feasible adjacency timelines
    per = {}
    for d in bodies:
        opts = []
        for bits in itertools.product((0, 1), repeat=L):
            ok = True
            for t in range(L):
                if mv[d][t] == pm[t] and bits[(t + 1) % L] != bits[t]:
                    ok = False; break
            if not ok:
                continue
            # fire slot: no moving adjacent body (push: V allowed)
            if bits[f] and mv[d][f] and not (kind == 'push' and d == 0):
                continue
            opts.append(bits)
        per[d] = opts
    res = {}
    for combo in itertools.product(*[per[d] for d in bodies]):
        a = dict(zip(bodies, combo))
        ok = True
        if maxadj is not None and sum(1 for d in bodies if any(a[d])) > maxadj:
            continue
        for t in range(L):
            movers = [d for d in bodies if mv[d][t] and a[d][t]]
            if pm[t] and not movers:
                ok = False; break
            if abs(rel[t]) == 1:
                if not a[0][t]:
                    ok = False; break
                if vm[t] and not (t in frozen) and not pm[t]:
                    ok = False; break
                if vm[t] and any(d != 0 for d in movers) and (pm[t] or t == f):
                    ok = False; break
            if t == f and kind == 'push' and any(d != 0 for d in movers):
                ok = False; break
        if not ok:
            continue
        cnt = np.zeros((L, L), dtype=np.int16)
        for d in bodies:
            for t in range(L):
                if pm[t] and mv[d][t] and a[d][t]:
                    cnt[bodies.index(d)][t] = 1
        res[cnt.tobytes()] = (cnt, a)
    return res, rel, pm, f


def pareto(items):
    arr = [(k, v[0].ravel()) for k, v in items.items()]
    keep = []
    for i, (k, x) in enumerate(arr):
        dom = False
        for j, (k2, y) in enumerate(arr):
            if j != i and np.all(y <= x) and np.any(y < x):
                dom = True; break
            if j < i and np.array_equal(x, y):
                dom = True; break
        if not dom:
            keep.append(k)
    return {k: items[k] for k in keep}


def solve(base, D, kinds, maxadj=None, verbose=False):
    """kinds: dict slot->'pull'/'push' for the three move slots of V_0."""
    bodies = sorted(D)
    pats = []
    meta = []
    for s, kind in kinds.items():
        r = patterns(base, D, kind, s, maxadj)
        if r is None:
            return None
        res, rel, pm, f = r
        if not res:
            return None
        res = pareto(res)
        pats.append(list(res.values()))
        meta.append((kind, s, f, rel, pm))
    best = None
    idx = {d: i for i, d in enumerate(bodies)}
    # precompute contribution to loads of V_0 at each t: sum_e cnt[(0-e)%5 -> body index][(t-e)%5]
    # body V_d in D loads: need for each d in D the load vector; ring symmetric => compute for d=0 only,
    # but body 0's load at t counts pistons of V_e (e in D) carried by relative body (0-e) in frame e.
    def contrib(cnt):
        out = np.zeros((len(bodies), L), dtype=np.int32)  # [which target body d_target (abs index in D)][t]
        for e in bodies:
            for dd in bodies:                    # relative body in frame e
                tgt = (e + dd) % L              # absolute rotation of that body
                if tgt not in idx:
                    continue
                for tau in range(L):
                    if cnt[idx[dd]][tau]:
                        out[idx[tgt]][(tau + e) % L] += 1
        return out
    # careful: cnt indexed by relative body index within sorted(D) of V_0's frame; frame e uses D_e = D (all e in D
    # have identical relative sets only if D is a group); require D subset closed? we only allow relative set = D.
    cons = [[contrib(c[0]) for c in p] for p in pats]
    for combo in itertools.product(*[range(len(p)) for p in pats]):
        tot = sum(cons[i][j] for i, j in enumerate(combo))
        # body d moves at t: only count where body moves
        mvmask = np.array([rot_moves(base, d) for d in bodies])
        loads = tot * mvmask
        key = (int(loads.max()), int(loads.sum()))
        if best is None or key < best[0]:
            best = (key, combo, loads)
    return best, pats, meta


if __name__ == '__main__':
    pass
