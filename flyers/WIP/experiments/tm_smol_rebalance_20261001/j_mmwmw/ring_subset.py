"""Ring of bodies = subset D of the 5 rotations of a base word; each body plays the same lifecycle shifted by e.
ILP: choose per (owner e, piston k) one adjacency pattern; minimise max rider load over (body g, move slot t)."""
import itertools, sys
import numpy as np
import rider_floor as R
from scipy.optimize import milp, LinearConstraint, Bounds
L=5
def run(base,kinds,D,maxadj=None,verbose=True):
    D=sorted(D)
    vars_=[]  # (e,k,cnt matrix dict (g,t)->1, adj, rel info)
    groups=[]
    for e in D:
        rel_set=sorted({(g-e)%L for g in D}|{0})
        for k,(s,kind) in enumerate(kinds.items()):
            r=R.patterns(base,rel_set,kind,s,maxadj)
            if r is None or not r[0]: return None
            res,rel,pm,f=r
            g0=len(vars_)
            for cnt,a in res.values():
                load={}
                for i,d in enumerate(rel_set):
                    for tau in range(L):
                        if cnt[i][tau]:
                            key=((e+d)%L,(tau+e)%L)
                            load[key]=load.get(key,0)+1
                vars_.append((e,k,load,a,rel_set,rel,pm,f))
            groups.append((g0,len(vars_)))
    n=len(vars_)
    # variables: x_0..x_{n-1}, M
    c=np.zeros(n+1); c[n]=1
    A=[];lb=[];ub=[]
    for g0,g1 in groups:
        row=np.zeros(n+1); row[g0:g1]=1; A.append(row); lb.append(1); ub.append(1)
    for g in D:
        mvg=R.rot_moves(base,g)
        for t in range(L):
            if not mvg[t]: continue
            row=np.zeros(n+1)
            for i,v in enumerate(vars_):
                row[i]=v[2].get((g,t),0)
            row[n]=-1
            A.append(row); lb.append(-np.inf); ub.append(0)
    res=milp(c,constraints=LinearConstraint(np.array(A),lb,ub),integrality=np.r_[np.ones(n),0],bounds=Bounds(np.r_[np.zeros(n),0],np.r_[np.ones(n),50]))
    if res.status!=0: return None
    return round(res.x[n]),vars_,res.x
if __name__=='__main__':
    base='mmwmw'
    for kinds in [{0:'pull',1:'push',3:'pull'},{0:'push',1:'pull',3:'pull'},{0:'pull',1:'pull',3:'push'},{0:'pull',1:'pull',3:'pull'},{0:'push',1:'push',3:'pull'},{0:'push',1:'push',3:'push'}]:
        for size in (2,3,4,5):
            best=None
            for D in itertools.combinations(range(5),size):
                if D[0]!=0: continue  # rotation symmetry: wlog contains 0
                r=run(base,kinds,D)
                if r is None: continue
                if best is None or r[0]<best[0]: best=(r[0],D)
            print(list(kinds.values()),'size',size,'best (maxriders, D):',best,flush=True)
