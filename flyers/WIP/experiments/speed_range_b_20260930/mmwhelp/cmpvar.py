import gen4,est,collections,time,sys,statistics
variant=sys.argv[1]; budget=float(sys.argv[2]); lay=eval(sys.argv[3])
kw=dict(orig={},rs=dict(share_rs=True),both=dict(share_rs=True,share_obs=True),obs=dict(share_obs=True))[variant]
res=[];st=collections.Counter();t0=time.time();seed=2000
while time.time()-t0<budget:
    seed+=1
    ans,reason=gen4.build2(seed,[(0,0),(0,lay[0]),(lay[1],lay[2])],**kw)
    if ans is None: st[reason]+=1; continue
    f,d=ans
    w,_=est.est_load([set(map(tuple,s)) for s in d['segments']],[(tuple(p),dp,ff,t,s) for p,dp,ff,t,s in d['pistons']],[(tuple(p),o,ob,dr) for p,o,ob,dr in d['sources']])
    res.append(w); st['ok']+=1
res.sort()
print(variant,lay,'n',len(res),'min',res[:5],'median',statistics.median(res),dict(st))
