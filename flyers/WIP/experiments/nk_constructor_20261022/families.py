"""Table-free N_k constructor (user rules, 2026-10-22/23):
- each FAMILY may spend 66 s in total over k = 3..24 (3 s per k on average, distributed freely); <= 15 families;
- per k at most 10 precomputed bits, shared by all families (BITS in bits.json, one int < 1024 per k);
- everything else (modules by CP-SAT with a deterministic budget, connectors) is computed at run time.

10-bit word per k:  bits 0-1 family (0 slab, 1 lat, 2 joint),  bits 2-5 box shape,  bits 6-9 layout.
  box (4 bits): a = a0 - 1 + (v & 3), b = b0 - 1 + (v >> 2), (a0, b0) = the slab rectangle for k.
  layout (4 bits): straight z shift sz = -(v & 1); corner cz = b + ((v >> 1) & 3) - 1; corner cy = a - 1.
  If the square has one body per side (k = 6: 4 bodies) the 8 bits 2-9 are the corner offset (cy+2, cz+2 nibbles)
  and the box is the slab rectangle.
Families: slab = rectangle module (perfect-code RBs, slab cover), no CP; lat = side-contact module (cp_module, CP-SAT,
1 worker, deterministic time DET_LAT); joint = module + straight-link glue in one CP (joint_cp, DET_JOINT), whose
corners are routed (joint_build).
python families.py           -> builds every k, prints per-family time and the sum of predicted PLs
"""
import sys, time, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import construct, square, sqbuild

KS = list(range(3, 25))
FAMS = ['slab', 'lat', 'joint']
def DET_LAT(k): return 1.0 if k <= 12 else 4.0
DET_JOINT = 6.0


def unpack(word, k):
    a0, b0 = construct.grid_module(k, 'slabP')['size']
    fam = FAMS[word & 3]
    m = square.ring_size(k) // 4
    if m == 1:
        return fam, (a0, b0), None, ((word >> 2) & 15) - 2, ((word >> 6) & 15) - 2
    v = (word >> 2) & 15; a, b = a0 - 1 + (v & 3), b0 - 1 + (v >> 2)
    l = (word >> 6) & 15
    return fam, (max(a, 2), max(b, 2)), -(l & 1), a - 1, b + ((l >> 1) & 3) - 1


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


def build(k, word):
    fam, (a, b), sz, cy, cz = unpack(word, k)
    m = square.ring_size(k) // 4
    if fam == 'joint':
        import joint_cp, joint_build
        res = joint_mod(k, a, b, sz if sz is not None else 0)
        if res is None: return None
        return joint_build.build(k, res, (cy, cz))
    mod = (construct.grid_module(k, 'slabP', box=(a, b)) if m > 1 else construct.grid_module(k, 'slabP')) if fam == 'slab' else lat_module(k, a, b)
    if mod is None: return None
    a, b = mod['size']
    step = (a + 2, 0) if m == 1 else (a + 1, sz)
    return sqbuild.assemble(k, mod, step, (cy, cz))


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
