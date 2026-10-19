"""Optimistic fixed-interface H1 three-normal screen, not a native proof.

Retain G1's three target glue cells, observer25,4,11 and H1 puller/root.
Enumerate all four shortest three-glue observer connectors, five direct T1
pull power positions, two early normal lanes and one late lane. Both early
identity assignments are checked. H1 extra glue connectivity is not enforced.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
from assemble import Flyer

def add(p,q):return tuple(a+b for a,b in zip(p,q))
def move(p,word,t):return (p[0]+word[:t].count('m'),p[1],p[2])
def near(p,q):return sum(abs(a-b) for a,b in zip(p,q))==1

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args(); f=Flyer.load(a.base/'problem.flyer')
    old={(23,4,10),(24,4,10),(24,4,11),(25,2,11)}
    occupied=set(f._cells)-old
    roots={(22,2,10),(22,3,10),(22,4,10)}
    routes=[]
    for steps in sorted(set(itertools.permutations([(1,0,0)]*3+[(0,0,1)]))):
        p=(22,4,10);cells=[]
        for step in steps:p=add(p,step);cells.append(p)
        assert p==(25,4,11)
        routes.append(cells[:-1])
    offsets=[(-1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
    sources=[(25,2,11),(24,1,11),(24,3,11),(24,2,10),(24,2,12)]
    rejected=Counter();survivors=[];tested=0;witnesses={}
    def reject(reason,record):
        rejected[reason]+=1
        if len(witnesses.setdefault(reason,[]))<2:witnesses[reason].append(record)
    for rid,route in enumerate(routes):
      glue=roots|set(route)
      for rb in sources:
       early=[tuple(v-o-(2 if k==0 else 0) for k,(v,o) in enumerate(zip(rb,off))) for off in offsets]
       late=[tuple(v-o-(1 if k==0 else 0) for k,(v,o) in enumerate(zip(rb,off))) for off in offsets]
       for pair in itertools.combinations(early,2):
        for last in late:
         tested+=1;reason=None
         actor_cells={*pair,last,(last[0]+1,last[1],last[2])}
         if len(actor_cells)!=4 or actor_cells & (occupied|set(route)|{rb}):reason='initial_overlap'
         elif not all(any(near(p,g) for g in glue) for p in pair):reason='early_G1_pickup_missing'
         elif not any(near(last,move(g,'mmwwm',1)) for g in glue):reason='late_G1_pickup_missing'
         elif any(near(move(g,'mmwwm',t),move(rb,'wwmmm',t)) for t in [0,1] for g in glue):reason='G1_picks_waiting_H1_source'
         elif any(move(g,'mmwwm',t) in {move((25,3,11),'wwmmm',t),move(rb,'wwmmm',t)} for t in range(5) for g in glue):reason='body_overlap'
         record={'route':rid,'G1_connector':route,'source':rb,'early_pair':pair,'late':last}
         if reason:reject(reason,record);continue
         assignments=[]
         for first,second in [pair,pair[::-1]]:
          hglue={(25,3,11),(first[0]+3,first[1],first[2]),(second[0]+3,second[1],second[2]),(last[0]+2,last[1],last[2])}
          actors=[(first,'mmwwm'),(second,'mmmww'),(last,'wmmmw')]
          good=True
          for t in range(5):
           gp={move(p,'mmwwm',t) for p in glue}; hp={move(p,'wwmmm',t) for p in hglue}
           ps=[move(p,w,t) for p,w in actors]
           if gp & hp or any(p in gp|hp|{move(rb,'wwmmm',t)} for p in ps) or len(set(ps))!=3:
            record['overlap_witness']={'slot':t,'G1_glue':sorted(gp),'H1_required_glue':sorted(hp),'pistons':ps}
            good=False;break
          if good:assignments.append({'first':first,'second':second,'late':last,'required_H1_glue':sorted(hglue)})
         if not assignments:reject('required_glue_or_actor_overlap',record);continue
         survivors.append({'route':rid,'G1_connector':route,'source':rb,'assignments':assignments})
    report={'scope':__doc__,'tested':tested,'rejections':dict(rejected),'witnesses':witnesses,'survivors':survivors,'routes':routes,
            'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',Path(__file__)]}}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tested':tested,'rejections':dict(rejected),'survivors':len(survivors)}))

if __name__=='__main__':main()
