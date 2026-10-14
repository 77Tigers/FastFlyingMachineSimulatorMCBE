"""Two rigid bodies, direction-selected observer routing; six-tick cycles.

In the compressed pose each body's observers power its normal piston; in the
expanded pose they power its sticky piston. Choose the initially pulsing body
to choose travel direction. The model excludes cross-body adhesion and requires
each body to be glue-connected, with at most 12 permanent blocks.
"""
import argparse, itertools, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ortools.sat.python import cp_model
from fastflyer import Flyer, Block, Kind

D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sx(a,x): return add(a,(x,0,0))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--time',type=int,default=300);ap.add_argument('--out',default='2way_bank/gated');ap.add_argument('--size',type=int,default=4);ap.add_argument('--cap',type=int,default=12);ap.add_argument('--seed',type=int,default=1);a=ap.parse_args()
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 m=cp_model.CpModel();box=list(itertools.product(range(-2,4),range(a.size),range(a.size)));B=set(box)
 ks=['g','T','N','S']+['O'+str(i) for i in range(6)]
 X={(s,p,k):m.NewBoolVar(f'{s}_{p}_{k}') for s in range(2) for p in box for k in ks}
 def x(s,p,k):return X.get((s,p,k),0)
 occ={};solid={};obs={}
 def OR(ls):
  ls=[l for l in ls if not isinstance(l,int) or l!=0]
  if not ls:return 0
  v=m.NewBoolVar('');m.AddMaxEquality(v,ls);return v
 def AND(u,v):
  if isinstance(u,int) and u==0 or isinstance(v,int) and v==0:return 0
  z=m.NewBoolVar('');m.Add(z<=u);m.Add(z<=v);m.Add(z>=u+v-1);return z
 def forbid(u,v):
  if isinstance(u,int) and u==0 or isinstance(v,int) and v==0:return
  m.Add(u+v<=1)
 for s in range(2):
  for p in box:
   occ[s,p]=m.NewBoolVar('');m.Add(sum(x(s,p,k) for k in ks)==occ[s,p])
   solid[s,p]=OR([x(s,p,'g'),x(s,p,'T')]);obs[s,p]=OR([x(s,p,'O'+str(i)) for i in range(6)])
  m.Add(sum(occ[s,p] for p in box)<=a.cap)
  for k in ['N','S']:m.Add(sum(x(s,p,k) for p in box)==1)
  m.Add(sum(obs[s,p] for p in box)==2)
  # Connected glue, rooted at the unique lowest-rank glue cell.
  roots=[];ranks={p:m.NewIntVar(0,a.cap,'') for p in box}
  for p in box:
   r=m.NewBoolVar('');roots.append(r);m.Add(r<=x(s,p,'g'));m.Add(ranks[p]==0).OnlyEnforceIf(r)
   parents=[]
   for d in D:
    q=add(p,d)
    if q not in B:continue
    v=m.NewBoolVar('');parents.append(v);m.Add(v<=x(s,q,'g'));m.Add(ranks[q]<ranks[p]).OnlyEnforceIf(v)
   m.Add(sum(parents)+r>=x(s,p,'g'))
   m.Add(sum(x(s,add(p,d),'g') for d in D)>=occ[s,p]-x(s,p,'g'))
  m.Add(sum(roots)==1)
 # Fix translation and one normal-to-target contact.
 m.Add(x(0,(0,1,1),'N')==1)
 m.Add(x(1,(1,1,1),'g')==1)
 for gap in (0,1):
  shift=[0,gap]
  def at(s,p):return sx(p,-shift[s])
  world=set(box)|{sx(p,gap) for p in box}
  for w in world:
   forbid(occ.get((0,w),0),occ.get((1,at(1,w)),0))
  # At both poses, normal/sticky targets and empty sticky heads.
  for s in range(2):
   other=1-s;fd=D[s]
   for p in box:
    w=sx(p,shift[s]);front=add(w,fd)
    k='N' if gap==0 else 'S';target=front if gap==0 else add(front,fd)
    m.Add(x(s,p,k)<=x(other,at(other,target),'g'))
    if gap:
     for o in range(2):forbid(x(s,p,'S'),occ.get((o,at(o,front)),0))
    # Cross glue adhesion permits only the initiating actuator.
    for d in D:
     q=at(other,add(w,d))
     for kk in ks:
      if kk not in ('g',k):forbid(x(s,p,'g'),x(other,q,kk))
    # Translation sweep: compressed bodies move apart, expanded together.
    move=(-1 if s==0 else 1)*(1 if gap==0 else -1)
    dest=at(other,sx(w,move))
    forbid(occ[s,p],occ.get((other,dest),0))
  # Observer pulses from either body must select exactly its appropriate piston.
  for source in range(2):
   hot={};direct={}
   for p in box:
    w=sx(p,shift[source])
    for di,d in enumerate(D):
     q=add(w,d);direct.setdefault(q,[]).append((x(source,p,'O'+str(di)),w))
     sol=OR([solid.get((s,at(s,q)),0) for s in range(2)])
     hot.setdefault(q,[]).append(AND(x(source,p,'O'+str(di)),sol))
   hot={p:OR(v) for p,v in hot.items()}
   for s in range(2):
    for p in box:
     w=sx(p,shift[s]);front=add(w,D[s]);src=[]
     src.extend(v for v,q in direct.get(w,[]) if q!=front)
     src.extend(hot.get(add(w,d),0) for d in D if add(w,d)!=front)
     power=OR(src)
     for k in ('N','S'):
      if s==source and k==('N' if gap==0 else 'S'):m.Add(x(s,p,k)<=power)
      else:forbid(x(s,p,k),power)
 # Minimize body size after finding feasibility.
 m.Minimize(sum(occ.values()))
 solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=a.time;solver.parameters.num_search_workers=8;solver.parameters.random_seed=a.seed
 print(f'Model built: cells={len(box)} cap={a.cap}',flush=True)
 status=solver.Solve(m);name=solver.StatusName(status);print(name,solver.ResponseStats(),flush=True)
 (out/'status.txt').write_text(name+'\n'+solver.ResponseStats())
 if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return
 cells=[(s,p,k) for (s,p,k),v in X.items() if solver.Value(v)]
 (out/'design.json').write_text(json.dumps(cells,indent=2))
 for mode in (0,1):
  f=Flyer(push_limit=12,rng_state=42)
  for s,p,k in cells:
   b=Block(Kind.SLIME if s==0 else Kind.HONEY) if k=='g' else Block(Kind.SMOOTH_STONE) if k=='T' else Block.piston(s,sticky=k=='S') if k in ('N','S') else Block.observer(int(k[1]),powered=s==mode)
   f.set(p,b)
  if mode:f.mirror('x')
  f.save(out/('A.flyer' if mode==0 else 'B.flyer'))
 print('SAVED',out,flush=True)

if __name__=='__main__':main()
