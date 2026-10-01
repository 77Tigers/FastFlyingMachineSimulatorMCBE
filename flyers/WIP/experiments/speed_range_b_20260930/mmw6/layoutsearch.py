"""Search 6-body placements (center, rotation q, front x) using the pair-feasibility table."""
import json,random,math,itertools,sys
D='flyers/WIP/experiments/speed_range_b_20260930/mmw6/'
T=json.load(open(D+'pairscan2.json'))
tab={}
for k,v in T.items():
    i,j,dy,dz=map(int,k.split(','));tab[(i,j,dy,dz)]=set(map(tuple,v))
    # symmetric entry
    tab[(j,i,-dy,-dz)]={(b,a,d,c) for (a,b,c,d) in v}
ALL=set(itertools.product(range(4),range(4),(-1,0,1),(-1,0,1)))
def combos(i,j,dy,dz):
    l1=abs(dy)+abs(dz)
    if l1>7:return ALL
    return tab.get((i,j,dy,dz),set())
W={}
for i,j in itertools.combinations(range(6),2):W[(i,j)]=0.4 if j-i==3 else 1.0
def cost(cen):
    return sum(W[(i,j)]*math.dist(cen[i],cen[j]) for i,j in W)
def search(seed,iters=3000):
    rng=random.Random(seed);best=None
    order=list(range(6));
    for _ in range(iters):
        rng.shuffle(order);cen={};dom={}
        ok=True
        for b in order:
            cands=[]
            for y in range(-10,11):
                for z in range(-10,11):
                    if not cen:
                        if (y,z)!=(0,0):continue
                    c=(y,z);d={(q,f) for q in range(4) for f in (-1,0,1)};good=True
                    for o,oc in cen.items():
                        i,j=(o,b);ss=combos(o,b,y-oc[0],z-oc[1])
                        nd={(q,f) for (q,f) in d if any((qo,q,fo,f) in ss for (qo,fo) in dom[o])}
                        if not nd:good=False;break
                        d=nd
                    if good:cands.append(((sum(W[tuple(sorted((o,b)))]*math.dist(c,oc) for o,oc in cen.items()) if cen else 0),c,d))
            if not cands:ok=False;break
            cands.sort(key=lambda t:t[0]+rng.random()*3)
            s,c,d=cands[0]
            cen[b]=c;dom[b]=d
            # shrink domains of placed bodies to be consistent
            for o in list(cen):
                if o==b:continue
                ss=combos(o,b,cen[o][0]-c[0]and 0 or 0,0) if False else None
        if not ok:continue
        # final consistency: find an assignment of (q,f) per body
        sol=None
        def dfs(k,assign):
            if k==6:return dict(assign)
            b=k
            for qf in sorted(dom[b]):
                if all(any(True for _ in [0]) and ((assign[o][0],qf[0],assign[o][1],qf[1]) in combos(o,b,cen[b][0]-cen[o][0],cen[b][1]-cen[o][1])) for o in assign):
                    assign[b]=qf;r=dfs(k+1,assign)
                    if r:return r
                    del assign[b]
            return None
        sol=dfs(0,{})
        if sol is None:continue
        c=cost(cen)
        if best is None or c<best[0]:best=(c,dict(cen),sol)
    return best
if __name__=='__main__':
    res=[]
    for s in range(int(sys.argv[1])):
        b=search(s,int(sys.argv[2]))
        if b:res.append(b);print(s,round(b[0],1),b[1],b[2],flush=True)
    res.sort(key=lambda t:t[0])
    json.dump([(c,{str(k):v for k,v in cen.items()},{str(k):v for k,v in a.items()}) for c,cen,a in res],open(D+'layouts.json','w'))
