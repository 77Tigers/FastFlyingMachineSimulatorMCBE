import itertools, sys
import numpy as np
import rider_floor as R
base='mmwmw'; D=[0,1,2,3,4]
kinds={0:'pull',1:'push',3:'pull'}
vm=R.rot_moves(base,0)
allp=[]
for s,kind in kinds.items():
    res,rel,pm,f=R.patterns(base,D,kind,s)
    print(kind,'slot',s,'fire',f,'REL',rel,'pm',pm,'npat(all)',len(res))
    allp.append((kind,s,f,rel,pm,list(res.values())))
# enumerate all combos of patterns (not pareto) with load max 3 and report neighbour sets
idx={d:i for i,d in enumerate(D)}
def contrib(cnt):
    out=np.zeros((5,5),dtype=np.int32)
    for e in D:
        for dd in D:
            tgt=(e+dd)%5
            for tau in range(5):
                if cnt[idx[dd]][tau]: out[idx[tgt]][(tau+e)%5]+=1
    return out
mvmask=np.array([R.rot_moves(base,d) for d in D])
cons=[[contrib(c) for c,a in p[5]] for p in allp]
sols=[]
for combo in itertools.product(*[range(len(p[5])) for p in allp]):
    tot=sum(cons[i][j] for i,j in enumerate(combo))*mvmask
    if tot.max()<=3:
        nb=set()
        for i,j in enumerate(combo):
            a=allp[i][5][j][1]
            for d in D:
                if any(a[d]) and d!=0: nb.add(d)
        sols.append((len(nb),sorted(nb),combo))
sols.sort()
print('solutions with rider max 3:',len(sols))
for s in sols[:8]: print(s[0],s[1])
n,nb,combo=sols[0]
print('--- best (fewest distinct neighbour bodies):',nb)
for i,j in enumerate(combo):
    kind,s,f,rel,pm,pl=allp[i]
    a=pl[j][1]
    print(kind,'at',s,'fire',f,'REL',rel,'moves',pm)
    for d in D:
        mv=R.rot_moves(base,d)
        if any(a[d]): print('   body V_%d (moves %s) adj by slot %s ; carries at %s'%(d,''.join(map(str,mv)),''.join(map(str,a[d])),[t for t in range(5) if pm[t] and mv[t] and a[d][t]]))
