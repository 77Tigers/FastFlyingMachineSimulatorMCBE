"""Per-body exact re-synthesis (MILP, scipy/HiGHS) of pickups/connectors given the other bodies fixed."""
import model, numpy as np, time, sys, itertools
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, csr_matrix
m=model.m; S=m.S; DISP=m.DISP; D=m.D
def recovery(f): return [t for t in range(6) if (t-f)%6 not in (0,1)]
def cover_set(i,c,ps):
    out=set()
    for j,(pp,dp,f,target,sticky) in enumerate(ps):
        for t in recovery(f):
            if S[i][t] and sum(abs(a-b) for a,b in zip(m.shift(c,DISP[i][t]),m.shift(pp,dp[t])))==1: out.add((j,t))
    return out
def optimize_body(i,ss,ps,src,mandatory,margin=2,timelimit=120,objective_extra=None,verbose=True,box=None):
    ss=[set(s) for s in ss]
    tmp=[set(s) for s in ss]
    legal=model.ns['make_legal'](tmp,ps,src)
    allcells=[p for s in ss for p in s]
    if box is None:
        lo=[min(p[k] for p in allcells)-margin for k in range(3)]; hi=[max(p[k] for p in allcells)+margin for k in range(3)]
    else: lo,hi=box
    cand=[]
    for x in range(lo[0],hi[0]+1):
      for y in range(lo[1],hi[1]+1):
        for z in range(lo[2],hi[2]+1):
            c=(x,y,z)
            if any(c in s for j,s in enumerate(ss) if j!=i): continue
            if c in mandatory or legal(c,i): cand.append(c)
    # fixed occupancy by pistons/sources at t=0 irrelevant: legal handles time-dependent
    idx={c:k for k,c in enumerate(cand)}
    n=len(cand)
    # needs: (j,t) uncovered by other bodies' cells
    need=set((j,t) for j,(pp,dp,f,tg,st) in enumerate(ps) for t in recovery(f))
    for k in range(3):
        if k==i: continue
        for c in ss[k]: need-=cover_set(k,c,ps)
    covers=[cover_set(i,c,ps) for c in cand]
    for c,cv in zip(cand,covers):
        pass
    # variables: x (n), flows on arcs
    arcs=[]
    for c in cand:
        for d in D:
            q=m.add(c,d)
            if q in idx: arcs.append((idx[c],idx[q]))
    na=len(arcs); K=len(ss[i])+10
    nv=n+na
    cost=np.zeros(nv); 
    for k,c in enumerate(cand):
        cost[k]=0 if c in mandatory else 1
    if objective_extra: 
        for k,c in enumerate(cand): cost[k]+=objective_extra(c)
    lb=np.zeros(nv); ub=np.ones(nv)
    for c in mandatory:
        lb[idx[c]]=1
    ub[n:]=K
    rows=[];rhs_l=[];rhs_u=[]
    A=lil_matrix((len(need)+n+2*na+0,nv))
    r=0
    # coverage
    needl=sorted(need)
    for (j,t) in needl:
        for k in range(n):
            if (j,t) in covers[k]: A[r,k]=1
        rhs_l.append(1);rhs_u.append(np.inf);r+=1
    # flow conservation: root = first mandatory cell; inflow - outflow = x_v for non-root; root supplies
    root=idx[sorted(mandatory)[0]]
    outs=[[] for _ in range(n)];ins=[[] for _ in range(n)]
    for a,(u,v) in enumerate(arcs): outs[u].append(n+a);ins[v].append(n+a)
    for v in range(n):
        if v==root: continue
        for a in ins[v]: A[r,a]=1
        for a in outs[v]: A[r,a]=-1
        A[r,v]=-1
        rhs_l.append(0);rhs_u.append(0);r+=1
    for a,(u,v) in enumerate(arcs):
        # f_uv <= K x_u ; f_uv <= K x_v
        A[r,n+a]=1;A[r,u]=-K;rhs_l.append(-np.inf);rhs_u.append(0);r+=1
        A[r,n+a]=1;A[r,v]=-K;rhs_l.append(-np.inf);rhs_u.append(0);r+=1
    A=csr_matrix(A[:r])
    integrality=np.zeros(nv);integrality[:n]=1
    t0=time.time()
    res=milp(cost,constraints=LinearConstraint(A,rhs_l,rhs_u),integrality=integrality,bounds=Bounds(lb,ub),options=dict(time_limit=timelimit,disp=False))
    if verbose: print('body',i,'cand',n,'arcs',na,'need',len(need),'status',res.status,res.message[:40],'obj',None if res.x is None else round(res.fun,2),'time %.1f'%(time.time()-t0),flush=True)
    if res.x is None: return None
    sel={cand[k] for k in range(n) if res.x[k]>0.5}
    return sel
if __name__=='__main__':
    ss,ps,src=model.load_geometry()
    # mandatory = cross cells: the 9 cells per body: recompute from segments via planar construction rule: choose cells in ss[i] within plane... derive from sources holders
    print([len(s) for s in ss])

def mandatory_sets(ss,ps,src):
    out=[]
    for i in range(3):
        hs=[(p[0]+1,p[1],p[2]) for p,o,ob,dr in src if o==i]
        x=hs[0][0]; assert all(h[0]==x for h in hs)
        cy=sum(h[1] for h in hs)/4; cz=sum(h[2] for h in hs)/4
        cy=int(round(cy)); cz=int(round(cz))
        cs={(x,cy,cz)}
        for d in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            cs.add((x,cy+d[1],cz+d[2])); cs.add((x,cy+2*d[1],cz+2*d[2]))
        assert cs<=ss[i],(i,cs-ss[i])
        out.append(cs)
    return out
