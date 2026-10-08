"""Generate the two-body handoff concept from explicit geometry; never reads the private input."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer,Block,Kind

def build(n=16,phase_z=9):
 f=Flyer(phase_x=0,phase_z=phase_z,rng_state=2,push_limit=20*n+9)
 S=Block(Kind.SLIME);H=Block(Kind.HONEY);R=Block(Kind.REDSTONE_BLOCK)
 for y in range(3*n+1):
  for x,z in [(3,5),(4,5),(6,6)]:f.set((x,y,z),S)
  for x,z in [(3,11),(4,11),(6,10)]:f.set((x,y,z),H)
  if y<3*n:
   for x,z in [(3,9),(4,9)]:f.set((x,y,z),S)
  if y>0:
   for x,z in [(4,7),(5,7)]:f.set((x,y,z),H)
  if y>0:f.set((5,y,6),R if y%3==2 else Block.piston(0))
  if y<3*n:f.set((5,y,10),R if y%3==1 else Block.piston(0,state=3))
 for x,z in [(5,5),(6,5),(6,7),(6,8),(5,8),(4,8)]:f.set((x,0,z),S)
 for x,z in [(5,8),(6,8),(6,9),(6,11),(5,11)]:f.set((x,3*n,z),H)
 return f
if __name__=='__main__':
 n=int(sys.argv[1]) if len(sys.argv)>1 else 16
 z=int(sys.argv[2]) if len(sys.argv)>2 else 9
 out=Path(__file__).parent/f'bank_n{n}_z{z}.flyer'
 f=build(n,z);f.save(out);print(out,len(f.blocks()),f.push_limit)

