"""Hill-climb (simulator fitness) over ring3 template layouts. Usage: python climb.py SEED NSTART STEPS OUTDIR"""
import sys, pathlib, random, time, copy, pickle
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[3]))
import ring3, simtools
from ring3 import Layout, sample, D6, add
from fastflyer import Flyer, Block, Kind

LIMIT = 60
def build(cells, mats, limit=LIMIT):
    return Layout.flyer(cells, mats, limit)
def score(r):
    ff = r['first_failure_tick']
    ff = int(ff) if ff not in ('', None) else 1000
    return (ff, int(r['distance']))
def evaluate(pop, ticks=240):
    vs = {f'c{i}': build(c, m) for i, (c, m) in enumerate(pop)}
    res = simtools.screen(vs, ticks)
    return [score(res[f'c{i}']) + (res[f'c{i}'],) for i in range(len(pop))]
def mutate(cells, mats, rnd):
    c = dict(cells)
    for _ in range(rnd.choice((1, 1, 2, 3))):
        glue = [p for p, v in c.items() if v[0] == 'G']
        kind = rnd.random()
        if kind < 0.3 and glue:      # remove glue
            p = rnd.choice(glue); del c[p]
        elif kind < 0.65 and glue:   # add glue next to an existing cell of same body
            p = rnd.choice(list(c)); b = c[p][1]
            q = add(p, rnd.choice(D6))
            if q not in c: c[q] = ('G', b, None)
        elif kind < 0.85 and glue:   # move glue
            p = rnd.choice(glue); q = add(p, rnd.choice(D6))
            if q not in c: c[q] = ('G', c[p][1], None); del c[p]
        else:                        # move a whole body in y/z or x
            b = rnd.randrange(3); d = rnd.choice(D6)
            moved = {p: v for p, v in c.items() if v[1] == b}
            rest = {p: v for p, v in c.items() if v[1] != b}
            new = {add(p, d): v for p, v in moved.items()}
            if any(q in rest for q in new): continue
            rest.update(new); c = rest
    return c

if __name__ == '__main__':
    seed = int(sys.argv[1]); keep = int(sys.argv[2]); steps = int(sys.argv[3]); poolf = sys.argv[4]; outd = pathlib.Path(sys.argv[5])
    budget = float(sys.argv[6]) if len(sys.argv) > 6 else 600
    outd.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(seed); t0 = time.time()
    pool = pickle.load(open(poolf, 'rb'))
    ev = evaluate(pool)
    ranked = sorted(zip(ev, range(len(pool))), key=lambda t: (t[0][0], t[0][1]), reverse=True)
    print('pool score top', [e[:2] for e, _ in ranked[:8]], flush=True)
    pop = [(pool[i][0], pool[i][1], e[:2]) for e, i in ranked[:keep]]
    best = pop[0][2]
    for step in range(steps):
        if time.time() - t0 > budget: break
        kids = []
        for (c, m, s) in pop:
            for _ in range(40): kids.append((mutate(c, m, rnd), m))
        ev = evaluate(kids)
        cand = [(kids[i][0], kids[i][1], ev[i][:2], ev[i][2]) for i in range(len(kids))]
        allp = [(c, m, s) for c, m, s in pop] + [(c, m, s) for c, m, s, _ in cand]
        # keep top by score, dedupe by score ties via random order
        rnd.shuffle(allp)
        allp.sort(key=lambda t: t[2], reverse=True)
        pop = allp[:keep]
        if pop[0][2] > best:
            best = pop[0][2]
            print(f'step {step} t={time.time()-t0:.0f}s best {best}', flush=True)
            build(pop[0][0], pop[0][1]).save(outd / f'best_{best[0]}_{best[1]}.flyer')
        if step % 10 == 0: print('step', step, [p[2] for p in pop[:4]], flush=True)
        if best[0] >= 1000 and best[1] >= 70: break
