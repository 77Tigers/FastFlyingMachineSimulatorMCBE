import sys, pathlib, random, time, pickle
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
import simtools
from fastflyer import Flyer, Block, Kind
src = sys.argv[1]; out = sys.argv[2]; ticks = int(sys.argv[3]) if len(sys.argv) > 3 else 600
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
rnd = random.Random(seed)
base = Flyer.load(src)
def cells(f): return {p: b for p, b in f.blocks()}
def good(r): return r['clean'] == 'true' and int(r['distance']) >= ticks // 3 - 2
def mk(cs, lim):
    f = Flyer.load(src); 
    for p, _ in list(f.blocks()): f.remove(p)
    f.push_limit = lim
    for p, b in cs.items(): f.set(p, b)
    return f
cs = cells(base)
print(len(cs), 'cells')
cur = simtools.screen({'a': mk(cs, 60)}, ticks)['a']; print('start', simtools.brief(cur))
GL = (Kind.SLIME, Kind.HONEY)
rounds = 0
while True:
    rounds += 1
    glue = [p for p, b in cs.items() if b.kind in GL]
    rnd.shuffle(glue)
    vs = {f'd{i}': mk({q: v for q, v in cs.items() if q != p}, 60) for i, p in enumerate(glue)}
    res = simtools.screen(vs, ticks)
    ok = [(int(res[f'd{i}']['max_successful_action']), i) for i, p in enumerate(glue) if good(res[f'd{i}'])]
    if not ok: break
    ok.sort(); 
    # remove the best (lowest load) and then try greedily to also remove others compatible: take only best
    l, i = ok[0]; del cs[glue[i]]
    print('round', rounds, 'removed', glue[i], 'load', l, 'cells', len(cs), 'candidates', len(ok), flush=True)
    mk(cs, 60).save(out)
