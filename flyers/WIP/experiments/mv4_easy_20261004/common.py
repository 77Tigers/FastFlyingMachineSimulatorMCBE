"""Existing six-core interfaces and verified physical keepouts, unchanged."""
import sys,json,collections,subprocess,copy,time,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'mv4_elegant_20261004'
sys.path.insert(0,str(HERE.parent/'mv4_20261002/synthesis'))
import six,final_router as base
sys.path.insert(0,str(OLD))
import paired_router
AUDIT=OLD/'audit_cores.exe'
RUNNER=six.ROOT/'flyers/WIP/experiments/bin/research_runner.exe'

def write_json(path,data):
    # OneDrive can transiently lock a live status file. Replace a closed temporary
    # file and retry, rather than lose the finite search to a logging failure.
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    for attempt in range(12):
        try:
            temp.write_text(json.dumps(data,indent=2),encoding='utf-8')
            temp.replace(path);return
        except OSError:
            if attempt==11:raise
            time.sleep(.1*(attempt+1))

def capture(meta):
    parent=meta.get('parent',meta)
    placement=(meta['centers'],meta['rotations'],meta['reflections'])
    six.OWN=parent.get('own',six.OWN);six.PREVIOUS=parent.get('previous',six.PREVIOUS)
    data={}
    def take(must,fixed,bounds,cap,rng):
        data.update(must=[set(s) for s in must],fixed=fixed,bounds=bounds)
        return None
    six.build(0,placement,cap=39,joint_router=take)
    if not data:raise ValueError('Saved interface rejected')
    return data

def valid(routes,data):
    for i in range(6):
        if not data['must'][i]<=routes[i] or routes[i]&data['fixed'][i]:return False
        if len(base.components(routes[i]))!=1:return False
        for j in range(i):
            if routes[i]&base.obstacles(routes[j],j,i):return False
    return all(paired_router.mirrored(routes[i])==routes[i+3] for i in range(3))

def blocked_pair(i,routes,data):
    blocked=set(data['fixed'][i])|paired_router.mirrored(data['fixed'][i+3])
    for j in range(6):
        if j not in (i,i+3):
            blocked.update(base.obstacles(routes[j],j,i))
            blocked.update(paired_router.mirrored(base.obstacles(routes[j],j,i+3)))
    return blocked

def score(routes):
    bends=branches=0
    for s in routes[:3]:
        for p in s:
            axes=[k for k in range(3) for d in (-1,1)
                  if tuple(p[t]+(d if t==k else 0) for t in range(3)) in s]
            bends+=len(axes)==2 and axes[0]!=axes[1]
            branches+=len(axes)>=3
    return max(map(len,routes)),sum(map(len,routes)),bends,branches

def save(meta,routes,path,limit):
    parent=meta.get('parent',meta)
    six.OWN=parent.get('own',six.OWN);six.PREVIOUS=parent.get('previous',six.PREVIOUS)
    placement=(meta['centers'],meta['rotations'],meta['reflections'])
    ans,why=six.build(0,placement,cap=max(map(len,routes)),joint_router=lambda *args:routes)
    if not ans:raise ValueError(why)
    f,m=ans;f.push_limit=limit;f.save(path)
    m.update(parent=parent,geometry_score=score(routes))
    path.with_suffix('.json').write_text(json.dumps(m,indent=2))
    return m

def screen(path,limit=None,ticks=300):
    csvpath=path.with_suffix(f'.screen{ticks}.csv')
    args=[str(AUDIT),str(path),str(ticks),str(csvpath)]
    if limit is not None:args.append(str(limit))
    trial=subprocess.run(args,capture_output=True,text=True,timeout=120)
    path.with_suffix(f'.screen{ticks}.txt').write_text(trial.stdout+trial.stderr)
    return trial.returncode==0
