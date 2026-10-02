"""Rear glue-reduction candidate generator for 3bps_original.
python gen_rear.py OUT MODE BODIES [--lim=12] [--r=2]
MODE del1: remove one non-RB cell.  del2add1: remove two cells (non-RB) of R, add one cell (R's material) touching R.
     del1addany: remove one R cell, add one glue cell (material of the body it touches) within r of the removed cell
     touching exactly one glue body (any body).  delrb: move RB (remove a glue cell, put RB elsewhere adjacent to R).
"""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE.parent))
argv=sys.argv; sys.argv=['x']; import planner as P; sys.argv=argv
from fastflyer import Flyer, Kind, Block
import os
SRC = HERE.parent/('snaps_orig/t100.flyer' if os.environ.get('SNAP') else 'orig.flyer')
DX = 14 if os.environ.get('SNAP') else 0
bodies, ev = P.parse(str(HERE.parent/'orig.bodytrack.txt'))
for _b in bodies.values(): _b['cells'] = {(c[0]+DX, c[1], c[2]): k for c, k in _b['cells'].items()}
own = {c: b for b, d in bodies.items() for c in d['cells']}
base = Flyer.load(str(SRC)); cells = {tuple(p): b for p, b in base.blocks()}
GL = {Kind.SLIME: 'sl', Kind.HONEY: 'ho'}
def mat(b):
    return Kind.SLIME if 'sl' in bodies[b]['cells'].values() else Kind.HONEY
def ok_new(c, kind, R, removed):
    if c in cells and c not in removed: return False
    touch = set()
    for f in P.FACES:
        q = P.add(c, f)
        if q in removed or q not in cells: continue
        k = cells[q].kind
        if k in GL:
            if k == kind: touch.add(own.get(q))
        elif k == Kind.REDSTONE_BLOCK and own.get(q) is not None and own.get(q) != R: return False
    return touch == {R}
def write(out, name, rm, add, lim):
    g = Flyer.load(str(SRC)); g.push_limit = lim
    for c in rm: g.remove(c)
    for c, k in add: g.set(c, Block(k))
    g.save(str(out/f'{name}.flyer'))
def n(c): return '%d.%d.%d' % c
if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); mode = sys.argv[2]; Rs = [int(x) for x in sys.argv[3].split(',')]
    lim = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--lim=')), 12))
    r = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--r=')), 2))
    out.mkdir(parents=True, exist_ok=True); cnt = 0
    for R in Rs:
        cs = list(bodies[R]['cells']); glue = [c for c in cs if bodies[R]['cells'][c] != 'RB']; m = mat(R)
        if mode == 'del1':
            for a in glue: write(out, f'B{R}_d{n(a)}', {a}, [], lim); cnt += 1
        elif mode == 'del2add1':
            for a, b in itertools.combinations(glue, 2):
                rm = {a, b}; keep = [c for c in cs if c not in rm]
                cand = {P.add(c, f) for c in keep for f in P.FACES}
                for c in sorted(cand):
                    if c in rm: continue
                    if ok_new(c, m, R, rm):
                        write(out, f'B{R}_d{n(a)}_{n(b)}_a{n(c)}', rm, [(c, m)], lim); cnt += 1
        elif mode == 'del1addany':
            for a in glue:
                rm = {a}
                for c in itertools.product(*[range(a[i]-r, a[i]+r+1) for i in range(3)]):
                    if c == a or c in cells: continue
                    for B in {own.get(P.add(c, f)) for f in P.FACES} - {None}:
                        if not bodies[B]['glue']: continue
                        k = mat(B)
                        if ok_new(c, k, B, rm):
                            write(out, f'B{R}_d{n(a)}_a{n(c)}B{B}', rm, [(c, k)], lim); cnt += 1
    print('wrote', cnt)
