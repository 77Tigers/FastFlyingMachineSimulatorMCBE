import sys, pathlib, random, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
import simtools
from fastflyer import Flyer, Block, Kind
src, out, budget, seed = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
ticks = 360; rnd = random.Random(seed); t0 = time.time()
D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
tmpl = Flyer.load(src)
def cellsof(f): return {p: b for p, b in f.blocks()}
GL = (Kind.SLIME, Kind.HONEY)
def mk(cs):
    f = Flyer(push_limit=60)
    for p, b in cs.items(): f.set(p, b)
    return f
def mutate(cs):
    c = dict(cs)
    for _ in range(rnd.choice((1, 1, 2, 2, 3))):
        glue = [p for p, b in c.items() if b.kind in GL]
        r = rnd.random()
        if r < 0.45: del c[rnd.choice(glue)]
        elif r < 0.7:
            p = rnd.choice(glue); q = add(p, rnd.choice(D6))
            if q not in c: c[q] = c[p]
        else:
            p = rnd.choice(glue); q = add(p, rnd.choice(D6))
            if q not in c: c[q] = c[p]; del c[p]
    return c
def key(r, n): return (int(r['max_successful_action']), n)
def good(r): return r['clean'] == 'true' and int(r['distance']) >= ticks // 3 - 2
cur = cellsof(tmpl); r0 = simtools.screen({'a': mk(cur)}, ticks)['a']; curk = key(r0, len(cur))
print('start', curk, flush=True); best = curk
while time.time() - t0 < budget:
    kids = [mutate(cur) for _ in range(160)]
    res = simtools.screen({f'k{i}': mk(k) for i, k in enumerate(kids)}, ticks)
    ok = [(key(res[f'k{i}'], len(k)), i) for i, k in enumerate(kids) if good(res[f'k{i}'])]
    if not ok: continue
    m = min(o[0] for o in ok); cands = [i for k, i in ok if k <= curk and k == m] or [i for k, i in ok if k <= curk]
    if not cands: continue
    i = rnd.choice(cands); cur = kids[i]; curk = key(res[f'k{i}'], len(cur))
    if curk < best:
        best = curk; mk(cur).save(out); print(f'{time.time()-t0:.0f}s best', best, flush=True)
