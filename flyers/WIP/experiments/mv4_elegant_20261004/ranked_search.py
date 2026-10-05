"""Survey-ranked symmetric layouts; lower cell caps, fixed bounded deadline.

Usage: python ranked_search.py [seconds=420]. Reuses the cheap interface survey,
deduplicates placements, and negotiates conflicts with an opposite copy as well.
No candidate above PL48; local corrected core checker screens real simulation.
"""
import sys,time,json,random,collections,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'mv4_20261002/synthesis'))
import six
sys.path.insert(0,str(HERE))
import paired_router
start=time.monotonic();deadline=start+min(600,int(sys.argv[1]) if len(sys.argv)>1 else 420)
pool=json.loads((HERE/'survey.json').read_text())['ranked']; seen=set();unique=[]
for p in pool:
    key=json.dumps([p['placement'],p['own'],p['previous']])
    if key not in seen:seen.add(key);unique.append(p)
stats=collections.Counter();best=None;records=[]
for attempt in range(10000):
    if time.monotonic()>=deadline:break
    parent=unique[attempt%len(unique)];report={}
    six.OWN=parent['own'];six.PREVIOUS=parent['previous']
    cap=(36,37,38)[(attempt//len(unique))%3]
    def joint(must,fixed,bounds,cap,rng):
        return paired_router.route(must,fixed,bounds,cap,rng,min(deadline,time.monotonic()+8),report)
    ans,why=six.build(50000+attempt,parent['placement'],cap=cap,joint_router=joint)
    stats['attempts']+=1;stats['routed' if ans else why[0]]+=1
    if report.get('best') is not None:
        score=report['best']
        if best is None or tuple(score)<tuple(best['score']):
            best=dict(attempt=attempt,score=score,cap=cap,parent=parent,report=report)
    if ans:
        f,m=ans;f.push_limit=48;path=HERE/f'ranked_a{attempt}_pl48.flyer';f.save(path)
        m.update(parent=parent,cap=cap)
        (HERE/f'ranked_a{attempt}.json').write_text(json.dumps(m,indent=2))
        trial=subprocess.run([str(HERE/'audit_cores.exe'),str(path),'300',str(HERE/f'ranked_a{attempt}.short80.csv')],
                             capture_output=True,text=True,timeout=max(1,deadline-time.monotonic()))
        (HERE/f'ranked_a{attempt}.short80.txt').write_text(trial.stdout+trial.stderr)
        stats['short80_pass' if trial.returncode==0 else 'short80_fail']+=1
        records.append(dict(attempt=attempt,path=str(path),counts=m['counts'],pass80=trial.returncode==0))
    state=dict(elapsed_seconds=round(time.monotonic()-start,1),statistics=stats,
               unique_placements=len(unique),best=best,candidates=records,status='searching')
    (HERE/'ranked_status.json').write_text(json.dumps(state,indent=2))
state['status']='completed';(HERE/'ranked_status.json').write_text(json.dumps(state,indent=2))
print(json.dumps(dict(elapsed=state['elapsed_seconds'],stats=stats,unique=len(unique),candidates=records)),flush=True)
