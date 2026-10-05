"""Cheap mandatory-interface survey; rigorous span bound before any routing.

Usage: python survey.py [placements=12000]. Does not simulate or save flyers.
The Manhattan component MST is only a ranking heuristic, never a feasibility
proof. The axis-span bound is a necessary condition for connected glue.
"""
import sys,json,random,time,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'mv4_20261002/synthesis'))
import six,final_router

def mst(cells):
    groups=final_router.components(cells); reached={0};total=0
    while len(reached)<len(groups):
        d,j=min((min(sum(abs(a[k]-b[k]) for k in range(3)) for a in groups[i] for b in groups[j]),j)
                for i in reached for j in range(len(groups)) if j not in reached)
        reached.add(j);total+=d
    return total

stats=collections.Counter();best=[];start=time.monotonic()
count=int(sys.argv[1]) if len(sys.argv)>1 else 12000
for seed in range(count):
    rng=random.Random(340004+seed)
    a=rng.choice((3,4,5,6,7));b=rng.choice((1,2,3,4));c=rng.choice((3,4,5,6,7))
    if seed%3==0: centers=[(a,c),(0,c),(-a,c),(-a,-c),(0,-c),(a,-c)];family='rectangle'
    else: centers=[(a,0),(b,c),(-b,c),(-a,0),(-b,-c),(b,-c)];family='hexagon'
    rot=[rng.randrange(4) for _ in range(3)];ref=[rng.choice((-1,1)) for _ in range(3)]
    placement=(centers,rot+[(q+2)%4 for q in rot],ref+ref)
    if seed%5==0:
        six.OWN=((1,1),(-1,1),(-1,1),(1,1));six.PREVIOUS=((2,0),(-2,0),(0,2),(2,0))
    else:
        six.OWN=((1,1),(-2,0),(1,1),(1,1));six.PREVIOUS=((2,0),(-1,1),(-1,1),(2,0))
    info={}
    def inspect(must,fixed,bounds,cap,rng):
        info['span_lower_bounds']=[max(len(s),1+sum(max(p[k] for p in s)-min(p[k] for p in s) for k in range(3))) for s in must]
        info['mst_rank']=[mst(s) for s in must[:3]]
        info['mandatory_counts']=list(map(len,must))
        return None
    ans,why=six.build(seed,placement,cap=39,joint_router=inspect)
    stats['placements']+=1;stats[why[0]]+=1
    if info:
        stats['interface_valid']+=1
        if max(info['span_lower_bounds'])>39:stats['span_reject_pl49']+=1
        if max(info['span_lower_bounds'])>25:stats['span_reject_glue25']+=1
        rank=(max(info['mst_rank']),sum(info['mst_rank']))
        best.append(dict(seed=seed,family=family,placement=placement,rank=rank,
                         own=six.OWN,previous=six.PREVIOUS,**info))
        if len(best)>128:best=sorted(best,key=lambda r:r['rank'])[:64]
    if time.monotonic()-start>120:break
best=sorted(best,key=lambda r:r['rank'])[:64]
(HERE/'survey.json').write_text(json.dumps(dict(elapsed_seconds=round(time.monotonic()-start,2),statistics=stats,ranked=best),indent=2))
print(json.dumps(dict(elapsed_seconds=round(time.monotonic()-start,2),statistics=stats,best=best[:1])),flush=True)
