import sys, json, random
import gen, model
from model import nb
def roles(d, B):
    tmpl = {b: {B.w(b, *c) for c in gen.TEMPLATE} for b in range(3)}
    out = {}
    for b in range(3):
        cells = [it for it in d.items if it.cat == 'glue' and it.body == b]
        rs = []
        for it in cells:
            p = it.pos[0]; r = []
            if p in tmpl[b]: r.append('T')
            for t in range(6):
                for q in nb(it.pos[t]):
                    o = d.occ[t].get(q)
                    if o is not None and o >= 0:
                        k = d.items[o]
                        if it.mv[t] and k.cat == 'piston' and k.mv[t] and k.victim != b: r.append(f'{k.name}@{t}')
                        if k.cat in ('rs','obs') and k.body == b and t == 0: r.append('hold'+k.cat)
            rs.append((p, sorted(set(r))))
        out[b] = rs
    return out
if __name__ == '__main__':
    g, p, o = json.load(open(sys.argv[1])); place = (tuple(g), [(a, tuple(b)) for a, b in p], o)
    best = None
    for s in range(30):
        B, why, info = gen.build2(s, place, jitter=0 if s == 0 else 1.0)
        if B is None: continue
        d = model.trim(B.d, random.Random(s)); L = d.max_load()
        gs = sum(1 for it in d.items if it.cat == 'glue')
        if best is None or (L, gs) < best[0]: best = ((L, gs), d, B)
    print(best[0])
    for b, rs in roles(best[1], best[2]).items():
        print(b, len(rs))
        for p, r in sorted(rs): print('   ', p, r)
