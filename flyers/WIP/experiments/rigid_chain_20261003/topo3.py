# Segment model: straight glue bridge in one lane from vp (pushed contact, rear end) to vs (pulled contact,
# front end), vp<=vs; pushers at x=u and stickies at x=w hang off the bridge sideways, vp<=u,w<=vs.
# Glue = vs-vp+1. Minimise max bridge length then total.
import itertools, sys, os
from scipy.optimize import milp, LinearConstraint, Bounds
import numpy as np
from topo import pos, still, contact_ok
from topo2 import designs
def solve(n,words,acts):
    U,W,VP,VS,LO,HI,PB,QB=0,n,2*n,3*n,4*n,5*n,6*n,7*n; M=8*n; nv=8*n+1
    A=[];lb=[];ub=[]
    def row(): return [0.0]*nv
    def ge(r,v): A.append(r); lb.append(v); ub.append(np.inf)
    for typ,a,t,k in acts:
        r=row()
        if typ=='push': r[VP+t]+=1; r[U+a]-=1; rhs=pos(words[a],k)-pos(words[t],k)+1
        else: r[W+a]+=1; r[VS+t]-=1; rhs=pos(words[t],k)-pos(words[a],k)+2
        A.append(r); lb.append(rhs); ub.append(rhs)
    for i in range(n):
        for X in (U,W,VP,VS):
            r=row(); r[X+i]=1; r[LO+i]=-1; ge(r,0)
            r=row(); r[HI+i]=1; r[X+i]=-1; ge(r,0)
        r=row(); r[PB+i]=30; r[VP+i]=-1; r[LO+i]=1; ge(r,0)   # vp>lo => a=1 (lateral pushed contact)
        r=row(); r[QB+i]=30; r[HI+i]=-1; r[VS+i]=1; ge(r,0)   # vs<hi => b=1
        r=row(); r[M]=1; r[HI+i]=-1; r[LO+i]=1; r[PB+i]=-1; r[QB+i]=-1; ge(r,1)
    r=row(); r[VP]=1; A.append(r); lb.append(0); ub.append(0)
    cost=np.zeros(nv); cost[M]=100
    for i in range(n): cost[HI+i]+=1; cost[LO+i]-=1; cost[PB+i]+=1; cost[QB+i]+=1
    bnd=Bounds([-30]*(8*n)+[0],[30]*(8*n)+[60]); bnd.lb[PB:QB+n]=0; bnd.ub[PB:QB+n]=1
    res=milp(cost,constraints=LinearConstraint(np.array(A),lb,ub),integrality=np.ones(nv),bounds=bnd)
    if res.status!=0: return None
    x=[round(v) for v in res.x]
    return [x[HI+i]-x[LO+i]+1+x[PB+i]+x[QB+i] for i in range(n)], [(x[U+i],x[W+i],x[VP+i],x[VS+i]) for i in range(n)]
if __name__=='__main__':
    n=int(sys.argv[1]); best={}; seen=0
    for words,acts in designs(n):
        adj={i:set() for i in range(n)}
        for _,a,t,_ in acts: adj[a].add(t); adj[t].add(a)
        st=[0]; vis={0}
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in vis: vis.add(y); st.append(y)
        if len(vis)<n or not contact_ok(words,acts): continue
        seen+=1
        r=solve(n,words,acts)
        if r is None: continue
        d,x=r; key=(max(d),sum(d))
        best.setdefault(key,[]).append((words,acts,d,x))
    print('designs',seen)
    for k in sorted(best)[:5]:
        print('maxglue,totalglue',k,'count',len(best[k]))
        for w,a,d,x in best[k][:3]: print('  ',w,a,'bridge',d,'x',x)
