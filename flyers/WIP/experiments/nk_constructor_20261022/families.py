"""Table-free N_k constructor (user rules, 2026-10-22/23):
- each FAMILY may spend 84 s in total over k = 2..30 (3 s per k on average, distributed freely); <= 15 families;
- per k at most 10 precomputed bits, shared by all families (BITS in bits.json, one int < 1024 per k);
- everything else (modules by CP-SAT with a deterministic budget, connectors) is computed at run time.

10-bit word per k:  bits 0-1 family (0 slab, 1 lat, 2 latbig = lat on a 4 x base ring, 3 terrace (see terrace_params)),  bits 2-5 box shape,  bits 6-9 layout.
  box (4 bits): a = a0 - 1 + (v & 3), b = b0 - 1 + (v >> 2), (a0, b0) = the slab rectangle for k.
  layout (4 bits): straight z shift sz = -(v & 1); bit 1: module mirrored in y; corner cz = b + 1 + ((v >> 2) & 1);
  corner cy = a - 1 + (v >> 3).
  If the square has one body per side (k = 6: 4 bodies) the layout nibble is the corner offset:
  cy = a - 1 + (v & 3), cz = b - 2 + (v >> 2).
Families: slab = rectangle module (perfect-code RBs, slab cover), no CP; lat = side-contact module (cp_module, CP-SAT,
1 worker, deterministic time DET_LAT); joint = module + straight-link glue in one CP (joint_cp, DET_JOINT), whose
corners are routed (joint_build).
python families.py           -> builds every k, prints per-family time and the sum of predicted PLs
"""
import sys, time, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import construct, square, sqbuild

KS = list(range(2, 31))
FAMS = ['slab', 'lat', 'latbig', 'terrace']
def DET_LAT(k): return 1.0 if k <= 12 else 4.0
DET_JOINT = 6.0


def unpack(word, k):
    a0, b0 = construct.grid_module(k, 'slabP')['size']
    fam = FAMS[word & 3]
    m = ((big_ring(k) or 4) if fam == 'latbig' else square.ring_size(k)) // 4
    v = (word >> 2) & 15; a, b = a0 - 1 + (v & 3), b0 - 1 + (v >> 2)
    l = (word >> 6) & 15
    if m == 1:   # 4-body ring: corner offset only (from the unclamped box)
        return fam, (max(a, 2), max(b, 2)), None, a - 1 + (l & 3), b - 2 + (l >> 2)
    a, b = max(a, 2), max(b, 2)
    return fam, (a, b), -(l & 1), a - 1 + ((l >> 3) & 1), b + 1 + ((l >> 2) & 1)


def mirror_y(mod):
    """the module reflected across its y axis (y -> a-1-y): the next body sits on the other side of its cover."""
    a = mod['size'][0]
    f3 = lambda c: (c[0], a - 1 - c[1], c[2])
    return dict(R=[f3(c) for c in mod['R']], P=[(a - 1 - c[0],) + tuple(c[1:]) for c in mod['P']],
                PLATE=[f3(c) for c in mod['PLATE']], CONT=[f3(c) for c in mod['CONT']], size=mod['size'])


import functools


@functools.lru_cache(maxsize=None)
def lat_module(k, a, b):
    import cp_module
    r = cp_module.solve(k, a, b, det=DET_LAT(k), workers=1)
    if r is None: return None
    T = lambda key: [tuple(c) for c in r[key]]
    return dict(R=[(0,) + c for c in T('R')], P=T('P'), PLATE=[(1,) + c for c in T('pl')],
                CONT=[(-2,) + c for c in T('w2')] + [(-3,) + c for c in T('w3')], size=(a, b))


@functools.lru_cache(maxsize=None)
def joint_mod(k, a, b, sz):
    import joint_cp
    return joint_cp.solve(k, a, b, (a + 1, sz), det=DET_JOINT, workers=1)


def terrace_params(k, word):
    """terrace word: bits 2-5 strip box (as above, relative to the slabP box for the largest floor),
    bit 6: strip pattern (0 slabP rectangle, 1 CP strip), bit 7: strip gap 1 + bit, bits 8-9: corner cz = b + bits
    (cy = a - 1); always g = 2 floors (g = 3 never won for k <= 30)."""
    import terrace
    l = (word >> 6) & 15; g = 2; gap = 1 + ((l >> 1) & 1)
    p = max(terrace.floor_sizes(k, g))
    a0, b0 = construct.grid_module(p, 'slabP')['size']
    v = (word >> 2) & 15; a, b = max(a0 - 1 + (v & 3), 2), max(b0 - 1 + (v >> 2), 2)
    return g, gap, (a - 1, b + (l >> 2)), (a, b), ('cp' if l & 1 else 'slab')


def big_ring(k):
    """latbig: the square ring with 4 x the base ring (only when that is larger than the default ring)"""
    from nk import bodies_for
    L = 4 * bodies_for(k)
    return L if L > square.ring_size(k) else None


def build(k, word):
    if FAMS[word & 3] == 'terrace':
        import terrace
        g, gap, cv, box, pat = terrace_params(k, word)
        r = terrace.build(k, g, gap, cv, box, pattern=pat)
        if r is None or terrace.collisions(r, bodies=list(range(min(r.T.L, 2 * (r.T.L // 4) + 4)))): return None
        return terrace.route_all(r)
    fam, (a, b), sz, cy, cz = unpack(word, k)
    L = big_ring(k) if fam == 'latbig' else square.ring_size(k)
    if L is None: return None
    m = L // 4
    mod = construct.grid_module(k, 'slabP', box=(a, b)) if fam == 'slab' else lat_module(k, a, b)
    if mod is None: return None
    if m > 1 and (word >> 7) & 1: mod = mirror_y(mod)
    a, b = mod['size']
    step = (a + 2, 0) if m == 1 else (a + 1, sz)
    return sqbuild.assemble(k, mod, step, (cy, cz), L)


if __name__ == '__main__':
    bits = {int(k): v for k, v in json.load(open(HERE / 'bits.json')).items()}
    spent = {f: 0.0 for f in FAMS}; total = 0
    for k in KS:
        t = time.time(); r = build(k, bits[k]); dt = time.time() - t
        fam = FAMS[bits[k] & 3]; spent[fam] += dt
        pl = max(r.size()) + k if r else None; total += pl or 0
        print(f'k={k:2d} family={fam:5s} PL={pl} time={dt:.2f}s', flush=True)
        if r: r.flyer(pl).save(str(HERE / 'out' / f'fam_n{k}.flyer'))
    print('time per family', {f: round(v, 1) for f, v in spent.items()}, 'sum', total)
