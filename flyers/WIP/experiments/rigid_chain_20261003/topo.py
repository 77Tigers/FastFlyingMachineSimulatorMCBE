# Enumerate small closed rigid designs at 2.5 bps: n segments, each with a 2-of-4-slot move word; every move
# is caused by a rigid push (actor still at k,k+1) or rigid pull (actor still at k-1,k; sticky extends k-1).
# For each assignment, minimise total x-span (sum over segments of max-min element x) subject to contact
# equations. Push X->Y at k: c_Y+pos_Y(k)+g = c_X+pos_X(k)+p+1. Pull Z of Y at k: c_Z+pos_Z(k)+s = c_Y+pos_Y(k)+h+2.
import itertools, sys
from scipy.optimize import milp, LinearConstraint, Bounds
import numpy as np
import os
WORDS=[w for w in itertools.combinations(range(4),2)]
if os.environ.get('CONSEC'): WORDS=[(0,1),(1,2),(2,3),(0,3)]
MAXP=int(os.environ.get('MAXP','9'))
def pos(w,k): return sum(1 for m in w if m<k)
def still(w,ks): return all((k%4) not in w for k in ks)
def solve(n,words,acts):
    # variables: c_i (n), element x per action endpoint (2 per action), span lo/hi per segment (2n)
    na=len(acts); nv=n+2*na+2*n+1
    A=[];lb=[];ub=[]
    def row(): return [0.0]*nv
    for a,(typ,act,tgt,k) in enumerate(acts):
        r=row(); ea=n+2*a; et=n+2*a+1
        if typ=='push':
            # c_t+pos_t+et = c_a+pos_a+ea+1
            r[tgt]+=1; r[et]+=1; r[act]-=1; r[ea]-=1
            rhs=pos(words[act],k)+1-pos(words[tgt],k)
        else:
            # c_a+pos_a+ea = c_t+pos_t+et+2
            r[act]+=1; r[ea]+=1; r[tgt]-=1; r[et]-=1
            rhs=pos(words[tgt],k)+2-pos(words[act],k)
        A.append(r); lb.append(rhs); ub.append(rhs)
    # span: lo_i <= e <= hi_i for elements of segment i
    for a,(typ,act,tgt,k) in enumerate(acts):
        for seg,e in ((act,n+2*a),(tgt,n+2*a+1)):
            lo=n+2*na+2*seg; hi=lo+1
            r=row(); r[e]=1; r[lo]=-1; A.append(r); lb.append(0); ub.append(np.inf)
            r=row(); r[hi]=1; r[e]=-1; A.append(r); lb.append(0); ub.append(np.inf)
    cost=np.zeros(nv)
    for i in range(n): cost[n+2*na+2*i+1]=1; cost[n+2*na+2*i]=-1
    for i in range(n):
        r=row(); r[nv-1]=1; r[n+2*na+2*i+1]=-1; r[n+2*na+2*i]=1; A.append(r); lb.append(0); ub.append(np.inf)
    cost[nv-1]=10
    r=row(); r[0]=1; A.append(r); lb.append(0); ub.append(0)
    res=milp(cost,constraints=LinearConstraint(np.array(A),lb,ub),integrality=np.ones(nv),bounds=Bounds(-20,20))
    if res.status!=0: return None
    x=res.x; spans=[round(x[n+2*na+2*i+1]-x[n+2*na+2*i]) for i in range(n)]
    return (max(spans),sum(spans),tuple(spans))
def mv(w,j): return (j%4) in w
def contact_ok(words,acts):
    for typ,a,t,k in acts:
        rel=lambda j: pos(words[a],j%4)+(2 if j%4<k%4 else 0)-pos(words[t],j%4)-(2 if j%4<k%4 else 0)
        # relative position actor-target at slot starts, unwrapped over one cycle starting at k
        r={}
        pa=0;pt=0
        for d in range(4):
            j=(k+d)%4; r[j]=pa-pt
            if mv(words[a],j): pa+=1
            if mv(words[t],j): pt+=1
        if typ=='push':
            # contact at k (r=0). r>0 overlap; r==0 elsewhere: actor must not move
            for j,v in r.items():
                if v>0: return False
                if v==0 and mv(words[a],j): return False
        else:
            # d = h - s = -2 at k  -> d(j) = -2 - r(j)
            for j,v in r.items():
                dd=-2-v
                if dd>=0: return False
                if dd==-1 and (mv(words[t],j) or j==(k-1)%4): return False
    return True
def designs(n):
    for words in itertools.product(WORDS,repeat=n):
        if words[0]!=(0,1): continue  # fix rotation
        # causes for each (seg,move)
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
    n=int(sys.argv[1]); best={}
    seen=0
    for words,acts in designs(n):
        # connectivity
        adj={i:set() for i in range(n)}
        for _,a,t,_ in acts: adj[a].add(t); adj[t].add(a)
        st=[0]; vis={0}
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in vis: vis.add(y); st.append(y)
        if len(vis)<n: continue
        # no actor fires twice in same slot with a pull extension conflicting is allowed (multiple pistons)
        if not contact_ok(words,acts): continue
        seen+=1
        sp=solve(n,words,acts)
        if sp is None: continue
        pc=[sum(1 for _,a,_,_ in acts if a==i) for i in range(n)]
        key=(sp[0],max(pc),sp[1])
        best.setdefault(key,[]).append((words,acts,sp[2],pc))
    print('designs',seen)
    for k in sorted(best)[:8]:
        print('maxspan,maxpistons,total',k,'count',len(best[k]))
        for w,a,sp,pc in best[k][:4]: print('  ',w,a,'spans',sp,'pistons',pc)
