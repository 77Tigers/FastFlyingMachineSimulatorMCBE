"""Independently audit a geometry-only witness and list removed foreign contacts.
No motion simulation or physical acceptance is performed.
"""
import argparse,json
from pathlib import Path
from assemble import Flyer
from fastflyer import Kind
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,d):return tuple(a+b for a,b in zip(p,d))
def dist(p,q):return sum(abs(a-b) for a,b in zip(p,q))
def connected(shape):
 seen={next(iter(shape))};todo=list(seen)
 while todo:
  p=todo.pop()
  for d in D:
   q=add(p,d)
   if q in shape and q not in seen:seen.add(q);todo.append(q)
 return seen==shape

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('run',type=Path);a=ap.parse_args()
 r=json.loads((a.run/'report.json').read_text(encoding='utf-8'));w=r['geometry_witness'];assert w and r['geometry_only']
 shapes={n:set(map(tuple,s)) for n,s in w['shapes'].items()};caps={'G2':6,'T0':8,'X0':6}
 for n,s in shapes.items():assert len(s)<=caps[n] and connected(s)
 assert not any(shapes[n]&shapes[m] for n in shapes for m in shapes if n<m)
 motor=tuple(w['motor']);obs=tuple(w['observer']);direction=w['direction'];assert add(obs,D[direction])==add(motor,(2,0,0))
 assert (15,1,11) in shapes['T0'] and (19,2,11) in shapes['T0'] and add(motor,(3,0,0)) in shapes['T0']
 assert all(dist(p,(18,1,11))>1 for p in shapes['T0'])
 assert all(add(motor,(k,0,0)) not in shapes['T0'] for k in [0,1,2])
 assert any(dist(p,motor)==1 for p in shapes['X0']) and any(dist(p,(16,2,11))==1 for p in shapes['X0'])
 assert any(dist(p,obs)==1 for p in shapes['G2'])
 for actor in [(14,1,12),(14,2,11),(14,3,12)]:assert any(dist(p,actor)==1 for p in shapes['G2'])
 f=Flyer.load(a.base/'problem.flyer');oldg={(13,2,12),(13,1,12),(13,3,12),(13,2,11)};oldt={(15,1,11),(15,1,10),(15,2,10),(16,2,10),(17,2,10),(18,2,10),(19,2,10),(19,2,11)}
 fixed=set(f._cells)-(oldg|oldt|{(16,3,11)});g0={p for p in fixed if f._cells[p].kind==Kind.SLIME};honey={p for p in fixed if f._cells[p].kind==Kind.HONEY}
 conflicts={'occupied':{n:sorted(s&fixed) for n,s in shapes.items()},'new_actors_occupied':[p for p in [motor,obs] if p in fixed]}
 for n,deltas in [('T0',[-2,-1,0,1]),('G2',[-2,-1,0])]:conflicts[n+'_G0']=[{'cell':p,'foreign':q,'delta':k} for p in sorted(shapes[n]) for q in sorted(g0) for k in deltas if dist(add(p,(k,0,0)),q)<=1]
 conflicts['X0_H2']=[{'cell':p,'foreign':q,'delta':k} for p in sorted(shapes['X0']) for q in sorted(honey) for k in [-1,0,1] if dist(add(p,(k,0,0)),q)<=1]
 result={'scope':__doc__,'verified_geometry':True,'counts':{n:len(s) for n,s in shapes.items()},'motor':motor,'observer':obs,'conflicts':conflicts}
 (a.run/'independent_geometry_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

if __name__=='__main__':main()
