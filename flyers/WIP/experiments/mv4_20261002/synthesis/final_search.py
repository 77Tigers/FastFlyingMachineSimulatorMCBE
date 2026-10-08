"""Final mv4 experiment: one wall-clock-bounded search, then verification.
Run: python final_search.py [search_seconds=2700]
No candidates above encoded PL49, no simulator/editor changes, no subagents.
"""
import json,random,time,subprocess,collections,sys,math,traceback
from pathlib import Path
import six,search,final_router
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
    from fastflyer.research import binary
    return binary(n)
OUT=search.OUT.parent/'final_experiment_20261003';OUT.mkdir(exist_ok=True)
LIMIT=min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 2700)
started=time.monotonic();deadline=started+LIMIT
baseline=json.loads((search.OUT.parent/'contacts/compact/six_bank.json').read_text())['best']
prior=json.loads((search.OUT/'quick_six/results.json').read_text())['records']
parents=[(baseline['centers'],[r for r,m in baseline['orientations']],[-1 if m else 1 for r,m in baseline['orientations']])]
parents += [(r['centers'],parents[0][1],parents[0][2]) for r in prior if r['failure'][0]=='route']
stats=collections.Counter();bestscore=None;bestmeta=None;winner=None;last_progress=0
runner=search.ROOT/'target/release/fastflyer-research.exe'
audit=_tb('mv4-audit-fast')
def checkpoint(status,**extra):
 record=dict(status=status,search_limit_seconds=LIMIT,elapsed_seconds=round(time.monotonic()-started,1),statistics=stats,best=bestmeta,**extra)
 temp=OUT/'status.tmp';temp.write_text(json.dumps(record,indent=2));temp.replace(OUT/'status.json')

def placement(seed):
 rng=random.Random(900000+seed)
 if seed<len(parents):return parents[seed]
 if seed%4!=0:
  p=rng.choice(parents);centers=[list(q) for q in p[0]];rot=list(p[1]);ref=list(p[2])
  for j in rng.sample(range(6),1+seed%3):
   centers[j][0]+=rng.choice((-2,-1,0,1,2));centers[j][1]+=rng.choice((-2,-1,0,1,2))
  if seed%3==0:
   j=rng.randrange(6);rot[j]=rng.randrange(4);ref[j]=rng.choice((-1,1))
 else:
  radius=rng.choice((3,4,5));centers=[(round(radius*math.cos(j*math.pi/3))+rng.randrange(-1,2),round(radius*math.sin(j*math.pi/3))+rng.randrange(-1,2)) for j in range(6)]
  rot=[rng.randrange(4) for _ in range(6)];ref=[rng.choice((-1,1)) for _ in range(6)]
 return centers,rot,ref

try:
 checkpoint('searching')
 for seed in range(100000):
  if time.monotonic()>=deadline:break
  p=placement(seed);report={}
  # A few equivalent interface choices; new port faces retain the same
  # movement phases and X obligations checked by the competition contract.
  if seed%5==0:
   six.OWN=((1,1),(-1,1),(-1,1),(1,1));six.PREVIOUS=((2,0),(-2,0),(0,2),(2,0))
  else:
   six.OWN=((1,1),(-2,0),(1,1),(1,1));six.PREVIOUS=((2,0),(-1,1),(-1,1),(2,0))
  def joint(mandatory,fixed,bounds,cap,rng):
   stats['routing_attempts']+=1
   return final_router.route(mandatory,fixed,bounds,cap,rng,min(deadline,time.monotonic()+20),report)
  ans,why=six.build(seed,p,cap=39,joint_router=joint)
  stats['placements']+=1;stats['routed' if ans else why[0]]+=1
  if report.get('best') is not None:
   score=tuple(report['best'])
   if bestscore is None or score<bestscore:
    bestscore=score;bestmeta=dict(seed=seed,score=score,placement=p,report=report,own=six.OWN,previous=six.PREVIOUS)
    (OUT/'best_routing.json').write_text(json.dumps(bestmeta,indent=2))
    if p not in parents:parents.append(p)
    if len(parents)>16:parents.pop(5)
  if ans:
   f,m=ans;f.push_limit=49;candidate=OUT/f'candidate_s{seed}_pl49.flyer';f.save(candidate)
   (OUT/f'candidate_s{seed}.json').write_text(json.dumps(m,indent=2))
   remaining=max(1,deadline-time.monotonic())
   trial=subprocess.run([str(runner),'audit',str(candidate),'300','12'],capture_output=True,text=True,timeout=remaining)
   result=trial.stdout+trial.stderr;(OUT/f'candidate_s{seed}.screen.txt').write_text(result)
   stats['screened']+=1
   if 'distance=100 ' in result and 'movement_failures=0' in result and 'conservation_mismatch_ticks=0' in result:
    shortcsv=OUT/f'candidate_s{seed}.short80.csv'
    trial=subprocess.run([str(audit),str(candidate),'120',str(shortcsv)],capture_output=True,text=True,timeout=max(1,deadline-time.monotonic()))
    (OUT/f'candidate_s{seed}.short80.txt').write_text(trial.stdout+trial.stderr)
    if trial.returncode==0:winner=candidate;break
   elif 'distance=' in result:
    # Keep every near miss; do not silently discard >30-block runs.
    import re
    d=re.search(r'\bdistance=(-?\d+)',result)
    if d and int(d.group(1))>30:stats['near_misses_over30']+=1
  if time.monotonic()-last_progress>30:
   checkpoint('searching');print(json.dumps(dict(elapsed=round(time.monotonic()-started),stats=stats,best=bestscore)),flush=True);last_progress=time.monotonic()
 if winner:
  checkpoint('validating',candidate=str(winner))
  full=subprocess.run([str(runner),'audit',str(winner),'10000','12'],capture_output=True,text=True,timeout=600)
  (OUT/'winner.audit10000.txt').write_text(full.stdout+full.stderr)
  full80=subprocess.run([str(audit),str(winner),'10000',str(OUT/'winner.fast_full80.csv')],capture_output=True,text=True,timeout=900)
  (OUT/'winner.fast_full80.txt').write_text(full80.stdout+full80.stderr)
  good=full.returncode==0 and 'movement_failures=0' in full.stdout and 'conservation_mismatch_ticks=0' in full.stdout and full80.returncode==0
  if good:
   from fastflyer import Flyer
   final=OUT/'mv4_pl49.flyer';Flyer.load(winner).save(final)
   checkpoint('verified',candidate=str(final),full80_pass=True)
  else:checkpoint('validation_failed',candidate=str(winner))
 else:checkpoint('finished_no_candidate')
except subprocess.TimeoutExpired:
 checkpoint('time_limit_reached',candidate=str(winner) if winner else None)
except Exception:
 (OUT/'error.txt').write_text(traceback.format_exc());checkpoint('error');raise
print((OUT/'status.json').read_text(),flush=True)
