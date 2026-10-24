"""Back-body link copied from the human 3 bps PL12 flyer (bank/pl12/human_3bps_original, body A), as a rule:
- column lane c = (0, 0); the router runs the connector down it from the front cluster to the cover;
- hoppers in lanes t1 = (1, 0) (beside the column) and t2 = (2, 1); one redstone block in r = (1, 1), touching both;
- front cluster (plate) = the two targets + the cell in front of the redstone block (an L of 3 cells at x = 1);
- the next body covers both spent hoppers with one cell in lane (2, 0), beside t1 and t2; that cell is the next
  body's cover lane c' = c + (-1, 0), so the straight step is (3, 0) (or (2, -1) with c' = c + (0, 1)).
Towers (tower2, power-only top, human sticky) stand on the front cluster.
construct(k, step, cv, phase): the family builder (k = 3: back bodies with k-1 = 2 hoppers); the level layouts are
tried in order and the first ring passing every check is returned (k = 3: largest body 10, PL14 in 0.8 s).
python human_link.py K H [NLAY NPOW]   (scan; settings from HL_* environment variables)"""
import sys, os, itertools
from concurrent.futures import ProcessPoolExecutor
import tower2
from terrace import collisions
from tower import route_all

MOD = dict(P=[(1, 0), (2, 1)], R=[(0, 1, 1)], PLATE=[(1, 1, 0), (1, 1, 1), (1, 2, 1)], CONT=[(-2, 2, 0)],
           size=(int(os.environ.get('HL_A', 3)), 2))
STEPS = [tuple(map(int, t.split(','))) for t in os.environ.get('HL_STEPS', '3,0;2,-1').split(';')]
HS = os.environ.get('HL_HS', '0') == '1'
PHASE = os.environ.get('HL_PHASE')
MG = tuple(int(x) for x in os.environ.get('HL_MG', '0,1').split(','))   # tower lanes may leave the box only across the side (z), never towards the neighbours (y)


def xoff(k):
    import square
    return tower2.balanced_xoff(k, square.ring_size(k), int(PHASE)) if PHASE is not None else None


def back_ring(k, step, cv):
    r = tower2.build(k, 1, 0, (), back=(MOD, step), cv=cv, xoff=xoff(k))
    if collisions(r): return None
    route_all(r)
    return r


def towers_fit(k, step, cv, h, nlay):
    for lc in itertools.product(range(nlay), repeat=h):
        b = tower2.build(k, 1, h, lc, back=(MOD, step), cv=cv, mg=MG, hs=HS, xoff=xoff(k))
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


def tower_ring(k, h, step, cv, lc, mod=None, mg=None, hs=None, xo=False):
    """back ring + towers with greedy power; None unless it passes collisions, power and the checker."""
    from nk2 import power_problems
    mod = mod or MOD; mg = MG if mg is None else mg; hs = HS if hs is None else hs
    r = tower2.build(k, 1, h, lc, back=(mod, step), cv=cv, mg=mg, hs=hs, xoff=xoff(k) if xo is False else xo)
    if r is None or collisions(r): return None, 'layout'
    if tower2.add_power_greedy(r) is None: return None, 'power'
    if collisions(r) or power_problems(r): return None, 'power2'
    try: route_all(r)
    except RuntimeError: return None, 'route'
    bad = r.check()
    if bad: return None, 'check ' + bad[0][2][:30]
    return r, 'ok'


def construct(k, step=(4, 0), cv=(5, -2), phase=None, h=3, nlay=4):
    """tower family: human-link back ring (4-lane step, balanced frame offsets), height-h human-sticky towers."""
    if k != 3: return None   # the link rule is written for back bodies with 2 hoppers
    import square
    from nk import bodies_for
    L, L0 = square.ring_size(k), bodies_for(k)
    mod = dict(MOD, size=(4, 2))
    xo = tower2.balanced_xoff(k, L, L0 - 1 if phase is None else phase)
    for lc in itertools.product(range(nlay), repeat=h):
        try: r, _ = tower_ring(k, h, step, cv, lc, mod=mod, mg=(0, 1), hs=True, xo=xo)
        except (AssertionError, RuntimeError): continue
        if r is None: continue
        try: r.flyer(1)
        except AssertionError: continue
        return r
    return None


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
        if r is None: continue
        p = f'out/hl_{k}_{h}_{step[0]}{step[1]}_{cv[0]}_{cv[1]}_{len(out)}.flyer'.replace('-', 'm')
        try: r.flyer(4 * k + 30).save(p)
        except AssertionError: continue
        out.append((sz, back, lc, min_pl(p, k, 4 * k + 10), p))
    return (step, cv), (dict(why), out)


if __name__ == '__main__':
    k, h = int(sys.argv[1]), int(sys.argv[2])
    nlay, npow = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (4, 6)
    jobs = [(k, h, st, cv, nlay, npow) for st in STEPS for cv in corners(k, st, h, nlay)]
    print(len(jobs), 'jobs', [j[2:4] for j in jobs], flush=True)
    with ProcessPoolExecutor(min(len(jobs), 12)) as ex:
        for key, res in ex.map(job, jobs): print(key, res, flush=True)
