"""Bounded elegance feasibility session; repeatable half-turn six-bank families.

Usage: python search.py [seconds=1380]. Search and validation share one deadline.
Outputs rejected counts, best routings, candidate geometry and real-run evidence.
"""
import sys, time, json, random, collections, subprocess, itertools, traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent
SYNTH=HERE.parent/'mv4_20261002/synthesis'
sys.path.insert(0,str(SYNTH))
import six, final_router
sys.path.insert(0,str(HERE))
import paired_router_initial as paired_router
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from fastflyer.research import binary
    return binary(n)

ROOT=six.ROOT
RUNNER=ROOT/'target/release/fastflyer-research.exe'
AUDIT=_tb('mv4-audit-fast')
SECONDS=min(1800,int(sys.argv[1]) if len(sys.argv)>1 else 1380)
START=time.monotonic(); DEADLINE=START+SECONDS; SEARCH_END=DEADLINE-210
stats=collections.Counter(); best=None; winners=[]; records=[]; last=0

def checkpoint(status,**extra):
    data=dict(status=status,elapsed_seconds=round(time.monotonic()-START,1),limit_seconds=SECONDS,
              statistics=dict(stats),best=best,winners=winners,**extra)
    p=HERE/'status.tmp';p.write_text(json.dumps(data,indent=2));p.replace(HERE/'status.json')

def placement(seed):
    r=random.Random(240004+seed)
    # Exact rectangular/hexagonal rings, never independent coordinate jitter.
    a=r.choice((3,4,5,6,7)); b=r.choice((1,2,3,4)); c=r.choice((3,4,5,6,7))
    if seed%3==0:
        centers=[(a,c),(0,c),(-a,c),(-a,-c),(0,-c),(a,-c)]; family='rectangle'
    else:
        centers=[(a,0),(b,c),(-b,c),(-a,0),(-b,-c),(b,-c)]; family='hexagon'
    # First try simple repeated orientation rules, then all symmetric assignments.
    pattern=seed%6
    if pattern==0: rot=[0,0,0]; ref=[1,1,1]
    elif pattern==1: rot=[0,1,2]; ref=[1,1,1]
    elif pattern==2: rot=[0,0,0]; ref=[-1,-1,-1]
    else: rot=[r.randrange(4) for _ in range(3)]; ref=[r.choice((-1,1)) for _ in range(3)]
    return (centers,rot+[(q+2)%4 for q in rot],ref+ref),family

try:
    checkpoint('searching')
    for seed in range(1000000):
        if time.monotonic() >= SEARCH_END: break
        p,family=placement(seed); report={}
        # Both proven shared-hub interface choices are repeated identically.
        if seed%5==0:
            six.OWN=((1,1),(-1,1),(-1,1),(1,1));six.PREVIOUS=((2,0),(-2,0),(0,2),(2,0))
        else:
            six.OWN=((1,1),(-2,0),(1,1),(1,1));six.PREVIOUS=((2,0),(-1,1),(-1,1),(2,0))
        cap=39 if not winners else min(39,min(max(w['counts']) for w in winners)-1)
        rail=((-3,-2,1,None)[(seed//6)%4])
        def joint(mandatory,fixed,bounds,cap,rng):
            stats['routing_attempts']+=1
            return paired_router.route(mandatory,fixed,bounds,cap,rng,
                       min(SEARCH_END,time.monotonic()+12),report,rail)
        ans,why=six.build(seed,p,cap=cap,joint_router=joint)
        stats['placements']+=1; stats[family]+=1
        stats['routed' if ans else why[0]]+=1
        if report.get('best') is not None:
            score=tuple(report['best'])
            if best is None or score<tuple(best['score']):
                best=dict(seed=seed,score=score,placement=p,report=report,rail=rail,cap=cap,
                          own=six.OWN,previous=six.PREVIOUS)
                (HERE/'best_routing.json').write_text(json.dumps(best,indent=2))
        if ans:
            f,m=ans;f.push_limit=49;path=HERE/f'candidate_s{seed}_pl49.flyer';f.save(path)
            m.update(family=family,rail=rail,own=six.OWN,previous=six.PREVIOUS,
                     elegance='three exact opposite half-turn template pairs')
            (HERE/f'candidate_s{seed}.json').write_text(json.dumps(m,indent=2))
            trial=subprocess.run([str(AUDIT),str(path),'300',str(HERE/f'candidate_s{seed}.short80.csv')],
                      capture_output=True,text=True,timeout=max(1,SEARCH_END-time.monotonic()))
            (HERE/f'candidate_s{seed}.short80.txt').write_text(trial.stdout+trial.stderr)
            stats['screened']+=1
            if trial.returncode==0:
                stats['short80_pass']+=1
                winners.append(dict(seed=seed,path=str(path),counts=m['counts'],family=family,rail=rail))
            records.append(dict(seed=seed,counts=m['counts'],short80_pass=trial.returncode==0))
            (HERE/'candidates.json').write_text(json.dumps(records,indent=2))
        if time.monotonic()-last>=30:
            checkpoint('searching'); print(json.dumps(dict(elapsed=round(time.monotonic()-START),stats=stats,
                          best=None if best is None else best['score'],winners=len(winners))),flush=True);last=time.monotonic()
    if winners:
        win=min(winners,key=lambda w:(max(w['counts']),sum(w['counts'])))
        checkpoint('validating',selected=win)
        path=win['path']
        trial=subprocess.run([str(RUNNER),'audit',path,'10000','12'],capture_output=True,text=True,
                             timeout=max(1,DEADLINE-time.monotonic()))
        txt=trial.stdout+trial.stderr;(HERE/'winner.audit10000.txt').write_text(txt)
        if 'movement_failures=0' in txt and 'conservation_mismatch_ticks=0' in txt:
            trial=subprocess.run([str(AUDIT),path,'10000',str(HERE/'winner.full80.csv')],capture_output=True,text=True,
                                 timeout=max(1,DEADLINE-time.monotonic()))
            (HERE/'winner.full80.txt').write_text(trial.stdout+trial.stderr)
            checkpoint('verified' if trial.returncode==0 else 'validation_failed',selected=win)
        else: checkpoint('validation_failed',selected=win)
    else: checkpoint('finished_no_candidate')
except subprocess.TimeoutExpired:
    checkpoint('time_limit_reached')
except Exception:
    (HERE/'error.txt').write_text(traceback.format_exc());checkpoint('error');raise
print((HERE/'status.json').read_text(),flush=True)
