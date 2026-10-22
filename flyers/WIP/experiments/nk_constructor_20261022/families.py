"""Table-free N_k constructor (rules of 2026-10-22, second revision):
- each FAMILY gets 3 s x 22 = 66 s in total over k = 3..24 (distributed freely); at most 15 distinct families;
- per k, at most 10 precomputed bits (BITS below), shared by all families: they choose layout parameters only;
- everything else (modules, connectors) is computed at run time; the best flyer per k wins.

Families
  slab   rectangle module, RBs on the perfect code, slab cover (construct.grid_module 'slabP'), square ring
  lat    side-contact module: CP-SAT (cp_module.solve, 1 worker, deterministic) with a per-k time budget,
         falling back to 'slab'; square ring
  joint  module + next body's straight-link glue in one CP (joint_cp.solve), small k only; square ring

python families.py [FAMILY ...]   -> per-family timings and the per-k best; flyers to out/fam/
"""
import sys, time, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import construct, square, sqbuild
from nk import Timing, Ring

KS = list(range(3, 25))

# ---- 10 bits per k: (straight z shift sz in {-1,0}: 1 bit, corner z offset cz-b in 0..3: 2 bits,
#      corner y offset cy-a in -2..1: 2 bits) = 5 bits for m>1; m=1 (k=6, 14?) uses cy, cz in 4 bits each.
def decode(bits, a, b, m):
    if m == 1:
        cy, cz = (bits & 15) - 2, ((bits >> 4) & 15) - 2
        return (a + 2, 0), (cy, cz)
    sz = -(bits & 1); cz = b + ((bits >> 1) & 3); cy = a - 2 + ((bits >> 3) & 3)
    return (a + 1, sz), (cy, cz)


def encode(step, cv, a, b, m):
    if m == 1: return (cv[0] + 2) | ((cv[1] + 2) << 4)
    return (-step[1]) | ((cv[1] - b) << 1) | ((cv[0] - a + 2) << 3)


BITS = {}   # family -> {k: bits}; filled by calibrate.py (one int < 1024 per k, shared value per family/k)


def ring_for(k, mod, bits):
    a, b = mod['size']; L = square.ring_size(k); m = L // 4
    step, cv = decode(bits, a, b, m)
    return sqbuild.assemble(k, mod, step, cv)


def module(fam, k, budget):
    if fam == 'slab': return construct.grid_module(k, 'slabP')
    if fam == 'lat':
        import cp_module
        a, b = construct.grid_module(k, 'slabP')['size']
        r = cp_module.solve(k, a, b, max(0.2, budget), workers=1)
        if r is None: return construct.grid_module(k, 'slabP')
        T = lambda key: [tuple(c) for c in r[key]]
        return dict(R=[(0,) + c for c in T('R')], P=T('P'), PLATE=[(1,) + c for c in T('pl')],
                    CONT=[(-2,) + c for c in T('w2')] + [(-3,) + c for c in T('w3')], size=(a, b))
    raise ValueError(fam)


def run_family(fam, budgets, bits):
    out, tot = {}, 0.0
    for k in KS:
        t = time.time()
        try:
            mod = module(fam, k, budgets.get(k, 0))
            r = ring_for(k, mod, bits.get(k, 0))
        except Exception:
            r = None
        dt = time.time() - t; tot += dt
        out[k] = (max(r.size()) + k if r else None, dt, r)
    return out, tot


if __name__ == '__main__':
    fams = sys.argv[1:] or ['slab']
    bits = json.load(open(HERE / 'bits.json')) if (HERE / 'bits.json').exists() else {}
    for fam in fams:
        b = {int(k): v for k, v in bits.get(fam, {}).items()}
        res, tot = run_family(fam, {k: 2.0 for k in KS}, b)
        print(fam, 'total time', round(tot, 1), 's; predicted PL per k:', {k: v[0] for k, v in res.items()})
