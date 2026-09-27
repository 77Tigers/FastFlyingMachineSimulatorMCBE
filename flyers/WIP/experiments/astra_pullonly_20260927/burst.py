"""Finite three-pull burst. NOT a repeating flyer or speed record."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
f=Flyer(push_limit=19,rng_state=5)
for z in range(7):f.set((0,2,z),Block(Kind.SLIME))
for z in (0,3,6):
 f.set((0,0,z),Block(Kind.SLIME));f.set((0,1,z),Block(Kind.SLIME))
for x in range(4):f.set((x,2,6),Block(Kind.SLIME))
f.set((3,1,6),Block.observer(3))
f.set((2,0,0),Block.piston(1,sticky=True,state=2));f.set((1,0,0),Block(Kind.PISTON_ARM))
f.set((3,0,3),Block.piston(1,sticky=True));f.set((3,-1,3),Block.observer(2,powered=True))
f.set((4,0,6),Block.piston(1,sticky=True))
f.save(Path(__file__).parent/'three_pull_burst.flyer')
