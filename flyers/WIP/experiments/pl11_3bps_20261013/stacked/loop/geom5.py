"""(a) weaker split: X carries at most one front piston per move (slots 0,1,2); T_a may carry the other at s1,s2."""
import json, itertools
from geom3 import *
from collections import Counter
def info(P_traj, Tb, Ta, kb, ka, fire):
    """per slot: (overlap?, movers set, power count)"""
    out = []
    for s in range(5):
        pos, occ, words = world(Tb, Ta, kb, ka, s)
        P = P_traj[s]
        if P in occ: out.append(('overlap', occ[P][0])); continue
        adj = {occ[(P[0]+d[0], P[1]+d[1], P[2]+d[2])][0] for d in D6 if (P[0]+d[0], P[1]+d[1], P[2]+d[2]) in occ and occ[(P[0]+d[0], P[1]+d[1], P[2]+d[2])][1] in GL}
        movers = {b for b in adj if s in words[b]}
        src = sum(1 for b, c in pos.items() for p, k in c.items() if k == 'RB' and sum(abs(p[i]-P[i]) for i in range(3)) == 1 and (p[0]-P[0], p[1]-P[1], p[2]-P[2]) != (1,0,0))
        out.append((movers, src))
    return out
def ok_first(inf, fire=3):
    for s in range(5):
        if inf[s][0] == 'overlap': return 'overlap'
        mv, src = inf[s]
        if (s == fire) != (src > 0): return 'power'
        if s in (0,1,2) and not mv: return f'first uncarried s{s}'
        if s in (0,1,2) and not mv <= {'B9', 'Ta'}: return f'first dragged s{s} {mv}'
        if s in (3,4) and not mv <= {'Tb'}: return f'first dragged s{s} {mv}'
    return None
def ok_second(inf, fire=4):
    for s in range(5):
        if inf[s][0] == 'overlap': return 'overlap'
        mv, src = inf[s]
        if (s == fire) != (src > 0): return 'power'
        if s == 0 and mv: return f'second carried at s0 {mv}'
        if s in (1,2) and (not mv or not mv <= {'B9', 'Ta'}): return f'second s{s} movers {mv}'
        if s in (3,4) and not mv <= {'Tb'}: return f'second dragged s{s} {mv}'
        if s == 3 and 'Tb' not in mv: return 'second does not ride Tb at s3'
    return None
def run(static, names=True):
    good = []; why = Counter(); mind = Counter()
    for sa, ta, sb, tb, ka, kb in static:
        Ta = shape('B24', tuple(sa), tuple(ta), 1); Tb = shape('B33', tuple(sb), tuple(tb), 3)
        rows = {}
        for p, k in Tb.items():
            if k in GL:
                key = (p[1], p[2])
                if key not in rows or p[0] < rows[key]: rows[key] = p[0]
        for r1, r2 in itertools.permutations(rows, 2):
            x1 = rows[r1] - 3; x2 = rows[r2] - 2
            P1 = [(x, r1[0], r1[1]) for x in [x1, x1+1, x1+2, x1+3, x1+3]]
            P2 = [(x, r2[0], r2[1]) for x in [x2, x2, x2+1, x2+2, x2+3]]
            i1 = info(P1, Tb, Ta, kb, ka, 3); i2 = info(P2, Tb, Ta, kb, ka, 4)
            a = ok_first(i1); b = ok_second(i2)
            if a or b: why[(a or 'ok')[:28] + ' | ' + (b or 'ok')[:28]] += 1; continue
            # budget: X carries at most one piston per slot 0..2
            bad = [s for s in (0,1,2) if sum(1 for inf in (i1, i2) if 'B9' in inf[s][0]) > 1]
            if bad: why[f'X budget exceeded s{bad}'] += 1; continue
            good.append((sa, ta, sb, tb, ka, kb, r1, r2))
    return good, why
if __name__ == '__main__':
    static = json.load(open('geom2_static.json'))
    good, why = run(static)
    print(len(good), 'feasible'); print(why.most_common(10))
    json.dump(good, open('geom5_good.json', 'w'))
    print(good[:5])
