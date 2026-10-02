import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
f = Flyer.load(str(ROOT/'flyers/bank/pl12/human_tm_smol_3bps.flyer'))
cells = {tuple(p): b for p, b in f.blocks()}
B0 = (2,6,4); tail=(2,5,4)
pist = cells[B0]
out = HERE/'b0move'; out.mkdir(exist_ok=True)
for q in out.glob('*.flyer'): q.unlink()
base = {p:b for p,b in cells.items() if p not in (B0,tail)}
n=0
for lim in (12,13,14):
  for x in range(2,8):
    for y in range(3,9):
      for z in range(1,9):
        p=(x,y,z)
        if p in base: continue
        for d in (0,):   # +X pushers only
            front=(x+1,y,z)
            g = Flyer(f.phase_x, f.phase_z, f.rng_state, lim)
            for q,b in base.items(): g.set(q,b)
            g.set(p, pist)
            g.save(str(out/f'L{lim}_{x}{y}{z}.flyer')); n+=1
print(n)
