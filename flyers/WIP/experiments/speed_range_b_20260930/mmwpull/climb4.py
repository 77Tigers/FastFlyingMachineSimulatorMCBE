"""placement climb with exact ILP routing. python climb4.py OUT SEED START(json|rand) HOURS"""
import sys, json, random, time
from pathlib import Path
import gen, ilp
from climb import mutate

def evaluate(place, rng):
    best = None
    for rs in (rng.randrange(1000), rng.randrange(1000)):
        try:
            d, L = ilp.solve(place, rs, radius=2, Lmax=24, time_limit=60, verbose=False)
        except Exception:
            continue
        if d is None:
            if L == 'base':
                return None
            continue
        key = (d.max_load(), sum(1 for it in d.items if it.cat == 'glue'))
        if best is None or key < best[0]:
            best = (key, d)
    return best

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
seed = int(sys.argv[2]); rng = random.Random(seed); hours = float(sys.argv[4])
end = time.time() + hours * 3600
if sys.argv[3] == 'rand':
    while True:
        place = gen.rand_place(rng, 3, 2); cur = evaluate(place, rng)
        if cur: break
else:
    g, p, o = json.load(open(sys.argv[3])); place = (tuple(g), [(a, tuple(b)) for a, b in p], o)
    cur = evaluate(place, rng)
    if cur is None:
        cur = ((99, 999), None)
print('start', cur[0], place, flush=True)
best = cur[0]; stall = 0
while time.time() < end:
    np_ = mutate(place, rng)
    res = evaluate(np_, rng)
    stall += 1
    if res is None:
        continue
    if res[0] <= cur[0]:
        if res[0] < cur[0]: stall = 0
        place, cur = np_, res
        print(round(time.time()), cur[0], place, flush=True)
        if cur[0] < best:
            best = cur[0]
            if best[0] <= 22:
                tag = f'c{seed}_L{best[0]}_g{best[1]}'
                f = cur[1].to_flyer(limit=best[0]); f.translate(20, 20, 20)
                f.save(out / f'{tag}.flyer'); (out / f'{tag}.json').write_text(json.dumps(place))
    if stall > 150:
        while True:
            place = gen.rand_place(rng, 3, 2); cur = evaluate(place, rng)
            if cur: break
        stall = 0; print('restart', cur[0], flush=True)
