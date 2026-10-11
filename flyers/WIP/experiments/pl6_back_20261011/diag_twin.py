"""For a sample of offsets that pass the relay prefilter: power-free feasibility vs powered."""
import itertools, random
from twin6 import build, rng
random.seed(1)
offs = [(mp, d) for mp in ('flipz', 'rot180', 'swap', 'rot90') for d in itertools.product(rng('m3:3'), rng('m4:4'), rng('m4:4'))]
random.shuffle(offs)
cnt = {}
n = 0
for mp, d in offs:
    M = build(mp, d, 6, skip=('power',))
    if isinstance(M, str): continue
    st, _ = M.solve(20, 2)
    cnt[st] = cnt.get(st, 0) + 1
    if st in ('OPTIMAL', 'FEASIBLE'): print(mp, d, 'power-free', st, flush=True)
    n += 1
    if n >= 60: break
print(cnt)
