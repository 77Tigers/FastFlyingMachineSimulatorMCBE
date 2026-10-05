# Like topo.py, but each segment has one piston x (u_i) and one glue x (v_i): pushed and pulled glue share x.
# Minimise max |u_i - v_i| then sum. Also reports per-segment pistons.
import itertools, sys, os
from scipy.optimize import milp, LinearConstraint, Bounds
import numpy as np
sys.argv += []
from topo import pos, still, contact_ok, mv
WORDS=[(0,1),(1,2),(2,3),(0,3)] if os.environ.get('CONSEC') else [w for w in itertools.combinations(range(4),2)]
MAXP=int(os.environ.get('MAXP','2'))
def solve(n,words,acts):
    # vars: u_0..u_{n-1}, v_0..v_{n-1}, d_i (abs diff), M
    nv=3*n+1; A=[];lb=[];ub=[]
    def row(): return [0.0]*nv
    for typ,a,t,k in acts:
        r=row()
        if typ=='push': r[n+t]+=1; r[a]-=1; rhs=pos(words[a],k)-pos(words[t],k)+1
        else: r[a]+=1; r[n+t]-=1; rhs=pos(words[t],k)-pos(words[a],k)+2
        A.append(r); lb.append(rhs); ub.append(rhs)
    for i in range(n):
        r=row(); r[2*n+i]=1; r[i]-=1; r[n+i]+=1; A.append(r); lb.append(0); ub.append(np.inf)
        r=row(); r[2*n+i]=1; r[i]+=1; r[n+i]-=1; A.append(r); lb.append(0); ub.append(np.inf)
        r=row(); r[3*n]=1; r[2*n+i]=-1; A.append(r); lb.append(0); ub.append(np.inf)
    r=row(); r[0]=1; A.append(r); lb.append(0); ub.append(0)
    cost=np.zeros(nv); cost[3*n]=100; cost[2*n:3*n]=1
    res=milp(cost,constraints=LinearConstraint(np.array(A),lb,ub),integrality=np.ones(nv),bounds=Bounds(-30,30))
    if res.status!=0: return None
    x=res.x; return [round(x[i]-x[n+i]) for i in range(n)], [round(v) for v in x[:2*n]]
def designs(n):
    for words in itertools.product(WORDS,repeat=n):
        if words[0]!=(0,1): continue
        opts=[]
        for t in range(n):
            for k in words[t]:
                o=[]
                for a in range(n):
                    if a==t: continue
                    if still(words[a],(k,k+1)): o.append(('push',a,t,k))
                    if still(words[a],(k-1,k)): o.append(('pull',a,t,k))
                opts.append(o)
        def rec(i,cur,pc):
            if i==len(opts): yield words,tuple(cur); return
            for o in opts[i]:
                if pc[o[1]]>=MAXP: continue
                pc[o[1]]+=1; cur.append(o)
                yield from rec(i+1,cur,pc)
                cur.pop(); pc[o[1]]-=1
        yield from rec(0,[],[0]*n)
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
        d,uv=r; key=(max(abs(z) for z in d),sum(abs(z) for z in d))
        best.setdefault(key,[]).append((words,acts,d,uv))
    print('designs',seen)
    for k in sorted(best)[:5]:
        print('maxspan,total',k,'count',len(best[k]))
        for w,a,d,uv in best[k][:3]: print('  ',w,a,'u-v',d,'uv',uv)
