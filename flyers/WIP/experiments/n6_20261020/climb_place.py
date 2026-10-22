"""local search over module placements starting from a given placement."""
import sys, random, json, math
from multiprocessing import Pool
from ring_designer import Ring, ORDER, V1, V2, V3, V4, V5, route_all
from search_place import footprint
LAY = {'V1': V1, 'V2': V2, 'V3': V3, 'V4': V4, 'V5': V5}


def score(name, place):
    mod = LAY[name]; used = set()
    for X in ORDER:
        x0, off, sym = place[X]
        fp = footprint(mod, sym, off)
        if fp & used: return None
        used |= fp
    try:
        ring = Ring(mod, place)
        route_all(ring)
        if ring.check(): return None
        sz = ring.size(); return (max(sz.values()), sum(sz.values()))
    except Exception:
        return None


def neighbours(place, rng, k=8):
    out = []
    for _ in range(k):
        p = dict(place); X = rng.choice(ORDER[1:]) if rng.random() < 0.8 else 'A'
        x0, (oy, oz), sym = p[X]
        r = rng.random()
        if r < 0.4: oy += rng.choice([-1, 1])
        elif r < 0.7: oz += rng.choice([-1, 1])
        elif r < 0.85: x0 += rng.choice([-1, 1])
        else: sym = rng.randrange(8)
        p[X] = (x0, (oy, oz), sym); out.append(p)
    return out


def ev(a): return score(*a), a[1]


if __name__ == '__main__':
    name = sys.argv[1]; place = json.loads(sys.argv[2]); iters = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
    rng = random.Random(seed)
    cur = score(name, place); best = (cur, place); print('start', cur, flush=True)
    T = 1.0
    with Pool(4) as pool:
        for it in range(iters):
            cands = neighbours(place, rng)
            res = [r for r in pool.map(ev, [(name, c) for c in cands]) if r[0]]
            if not res: continue
            res.sort(key=lambda r: r[0])
            s, p = res[0]
            if s <= cur or rng.random() < math.exp(-((s[0] - cur[0]) * 10 + (s[1] - cur[1])) / T):
                cur, place = s, p
                if s < best[0]: best = (s, p); print(it, 'best', s, p, flush=True)
            T = max(0.2, T * 0.98)
    print('final best', best)
    json.dump({'name': name, 'score': best[0], 'place': best[1]}, open(f'out/climb_{name}_{seed}.json', 'w'))
