import json, itertools
from geom3 import *
def search_cells(Ta, Tb, ka, kb):
    rows = {}
    for p, k in Tb.items():
        if k in GL:
            key = (p[1], p[2])
            if key not in rows or p[0] < rows[key]: rows[key] = p[0]
    out = []
    for r1, r2 in itertools.permutations(rows, 2):
        x1 = rows[r1] - 3; x2 = rows[r2] - 2
        t1 = [x1, x1+1, x1+2, x1+3, x1+3]; t2 = [x2, x2, x2+1, x2+2, x2+3]
        P1 = [(x, r1[0], r1[1]) for x in t1] + [(x1+3,) + r1]
        P2 = [(x, r2[0], r2[1]) for x in t2] + [(x2+3,) + r2]
        a = piston_ok(P1, 'P1', Tb, Ta, kb, ka, 3, {0: {'Ta'}, 1: {'Ta'}, 2: {'Ta'}, 3: None, 4: None}, {})
        b = piston_ok(P2, 'P2', Tb, Ta, kb, ka, 4, {0: set(), 1: {'B9'}, 2: {'B9'}, 3: None, 4: None}, {})
        out.append((r1, r2, a, b))
    return out
def variants(Ta):
    """T_a with one glass cell converted into a glue cell placed (adjacent to existing T_a glue) = short arm, 8 cells kept."""
    glass = [p for p, k in Ta.items() if k == 'gl']
    glue = [p for p, k in Ta.items() if k in GL]
    out = [('orig', Ta)]
    for g in glass:
        base = {p: k for p, k in Ta.items() if p != g}
        cand = set()
        for q in glue:
            for d in D6:
                c = (q[0]+d[0], q[1]+d[1], q[2]+d[2])
                if c not in base and c != g: cand.add(c)
        for c in sorted(cand):
            v = dict(base); v[c] = 'sl'; out.append((f'-{g}+{c}', v))
    return out
if __name__ == '__main__':
    static = json.load(open('geom2_static.json'))
    good = []
    seen = set()
    for sa, ta, sb, tb, ka, kb in static:
        Ta0 = shape('B24', tuple(sa), tuple(ta), 1); Tb = shape('B33', tuple(sb), tuple(tb), 3)
        for name, Ta in variants(Ta0):
            if name == 'orig': continue
            if check(Tb, Ta, kb, ka): continue
            for r1, r2, a, b in search_cells(Ta, Tb, ka, kb):
                if a is None and b is None:
                    good.append((sa, ta, sb, tb, ka, kb, name, r1, r2))
    print(len(good), 'arm variants fully feasible')
    json.dump(good, open('geom4_good.json', 'w'))
    for g in good[:10]: print(g)
