"""Single-perturbation repair screen for a stalled flyer.
python perturb.py IN.flyer TICKS [LIMIT]  -> prints candidates sorted by distance (top 25)."""
import sys, pathlib, copy
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer, Block, Kind, DIRECTIONS
import simtools, bodies
def clone(f):
    g = Flyer(f.phase_x, f.phase_z, f.rng_state, f.push_limit)
    for p, b in f.blocks(): g.set(p, b)
    return g
def variants(f):
    cells = dict(f.blocks())
    for p, b in cells.items():
        if b.kind == Kind.PISTON_ARM: continue
        g = clone(f); g.remove(p)
        if b.kind == Kind.PISTON and b.state == 2:
            d = DIRECTIONS[b.direction]; g.remove((p[0]+d[0], p[1]+d[1], p[2]+d[2]))
        yield f'del{p}', g
        if b.kind in (Kind.SLIME, Kind.HONEY):
            g = clone(f); g.set(p, Block(Kind.HONEY if b.kind == Kind.SLIME else Kind.SLIME)); yield f'swap{p}', g
        if b.kind == Kind.PISTON:
            d = DIRECTIONS[b.direction]; a = (p[0]+d[0], p[1]+d[1], p[2]+d[2])
            g = clone(f)
            if b.state == 2:
                g.remove(a); g.set(p, Block.piston(b.direction, b.sticky, state=0)); yield f'retract{p}', g
            elif a not in cells:
                g.set(a, Block(Kind.PISTON_ARM)); g.set(p, Block.piston(b.direction, b.sticky, state=2)); yield f'extend{p}', g
    _, comps = bodies.bodies(f)
    for i, c in enumerate(comps):
        if len(c) < 2: continue
        for dx in (-2, -1, 1, 2):
            moved = {(p[0]+dx, p[1], p[2]) for p in c}
            if any(q in cells and q not in set(c) for q in moved): continue
            g = clone(f)
            for p in c: g.remove(p)
            for p in c: g.set((p[0]+dx, p[1], p[2]), cells[p])
            yield f'shift{min(c)}n{len(c)}dx{dx}', g
if __name__ == '__main__':
    f = Flyer.load(sys.argv[1]); ticks = int(sys.argv[2])
    if len(sys.argv) > 3: f.push_limit = int(sys.argv[3])
    vs = dict(variants(f)); print(len(vs), 'variants')
    res = simtools.screen(vs, ticks)
    rows = sorted(res.items(), key=lambda kv: (-int(kv[1]['distance']), int(kv[1]['movement_failures'])))
    for n, r in rows[:25]: print(f'{n:<34}', simtools.brief(r))
