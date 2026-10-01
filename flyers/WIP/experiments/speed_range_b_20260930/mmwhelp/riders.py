import json,sys,model,lazy
m=model.m;S=m.S;DISP=m.DISP
d=json.load(open(sys.argv[1]))
ss=[set(map(tuple,s)) for s in d['segments']];ps=[(tuple(p),dp,f,t,st) for p,dp,f,t,st in d['pistons']];src=[(tuple(p),o,ob,dr) for p,o,ob,dr in d['sources']]
need={(j,t) for j,(pp,dp,f,tg,st) in enumerate(ps) for t in lazy.recovery(f)}
for i in range(3):
    for t in range(6):
        if not S[i][t]: continue
        rid=[]
        for j,(pp,dp,f,tg,st) in enumerate(ps):
            if (t-f)%6 in (0,1): continue
            b=m.shift(pp,dp[t])
            if any(sum(abs(a-c) for a,c in zip(m.shift(g,DISP[i][t]),b))==1 for g in ss[i]): rid.append((j,tg))
        print('body',i,'slot',t,'riders',len(rid),rid)
