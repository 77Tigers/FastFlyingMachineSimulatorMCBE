import sys, pathlib, itertools, subprocess
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]; sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
SN = HERE.parent / 'snaps' / 't100.flyer'
base = Flyer.load(str(SN))
cells = {tuple(p): b for p, b in base.blocks()}
def s(p): return (p[0]-2, p[1], p[2])
print('B22 base (7,1,3) -> snap', s((7,1,3)), cells.get(s((7,1,3))))
for p in [(7,0,3),(7,0,4),(7,0,5),(7,1,3),(8,0,3)]: print(p, cells.get(s(p)))
OPTS = [
 [('sl',(9,0,3)),('sl',(10,0,3)),('O+Y',(11,0,3)),('S',(11,1,3))],
 [('sl',(9,0,4)),('sl',(10,0,4)),('O-Z',(11,0,4)),('sl35',(11,0,2)),('S',(11,0,3))],
 [('sl',(8,-1,3)),('sl',(9,0,3)),('sl',(10,0,3)),('O-Y',(11,0,3)),('sl35',(11,-1,2)),('S',(11,-1,3)),('sl35',(11,0,2))],
]
DIR = {'O+Y':2,'O-Y':3,'O-Z':5}
out = HERE/'b24pull'
for q in out.glob('*.flyer'): q.unlink()
for oi, op in enumerate(OPTS):
    for delB22 in (0,1):
        for lim in (12,13,14):
            g = Flyer(base.phase_x, base.phase_z, base.rng_state, lim)
            c = dict(cells); clash=False
            if delB22: c.pop(s((7,1,3)), None)
            for k,p in op:
                q = s(p)
                if q in c: clash=True; print('clash', oi, k, p, c[q])
                if k.startswith('sl'): c[q]=Block(Kind.SLIME)
                elif k=='S': c[q]=Block(Kind.PISTON, direction=1, sticky=True)
                else: c[q]=Block.observer(DIR[k])
            for p,b in c.items(): g.set(p,b)
            g.save(str(out/f'o{oi}_d{delB22}_L{lim}.flyer'))
