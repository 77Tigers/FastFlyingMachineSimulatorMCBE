from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
out=Path(__file__).parent
f=Flyer(push_limit=100,rng_state=5)
for x in range(3): f.set((x,1,0),Block(Kind.SLIME))
for z in range(5): f.set((0,1,z),Block(Kind.SLIME))
f.set((0,0,4),Block(Kind.SLIME))
for z in range(5): f.set((0,-1,z),Block(Kind.HONEY))
f.set((0,0,0),Block(Kind.HONEY));f.set((1,-1,4),Block(Kind.HONEY))
f.set((2,0,0),Block.piston(1,sticky=True));f.set((2,2,0),Block.observer(3,powered=True))
f.set((1,0,4),Block.piston(1,sticky=True));f.set((1,-2,4),Block.observer(2))
f.save(out/'baseline.flyer')
