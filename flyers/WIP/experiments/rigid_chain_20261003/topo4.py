"""Closed rigid designs ranked by estimated max segment load = glue + pistons + carried power blocks.
Glue model per segment (one straight bridge lane from lo to hi): glue = hi-lo+1 + [vp>lo] + [vs<hi]
(lo/hi over all element x; vp/vs = x of pushed/pulled contact; extra lateral contact costs 1 each).
Power: each segment with pistons needs one block on another segment j whose relative offset at the
fire slot is unique over the cycle; carrier load +1.
usage: CONSEC=1 MAXP=3 python topo4.py N
"""
import itertools, sys, os
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from topo import pos, contact_ok
from topo2 import designs

def P4(w, t): return 2 if t == 4 else pos(w, t)
def fire_slot(w):
    for k in range(4):
        if (k % 4) not in w and ((k + 1) % 4) not in w: return k
def unique_offset(wi, wj, k):
    rel = [P4(wj, t) - P4(wi, t) for t in range(4)]
    return rel.count(rel[k]) == 1

def solve(n, words, acts):
    pist = [sum(1 for x in acts if x[1] == i) for i in range(n)]
    # vars: U_i (pusher x), W_i (sticky x), VP_i, VS_i, LO_i, HI_i, A_i, B_i (bin), y_ij (bin), M
    idx = {}; nv = 0
    def var(name):
        nonlocal nv; idx[name] = nv; nv += 1
    for i in range(n):
        for nm in ('U', 'W', 'VP', 'VS', 'LO', 'HI', 'A', 'B'): var((nm, i))
    pw = [i for i in range(n) if pist[i] > 0]
    for i in pw:
        for j in range(n):
            if j != i and unique_offset(words[i], words[j], fire_slot(words[i])): var(('y', i, j))
    var('M')
    A = []; lb = []; ub = []
    def row(): return [0.0] * nv
    def eq(r, v): A.append(r); lb.append(v); ub.append(v)
    def ge(r, v): A.append(r); lb.append(v); ub.append(np.inf)
    for typ, a, t, k in acts:
        r = row()
        if typ == 'push': r[idx[('VP', t)]] += 1; r[idx[('U', a)]] -= 1; rhs = pos(words[a], k) - pos(words[t], k) + 1
        else: r[idx[('W', a)]] += 1; r[idx[('VS', t)]] -= 1; rhs = pos(words[t], k) - pos(words[a], k) + 2
        eq(r, rhs)
    has_push = [any(x[1] == i and x[0] == 'push' for x in acts) for i in range(n)]
    has_pull = [any(x[1] == i and x[0] == 'pull' for x in acts) for i in range(n)]
    for i in range(n):
        els = ['VP', 'VS'] + (['U'] if has_push[i] else []) + (['W'] if has_pull[i] else [])
        for e in els:
            r = row(); r[idx[(e, i)]] = 1; r[idx[('LO', i)]] = -1; ge(r, 0)
            r = row(); r[idx[('HI', i)]] = 1; r[idx[(e, i)]] = -1; ge(r, 0)
        r = row(); r[idx[('A', i)]] = 30; r[idx[('VP', i)]] = -1; r[idx[('LO', i)]] = 1; ge(r, 0)
        r = row(); r[idx[('B', i)]] = 30; r[idx[('HI', i)]] = -1; r[idx[('VS', i)]] = 1; ge(r, 0)
        # load_i = HI-LO+1+A+B + pist_i + sum_y(.,i) <= M
        r = row(); r[idx['M']] = 1; r[idx[('HI', i)]] = -1; r[idx[('LO', i)]] = 1; r[idx[('A', i)]] = -1; r[idx[('B', i)]] = -1
        for p in pw:
            if ('y', p, i) in idx: r[idx[('y', p, i)]] = -1
        ge(r, 1 + pist[i])
    for p in pw:
        r = row(); ok = False
        for j in range(n):
            if ('y', p, j) in idx: r[idx[('y', p, j)]] = 1; ok = True
        if not ok: return None
        eq(r, 1)
    r = row(); r[idx[('VP', 0)]] = 1; eq(r, 0)
    cost = np.zeros(nv); cost[idx['M']] = 100
    for i in range(n): cost[idx[('HI', i)]] += 1; cost[idx[('LO', i)]] -= 1
    lo = np.full(nv, -30.0); hi = np.full(nv, 30.0)
    for k, v in idx.items():
        if k[0] in ('A', 'B', 'y'): lo[v] = 0; hi[v] = 1
    lo[idx['M']] = 0; hi[idx['M']] = 60
    res = milp(cost, constraints=LinearConstraint(np.array(A), lb, ub), integrality=np.ones(nv), bounds=Bounds(lo, hi))
    if res.status != 0: return None
    x = [round(v) for v in res.x]
    loads = []
    for i in range(n):
        g = x[idx[('HI', i)]] - x[idx[('LO', i)]] + 1 + x[idx[('A', i)]] + x[idx[('B', i)]]
        carried = sum(x[idx[('y', p, i)]] for p in pw if ('y', p, i) in idx)
        loads.append((g, pist[i], carried))
    els = [(x[idx[('U', i)]], x[idx[('W', i)]], x[idx[('VP', i)]], x[idx[('VS', i)]]) for i in range(n)]
    carriers = {p: [j for j in range(n) if ('y', p, j) in idx and x[idx[('y', p, j)]]] for p in pw}
    return x[idx['M']], loads, els, carriers

if __name__ == '__main__':
    n = int(sys.argv[1]); best = {}; seen = 0
    shard = int(os.environ.get('SHARD', '-1'))
    for words, acts in designs(n):
        if shard >= 0 and [(0,1),(1,2),(2,3),(0,3)].index(tuple(words[1])) != shard: continue
        adj = {i: set() for i in range(n)}
        for _, a, t, _ in acts: adj[a].add(t); adj[t].add(a)
        st = [0]; vis = {0}
        while st:
            v = st.pop()
            for y in adj[v]:
                if y not in vis: vis.add(y); st.append(y)
        if len(vis) < n or not contact_ok(words, acts): continue
        seen += 1
        r = solve(n, words, acts)
        if r is None: continue
        best.setdefault(r[0], []).append((words, acts) + r[1:])
    print('designs', seen)
    for k in sorted(best)[:3]:
        print('maxload', k, 'count', len(best[k]))
        for item in best[k][:5]: print('  ', item)
