import model, itertools
m=model.m
ss,ps,src=model.load_geometry()
D=m.D
def dist1(a,b): return sum(abs(x-y) for x,y in zip(a,b))==1
def served(c,owner):
    """For RS at rel cell c owned by owner: return dict piston->set(slots) where it is adjacent (not in front)"""
    out={}
    for j,(pp,dp,f,target,sticky) in enumerate(ps):
        for t in range(6):
            r=m.shift(c,m.DISP[owner][t]); b=m.shift(pp,dp[t])
            if dist1(r,b) and r!=m.shift(b,1):
                out.setdefault(j,set()).add(t)
    return out
cells=set()
for s in ss:
    for p in s: cells.add(p)
xs=[p[0] for s in ss for p in s]; ys=[p[1] for s in ss for p in s]; zs=[p[2] for s in ss for p in s]
res=[]
for owner in range(3):
    for x in range(min(xs)-2,max(xs)+3):
      for y in range(min(ys)-2,max(ys)+3):
        for z in range(min(zs)-2,max(zs)+3):
            c=(x,y,z)
            a=served(c,owner)
            good={j for j,ts in a.items() if ts=={ps[j][2]}}
            bad={j for j,ts in a.items() if ts!={ps[j][2]}}
            if len(good)>=2 and not bad: res.append((owner,c,sorted(good)))
print(len(res))
for r in res[:60]: print(r)

print('--- with legality')
S=m.S;DISP=m.DISP
def fixed_at(t,exclude_src=None):
    w=set()
    for k,(rp,owner,observer,direction) in enumerate(src):
        if k==exclude_src: continue
        w.add(m.shift(rp,DISP[owner][t]))
    for pp,dp,f,target,sticky in ps:
        q=m.shift(pp,dp[t]); w.add(q)
        if (t-f)%6==1: w.add(m.shift(q,1))
    return w
def src_legal(c,owner,exclude=()):
    for t in range(6):
        q=m.shift(c,DISP[owner][t])
        fx=set()
        for k,(rp,o,ob,dr) in enumerate(src):
            if k in exclude: continue
            fx.add(m.shift(rp,DISP[o][t]))
        for pp,dp,f,target,sticky in ps:
            b=m.shift(pp,dp[t]); fx.add(b)
            if (t-f)%6==1: fx.add(m.shift(b,1))
        if q in fx: return False
        for j,cells in enumerate(ss):
            if j==owner: continue
            for delta in range(-S[owner][t],S[j][t]+1):
                for g in cells:
                    gt=m.shift(m.shift(g,DISP[j][t]),delta)
                    if sum(abs(a-b) for a,b in zip(gt,q))<=1: return False
    return True
res2=[r for r in res if src_legal(r[1],r[0])]
print(len(res2))
for r in res2: print(r)
