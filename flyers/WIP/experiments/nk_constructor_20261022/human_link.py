"""Back-body link copied from the human 3 bps PL12 flyer (bank/pl12/human_3bps_original, body A), as a rule:
- column lane c = (0, 0); the router runs the connector down it from the front cluster to the cover;
- hoppers in lanes t1 = (1, 0) (beside the column) and t2 = (2, 1); one redstone block in r = (1, 1), touching both;
- front cluster (plate) = the two targets + the cell in front of the redstone block (an L of 3 cells at x = 1);
- the next body covers both spent hoppers with one cell in lane (2, 0), beside t1 and t2; that cell is the next
  body's cover lane c' = c + (-1, 0), so the straight step is (3, 0) (or (2, -1) with c' = c + (0, 1)).
Towers (tower2, power-only top) stand on the front cluster.
python human_link.py K H [NLAY NPOW]"""
import sys, os, itertools
from concurrent.futures import ProcessPoolExecutor
import tower2
from terrace import collisions
from tower import route_all

MOD = dict(P=[(1, 0), (2, 1)], R=[(0, 1, 1)], PLATE=[(1, 1, 0), (1, 1, 1), (1, 2, 1)], CONT=[(-2, 2, 0)],
           size=(int(os.environ.get('HL_A', 3)), 2))
STEPS = [tuple(map(int, t.split(','))) for t in os.environ.get('HL_STEPS', '3,0;2,-1').split(';')]
HS = os.environ.get('HL_HS', '0') == '1'
MG = tuple(int(x) for x in os.environ.get('HL_MG', '0,1').split(','))   # tower lanes may leave the box only across the side (z), never towards the neighbours (y)


def back_ring(k, step, cv):
    r = tower2.build(k, 1, 0, (), back=(MOD, step), cv=cv)
    if collisions(r): return None
    route_all(r)
    return r


def towers_fit(k, step, cv, h, nlay):
    for lc in itertools.product(range(nlay), repeat=h):
        b = tower2.build(k, 1, h, lc, back=(MOD, step), cv=cv, mg=MG, hs=HS)
        if b is not None and not collisions(b): return True
    return False


def corners(k, step, h=3, nlay=4, keep=int(os.environ.get('HL_KEEP', 4)), span=int(os.environ.get('HL_SPAN', 9))):
    """corner offsets whose back ring routes cleanly and leaves room for the towers, cheapest first"""
    out = []
    for cv in itertools.product(range(-2, span), repeat=2):
        try: r = back_ring(k, step, cv)
        except (AssertionError, RuntimeError): continue
        if r is None or r.check() or not towers_fit(k, step, cv, h, nlay): continue
        out.append((max(r.size()), sum(r.size()), cv))
    return [cv for _, _, cv in sorted(out)[:keep]]


def tower_ring(k, h, step, cv, lc):
    """back ring + towers with greedy power; None unless it passes collisions, power and the checker."""
    from nk2 import power_problems
    r = tower2.build(k, 1, h, lc, back=(MOD, step), cv=cv, mg=MG, hs=HS)
    if r is None or collisions(r): return None, 'layout'
    if tower2.add_power_greedy(r) is None: return None, 'power'
    if collisions(r) or power_problems(r): return None, 'power2'
    try: route_all(r)
    except RuntimeError: return None, 'route'
    bad = r.check()
    if bad: return None, 'check ' + bad[0][2][:30]
    return r, 'ok'


def job(args):
    k, h, step, cv, nlay, npow = args
    import collections
    from tower import min_pl
    res, why = [], collections.Counter()
    for lc in itertools.product(range(nlay), repeat=h):
        try: r, w = tower_ring(k, h, step, cv, lc)
        except (AssertionError, RuntimeError) as e: r, w = None, 'err'
        why[w] += 1
        if r is not None: res.append((max(r.size()), max(r.size()[:r.L0]), lc))
    res.sort()
    out = []
    for sz, back, lc in res[:2]:
        r, _ = tower_ring(k, h, step, cv, lc)
        p = f'out/hl_{k}_{h}_{step[0]}{step[1]}_{cv[0]}_{cv[1]}_{len(out)}.flyer'.replace('-', 'm')
        r.flyer(4 * k + 30).save(p)
        out.append((sz, back, lc, min_pl(p, k, 4 * k + 10), p))
    return (step, cv), (dict(why), out)


if __name__ == '__main__':
    k, h = int(sys.argv[1]), int(sys.argv[2])
    nlay, npow = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (4, 6)
    jobs = [(k, h, st, cv, nlay, npow) for st in STEPS for cv in corners(k, st, h, nlay)]
    print(len(jobs), 'jobs', [j[2:4] for j in jobs], flush=True)
    with ProcessPoolExecutor(min(len(jobs), 12)) as ex:
        for key, res in ex.map(job, jobs): print(key, res, flush=True)
