"""Apply the working o0 edit (B35 sticky pulls B24 @s2, victim observer on B24, delete pusher B22; base-frame cells)
to another tm_smol-derived flyer, after finding the X/Y/Z offset that best aligns tm_smol's cells."""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from fastflyer import Flyer, Block, Kind
ROOT = HERE.parents[4]
tm = {tuple(p): b.kind for p, b in Flyer.load(str(ROOT/'flyers/bank/pl12/human_tm_smol_3bps.flyer')).blocks()}
tgt = Flyer.load(sys.argv[1]); out = pathlib.Path(sys.argv[2]); out.mkdir(exist_ok=True)
tc = {tuple(p): b for p, b in tgt.blocks()}
best = max(((sum(1 for p, k in tm.items() if tc.get((p[0]+dx, p[1]+dy, p[2]+dz)) and tc[(p[0]+dx, p[1]+dy, p[2]+dz)].kind == k), (dx, dy, dz))
            for dx in range(-6, 7) for dy in range(-3, 4) for dz in range(-3, 4)))
print('alignment', best, 'of', len(tm))
dx, dy, dz = best[1]
OPTS = [[('sl',(9,0,3)),('sl',(10,0,3)),('O',(11,0,3),2),('S',(11,1,3))],
        [('sl',(9,0,4)),('sl',(10,0,4)),('O',(11,0,4),5),('sl',(11,0,2)),('S',(11,0,3))]]
for oi, op in enumerate(OPTS):
    for sh in (-2, -1, 0, 1, 2):           # extra X shift: start phase may differ from the t100 snapshot frame
        for lim in (13, 14):
            c = dict(tc); clash = 0
            c.pop((7+dx+sh, 1+dy, 3+dz), None)  # B22
            for it in op:
                k, p = it[0], it[1]; q = (p[0]+dx+sh, p[1]+dy, p[2]+dz)
                clash += q in c
                c[q] = Block(Kind.SLIME) if k == 'sl' else (Block(Kind.PISTON, direction=1, sticky=True) if k == 'S' else Block.observer(it[2]))
            g = Flyer(tgt.phase_x, tgt.phase_z, tgt.rng_state, lim)
            for p, b in c.items(): g.set(p, b)
            g.save(str(out/f'o{oi}_sh{sh}_L{lim}_c{clash}.flyer'))
