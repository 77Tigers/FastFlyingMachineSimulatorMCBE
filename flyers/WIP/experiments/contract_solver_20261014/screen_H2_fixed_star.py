"""Six ordinary four-glue H2 columns retaining the two current relay roots.
Static conflicts for this fixed relay/T0/X0/G0 placement, not a global bound.
"""
import argparse,itertools,json
from pathlib import Path
from assemble import Flyer
D=[(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,d):return tuple(a+b for a,b in zip(p,d))
def dist(p,q):return sum(abs(a-b) for a,b in zip(p,q))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
 f=Flyer.load(a.base/'problem.flyer');prep=json.loads((a.base/'preparation.json').read_text(encoding='utf-8'));x=set(map(tuple,prep['shapes_G2_T0_X0'][2]));roots={(15,1,12),(15,2,12)};obs=[(17,1,13),(17,2,13)];rows=[]
 for center in sorted(roots):
  rb=add(center,(-1,0,0))
  for dirs in itertools.combinations(D,3):
   targets={add(center,d) for d in dirs};glue=roots|targets
   if len(glue)>4:continue
   motors={add(p,(-1,0,0)) for p in targets};new=glue-roots;conflicts={
    'occupied':sorted((new|motors|{rb})&f._cells.keys()),
    'initial_honey_join':[{'new':p,'X0':q} for p in new for q in x if dist(p,q)==1],
    'G0_observer_pickup_before_move1':[{'new':p,'observer':q} for p in new for q in obs if dist(add(p,(1,0,0)),q)==1]}
   rows.append({'RB':rb,'normals':sorted(motors),'H2_glue':sorted(glue),'conflicts':conflicts,'clear_static':not any(conflicts.values())})
 assert len(rows)==6
 a.out.write_text(json.dumps({'scope':__doc__,'rows':rows,'clear_static_count':sum(r['clear_static'] for r in rows)},indent=2)+'\n',encoding='utf-8');print(json.dumps({'allocations':len(rows),'clear_static':sum(r['clear_static'] for r in rows)}))
if __name__=='__main__':main()
