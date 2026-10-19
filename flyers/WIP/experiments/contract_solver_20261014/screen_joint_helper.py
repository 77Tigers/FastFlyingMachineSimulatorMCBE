"""Bounded joint front-power/ordinary-column geometry screen, not physics proof.

Free T1 sticky among three attached lanes; free H1 direct RB, H1 sticky contact
on a G1 target, H1 power glue and G1 observer. G1 has three fixed target glue
cells plus at most three connected extra cells. H1 glue connectivity and many
dynamic power/arm/material constraints are omitted. Leads need native checks.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time
from assemble import Flyer
from fastflyer import Kind
from screen_helper_column import add,move,near

D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
NORMAL=[(-1,0,0),*D[2:]]
STICKY=[(1,0,0),*D[2:]]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--max-leads',type=int,default=24)
    ap.add_argument('--split-column-power',action='store_true',help='Add one H1 RB for the two early pushers')
    a=ap.parse_args();start=time.monotonic();f=Flyer.load(a.base/'problem.flyer')
    freed={(23,4,10),(24,4,10),(24,4,11),(25,4,11),(25,3,11),(25,3,10),(25,2,11),(22,2,11)}
    fixed=set(f._cells)-freed;roots={(22,2,10),(22,3,10),(22,4,10)}
    contract=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    fixed_glue=[]
    for port in contract['ports']:
        if port['name'] not in ['X0','T0','X1','T1','X2','T2']:continue
        root=tuple(port['at']);kind=f._cells[root].kind;seen={root}
        while True:
            expanded=seen|{add(p,d) for p in seen for d in D if add(p,d) in f._cells and f._cells[add(p,d)].kind==kind}
            if expanded==seen:break
            seen=expanded
        fixed_glue.extend((p,port['word']) for p in seen)
    def g_allowed(p):
        return p not in fixed and all(move(p,'mmwwm',t)!=move(q,w,t) for q,w in fixed_glue for t in range(5))
    shapes={frozenset(roots)};all_shapes=set(shapes)
    for _ in range(3):
        shapes={s|{p} for s in shapes for q in s for d in D
                if (p:=add(q,d)) not in s and 21<=p[0]<=26 and 0<=p[1]<=6 and 8<=p[2]<=13 and g_allowed(p)}
        all_shapes.update(shapes)
    shapes=sorted(all_shapes,key=lambda s:(len(s),sorted(s))); counts=Counter();leads=[];tested=0;complete=True
    # Calibration: the accepted connector and pulse primitive must remain in scope.
    control=roots|{(23,4,10),(24,4,10),(24,4,11)}
    assert frozenset(control) in shapes,'known G1 glue fixture lost from domain'
    def pulse_ok(o,d,hp,hs,hglue):
        return all(not (near(move(hs,'wwmmm',t),add(move(o,'mmwwm',t),d)) and
                        add(move(o,'mmwwm',t),d) in {move(p,'wwmmm',t) for p in hglue}) for t in [1,2])
    assert pulse_ok((25,4,11),(0,-1,0),(25,3,11),(25,3,10),{(25,3,11)})
    for shape in shapes:
      if time.monotonic()-start>a.seconds:complete=False;break
      observer_options={add(g,d) for g in shape for d in D}-set(shape)-fixed
      for ty in [2,3,4]:
       ts=(22,ty,11)
       if ts in shape:continue
       for off in STICKY:
        rb=add((24,ty,11),off)
        if rb in fixed|set(shape)|{ts}:continue
        if any(near(move(g,'mmwwm',t),rb) for g in shape for t in [0,1]):counts['waiting_RB_pickup']+=1;continue
        column_sources={rb}
        if a.split_column_power:
            column_sources={add(add(add(g,d),(2,0,0)),off) for g in shape for d in D for off in NORMAL}
        for crb in sorted(column_sources):
         if time.monotonic()-start>a.seconds:complete=False;break
         if crb!=rb and (crb in fixed|set(shape)|{ts} or any(near(move(g,'mmwwm',t),crb) for g in shape for t in [0,1])):continue
         early=[add(crb,(-2-d[0],-d[1],-d[2])) for d in NORMAL]
         late=[add(rb,(-1-d[0],-d[1],-d[2])) for d in NORMAL]
         for pair in itertools.combinations(early,2):
          if not all(any(near(p,g) for g in shape) for p in pair):continue
          for last in late:
           tested+=1;actor_cells={*pair,last,add(last,(1,0,0))}
           if len(actor_cells)!=4 or actor_cells & (fixed|set(shape)|{rb,crb,ts}):counts['initial_overlap']+=1;continue
           if not any(near(last,move(g,'mmwwm',1)) for g in shape):counts['late_pickup_missing']+=1;continue
           targets={add(p,(3,0,0)) for p in pair}|{add(last,(2,0,0))}
           for y in [2,3,4]:
            hs=(25,y,10)
            if hs in fixed|set(shape)|actor_cells|{rb,crb,ts}:continue
            for hd in STICKY:
             hp=add(hs,hd);hglue=targets|{hp}
             if hglue & (fixed|set(shape)|actor_cells|{rb,crb,ts,hs}):continue
             for d in D:
              o=add(hp,tuple(-v for v in d))
              if o not in observer_options or o in actor_cells|hglue|{hs,rb,crb,ts}:continue
              if not pulse_ok(o,d,hp,hs,hglue):continue
              good=[]
              for first,second in [pair,pair[::-1]]:
               actors=[(first,'mmwwm'),(second,'mmmww'),(last,'wmmmw')]
               valid=True
               for t in range(5):
                gp={move(p,'mmwwm',t) for p in shape}|{move(o,'mmwwm',t),move(ts,'mmwwm',t)}
                hh={move(p,'wwmmm',t) for p in hglue}|{move(rb,'wwmmm',t),move(crb,'wwmmm',t),move(hs,'wwmmm',t)}
                ps=[move(p,w,t) for p,w in actors]
                foreign={move(p,w,t) for p,w in fixed_glue}
                if gp & hh or hh & foreign or any(p in gp|hh|foreign for p in ps) or len(set(ps))!=3:valid=False;break
               if valid:good.append({'first':first,'second':second,'late':last})
              if not good:counts['dynamic_overlap']+=1;continue
              leads.append({'G1_glue':sorted(shape),'T1_sticky':ts,'H1_RB':rb,'H1_column_RB':crb,'added_H1_power_blocks':int(crb!=rb),'H1_sticky':hs,
                            'H1_power_glue':hp,'H1_required_glue':sorted(hglue),'observer':o,'observer_direction':D.index(d),
                            'normal_assignments':good,'optimistic_G1_mass':len(shape)+3,'G1_slot1_with_three_riders':len(shape)+6})
              if len(leads)>=a.max_leads:complete=False;break
             if len(leads)>=a.max_leads:break
           if len(leads)>=a.max_leads:break
          if len(leads)>=a.max_leads:break
         if len(leads)>=a.max_leads:break
        if len(leads)>=a.max_leads:break
       if len(leads)>=a.max_leads:break
      if len(leads)>=a.max_leads:break
    report={'scope':__doc__,'complete':complete,'elapsed_seconds':time.monotonic()-start,'G1_shapes':len(shapes),
            'tested_supported_triples':tested,'rejections':dict(counts),'leads':leads,'control_in_domain':True,'split_column_power':a.split_column_power,
            'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.base/'before_natural.json',Path(__file__)]}}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['leads','sha256']}));print(f'Geometric leads: {len(leads)}; not verified hardware')

if __name__=='__main__':main()
