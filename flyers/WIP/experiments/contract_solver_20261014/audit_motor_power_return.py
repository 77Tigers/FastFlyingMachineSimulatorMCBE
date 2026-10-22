"""Identity and power-stage audit over native traces; diagnostics, never acceptance."""
import argparse,json
from pathlib import Path
from search_T1_two_pushes import D,add

def power_sources(state,p):
 b=state[p]
 if b&16:return []
 hard={}
 for q,v in state.items():
  if v&16:continue
  if v&15==8 or (v&15==7 and v&256):
   target=add(q,D[(v>>5)&7]);cell=state.get(target,0)
   if not cell&16 and cell&15 in [1,2,3,5]:hard.setdefault(target,[]).append(q)
 out=[]
 for i,d in enumerate(D):
  if i==(b>>5)&7:continue
  q=add(p,d);v=state.get(q,0)
  for src in hard.get(q,[]):out.append({'source':src,'via':q})
  if v&16:continue
  if v&15 in [6,8] or (v&15==7 and v&256 and add(q,D[(v>>5)&7])==p):out.append({'source':q,'via':None})
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--trace',default='trace_failure_0_0_7.jsonl');a=ap.parse_args();prep=json.loads((a.run/'preparation.json').read_text(encoding='utf-8'));delta=prep['normalization_delta'];motors=[add(tuple(p),tuple(delta)) for p in prep['source_record']['motors']];labels={p:f'M{i}' for i,p in enumerate(motors)}
 rows=[json.loads(line) for line in (a.run/a.trace).read_text(encoding='utf-8').splitlines()];origins={tuple(c[:3]):tuple(c[:3]) for c in rows[0]['trace']['initial'] if c[3]&15!=10};ports={tuple(p['at']):p['name'] for p in json.loads((a.run/'before_natural.json').read_text(encoding='utf-8'))['ports']};report=[]
 for row in rows:
  if row['tick']>=20:break
  state={tuple(c[:3]):c[3] for c in row['trace']['initial']};inverse={origin:q for q,origin in origins.items()};snapshot={}
  for origin,label in labels.items():
   q=inverse[origin];v=state[q];snapshot[label]={'at':q,'state':v>>10&3,'moving':bool(v&16),'angry':bool(v&512),'sources':power_sources(state,q),'events':[]}
  pulses=[{'at':q,'powered':bool(v&256),'moving':bool(v&16)} for q,v in state.items() if v&15==7 and (prep.get('pulse_observer') is not None and origins.get(q)==add(tuple(prep['pulse_observer']),tuple(delta)))]
  for step in row['trace']['steps']:
   actor=tuple(step['active_piston']) if step.get('active_piston') is not None else None;origin=origins.get(actor)
   if origin in labels:snapshot[labels[origin]]['events'].append({'action':step['action'],'at':actor})
   move=step.get('movement') or {};src=list(map(tuple,move.get('sources',[])));dst=list(map(tuple,move.get('destinations',[])))
   if not move.get('failure') and src and dst:
    assert len(src)==len(dst);names=sorted({ports[origins[q]] for q in src if origins.get(q) in ports});updates={d:origins[q] for q,d in zip(src,dst) if q in origins}
    for q,d in zip(src,dst):
     if origins.get(q) in labels:snapshot[labels[origins[q]]]['events'].append({'carried_by':names,'from':q,'to':d})
    for q in src:origins.pop(q,None)
    origins.update(updates)
  report.append({'tick':row['tick'],'motors':snapshot,'own_observer':pulses})
 out={'scope':__doc__+' Power sources are a read-only transcription of src/sim.rs power_stage; the action and carrier events come from the native simulator. Single sample only.','origin_labels':{v:k for k,v in labels.items()},'ticks':report};(a.run/'motor_power_return_audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print(json.dumps([{'tick':r['tick'],'motors':{k:{'at':v['at'],'state':v['state'],'powered':bool(v['sources']),'events':v['events']} for k,v in r['motors'].items()}} for r in report if r['tick']%2==0]))
if __name__=='__main__':main()
