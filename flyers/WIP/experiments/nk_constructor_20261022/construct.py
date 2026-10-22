"""Generic N_k constructor: python construct.py K [PL] [family] -> out/n{K}_{family}.flyer"""
import sys, time, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from nk import Timing, Ring, add, D6

OUT = pathlib.Path(__file__).resolve().parent / 'out'


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def nb(c): return [(c[0] + dy, c[1] + dz) for dy, dz in N4]


def connected(cells):
    cells = set(cells)
    if not cells: return True
    st, seen = [next(iter(cells))], set()
    while st:
        u = st.pop()
        if u in seen: continue
        seen.add(u); st += [v for v in nb(u) if v in cells]
    return len(seen) == len(cells)


def cp_table_module(k):
    """exact slab module from modules_cp.json (cp_slab.py), else the slabP rectangle."""
    import json, pathlib
    tab = json.load(open(pathlib.Path(__file__).resolve().parent / 'modules_cp.json'))
    if str(k) not in tab: return grid_module(k, 'slabP')
    r = tab[str(k)]; P = [tuple(c) for c in r['P']]; R = [tuple(c) for c in r['R']]
    cells = P + R + [tuple(c) for c in r['W']]
    y0 = min(c[0] for c in cells); z0 = min(c[1] for c in cells)
    sh = lambda c: (c[0] - y0, c[1] - z0)
    a = max(c[0] for c in cells) - y0 + 1; b = max(c[1] for c in cells) - z0 + 1
    return dict(R=[(0,) + sh(c) for c in R], P=[sh(c) for c in P], PLATE=[(1,) + sh(c) for c in P + R],
                CONT=[(-3,) + sh(tuple(c)) for c in r['W']], size=(a, b))


def lat_table_module(k):
    """exact lateral/behind cover module from modules_lat.json (cp_module.py)."""
    import json, pathlib
    tab = json.load(open(pathlib.Path(__file__).resolve().parent / 'modules_lat.json'))
    if str(k) not in tab: return cp_table_module(k)
    r = tab[str(k)]; T = lambda key: [tuple(c) for c in r[key]]
    cells = T('P') + T('R') + T('pl') + T('w2') + T('w3')
    y0 = min(c[0] for c in cells); z0 = min(c[1] for c in cells)
    sh = lambda c: (c[0] - y0, c[1] - z0)
    a = max(c[0] for c in cells) - y0 + 1; b = max(c[1] for c in cells) - z0 + 1
    return dict(R=[(0,) + sh(c) for c in T('R')], P=[sh(c) for c in T('P')], PLATE=[(1,) + sh(c) for c in T('pl')],
                CONT=[(-2,) + sh(c) for c in T('w2')] + [(-3,) + sh(c) for c in T('w3')], size=(a, b))


def grid_module(k, variant='slab'):
    if variant == 'cp': return cp_table_module(k)
    if variant == 'latcp': return lat_table_module(k)
    """flat module from a rectangle of lanes. variants:
    slab   plate over the rectangle, next body's cover = slab at x=-3 over the rectangle (baseline)
    slabP  plate over P+R lanes, cover = slab at x=-3 behind P lanes only
    lat    R and C lanes on two perfect codes ((y+2z)%5 == 0 / 1); cover = C cells at x=-2 (router connects)"""
    best = None
    for a in range(1, 14):
        for b in range(a, 14):
            if a * b > 3 * k + 12: break
            for off in range(5):
                cells = [(y, z) for y in range(a) for z in range(b)]
                code = lambda c, t: (c[0] + 2 * c[1] + off) % 5 == t
                Rs = {c for c in cells if code(c, 0)}
                Cs = {c for c in cells if code(c, 1)} if variant == 'lat' else set()
                cand = [c for c in cells if c not in Rs and c not in Cs and any(v in Rs for v in nb(c))
                        and (variant != 'lat' or any(v in Cs for v in nb(c)))]
                if len(cand) < k: continue
                # prefer P lanes near the centre (compact plate)
                cy, cz = (a - 1) / 2, (b - 1) / 2
                cand.sort(key=lambda c: (abs(c[0] - cy) + abs(c[1] - cz)))
                P = cand[:k]; Ps = set(P)
                R = [r for r in Rs if any(v in Ps for v in nb(r))]
                C = [c for c in Cs if any(v in Ps for v in nb(c))]
                if variant == 'slab':
                    plate = cells; cover = [(-3,) + c for c in cells]
                else:
                    plate = sorted(Ps | set(R))
                    if not connected(plate): continue
                    cover = [(-3,) + c for c in P] if variant == 'slabP' else [(-2,) + c for c in C]
                    if variant == 'slabP' and not connected(P): continue
                cost = len(plate) + len(cover) + len(R) + (len(C) if variant == 'lat' else 0)
                if best is None or cost < best[0]:
                    best = (cost, a, b, P, R, plate, cover)
    _, a, b, P, R, plate, cover = best
    return dict(R=[(0,) + r for r in R], P=P, PLATE=[(1,) + c for c in plate], CONT=cover, size=(a, b))


def strip_module(k):
    """strips of two pusher rows between lines of the next body's lateral cover (x=-2):
    rows z%3==0: cover line C; z%3==1,2: pusher rows, RBs at y%4==0 (row 1) / y%4==2 (row 2).
    plate at x=1 over P+R, bridged over each inner C line at one column."""
    best = None
    for s_ in range(1, 8):
        for n in range(2, 40):
            rows = 3 * s_ + 1
            P, R, C = [], [], []
            for z in range(rows):
                for y in range(n):
                    if z % 3 == 0: C.append((y, z))
                    elif (z % 3 == 1 and y % 4 == 0) or (z % 3 == 2 and y % 4 == 2): R.append((y, z))
                    else: P.append((y, z))
            Rs = set(R)
            P = [p for p in P if any(v in Rs for v in nb(p))]
            if len(P) < k: continue
            # keep the k pushers nearest the module centre line (y small first keeps strips full)
            P.sort(key=lambda p: (p[0], p[1]))
            P = P[:k]; Ps = set(P)
            R = [r for r in R if any(v in Ps for v in nb(r))]
            C = [c for c in C if any(v in Ps for v in nb(c))]
            plate = set(P) | set(R)
            ys = sorted({p[0] for p in P}); y0 = ys[0]
            for z in range(3, rows - 1, 3):
                if any(c[1] == z for c in C): plate.add((y0, z))
            if not connected(plate): continue
            cost = len(plate) + len(R) + len(C)
            if best is None or cost < best[0]:
                best = (cost, n, rows, P, R, C, sorted(plate))
            break
    _, n, rows, P, R, C, plate = best
    return dict(R=[(0,) + r for r in R], P=P, PLATE=[(1,) + c for c in plate], CONT=[(-2,) + c for c in C],
                size=(n, rows))


# periodic 4x4 pattern (cp_periodic.py 4 4 8 0): P pushers, R redstone (plate above), C next-body cover at x=-2
TILE = ["P..P",   # z=0  (string index = y)
        "RP.P",   # z=1
        "P..P",   # z=2
        "P.PR"]   # z=3
TILE_C = {(1, 0), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)}


def tile_at(y, z):
    t = TILE[z % 4][y % 4]
    if t == '.' and (y % 4, z % 4) in TILE_C: return 'C'
    return t


def tile_module(k):
    best = None
    for a in range(2, 14):
        for b in range(2, 14):
            for oy in range(4):
                for oz in range(4):
                    cells = [(y, z) for y in range(a) for z in range(b)]
                    P = [c for c in cells if tile_at(c[0] + oy, c[1] + oz) == 'P']
                    if len(P) < k: continue
                    cy, cz = (a - 1) / 2, (b - 1) / 2
                    P.sort(key=lambda c: abs(c[0] - cy) + abs(c[1] - cz))
                    P = P[:k]; Ps = set(P)
                    near = {v for p in P for v in nb(p)}
                    R = sorted(c for c in near if tile_at(c[0] + oy, c[1] + oz) == 'R')
                    C = sorted(c for c in near if tile_at(c[0] + oy, c[1] + oz) == 'C')
                    if not all(any(tile_at(v[0] + oy, v[1] + oz) == 'R' for v in nb(p)) for p in P): continue
                    plate = sorted(Ps | set(R))
                    if not connected(plate): continue
                    cost = len(plate) + len(R) + len(C) + 2 * (a + b) // 4
                    if best is None or cost < best[0]: best = (cost, P, R, C, plate)
                break
    _, P, R, C, plate = best
    ys = [c[0] for c in plate + C]; zs = [c[1] for c in plate + C]
    y0, z0 = min(ys), min(zs)
    sh = lambda c: (c[0] - y0, c[1] - z0)
    P = [sh(c) for c in P]; R = [sh(c) for c in R]; C = [sh(c) for c in C]; plate = [sh(c) for c in plate]
    return dict(R=[(0,) + r for r in R], P=P, PLATE=[(1,) + c for c in plate], CONT=[(-2,) + c for c in C],
                size=(max(ys) - y0 + 1, max(zs) - z0 + 1))


def ring_layout(L, a, b, gy=2, gz=1):
    """module origins (y,z): two-row racetrack, bottom row +y, top row -y (odd L: top row offset by half a step)."""
    sy, sz = a + gy, b + gz
    nb = (L + 1) // 2; nt = L - nb
    pts = [(i * sy, 0) for i in range(nb)]
    if nt == nb: pts += [((nb - 1 - j) * sy, sz) for j in range(nt)]
    else: pts += [(round((nb - 1.5 - j) * sy), sz) for j in range(nt)]
    return pts


def racetrack(L, a, b, gy=2, gz=1, sym_top=0, top_shift=(0, 0), half=True):
    """two rows of unrotated (bottom, +y) and sym_top-oriented (top, -y) modules; odd L: top row offset by half a step."""
    from nk import SYMS
    sy = a + gy; nb = (L + 1) // 2; nt = L - nb
    pts = [((i * sy, 0), 0) for i in range(nb)]
    ys = [(nb - 1 - j) * sy for j in range(nt)] if (nt == nb or not half) else [round((nb - 1.5 - j) * sy) for j in range(nt)]
    ry = [SYMS[sym_top](y, z) for y in (0, a - 1) for z in (0, b - 1)]
    oy = -min(p[0] for p in ry); oz = -min(p[1] for p in ry)
    pts += [((y + oy + top_shift[0], b + gz + oz + top_shift[1]), sym_top) for y in ys]
    return [(0, p, s) for p, s in pts]


LAYOUTS = [dict()] + [dict(gz=gz, sym_top=st, top_shift=(-1, 0), half=h) for st in (0, 2, 5) for gz in (0, 1) for h in (0, 1)]


def build(k, family='slabP', small_search=8):
    """small k: try the racetrack variants and keep the checker-clean ring with the smallest largest body."""
    T = Timing(k)
    mod = {'strip': strip_module, 'tile': tile_module}.get(family, lambda k: grid_module(k, family))(k)
    a, b = mod['size']
    best = None
    for lay in (LAYOUTS if k <= small_search else LAYOUTS[:1]):
        ring = Ring(T, [mod] * T.L, racetrack(T.L, a, b, **lay))
        try:
            for X in range(T.L): ring.route(X)
        except RuntimeError:
            continue
        if k <= small_search and ring.check(): continue
        if best is None or max(ring.size()) < max(best.size()): best = ring
    return best


if __name__ == '__main__':
    k = int(sys.argv[1]); fam = sys.argv[3] if len(sys.argv) > 3 else 'slab'
    t = time.time()
    ring = build(k, fam)
    bad = ring.check()
    sz = ring.size()
    pl = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != '-' else max(sz) + k + 4
    OUT.mkdir(exist_ok=True)
    p = OUT / f'n{k}_{fam}.flyer'
    ring.flyer(pl).save(str(p))
    print(f'k={k} L={ring.T.L} sizes={sz} bad={len(bad)} {bad[:3]} time={time.time() - t:.2f}s -> {p}')
