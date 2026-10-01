"""Concrete side contacts and U-shaped recovery, derived from the local fixture.

Three new bodies H0/J2/F4. H pulls original body0's last move; J pulls H;
F powers J. J and F temporarily use three-normal drives (user-approved).
No added original-body glue. All assemblies encoded24.
"""
from pathlib import Path
import sys,csv,json,subprocess,itertools
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import three_cell_mixed as b
from fastflyer import Flyer,Block,Kind
def add(p,q):return tuple(a+c for a,c in zip(p,q))
def sh(p,x):return p[0]+x,p[1],p[2]
def mul(p,k):return tuple(v*k for v in p)
def main():
 out=HERE/'compact_helper_cascade';out.mkdir(exist_ok=True);records=[]
 for row in list(csv.reader((HERE/'two_normal_fixture.inputs.csv').open()))[4:]:
  file,*nums=row;rx,ry,rz,ys,zs,kind=map(int,nums);red=(rx,ry,rz);dy=(0,ys,0);dz=(0,0,zs)
  B=add(red,mul(add(dy,dz),-1));base=Flyer.load(file);base.push_limit=24
  # Find the old extended member at the original body0 front-group center.
  # The original source is the nearest old redstone to this side anchor.
  reds=[p for p,x in base._cells.items() if x.kind==Kind.REDSTONE_BLOCK and p!=red]
  source=min(reds,key=lambda p:abs(p[0]-(B[0]-1))+abs(p[1]-B[1])+abs(p[2]-B[2]))
  old=[p for p,x in base._cells.items() if x.kind==Kind.PISTON and x.state==2 and p[0]==source[0]-1 and abs(p[1]-source[1])+abs(p[2]-source[2])==1]
  if len(old)!=1:records.append(dict(file=file,reason='old_member',source=source,members=old));continue
  base._cells.pop(old[0]);base._cells.pop(sh(old[0],1))
  Rj=sh(B,4);Rf=add(sh(B,5),add(mul(dy,2),dz));Sj=add(sh(B,4),add(dy,dz))
  new={};conflicts=[]
  def put(p,x):
   if p in new and new[p]!=x:conflicts.append(('new',p))
   if p in base._cells:conflicts.append(('old',p))
   new[p]=x
  # H's missing fourth corner is the pulling piston; route through two
  # helper-only cells around it instead of filling it with sticky material.
  for p in (add(sh(B,1),mul(dy,-1)),add(sh(B,1),add(mul(dy,-1),dz))):put(p,Block(Kind.HONEY))
  put(sh(B,1),Block.piston(1,sticky=True))
  J={sh(Rj,1),*[add(sh(Rj,1),d) for d in (dy,dz,mul(dy,-1))],add(sh(B,4),dy),add(sh(B,4),mul(dy,2))}
  for d in ((0,0,0),dy,dz,mul(dz,-1)):J.add(add(sh(Rf,-2),d))
  for p in J:put(p,Block(Kind.SLIME))
  put(Rj,Block(Kind.REDSTONE_BLOCK));put(Sj,Block.piston(1,sticky=True))
  for j,d in enumerate((dy,dz,mul(dy,-1))):
   p=add(sh(Rj,-2+j),d);state=2 if j==1 else 0;put(p,Block.piston(0,state=state))
   if state:put(sh(p,1),Block(Kind.PISTON_ARM))
  F={sh(Rf,1),*[add(sh(Rf,1),d) for d in (dy,dz,mul(dz,-1))]}
  for p in F:put(p,Block(Kind.HONEY))
  put(Rf,Block(Kind.REDSTONE_BLOCK))
  for d in (dy,dz,mul(dz,-1)):put(add(sh(Rf,-1),d),Block.piston(0))
  record=dict(base=file,anchor=B,removed=old[0],source=source,J_source=Rj,F_source=Rf,J_sticky=Sj,J_glue=len(J),F_glue=len(F),conflicts=conflicts)
  if not conflicts:
   base._cells.update(new);name=Path(file).stem+'.flyer';base.save(out/name);record['file']=name
  records.append(record)
 (HERE/'compact_helper_cascade.manifest.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
 runner=HERE.parent/'bin/research_runner.exe'
 p=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/'compact_helper_cascade.screen.csv')],capture_output=True,text=True)
 (HERE/'compact_helper_cascade.screen.txt').write_text(p.stdout+p.stderr);print(p.stdout)
if __name__=='__main__':main()
