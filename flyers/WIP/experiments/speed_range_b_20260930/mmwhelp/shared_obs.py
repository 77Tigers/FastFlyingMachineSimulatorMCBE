import model
m=model.m;S=m.S;DISP=m.DISP;D=m.D
ss,ps,src=model.load_geometry()
def dist1(a,b): return sum(abs(x-y) for x,y in zip(a,b))==1
# observer ports per body = pistons whose own source is an observer
obs_ports={}
for i in range(3):
    ports=[]
    for j,(pp,dp,f,tg,st) in enumerate(ps):
        if tg==i:
            # find the source adjacent at slot f
            pass
    obs_ports[i]=None
# simple: identify observer ports by sources list order: sources[k] belongs to ps[k]
obsj={i:[k for k,(p,o,ob,dr) in enumerate(src) if o==i and ob] for i in range(3)}
print(obsj)
cells=[p for s in ss for p in s]
lo=[min(p[k] for p in cells)-3 for k in range(3)];hi=[max(p[k] for p in cells)+3 for k in range(3)]
for i in range(3):
    want={(j,ps[j][2]) for j in obsj[i]}
    found=[]
    for x in range(lo[0],hi[0]+1):
      for y in range(lo[1],hi[1]+1):
        for z in range(lo[2],hi[2]+1):
            G=(x,y,z)
            powered=set()
            for t in range(6):
                if not S[i][(t-1)%6]: continue
                g=m.shift(G,DISP[i][t])
                for j,(pp,dp,f,tg,st) in enumerate(ps):
                    b=m.shift(pp,dp[t])
                    if dist1(g,b) and g!=m.shift(b,1): powered.add((j,t))
            if powered==want: found.append(G)
    print(i,want,len(found),found[:10])
