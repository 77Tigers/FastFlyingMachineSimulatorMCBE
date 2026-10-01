import model
m=model.m; S=m.S; DISP=m.DISP
def est_load(ss,ps,src):
    worst=0;detail={}
    for i in range(3):
        nsrc=sum(1 for p,o,ob,dr in src if o==i)
        for t in range(6):
            if not S[i][t]: continue
            riders=0
            for j,(pp,dp,f,tg,st) in enumerate(ps):
                if (t-f)%6 in (0,1): continue
                b=m.shift(pp,dp[t])
                if any(sum(abs(a-c) for a,c in zip(m.shift(g,DISP[i][t]),b))==1 for g in ss[i]): riders+=1
            L=len(ss[i])+nsrc+riders
            detail[(i,t)]=(len(ss[i]),nsrc,riders)
            worst=max(worst,L)
    return worst,detail
if __name__=='__main__':
    ss,ps,src=model.load_geometry()
    w,d=est_load(ss,ps,src); print(w); 
    for k,v in sorted(d.items()): print(k,v,sum(v))
