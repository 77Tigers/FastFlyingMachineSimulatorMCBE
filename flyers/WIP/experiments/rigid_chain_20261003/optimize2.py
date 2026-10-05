"""Local search with compound moves (delete, move, transfer between bodies, add+delete pairs, observer/rod
re-facing), keeping rigid.check valid, minimising loads then max body then total."""
import pickle, random, sys, pathlib, copy
from rigid import check, loads, to_flyer, add, D6, kind_of, reserved_cells
def score(segs): return (loads(segs), max(len(s.cells) for s in segs if not s.rider), sum(len(s.cells) for s in segs))
def mutate(cand, rng):
    bodies = [x for x in cand if not x.rider]
    s = rng.choice(bodies)
    cells = [c for c, k in s.cells.items() if kind_of(k) in ('g', 'R', 'D', 'O')]
    op = rng.random()
    if op < 0.25 and cells:                       # delete
        del s.cells[rng.choice(cells)]
    elif op < 0.5 and cells:                      # move within body
        c = rng.choice(cells); k = s.cells.pop(c)
        n = add(c, rng.choice(D6))
        if n in s.cells: return False
        if kind_of(k) in ('D', 'O') and rng.random() < 0.5: k = (kind_of(k), rng.randrange(6))
        s.cells[n] = k
    elif op < 0.7 and cells:                      # transfer a cell's kind to another body near its glue
        c = rng.choice(cells); k = s.cells.pop(c)
        o = rng.choice([b for b in bodies if b is not s])
        og = [x for x, kk in o.cells.items() if kk == 'g']
        n = add(rng.choice(og), rng.choice(D6))
        if n in o.cells: return False
        o.cells[n] = k
    elif op < 0.85:                               # add glue + delete another
        g = [x for x, kk in s.cells.items() if kk == 'g']
        n = add(rng.choice(g), rng.choice(D6))
        if n in s.cells: return False
        s.cells[n] = 'g'
        if cells and rng.random() < 0.8: del s.cells[rng.choice(cells)]
    else:                                         # re-face an observer/rod
        sr = [c for c, k in s.cells.items() if kind_of(k) in ('D', 'O')]
        if not sr: return False
        c = rng.choice(sr); s.cells[c] = (kind_of(s.cells[c]), rng.randrange(6))
    return True
def optimize(segs, rng, iters):
    cur = copy.deepcopy(segs); best = copy.deepcopy(segs); bs = score(best)
    for it in range(iters):
        cand = copy.deepcopy(cur)
        if not mutate(cand, rng): continue
        if rng.random() < 0.3: mutate(cand, rng)
        if check(cand) is not None: continue
        sc = score(cand)
        if sc <= score(cur) or rng.random() < 0.02:
            cur = cand
            if sc < bs: best, bs = copy.deepcopy(cand), sc; print('improved', bs, flush=True)
    return best, bs
if __name__ == '__main__':
    import importlib
    src = sys.argv[1]; out = pathlib.Path(sys.argv[2]); out.mkdir(exist_ok=True)
    rng = random.Random(int(sys.argv[3])); iters = int(sys.argv[4])
    if src.endswith('.pkl'): segs = pickle.load(open(src, 'rb'))
    else: segs = importlib.import_module(src).model()
    print('start', score(segs), check(segs))
    best, bs = optimize(segs, rng, iters)
    tag = f'{pathlib.Path(src).stem}_s{sys.argv[3]}_L{bs[0]}'
    pickle.dump(best, open(out / f'{tag}.pkl', 'wb')); to_flyer(best, bs[0]).save(out / f'{tag}.flyer')
    print('final', bs, [(s.name, sorted(s.cells.items())) for s in best if not s.rider])
