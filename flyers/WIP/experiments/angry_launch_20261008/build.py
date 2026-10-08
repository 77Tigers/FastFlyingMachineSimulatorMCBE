"""Small one-shot angry-piston launch demonstration. No private input files used."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from fastflyer import Block,Flyer,Kind
MASK=(1<<64)-1
INC=0x9e3779b97f4a7c15
def draw(s):
 s=(s+INC)&MASK;v=s
 v=((v^(v>>30))*0xbf58476d1ce4e5b9)&MASK
 v=((v^(v>>27))*0x94d049bb133111eb)&MASK
 return s,v^(v>>31)
# Select the two-chunk schedule directly, without testing candidate flyers.
seed=0
while True:
 s=seed
 for _ in range(3):s,tickseed=draw(s)
 if draw(tickseed)[1]%2==1:break
 seed+=1
f=Flyer(phase_x=0,phase_z=15,rng_state=seed,push_limit=3)
f.set((0,1,0),Block.piston(0))                  # P: starts NOT angry
f.set((0,0,0),Block(Kind.REDSTONE_BLOCK))       # keep P powered until pickup
f.set((1,1,0),Block.piston(0,sticky=True,state=2)) # extended blocker base
f.set((2,1,0),Block(Kind.PISTON_ARM))
f.set((1,0,0),Block(Kind.REDSTONE_BLOCK))       # hold blocker extended
f.set((0,2,0),Block.piston(4,state=3))          # carrier driver: one-tick delay
f.set((0,3,0),Block(Kind.REDSTONE_BLOCK))
f.set((0,2,1),Block(Kind.HONEY))
f.set((0,1,1),Block(Kind.HONEY))
f.set((1,1,1),Block(Kind.SLIME))               # target
out=Path(__file__).with_name('angry_launch_demo.flyer')
f.save(out)
print(f'{out}: {len(f.blocks())} cells including one arm, seed={seed}, PL3, X0/Z15')
