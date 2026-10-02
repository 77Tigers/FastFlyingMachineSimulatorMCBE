import sys, pathlib, subprocess
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind
f = Flyer.load(str(ROOT/'flyers/bank/pl12/human_tm_smol_3bps.flyer'))
cells = {tuple(p): b for p, b in f.blocks()}
mn = min(p[0] for p in cells)
print('minx', mn, 'n', len(cells))
B15 = [(2,5,4),(3,5,4),(4,5,4),(5,5,4),(6,4,4),(6,5,4),(7,3,4),(7,4,3),(7,4,4),(7,5,4)]
for dx in (0,-1,1,-2,2):
    ok = sum(1 for c in B15 if (c[0]+dx,c[1],c[2]) in cells and cells[(c[0]+dx,c[1],c[2])].kind in (Kind.SLIME,Kind.REDSTONE_BLOCK))
    print('dx',dx,ok)
import itertools
out = HERE/'b15del'; out.mkdir(exist_ok=True)
def write(name, rm, lim):
    g = Flyer(f.phase_x, f.phase_z, f.rng_state, lim)
    for p, b in f.blocks():
        if tuple(p) not in rm: g.set(p, b)
    g.save(str(out/f'{name}.flyer'))
for lim in (13,14):
    for c in B15: write(f'L{lim}_d{c[0]}{c[1]}{c[2]}', {c}, lim)
    for a,b in itertools.combinations(B15[:4]+[B15[5]],2): write(f'L{lim}_d{a[0]}{a[1]}{a[2]}_{b[0]}{b[1]}{b[2]}', {a,b}, lim)
