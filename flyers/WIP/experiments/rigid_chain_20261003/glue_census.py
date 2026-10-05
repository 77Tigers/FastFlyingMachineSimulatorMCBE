"""Census of minimum body glue in the 2-body hand-off family (hop4 geometry). Prints a histogram of
(min glue A, min glue B) over many random contact layouts, ignoring power, plus how many reach each stage."""
import hop4, random, itertools, sys, re, time
from collections import Counter
from rigid import add
seed = int(sys.argv[1]); N = int(sys.argv[2])
_mg = hop4.min_glue
hop4.min_glue = lambda *a, **k: _mg(*a, **{**k, 'cap': 2500})
rng = random.Random(seed)
lat = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in range(-2, 3) for dz in range(-2, 3)
       if (dx, dy, dz) != (0, 0, 0) and abs(dy) + abs(dz) <= 2 and (dx == 0 or abs(dy) + abs(dz) >= 1)]
cBs = [(x, y, z) for x in range(-3, 4) for y in range(-2, 3) for z in range(-2, 3)]
cnt = Counter(); hist = Counter(); t0 = time.time()
for it in range(N):
    cA2 = rng.choice(lat); cB1 = rng.choice(cBs); dB = rng.choice(lat)
    mats = rng.choice([('slime', 'honey'), ('honey', 'slime'), ('slime', 'slime'), ('honey', 'honey')])
    hop4.DBG.clear()
    segs, why = hop4.build(cA2, cB1, add(cB1, dB), mats, rng, 7)
    cnt[re.sub(r'[-0-9(), ]+', '#', str(why))] += 1
    g = {k: v for k, v in hop4.DBG.items() if k.startswith('glue')}
    a = [int(k.split('_')[1]) for k in g if k.startswith('glueA')]
    b = [int(k.split('_')[1]) for k in g if k.startswith('glueB')]
    if a or b: hist[(a[0] if a else None, b[0] if b else None)] += 1
    if it % 50 == 49: print('progress', it + 1, 'secs', round(time.time() - t0), 'stages', dict(cnt.most_common(4)), 'hist', dict(hist), flush=True)
print('seed', seed, 'jobs', N, 'secs', round(time.time() - t0), flush=True)
print('stages', dict(cnt.most_common(8)))
print('glue (A,B) histogram', dict(sorted(hist.items(), key=lambda x: str(x[0]))))
