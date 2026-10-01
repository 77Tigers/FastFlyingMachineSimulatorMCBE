"""restarting placement climb (build2 router). python climb3.py OUT SEED HOURS RETRIES PATIENCE"""
import sys, json, random, time
from pathlib import Path
import gen, model
from climb import mutate

def evaluate(place, rng, retries):
    best = None
    for r in range(retries):
        s = rng.randrange(10**9)
        B, why, info = gen.build2(s, place, jitter=0 if r == 0 else 1.0)
        if B is None:
            if why == 'template':
                return None
            continue
        if B.d.max_load() > 36:
            continue
        d = model.trim(B.d, random.Random(s))
        key = (d.max_load(), sum(1 for it in d.items if it.cat == 'glue'))
        if best is None or key < best[0]:
            best = (key, d)
    return best

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
seed = int(sys.argv[2]); rng = random.Random(seed)
hours, retries, patience = float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
end = time.time() + hours * 3600
gbest = None
while time.time() < end:
    while True:
        place = gen.rand_place(rng, 3, 2)
        cur = evaluate(place, rng, retries)
        if cur: break
    stall = 0
    while stall < patience and time.time() < end:
        np_ = mutate(place, rng)
        res = evaluate(np_, rng, retries)
        stall += 1
        if res is None:
            continue
        if res[0] < cur[0]:
            stall = 0
        if res[0] <= cur[0]:
            place, cur = np_, res
    print('restart-end', cur[0], place, flush=True)
    if gbest is None or cur[0] < gbest:
        gbest = cur[0]
    if cur[0][0] <= 23:
        L, g = cur[0]
        f = cur[1].to_flyer(limit=L); f.translate(20, 20, 20)
        tag = f'r{seed}_{int(time.time())%100000}_L{L}_g{g}'
        f.save(out / f'{tag}.flyer'); (out / f'{tag}.json').write_text(json.dumps(place))
        print('saved', tag, flush=True)
