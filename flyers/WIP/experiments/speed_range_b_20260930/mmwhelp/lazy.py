"""Per-body re-synthesis with lazy connectivity cuts (scipy HiGHS). Other bodies fixed."""
import model, numpy as np, time, sys
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, csr_matrix, vstack
m=model.m; S=m.S; DISP=m.DISP; D=m.D
def recovery(f): return [t for t in range(6) if (t-f)%6 not in (0,1)]
def dist1(a,b): return sum(abs(x-y) for x,y in zip(a,b))==1
def cover_set(i,c,ps):
    out=set()
    for j,(pp,dp,f,target,sticky) in enumerate(ps):
        for t in recovery(f):
            if S[i][t] and dist1(m.shift(c,DISP[i][t]),m.shift(pp,dp[t])): out.add((j,t))
    return out
def optimize_body(i,ss,ps,src,mandatory,margin=2,timelimit=60,verbose=True,forbid=()):
    """mandatory: cells forced in; holders: each source of owner i must have an adjacent selected cell."""
    tmp=[set(s) for s in ss]
    legal=model.ns['make_legal'](tmp,ps,src)
    allc=[p for s in ss for p in s]
    lo=[min(p[k] for p in allc)-margin for k in range(3)]; hi=[max(p[k] for p in allc)+margin for k in range(3)]
    cand=[]
    for x in range(lo[0],hi[0]+1):
      for y in range(lo[1],hi[1]+1):
        for z in range(lo[2],hi[2]+1):
            c=(x,y,z)
            if c in forbid: continue
            if any(c in s for j,s in enumerate(ss) if j!=i): continue
            if c in mandatory or legal(c,i): cand.append(c)
    idx={c:k for k,c in enumerate(cand)}; n=len(cand)
    need=set((j,t) for j,(pp,dp,f,tg,st) in enumerate(ps) for t in recovery(f))
    for k in range(3):
        if k==i: continue
        for c in ss[k]: need-=cover_set(k,c,ps)
    covers=[cover_set(i,c,ps) for c in cand]
    rows=[];lo_b=[];hi_b=[]
    def addrow(coefs,l,u):
        rows.append(coefs);lo_b.append(l);hi_b.append(u)
    for (j,t) in sorted(need):
        addrow({k:1 for k in range(n) if (j,t) in covers[k]},1,np.inf)
    # holders
    for p,o,ob,dr in src:
        if o!=i: continue
        nb=[m.add(p,d) for d in D]
        addrow({idx[q]:1 for q in nb if q in idx},1,np.inf)
    cost=np.array([0 if c in mandatory else 1 for c in cand],float)
    lb=np.zeros(n);ub=np.ones(n)
    for c in mandatory: lb[idx[c]]=1
    root=idx[sorted(mandatory)[0]]
    t0=time.time();it=0
    while True:
        it+=1
        A=lil_matrix((len(rows),n))
        for r,co in enumerate(rows):
            for k,v in co.items(): A[r,k]=v
        res=milp(cost,constraints=LinearConstraint(csr_matrix(A),lo_b,hi_b),integrality=np.ones(n),bounds=Bounds(lb,ub),options=dict(time_limit=timelimit,disp=False))
        if res.x is None:
            if verbose: print('  no solution',res.message); 
            return None
        sel={k for k in range(n) if res.x[k]>0.5}
        # components
        comps=[];seen=set()
        for k in sel:
            if k in seen: continue
            comp={k};st=[k];seen.add(k)
            while st:
                u=st.pop()
                for d in D:
                    q=m.add(cand[u],d)
                    v=idx.get(q)
                    if v is not None and v in sel and v not in seen: seen.add(v);comp.add(v);st.append(v)
            comps.append(comp)
        if len(comps)==1: break
        for comp in comps:
            if root in comp: continue
            nbrs=set()
            for u in comp:
                for d in D:
                    v=idx.get(m.add(cand[u],d))
                    if v is not None and v not in comp: nbrs.add(v)
            u=min(comp)
            co={v:1 for v in nbrs}; co[u]=co.get(u,0)-1
            addrow(co,0,np.inf)
        if time.time()-t0>timelimit*4: 
            if verbose: print('  timeout in cuts'); 
            return None
    if verbose: print('  body',i,'cand',n,'need',len(need),'obj',round(res.fun,1),'status',res.status,'iters',it,'time %.1f'%(time.time()-t0),flush=True)
    return {cand[k] for k in sel}
