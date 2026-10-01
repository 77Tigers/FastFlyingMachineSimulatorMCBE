"""placement hill-climb. python climb.py OUT SEED START_PLACE_JSON ITERS RETRIES
START_PLACE_JSON: json [gtypes, places, oopt] or 'rand'."""
import sys, json, random
from pathlib import Path
import gen, model

GTS = [('S', 'H', 'S'), ('S', 'S', 'H'), ('H', 'S', 'S')]

def evaluate(place, rng, retries):
    best = None
    for r in range(retries):
        s = rng.randrange(10**9)
        B, why, info = gen.build(s, place=place, jitter=0 if r == 0 else 2.0)
        if B is None:
            if why == 'template':
                return None
            continue
        if B.d.max_load() > 34:
            continue
        d = model.trim(B.d, random.Random(s))
        L = d.max_load()
        g = [sum(1 for it in d.items if it.cat == 'glue' and it.body == b) for b in range(3)]
        key = (L, sum(g))
        if best is None or key < best[0]:
            best = (key, d)
    return best

def mutate(place, rng):
    gt, places, oopt = place
    places = [list(p) for p in places]; oopt = list(oopt); gt = tuple(gt)
    m = rng.randrange(10)
    if m < 6:
        b = rng.choice((1, 2)); ax = rng.randrange(3)
        o = list(places[b][1]); o[ax] += rng.choice((-1, 1)); places[b][1] = tuple(o)
    elif m < 8:
        b = rng.randrange(3); places[b][0] = rng.randrange(8)
    elif m < 9:
        b = rng.randrange(3); oopt[b] ^= 1
    else:
        gt = rng.choice(GTS)
    return (gt, [(p[0], tuple(p[1])) for p in places], oopt)

if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    seed = int(sys.argv[2]); rng = random.Random(seed)
    iters, retries = int(sys.argv[4]), int(sys.argv[5])
    if sys.argv[3] == 'rand':
        while True:
            place = gen.rand_place(rng, 3, 2)
            cur = evaluate(place, rng, retries)
            if cur: break
    else:
        g, p, o = json.loads(sys.argv[3]); place = (tuple(g), [(a, tuple(b)) for a, b in p], o)
        cur = evaluate(place, rng, retries)
    print('start', cur[0], place, flush=True)
    bestL = cur[0][0]
    for it in range(iters):
        np_ = mutate(place, rng)
        res = evaluate(np_, rng, retries)
        if res is None:
            continue
        if res[0] <= cur[0]:
            place, cur = np_, res
            print(it, cur[0], place, flush=True)
            if cur[0][0] <= bestL:
                bestL = cur[0][0]
                f = cur[1].to_flyer(limit=bestL); f.translate(20, 20, 20)
                f.save(out / f'climb{seed}_L{bestL}_g{cur[0][1]}.flyer')
                (out / f'climb{seed}_L{bestL}_g{cur[0][1]}.json').write_text(json.dumps(place))
