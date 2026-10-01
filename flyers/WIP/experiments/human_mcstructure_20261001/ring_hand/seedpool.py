import sys, pathlib, random, pickle, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import climb, ring3, simtools
from ring3 import Layout, sample
seed = int(sys.argv[1]); n = int(sys.argv[2]); out = sys.argv[3]
rnd = random.Random(seed); pool = []; t0 = time.time()
mats_opts = (('S','H','S'), ('H','S','H'), ('S','H','H'), ('H','S','S'), ('S','S','H'), ('H','H','S'))
tried = 0
while tried < n and time.time() - t0 < 240:
    tried += 1
    A, ori, hs = sample(rnd)
    L = Layout(A, ori, hs)
    if not L.ok: continue
    mats = dict(zip((0,1,2), rnd.choice(mats_opts)))
    cells = L.route(mats, rnd)
    if cells is not None: pool.append((cells, mats))
print('tried', tried, 'pool', len(pool), time.time() - t0)
pickle.dump(pool, open(out, 'wb'))
