"""Isolate the two-normal interface on the segment after heavy body3.

The fixture supplies the helper's third pull externally. It is explicitly
NOT a self-propelled flyer or bank candidate. No old glue is added/removed.
"""
from pathlib import Path
import sys,itertools,csv,json
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import three_cell_mixed as b
from fastflyer import Flyer,Block,Kind
def add(p,q):return tuple(x+y for x,y in zip(p,q))
def shift(p,x):return p[0]+x,p[1],p[2]

def main():
 out=HERE/'two_normal_fixture';out.mkdir(exist_ok=True)
 # Original body0 is the next target after original body3. Start after
 # its three advances, so new normals fire in the two waiting slots.
 world=b.FRAMES[3];carrier={shift(p,3) for p in b.BODY[0]}
 helperkind=Kind.HONEY if b.KINDS[0]==Kind.SLIME else Kind.SLIME
 rows=[]
 for anchor,ys,zs in itertools.product(sorted(carrier),(-1,1),(-1,1)):
  dy=(0,ys,0);dz=(0,0,zs);red=add(anchor,add(dy,dz))
  normals=[add(anchor,dy),add(anchor,dz)]
  glue=[shift(red,1),*[shift(p,1) for p in normals]]
  new=normals+[red]+glue
  if len(set(new))!=6 or any(p in world for p in new):continue
  f=Flyer(rng_state=5,push_limit=24);f._cells=world.copy()
  for p in normals:f._cells[p]=Block.piston(0)
  f._cells[red]=Block(Kind.REDSTONE_BLOCK)
  for p in glue:f._cells[p]=Block(helperkind)
  file=out/f'c{len(rows):03}.flyer';f.save(file);g=Flyer.load(file)
  delta=tuple(min(p[a] for p in g._cells)-min(p[a] for p in f._cells) for a in range(3))
  rr=add(red,delta)
  rows.append([str(file),*rr,ys,zs,int(helperkind)])
 with (HERE/'two_normal_fixture.inputs.csv').open('w',newline='') as h:
  csv.writer(h).writerows(rows)
 print('local fixtures',len(rows))
if __name__=='__main__':main()
