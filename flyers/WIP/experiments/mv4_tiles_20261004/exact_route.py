"""Exact bounded node-Steiner check of one saved ring interface.

Uses numpy only; no solver installation or simulator edits. Mandatory glue
components are contracted to zero-cost terminals; optional glue costs one.
Dreyfus-Wagner subset DP + Dijkstra gives a minimum within the specified box
and cost cutoff. This checks one body against OTHER MANDATORY bodies only;
it is not a simultaneous full-flyer proof.
"""
import argparse, heapq, itertools, json, time
import numpy as np
import ring as r


def solve(must,blocked,bounds,cap=36):
    start=time.monotonic();groups=r.base.components(must);k=len(groups)
    if k>12:raise ValueError('Subset DP restricted to <=12 terminal components')
    budget=cap-len(must);inf=10000
    where={p:i for i,g in enumerate(groups) for p in g}
    points=[None]*k
    for p in itertools.product(*(range(bounds[2*i],bounds[2*i+1]+1) for i in range(3))):
        if p not in blocked and p not in where:where[p]=len(points);points.append(p)
    adj=[set() for _ in points]
    for p,i in where.items():
        for d in r.b.D:
            q=r.b.add(p,d)
            if q in where and where[q]!=i:adj[i].add(where[q])
    adj=[sorted(a) for a in adj];n=len(points)
    weights=np.ones(n,dtype=np.int32);weights[:k]=0
    dp=np.full((1<<k,n),inf,dtype=np.int32)
    choice=np.full((1<<k,n),-1,dtype=np.int32)
    for i in range(k):dp[1<<i,i]=0
    last=time.monotonic()
    for mask in range(1,1<<k):
        sub=(mask-1)&mask
        while sub:
            other=mask^sub
            if sub<other:
                candidate=dp[sub]+dp[other]-weights
                good=(candidate<dp[mask])&(candidate<=budget)
                dp[mask,good]=candidate[good];choice[mask,good]=-2-sub
            sub=(sub-1)&mask
        row=dp[mask]
        heap=[(int(row[i]),i) for i in np.flatnonzero(row<=budget)]
        heapq.heapify(heap)
        while heap:
            cost,i=heapq.heappop(heap)
            if cost!=row[i]:continue
            for j in adj[i]:
                total=cost+int(weights[j])
                if total<=budget and total<row[j]:
                    row[j]=total;choice[mask,j]=i;heapq.heappush(heap,(total,j))
        if time.monotonic()-last>25:
            print(json.dumps(dict(stage='exact_subset_dp',done=mask,total=(1<<k)-1,nodes=n)),flush=True)
            last=time.monotonic()
    full=(1<<k)-1;node=int(np.argmin(dp[full]));extra=int(dp[full,node])
    result=dict(mandatory=len(must),components=k,allowed_nodes=n,cap=cap,seconds=round(time.monotonic()-start,2))
    if extra>budget:return result | dict(status='infeasible_within_box_and_cap')
    cells=set(must);seen=set();todo=[(full,node)]
    while todo:
        mask,i=todo.pop()
        if (mask,i) in seen:continue
        seen.add((mask,i))
        if points[i] is not None:cells.add(points[i])
        c=int(choice[mask,i])
        if c>=0:todo.append((mask,c))
        elif c<=-2:
            sub=-2-c;todo.extend(((sub,i),(mask^sub,i)))
    assert len(cells)==len(must)+extra
    assert len(r.base.components(cells))==1
    return result | dict(status='optimal_within_box',minimum=len(cells),cells=sorted(cells))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--body',type=int,choices=(0,1,2),default=0)
    parser.add_argument('--cap',type=int,default=36)
    args=parser.parse_args()
    summaries=json.loads((r.HERE/'ring_summary.json').read_text())
    saved=r.HERE/'exact_summary.json'
    selected=json.loads(saved.read_text())['placement'] if saved.exists() else summaries[-1]['best']
    assert selected is not None
    centers=[];rots=[];refs=[]
    for q in range(4):
        for i in range(3):
            _,y,z=r.rotate((0,selected['radius'],(i-1)*selected['spacing']),q)
            centers.append((y,z));rots.append((selected['rotations'][i]+q)%4);refs.append(selected['reflections'][i])
    captured={}
    def take(must,fixed,bounds,*args):captured.update(must=must,fixed=fixed,bounds=bounds)
    r.b.build(0,(centers,rots,refs),cap=36,joint_router=take,
              config=r.CFG | dict(planes=(0,*selected.get('axial',(0,0)))*4))
    results=[]
    for i in (args.body,):
        blocked=set(captured['fixed'][i])
        for j in range(r.N):
            if j!=i:blocked.update(r.obstacles(captured['must'][j],j,i))
        result=solve(captured['must'][i],blocked,captured['bounds'],args.cap)
        result['body']=i;results.append(result)
        print(json.dumps({k:v for k,v in result.items() if k!='cells'}),flush=True)
        (r.HERE/'exact_summary.json').write_text(json.dumps(dict(placement=selected,results=results),indent=2))
    (r.HERE/'exact_summary.json').write_text(json.dumps(dict(placement=selected,results=results),indent=2))
