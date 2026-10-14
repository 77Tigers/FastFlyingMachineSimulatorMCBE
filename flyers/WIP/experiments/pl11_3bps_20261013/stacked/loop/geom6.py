"""(a) weaker split with the both-powered column: roles of the two rows may swap randomly, so every row must work as first and as second."""
import json, itertools
from geom5 import info, ok_first, ok_second
from geom3 import *
from collections import Counter
def first_ok(inf):
    for s in range(5):
        if inf[s][0] == 'overlap': return 'overlap'
        mv, src = inf[s]
        if s in (0,1,2) and src: return f'early power s{s}'
        if s == 3 and not src: return 'no power s3'
        if s in (0,1,2) and (not mv or not mv <= {'B9','Ta'}): return f'first s{s} movers {mv}'
        if s in (3,4) and not mv <= {'Tb'}: return f'first dragged s{s} {mv}'
    return None
def second_ok(inf):
    for s in range(5):
        if inf[s][0] == 'overlap': return 'overlap'
        mv, src = inf[s]
        if s in (0,1,2) and src: return f'early power s{s}'
        if s == 4 and not src: return 'no power s4'
        if s == 0 and mv: return f'second carried at s0 {mv}'
        if s in (1,2) and (not mv or not mv <= {'B9','Ta'}): return f'second s{s} movers {mv}'
        if s == 3 and 'Tb' not in mv: return 'second does not ride'
        if s in (3,4) and not mv <= {'Tb'}: return f'second dragged s{s} {mv}'
    return None
def evaluate_rows(Ta, Tb, ka, kb):
    rows = {}
    for p, k in Tb.items():
        if k in GL:
            key = (p[1], p[2])
            if key not in rows or p[0] < rows[key]: rows[key] = p[0]
    res = {}
    for r, xt in rows.items():
        x1 = xt - 3; x2 = xt - 2
        P1 = [(x, r[0], r[1]) for x in [x1, x1+1, x1+2, x1+3, x1+3]]
        P2 = [(x, r[0], r[1]) for x in [x2, x2, x2+1, x2+2, x2+3]]
        i1 = info(P1, Tb, Ta, kb, ka, 3); i2 = info(P2, Tb, Ta, kb, ka, 4)
        res[r] = (i1, i2, first_ok(i1), second_ok(i2))
    return res
if __name__ == '__main__':
    static = json.load(open('geom2_static.json'))
    why1 = Counter(); why2 = Counter(); both_row = []; pairs = []
    for sa, ta, sb, tb, ka, kb in static:
        Ta = shape('B24', tuple(sa), tuple(ta), 1); Tb = shape('B33', tuple(sb), tuple(tb), 3)
        res = evaluate_rows(Ta, Tb, ka, kb)
        for r, (i1, i2, a, b) in res.items():
            why1[(a or 'ok')[:26]] += 1; why2[(b or 'ok')[:26]] += 1
        good_rows = [r for r, (i1, i2, a, b) in res.items() if a is None and b is None]
        both_row += [(sa, ta, sb, tb, ka, kb, r) for r in good_rows]
        for rA, rB in itertools.combinations(good_rows, 2):
            ok = True
            for (f, s) in ((rA, rB), (rB, rA)):
                for t in (0,1,2):
                    n = sum(1 for inf in (res[f][0], res[s][1]) if 'B9' in inf[t][0])
                    if n > 1: ok = False
            if ok: pairs.append((sa, ta, sb, tb, ka, kb, rA, rB))
    print('rows valid as first AND second:', len(both_row), ' row pairs with X budget<=1 in both assignments:', len(pairs))
    print('first-role reasons', why1.most_common(6)); print('second-role reasons', why2.most_common(6))
    json.dump(pairs, open('geom6_pairs.json', 'w')); print(pairs[:4])
