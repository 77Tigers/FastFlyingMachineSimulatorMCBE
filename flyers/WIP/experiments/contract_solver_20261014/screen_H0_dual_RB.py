"""Bounded dual-RB H0 source preflight on fixed verified70 geometry; no native acceptance."""
import argparse,collections,itertools,json,time,hashlib
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Kind
from search_T1_two_pushes import D,add,adj,dist
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum
HERE=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=60);a=ap.parse_args();start=time.monotonic();base=HERE/'out/quarter_ring_contacts/joint_T1_self_RB_shifted_search/case5167';out=HERE/'out/quarter_ring_contacts/H0_dual_RB_preflight';out.mkdir(exist_ok=False)
 f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={q['name']:q for q in c['ports']};parent=HERE/'out/quarter_ring_contacts/H0_front_source_budget/full39.json';budget=json.loads(parent.read_text(encoding='utf-8'));root=tuple(ports['H0_front']['at']);fixed=set(f._cells)-body_of(f._cells,root);others=[(name,body_of(f._cells,tuple(q['at'])),f._cells[tuple(q['at'])].kind,q['word']) for name,q in ports.items() if name!='H0_front'];supports={}
 for act in budget['actions']:
  if act['target']!='H0':continue
  ext=next(q for q in act['contacts'] if q['body'] in ['G0','T1'] and q['carries_at']);name='T1_front' if ext['body']=='T1' else 'G0';shape=body_of(f._cells,tuple(ports[name]['at']));support=None
  for t in ext['carries_at']:
   dx=budget['words'][ext['body']][:t].count('m')-act['piston_word'][:t].count('m');choices={n for q in shape for n in adj(add(q,(dx,0,0)))};support=choices if support is None else support&choices
  supports[act['slot']]=support
 records=[];seen=set();counts=collections.Counter();domain=list(itertools.product(range(14,24),range(-1,8),range(10,19)));complete=True
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
      B4=add(add(m4,(1,0,0)),tuple(-v for v in d4));head=add(m4,(1,0,0));hardware={B,B4,m0,m1,m4,head};pins={root,add(m0,(1,0,0)),add(m1,(1,0,0)),add(m4,(2,0,0))};key=(B,B4,m0,m1,m4)
      if key in seen:continue
      seen.add(key);rec={'RBs':[B,B4],'motors':[m0,m1,m4],'head':head,'pins':sorted(pins)}
      if len(hardware)!=6 or hardware&fixed or hardware&pins or (pins-{root})&fixed:counts['occupied']+=1;continue
      if any(dist(x,y)>6 for x in pins for y in pins):counts['terminal_diameter']+=1;continue
      for mat in [Kind.HONEY,Kind.SLIME]:
       cells={q for q in domain if q not in fixed|hardware and all(dist(root,q)+dist(q,t)+dist(root,t)<=12 for t in pins)}
       cells={q for q in cells if not any(any(dist(add(q,(k,0,0)),v)<=(1 if mat==kind else 0) for k in offsets('mmwwm',w) for v in sh) for _,sh,kind,w in others)}
       groups=[{q} for q in pins]+[set(adj(B)),set(adj(B4))];minimum=connected_glue_minimum(cells,groups);status='survivor' if minimum is not None and minimum<=7 else 'glue_bound';counts[status]+=1;records.append({**rec,'material':mat.name,'minimum':minimum,'cap':7,'domain_cells':len(cells),'status':status})
     if not complete:break
    if not complete:break
   if not complete:break
  if not complete:break
 result={'scope':__doc__+' Full39 H0 permanent9 reallocated from8glue+RB1 to7glue+RB2. Support sets and fixed interbody phases retained; other hardware pickup/power omitted. Bounds local to this grammar.','complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'records':records,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()};(out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());budget['source_allocation']['H0']={'total_glue_cap':7,'RB':2,'mass':9,'change':'two independent power sites, no mass or carrier change'};budget['scope']='Dual-RB H0 source budget only; power/layout unbuilt. All39 roles and loads unchanged.';assert max(v for ds in budget['loads'].values() for v in ds.values())==12;(out/'full39_budget.json').write_text(json.dumps(budget,indent=2)+'\n',encoding='utf-8');print(json.dumps({'complete':complete,'seconds':result['seconds'],'counts':dict(counts),'survivors':[r for r in records if r['status']=='survivor'][:8]}))
if __name__=='__main__':main()
