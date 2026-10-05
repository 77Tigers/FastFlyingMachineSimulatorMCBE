"""Direction-aware shortest-bridge heuristic, with a cost for route bends.

Returned glue still goes through the same connectivity, swept-collision and
simulation checks. This does not prove a globally minimum-bend Steiner tree.
"""
import heapq,time
import common as c

def bridge(cells,blocked,weights,bounds,rng,deadline,bend=.15):
    groups=c.base.components(cells)
    if len(groups)==1:return set()
    heap=[];dist={};owner={};prev={}
    for j,group in enumerate(groups):
        for p in sorted(group):
            state=(p,3);dist[state]=0;owner[state]=j;prev[state]=None
            heapq.heappush(heap,(0,rng.random(),state))
    best=float('inf');meeting=None;visits=0
    while heap:
        cost,_,state=heapq.heappop(heap)
        if cost!=dist[state]:continue
        if cost>best:break
        visits+=1
        if visits%256==0 and time.monotonic()>deadline:return None
        p,lastaxis=state
        for axis in range(3):
            for sign in (-1,1):
                q=tuple(p[k]+(sign if k==axis else 0) for k in range(3))
                if not all(bounds[2*k]<=q[k]<=bounds[2*k+1] for k in range(3)):continue
                if q not in cells and q in blocked:continue
                step=0 if q in cells else 1+weights.get(q,0)+(bend if lastaxis not in (axis,3) else 0)
                for otheraxis in range(4):
                    other=(q,otheraxis)
                    if other in owner and owner[other]!=owner[state]:
                        total=cost+step+dist[other]
                        if total<best:best=total;meeting=(state,other)
                nxt=(q,axis);nc=cost+step
                if nxt in owner and owner[nxt]!=owner[state]:continue
                if nc<dist.get(nxt,float('inf')):
                    dist[nxt]=nc;owner[nxt]=owner[state];prev[nxt]=state
                    heapq.heappush(heap,(nc,rng.random(),nxt))
    if meeting is None:return None
    path=set()
    for state in meeting:
        while state is not None:
            if state[0] not in cells:path.add(state[0])
            state=prev[state]
    return path
