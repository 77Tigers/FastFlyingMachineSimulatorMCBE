"""Necessary joint T2/G2 geometry screen for a budgeted T2 observer pull.

Use a selected regenerated T2 own column and retain the X2 puller. Free T2 glue (<=6),
G2 three normals and one extra column RB. Either RB may power each normal;
G2 old RB still powers X2.
Select a G2 sticky on a T2 target plus T2-carried observer. G2 glue
connectivity, arms, full power and foreign glue contacts are not certified.
A lead is only a candidate for native construction, never a complete flyer.
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
    ap.add_argument('--own-columns',type=Path,required=True);ap.add_argument('--own-index',type=int,required=True);
    ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--max-leads',type=int,default=24)
    ap.add_argument('--split-column-power',action='store_true',default=True,help='One extra G2 column RB is allowed')
    a=ap.parse_args();start=time.monotonic();f=Flyer.load(a.base/'problem.flyer')
    freed={(21,4,13),(21,4,14),(21,5,13),(21,6,13),(22,5,13),(21,7,13),(22,7,13),(25,6,12),(25,5,12),(25,7,12),(25,6,13),(22,5,12),(22,7,12),(23,6,13),(24,6,13)}
    own=json.loads(a.own_columns.read_text(encoding='utf-8'))['leads'][a.own_index]
    freed|={(20,4,13),(20,5,13),(19,4,14),(20,4,14)}
    fixed=set(f._cells)-freed-{(24,6,12),(21,6,12)}
    fixed|={tuple(own['first']),tuple(own['late']),add(tuple(own['late']),(1,0,0)),tuple(own['RB'])}
    roots=set(map(tuple,own['T2_glue']))
    assert not roots&fixed
    contract=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    fixed_glue=[]
    for port in contract['ports']:
        if port['name'] not in ['X0','T0','X1','T1','X2','G1_power','H1_power']:continue
        root=tuple(port['at']);kind=f._cells[root].kind;seen={root}
        while True:
            expanded=seen|{add(p,d) for p in seen for d in D if add(p,d) in f._cells and f._cells[add(p,d)].kind==kind}
            if expanded==seen:break
            seen=expanded
        fixed_glue.extend((p,port['word']) for p in seen)
    def g_allowed(p):
        return p not in fixed and all(move(p,'mmwwm',t)!=move(q,w,t) for q,w in fixed_glue for t in range(5))
    shapes={frozenset(roots)};all_shapes=set(shapes)
    for _ in range(6-len(roots)):
        shapes={s|{p} for s in shapes for q in s for d in D
                if (p:=add(q,d)) not in s and 21<=p[0]<=25 and 3<=p[1]<=8 and 11<=p[2]<=15 and g_allowed(p)}
        all_shapes.update(shapes)
    shapes=sorted(all_shapes,key=lambda s:(len(s),sorted(s))); counts=Counter();leads=[];tested=0;complete=True
    # The old seven-cell T2 shape exceeds the six-cell observer budget.
    # Four retained targets form a connected calibration root; every generated
    # shape is connected by construction. Acceptance remains a native check.
    assert frozenset(roots) in shapes
    # Positive calibration of the same phase-prefix overlap/pickup model:
    # the independently verified seven-glue G2 column has no new observer.
    fixture={(21,4,13),(21,4,14),(21,5,13),(21,6,13),(22,5,13),(21,7,13),(22,7,13)}
    fp=[((22,5,12),'mmwwm'),((22,7,12),'mmmww'),((23,6,13),'wmmmw')]
    fh={(25,6,12),(25,5,12),(25,7,12),(25,6,13),(24,6,12)}
    assert all(any(near(p,g) for g in fixture) for p,w in fp[:2])
    assert any(near(fp[2][0],move(g,'mmwwm',1)) for g in fixture)
    for t in range(5):
        gp={move(p,'mmwwm',t) for p in fixture|{(21,6,12)}}
        hp={move(p,'wwmmm',t) for p in fh}
        ps=[move(p,w,t) for p,w in fp]
        assert not gp&hp and len(set(ps))==3
        assert all(p not in gp|hp for p in ps)
    # Pull contact includes relative phase prefixes, not merely two cells.
    def pull_base(q,target_word,carrier_word,slot):
        return add(q,(target_word[:slot].count('m')+2-carrier_word[:slot].count('m'),0,0))
    assert pull_base((22,4,10),'mmwwm','wwmmm',1)==(25,4,10)  # accepted G1/H1
    assert pull_base((19,6,12),'wmmmw','mmwwm',3)==(21,6,12)  # accepted X2/T2
    assert pull_base((22,5,13),'mmwwm','wwmmm',1)==(25,5,13)  # actual T2 pull
    def pulse_ok(o,d,hp,hs,hglue):
        return all(not (near(move(hs,'wwmmm',t),add(move(o,'mmwwm',t),d)) and
                        add(move(o,'mmwwm',t),d) in {move(p,'wwmmm',t) for p in hglue}) for t in [1,2])
    for shape in shapes:
      if time.monotonic()-start>a.seconds:complete=False;break
      observer_options={add(g,d) for g in shape for d in D}-set(shape)-fixed
      for ty in [0]:
       ts=(21,6,12)
       if ts in shape:continue
       for off in [(0,0,0)]:
        rb=(24,6,12)
        if rb in set(shape)|{ts}:continue
        if any(near(move(g,'mmwwm',t),rb) for g in shape for t in [0,1]):counts['waiting_RB_pickup']+=1;continue
        column_sources={rb}
        if a.split_column_power:
            column_sources={add(add(add(g,d),(2,0,0)),off) for g in shape for d in D for off in NORMAL}
        for crb in sorted(column_sources):
         if time.monotonic()-start>a.seconds:complete=False;break
         if crb!=rb and (crb in fixed|set(shape)|{ts} or any(near(move(g,'mmwwm',t),crb) for g in shape for t in [0,1])):continue
         early=sorted({add(r,(-2-d[0],-d[1],-d[2])) for r in {rb,crb} for d in NORMAL})
         late=sorted({add(r,(-1-d[0],-d[1],-d[2])) for r in {rb,crb} for d in NORMAL})
         for pair in itertools.combinations(early,2):
          if not all(any(near(p,g) for g in shape) for p in pair):continue
          for last in late:
           tested+=1;actor_cells={*pair,last,add(last,(1,0,0))}
           if len(actor_cells)!=4 or actor_cells & (fixed|set(shape)|{rb,crb,ts}):counts['initial_overlap']+=1;continue
           if not any(near(last,move(g,'mmwwm',1)) for g in shape):counts['late_pickup_missing']+=1;continue
           targets={add(p,(3,0,0)) for p in pair}|{add(last,(2,0,0))}
           for contact in sorted(shape):
            hs=pull_base(contact,'mmwwm','wwmmm',1)
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
              leads.append({'T2_glue':sorted(shape),'X2_sticky':ts,'G2_RB':rb,'G2_column_RB':crb,'added_G2_power_blocks':int(crb!=rb),'G2_sticky':hs,
                            'G2_power_glue':hp,'G2_required_glue':sorted(hglue),'observer':o,'observer_direction':D.index(d),
                            'normal_assignments':good,'optimistic_T2_mass':len(shape)+3,'T2_slot1_with_three_riders':len(shape)+6})
              if len(leads)>=a.max_leads:complete=False;break
             if len(leads)>=a.max_leads:break
           if len(leads)>=a.max_leads:break
          if len(leads)>=a.max_leads:break
         if len(leads)>=a.max_leads:break
        if len(leads)>=a.max_leads:break
       if len(leads)>=a.max_leads:break
      if len(leads)>=a.max_leads:break
    report={'scope':__doc__,'complete':complete,'elapsed_seconds':time.monotonic()-start,'T2_shapes':len(shapes),
            'tested_supported_triples':tested,'rejections':dict(counts),'leads':leads,'control_in_domain':True,'split_column_power':a.split_column_power,
            'positive_G2_phase_fixture':True,'selected_T2_own_column':own,'own_index':a.own_index,
            'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.base/'before_natural.json',a.own_columns,Path(__file__)]}}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['leads','sha256']}));print(f'Geometric leads: {len(leads)}; not verified hardware')

if __name__=='__main__':main()
