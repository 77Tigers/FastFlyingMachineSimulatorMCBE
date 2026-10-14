import json, itertools, sys
from geom2 import *
RB_BODIES = ('B7','B8','B9','B15','B16')
def world(Tb, Ta, kb, ka, s):
    bodies = {b: cells[b] for b in RB_BODIES}; bodies['Ta'] = Ta; bodies['Tb'] = Tb
    words = dict(W); words['Ta'] = W['B24']; words['Tb'] = W['B33']
    pos = {b: at_slot(c, words[b], s) for b, c in bodies.items()}
    occ = {}
    for b, c in pos.items():
        for p, k in c.items(): occ[p] = (b, k)
    return pos, occ, words
def moves_at(b, words, s): return s in words[b]
def piston_ok(P_traj, role, Tb, Ta, kb, ka, fire, carriers_by_slot, allowed_t):
    """P_traj[s] = piston position at start of slot s. Returns reason string or None."""
    for s in range(5):
        pos, occ, words = world(Tb, Ta, kb, ka, s)
        P = P_traj[s]
        P_after = P_traj[s+1] if s < 4 else (P_traj[0][0]+3, P_traj[0][1], P_traj[0][2])
        if P in occ: return f'{role} overlaps {occ[P][0]} at s{s}'
        adj = set()
        for d in D6:
            q = (P[0]+d[0], P[1]+d[1], P[2]+d[2])
            if q in occ and occ[q][1] in GL:
                b = occ[q][0]
                kind = occ[q][1] if b not in ('Ta','Tb') else (ka if b=='Ta' else kb)
                adj.add(b)
        movers = {b for b in adj if s in words[b]}
        need = carriers_by_slot[s]
        if need is not None and movers != need:
            # allow Tb extra at fire/post slots
            if not (movers - need <= allowed_t.get(s, set()) and need <= movers): return f'{role} s{s}: adjacent movers {movers} need {need}'
        # power
        src = 0
        for b, c in pos.items():
            for p, k in c.items():
                if k == 'RB' and sum(abs(p[i]-P[i]) for i in range(3)) == 1 and (p[0]-P[0], p[1]-P[1], p[2]-P[2]) != (1,0,0): src += 1
        if (s == fire) != (src > 0): return f'{role} power {src} at s{s} (fire s{fire})'
    return None
def search(sa, ta, sb, tb, ka, kb):
    Ta = shape('B24', sa, ta, 1); Tb = shape('B33', sb, tb, 3)
    rows = {}
    for p, k in Tb.items():
        if k in GL:
            key = (p[1], p[2])
            if key not in rows or p[0] < rows[key]: rows[key] = p[0]
    out = []
    for r1, r2 in itertools.permutations(rows, 2):
        x1 = rows[r1] - 3; x2 = rows[r2] - 2
        # P1 moves at s0,s1,s2 (carried by Ta); P2 moves at s1,s2 (X_b) and s3 (rides T_b)
        t1 = [x1, x1+1, x1+2, x1+3, x1+3]; t2 = [x2, x2, x2+1, x2+2, x2+3]
        P1 = [(x, r1[0], r1[1]) for x in t1] + [(x1+3, r1[0], r1[1])]
        P2 = [(x, r2[0], r2[1]) for x in t2] + [(x2+3, r2[0], r2[1])]
        c1 = {0: {'Ta'}, 1: {'Ta'}, 2: {'Ta'}, 3: None, 4: None}
        c2 = {0: set(), 1: {'B9'}, 2: {'B9'}, 3: None, 4: None}
        a = piston_ok(P1, 'P1', Tb, Ta, kb, ka, 3, c1, {})
        b = piston_ok(P2, 'P2', Tb, Ta, kb, ka, 4, c2, {})
        out.append((r1, r2, a, b))
    return out
if __name__ == '__main__':
    static = json.load(open('geom2_static.json'))
    n = 0; good = []
    from collections import Counter
    why = Counter()
    for sa, ta, sb, tb, ka, kb in static:
        sa, sb = tuple(sa), tuple(sb)
        for r1, r2, a, b in search(sa, tuple(ta), sb, tuple(tb), ka, kb):
            if a is None and b is None: good.append((sa, ta, sb, tb, ka, kb, r1, r2))
            else:
                why[(a or 'ok')[:30] + ' | ' + (b or 'ok')[:30]] += 1
    print(len(good), 'fully feasible'); print(why.most_common(8))
    json.dump(good, open('geom3_good.json', 'w'))
