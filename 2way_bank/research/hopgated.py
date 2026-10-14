"""Reversible six-tick design: both sticky pistons ride the first-moving body.
Finite CP-SAT construction model; every solution must pass the real simulator.
"""
import argparse,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from ortools.sat.python import cp_model
from fastflyer import Flyer,Block,Kind
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sx(p,x):return add(p,(x,0,0))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--time',type=int,default=300);ap.add_argument('--out',default='2way_bank/hopgated');ap.add_argument('--size',type=int,default=4);ap.add_argument('--cap',type=int,default=12);ap.add_argument('--seed',type=int,default=1);a=ap.parse_args()
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 m=cp_model.CpModel();box=list(itertools.product(range(-2,4),range(a.size),range(a.size)));bs=set(box)
 ks=['g','T','N','S']+['O'+str(i) for i in range(6)]
 X={(s,p,k):m.NewBoolVar(f'{s}_{p}_{k}') for s in range(2) for p in box for k in ks}
 def x(s,p,k):return X.get((s,p,k),0)
 def OR(ls):
  ls=[l for l in ls if not isinstance(l,int) or l!=0]
  if not ls:return 0
  if len(ls)==1:return ls[0]
  v=m.NewBoolVar('');m.AddMaxEquality(v,ls);return v
 def AND(u,v):
  if isinstance(u,int) and u==0 or isinstance(v,int) and v==0:return 0
  z=m.NewBoolVar('');m.Add(z<=u);m.Add(z<=v);m.Add(z>=u+v-1);return z
 def forbid(u,v):
  if isinstance(u,int) and u==0 or isinstance(v,int) and v==0:return
  m.Add(u+v<=1)
 occ={};ordinary={}
 for s in range(2):
  for p in box:
   occ[s,p]=m.NewBoolVar('');m.Add(sum(x(s,p,k) for k in ks)==occ[s,p])
   ordinary[s,p]=OR([x(s,p,k) for k in ks if k!='S'])
  m.Add(sum(ordinary[s,p] for p in box)+2<=a.cap)
  for k in ['N','S']:m.Add(sum(x(s,p,k) for p in box)==1)
  m.Add(sum(x(s,p,k) for p in box for k in ks if k.startswith('O'))==2)
  ranks={p:m.NewIntVar(0,a.cap,'') for p in box};roots=[]
  for p in box:
   r=m.NewBoolVar('');roots.append(r);m.Add(r<=x(s,p,'g'));m.Add(ranks[p]==0).OnlyEnforceIf(r)
   parents=[]
   for d in D:
    q=add(p,d)
    if q not in bs:continue
    v=m.NewBoolVar('');parents.append(v);m.Add(v<=x(s,q,'g'));m.Add(ranks[q]<ranks[p]).OnlyEnforceIf(v)
   m.Add(sum(parents)+r>=x(s,p,'g'))
   m.Add(sum(x(s,add(p,d),'g') for d in D)>=ordinary[s,p]-x(s,p,'g'))
   for o in range(2):m.Add(sum(x(o,add(p,d),'g') for d in D)>=x(s,p,'S'))
  m.Add(sum(roots)==1)
 m.Add(x(0,(0,1,1),'N')==1);m.Add(x(1,(1,1,1),'g')==1)
 if 'sym' in a.out:
  for p in box:
   q=(1-p[0],p[1],a.size-1-p[2])
   for k in ks:
    kk=k
    if k.startswith('O'):
     di=int(k[1]);kk='O'+str(di^1 if di<2 or di>=4 else di)
    m.Add(x(0,p,k)==x(1,q,kk))
 if 'pinned' in a.out:
  m.Add(x(0,(0,1,3),'S')==1)
 # mode is the body whose observers pulse first: 0 => +X, 1 => -X.
 print('Connectivity model built',flush=True)
 for mode in (0,1):
  lead=1-mode
  for gap in (0,1):
   print('Building mode/pose',mode,gap,flush=True)
   def sh(s,k):return 0 if not gap else (1 if mode==0 and (s==1 or k=='S') or mode==1 and s==1 and k!='S' else 0)
   def wx(s,w,k):return x(s,sx(w,-sh(s,k)),k)
   def occupied(w):return OR([wx(s,w,k) for s in range(2) for k in ks])
   worlds=set(sx(p,sh(s,k)) for s in range(2) for p in box for k in ks)
   for w in worlds:m.AddAtMostOne([wx(s,w,k) for s in range(2) for k in ks if not isinstance(wx(s,w,k),int)])
   mover=lead if not gap else mode;act_s=mode if not gap else lead;act_k='N' if not gap else 'S'
   move=(1 if mode==0 else -1)
   def moves(s,k):return (s==mover and k!='S') or (not gap and k=='S')
   for s in range(2):
    for p in box:
     w=sx(p,sh(s,'g'))
     if s==mover:
      for d in D:
       q=add(w,d)
       for o in range(2):
        for k in ks:
         if moves(o,k) or k=='g' or (o==act_s and k==act_k):continue
         forbid(x(s,p,'g'),wx(o,q,k))
     for k in ks:
      if not moves(s,k):continue
      dest=sx(p,sh(s,k)+move)
      for o in range(2):
       for kk in ks:
        if not moves(o,kk):forbid(x(s,p,k),wx(o,dest,kk))
     # Active actuator requires glue on the moved body.
     fd=D[s];pw=sx(p,sh(s,act_k));front=add(pw,fd)
     if s==act_s:
      target=front if not gap else add(front,fd)
      m.Add(x(s,p,act_k)<=wx(mover,target,'g'))
      if gap:forbid(x(s,p,'S'),occupied(front))
   # Each sticky must be attached to the leading body's glue in the expanded pose.
   if gap:
    for s in range(2):
     for p in box:
      w=sx(p,sh(s,'S'));m.Add(sum(wx(lead,add(w,d),'g') for d in D)>=x(s,p,'S'))
   source=mode if not gap else lead
   hot={};direct={}
   for p in box:
    w=sx(p,sh(source,'O0'))
    for di,d in enumerate(D):
     q=add(w,d);v=x(source,p,'O'+str(di));direct.setdefault(q,[]).append((v,w))
     sol=OR([wx(s,q,k) for s in range(2) for k in ('g','T')]);hot.setdefault(q,[]).append(AND(v,sol))
   hot={p:OR(v) for p,v in hot.items()}
   for s in range(2):
    for p in box:
     for k in ('N','S'):
      w=sx(p,sh(s,k));front=add(w,D[s]);src=[v for v,q in direct.get(w,[]) if q!=front]
      src.extend(hot.get(add(w,d),0) for d in D if add(w,d)!=front);power=OR(src)
      if s==act_s and k==act_k:m.Add(x(s,p,k)<=power)
      else:forbid(x(s,p,k),power)
 # Need compatible normal and sticky arms while updates interleave at the expanded pose.
 # Added after extracting a real-simulator counterexample if needed.
 m.Minimize(sum(ordinary.values()))
 solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=a.time;solver.parameters.num_search_workers=8;solver.parameters.random_seed=a.seed
 class Found(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   cells=[(s,p,k) for (s,p,k),v in X.items() if self.Value(v)]
   (out/'design.json').write_text(json.dumps(cells,indent=2));print('FOUND',self.ObjectiveValue()+2,flush=True)
   for mode in (0,1):
    f=Flyer(push_limit=12,rng_state=42)
    for s,p,k in cells:
     b=Block(Kind.SLIME if s==0 else Kind.HONEY) if k=='g' else Block(Kind.SMOOTH_STONE) if k=='T' else Block.piston(s,sticky=k=='S') if k in ('N','S') else Block.observer(int(k[1]),powered=s==mode)
     f.set(p,b)
    if mode:f.mirror('x')
    f.save(out/('A.flyer' if mode==0 else 'B.flyer'))
 print(f'Model built: {len(box)} cells cap={a.cap}',flush=True)
 status=solver.Solve(m,Found());name=solver.StatusName(status);print(name,solver.ResponseStats(),flush=True)
 (out/'status.txt').write_text(name+'\n'+solver.ResponseStats())
if __name__=='__main__':main()
