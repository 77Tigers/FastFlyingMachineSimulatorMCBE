import sys,time,itertools
sys.path.insert(0,'flyers/WIP/experiments/speed_range_b_20260930/mmw6')
import gen6
m=gen6.m
def comps(s):
    s=set(s);out=[]
    while s:
        c={min(s)};st=list(c)
        while st:
            p=st.pop()
            for d in m.D:
                q=m.add(p,d)
                if q in s and q not in c:c.add(q);st.append(q)
        out.append(c);s-=c
    return out
def estimate(ss):
    tot=[]
    for s in ss:
        cs=comps(s)
        # Prim over components with manhattan distances
        inn=[cs[0]];rest=cs[1:];cost=0
        while rest:
            best=None
            for c in rest:
                d=min(sum(abs(a-b) for a,b in zip(p,q)) for p in c for q in itertools.chain.from_iterable(inn))
                if best is None or d<best[0]:best=(d,c)
            cost+=best[0]-1;inn.append(best[1]);rest.remove(best[1])
        tot.append(len(s)+cost)
    return tot
def run(name,centers,n=12):
    out=[];fails={}
    for seed in range(n):
        # need ss: monkeypatch build to return ss
        ans,r=gen6.build(seed,centers,pickup_only=True)
        if ans is None:fails[r]=fails.get(r,0)+1;continue
        out.append(ans[2])
    return out,fails
if __name__=='__main__':pass
