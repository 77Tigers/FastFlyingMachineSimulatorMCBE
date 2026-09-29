"""Small forward realization from contracts/design.md; no reference geometry loaded."""
from pathlib import Path
from fastflyer import Block, Flyer, Kind

OUT = Path(__file__).resolve().parent

# Coordinates use the handoff's initial world X gauge. The seven cells of each
# sticky body join the action, pickup, and power terminals without extra cells.
A = [(0,2,1), (0,3,0), (0,2,0), (1,2,0), (2,2,0), (3,2,0), (3,2,1)]
B = [(2,2,2), (2,1,1), (2,1,2), (2,3,2), (2,3,1), (3,1,2), (4,1,2)]

f = Flyer(phase_x=0, phase_z=0, rng_state=0, push_limit=10)
for p in A:
    f.set(p, Block(Kind.SLIME))
for p in B:
    f.set(p, Block(Kind.HONEY))
f.set((2,1,0), Block.observer(2))
f.set((4,0,2), Block.observer(2, powered=True))
for name, pos, state in [
    ('A0',(2,2,1),2), ('A1',(2,3,0),0),
    ('B0',(4,2,2),0), ('B1',(3,1,1),0),
]:
    f.set(pos, Block.piston(1, sticky=True, state=state))
f.set((1,2,1), Block(Kind.PISTON_ARM))
f.save(OUT / 'candidate_pl10.flyer')
print('saved', OUT / 'candidate_pl10.flyer', 'cells', len(list(f.blocks())))
