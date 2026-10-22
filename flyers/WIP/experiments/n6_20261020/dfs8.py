"""DFS for 8-body rings alternating V9 / M-type modules (s = 3 on V9->M links, 2 on M->V9 links),
pruning by module footprint overlap; last link closed by lookup. usage: python dfs8.py MODS.json MTYPES MAXSOL"""
import sys, json, itertools
from collections import defaultdict
import ring_designer as rd
from ring_designer import Ring, route_all, hard_conflicts, set_bodies, SYMS, local, shift, pusher_options, PREV, NEXT
from close_ring import apply, COMP, INV
from module_eval import mod_of
from try_ring import sim, OUT
rd.STRICT = True
set_bodies(8)
NAMES = 'ABCDEFGH'
rows = json.load(open(sys.argv[1])); mtypes = [int(v) for v in sys.argv[2].split(',')]; maxsol = int(sys.argv[3])
mods_by = {i: mod_of(*rows[i][3:6]) for i in [0] + mtypes}


def table(a, b, s):
    best = {}
    for g, rel in json.load(open(f'out/mix_{a}_{b}.json')):
        if rel[0] == s - 3 and g <= 16:
            k = (rel[0], tuple(rel[1]), rel[2]); best[k] = min(best.get(k, 99), g)
    return list(best)


def footprint(mod):
    """cells (x,y,z) a module occupies (own hardware/plate over all slot offsets + next body's cover), module frame."""
    cells = set()
    for r in mod['R']: cells.add((0,) + tuple(r))
    for p in mod['P']:
        for dx in (0, -1, -2): cells.add((dx,) + tuple(p))
    for c in mod['PLATE']: cells.add(tuple(c))
    for c in mod['CONT']:
        for d in (0, 1, 2): cells.add((c[0] + d, c[1], c[2]))
    return cells


FP = {t: footprint(m) for t, m in mods_by.items()}


def world_fp(t, place):
    x0, (oy, oz), si = place
    out = set()
    for (x, y, z) in FP[t]:
        yy, zz = SYMS[si](y, z); out.add((x0 + x, oy + yy, oz + zz))
    return out


T = {}
for m in mtypes:
    T[0, m] = table(0, m, 3); T[m, 0] = table(m, 0, 2)
sols = []


def dfs(i, place, types, used):
    if len(sols) >= maxsol: return
    U = NAMES[i]; tU = types[i]
    nxt_types = mtypes if tU == 0 else [0]
    for tX in nxt_types:
        if i == 7 and tX != types[0]: continue
        for rel in T[tU, tX]:
            dx = rel[0] + (2 if rd.REST[U] == 6 else 0)
            xu, (uy, uz), su = place[U]
            oy, oz = apply(su, rel[1])
            pX = (xu + dx, (uy + oy, uz + oz), COMP[rel[2], su])
            if i == 7:
                if pX == (0, (0, 0), 0): sols.append((dict(place), types + []))
                continue
            fp = world_fp(tX, pX)
            if fp & used: continue
            halo = {(a + d[0], b + d[1], c + d[2]) for a, b, c in fp for d in rd.D6}
            prev_fps = FPS[:-1] if i < 6 else FPS[1:-1]     # all but U (and A when closing next)
            if any(halo & f for f in prev_fps): continue
            X = NAMES[i + 1]
            place[X] = pX; FPS.append(fp)
            dfs(i + 1, place, types + [tX], used | fp)
            del place[X]; FPS.pop()


start = (0, (0, 0), 0)
FPS = [world_fp(0, start)]
dfs(0, {'A': start}, [0], world_fp(0, start))
print(len(sols), 'footprint-clean closed rings', flush=True)
good = 0
for place, types in sols:
    mods = {X: mods_by[t] for X, t in zip(NAMES, types)}
    ring = Ring(mods, place)
    if hard_conflicts(ring, first=True): continue
    try: sz = route_all(ring)
    except Exception: continue
    bad = ring.check()
    if bad: continue
    ld = {X: len(ring.glue[X]) + len(mods[X]['R']) + 6 for X in NAMES}
    print('types', types, 'glue', sz, 'maxload', max(ld.values()), flush=True)
    if max(ld.values()) <= 25:
        tag = f'ring8_{good}'
        ring.flyer(40).save(str(OUT / f'{tag}.flyer')); print('  sim', sim(OUT / f'{tag}.flyer'), tag, flush=True)
        json.dump({'place': place, 'types': types}, open(OUT / f'{tag}.json', 'w'))
        good += 1
