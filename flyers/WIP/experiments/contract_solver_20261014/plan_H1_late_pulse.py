"""Bound a shared H1 pulse source for pushes3/4 with fixed first-source core.

Optimistic necessary geometry only: no native acceptance, no complete flyer.
At permanent9, H1 can carry six glue, its existing stone and two observers.
"""
import collections,itertools,json,time,hashlib
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from search_T1_two_pushes import D,add,adj,dist
from model_recovery_layout import connectivity
HERE=Path(__file__).resolve().parent
def main():
 start=time.monotonic();base=HERE/'out/quarter_ring_contacts/H1_first_front_pulse_hard';out=HERE/'out/quarter_ring_contacts/H1_late_pulse_bound';out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};old=body_of(f._cells,tuple(ports['H1_power']['at']));h=body_of(f._cells,tuple(ports['H0_front']['at']));fixed=set(f._cells)-old;root=tuple(ports['H1_power']['at']);count=collections.Counter();records=[];cap=9;complete=True
 s3={q for p in h for q in adj(p)}-set(f._cells);s4={q for p in h for q in adj(add(p,(1,0,0)))}-set(f._cells)
 for q3,q4 in itertools.product(sorted(s3),sorted(s4)):
  if time.monotonic()-start>55:complete=False;break
  if q4==add(q3,(1,0,0)):count['extended_motor_blocks_recovery0']+=1;continue
  # A+H1_prefix is a hard target adjacent to the actor, excluding its front.
  hard3={add(add(q3,(2,0,0)),d) for d in D if d!=(1,0,0)}
  hard4={add(add(q4,(1,0,0)),d) for d in D if d!=(1,0,0)}
  for target in sorted(hard3&hard4):
   pins=old|{add(q3,(3,0,0)),add(q4,(2,0,0)),target};heads={q3,q4,add(q4,(1,0,0))}
   if len(heads)!=3 or pins&fixed or pins&heads or heads&set(f._cells):count['occupied']+=1;continue
   # A face-adjacent H1 observer powers this hard target on3/4.
   for direction,d in enumerate(D):
    obs=add(target,tuple(-v for v in d));hw=heads|{obs}
    if obs in set(f._cells)|pins or len(hw)!=4:continue
    if any(dist(x,y)>cap-1 for x in pins for y in pins):count['diameter']+=1;continue
    ranges=[range(max(q[k] for q in pins)-cap+1,min(q[k] for q in pins)+cap) for k in range(3)];domain={q for q in itertools.product(*ranges) if q not in fixed|hw and all(dist(q,p)<=cap-1 for p in pins)}
    domain-={add(q3,(k,0,0)) for k in [1,2]}|{add(q4,(1,0,0))}
    if not pins<=domain:count['motor_travel_conflict']+=1;continue
    model=cp_model.CpModel();v={q:model.NewBoolVar(str(q)) for q in domain}
    for q in pins:model.Add(v[q]==1)
    model.Add(sum(v.values())<=cap);model.Add(sum(v[q] for q in adj(obs) if q in v)>=1);connectivity(model,v,root,cap);model.Minimize(sum(v.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=.2;s.parameters.num_search_workers=2;status=s.Solve(model)
    record={'motors':[q3,q4],'hard_target':target,'observer':obs,'direction':direction,'status':s.StatusName(status),'lower_bound':s.BestObjectiveBound()}
    if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
     shape=sorted(q for q,b in v.items() if s.Value(b));record.update(glue=len(shape),shape=shape);count['within6' if len(shape)<=6 else 'over6']+=1
    else:count[s.StatusName(status)]+=1
    records.append(record)
 report={'scope':__doc__,'complete_bindings':complete,'seconds':time.monotonic()-start,'counts':dict(count),'records':records,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'complete':complete,'seconds':report['seconds'],'counts':dict(count),'best':min((r.get('glue',100) for r in records),default=None)}))
if __name__=='__main__':main()
