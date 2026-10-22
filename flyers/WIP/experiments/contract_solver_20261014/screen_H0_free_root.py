"""Root-free dual-RB H0 necessary geometry bound on verified71; not physical acceptance."""
import argparse, collections, hashlib, itertools, json, time
from pathlib import Path
from assemble import Flyer, body_of
from fastflyer import Kind
from search_T1_two_pushes import D, add, adj, dist
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum
HERE=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--out',default='H0_free_root_preflight');ap.add_argument('--passenger-sweeps',action='store_true');a=ap.parse_args();start=time.monotonic()
 base=HERE/'out/quarter_ring_contacts/T1_sticky_on_G1_transfer';out=HERE/'out/quarter_ring_contacts'/a.out;out.mkdir(exist_ok=False)
 f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']}
 budget_path=HERE/'out/quarter_ring_contacts/H0_free_root_budget/full39.json';budget=json.loads(budget_path.read_text(encoding='utf-8'))
 fixed=set(f._cells)-body_of(f._cells,tuple(ports['H0_front']['at']))
 others=[(name,body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for name,p in ports.items() if name!='H0_front'];supports={}
 for act in budget['actions']:
  if act['target']!='H0':continue
  ext=next(p for p in act['contacts'] if p['body'] in ['G0','T1'] and p['carries_at']);name='T1_front' if ext['body']=='T1' else 'G0';shape=body_of(f._cells,tuple(ports[name]['at']));support=None
  for t in ext['carries_at']:
   dx=budget['words'][ext['body']][:t].count('m')-act['piston_word'][:t].count('m');choices={n for q in shape for n in adj(add(q,(dx,0,0)))};support=choices if support is None else support&choices
  supports[act['slot']]=support
 sweep_path=HERE/'out/quarter_ring_contacts/H0_passenger_sweeps/report.json';sweeps=json.loads(sweep_path.read_text(encoding='utf-8'))['records'] if a.passenger_sweeps else [];words=['wwmmm','mwwmm','wmmmw'];counts=collections.Counter();records=[];seen=set();complete=True
 for m0 in sorted(supports[0]-fixed):
  for d0 in D[2:]:
   B=add(m0,tuple(-v for v in d0))
   for d1 in D[2:]:
    if d1==d0:continue
    m1=add(B,d1)
    if m1 not in supports[1]-fixed or m1<m0:continue
    for m4 in sorted(supports[4]-fixed):
     for d4 in D[2:]:
      if time.monotonic()-start>a.seconds:complete=False;break
      B4=add(add(m4,(1,0,0)),tuple(-v for v in d4));head=add(m4,(1,0,0));hardware={B,B4,m0,m1,m4,head};pins={add(m0,(1,0,0)),add(m1,(1,0,0)),add(m4,(2,0,0))};key=(B,B4,m0,m1,m4)
      if key in seen:continue
      seen.add(key)
      if len(hardware)!=6 or hardware&fixed or hardware&pins or pins&fixed:counts['occupied']+=1;continue
      collision=next((r for motor,word in zip([m0,m1,m4],words) for r in sweeps if word[r['slot']]=='w' and tuple(r['to'])==add(motor,(word[:r['slot']].count('m'),0,0))),None)
      if collision:counts['parent_passenger_collision']+=1;continue
      if any(dist(x,y)>7 for x in pins for y in pins):counts['terminal_diameter']+=1;continue
      # Any <=8-node connected body has <=7-edge paths between every cell and pin.
      ranges=[range(max(p[i] for p in pins)-7,min(p[i] for p in pins)+8) for i in range(3)]
      domain={q for q in itertools.product(*ranges) if q not in fixed|hardware and all(dist(q,p)<=7 for p in pins) and all(dist(x,q)+dist(q,y)+dist(x,y)<=14 for x in pins for y in pins)}
      groups=[{p} for p in sorted(pins)]+[set(adj(B)),set(adj(B4))]
      raw=connected_glue_minimum(domain,groups)
      if raw is None or raw>8:counts['raw_glue_bound']+=1;continue
      for mat in [Kind.HONEY,Kind.SLIME]:
       cells={q for q in domain if not any(any(dist(add(q,(k,0,0)),v)<=(1 if mat==kind else 0) for k in offsets('mmwwm',word) for v in shape) for _,shape,kind,word in others)}
       minimum=connected_glue_minimum(cells,groups);status='survivor' if minimum is not None and minimum<=8 else 'phase_glue_bound';counts[status]+=1
       records.append({'RBs':[B,B4],'motors':[m0,m1,m4],'head':head,'pins':sorted(pins),'material':mat.name,'raw_minimum':raw,'minimum':minimum,'cap':8,'domain_cells':len(cells),'status':status})
     if not complete:break
    if not complete:break
   if not complete:break
  if not complete:break
 result={'scope':__doc__+' H0 permanent10=8glue+2RB; no mandatory rear or placeholder root. Fixed interbody phases retained. Other hardware pickup/power omitted.','passenger_sweeps':a.passenger_sweeps,'sweep_sha256':hashlib.sha256(sweep_path.read_bytes()).hexdigest() if a.passenger_sweeps else None,'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'records':records,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'budget_sha256':hashlib.sha256(budget_path.read_bytes()).hexdigest()}
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'complete':complete,'seconds':result['seconds'],'counts':dict(counts),'survivors':[r for r in records if r['status']=='survivor'][:8]}))
if __name__=='__main__':main()
