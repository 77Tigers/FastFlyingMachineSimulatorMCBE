import model, itertools, collections
m=model.m;S=m.S;DISP=m.DISP
ss,ps,src=model.load_geometry()
def rec(f): return [t for t in range(6) if (t-f)%6 not in (0,1)]
def enum(j,kinds=(('beside',0),),maxn=3):
    pp,dp,f,tg,st=ps[j]
    R=rec(f)
    allo=[]
    for X in range(3):
        for cx in range(-8,9):
            for kind,dl in kinds:
                cov=frozenset(t for t in R if S[X][t] and (cx+DISP[X][t])==(pp[0]+dp[t]+dl))
                if cov: allo.append((X,cx,kind,cov))
    sols=[]
    for n in range(1,maxn+1):
        for combo in itertools.combinations(allo,n):
            cov=set();per=collections.defaultdict(set)
            for X,cx,k,c in combo: cov|=c;per[X]|=c
            if cov!=set(R): continue
            dbl=sum(1 for t in R if sum(1 for X in per if t in per[X])>1)
            # also doubles within the same body are fine
            if dbl==0: sols.append([(X,cx-pp[0],k,sorted(c)) for X,cx,k,c in combo])
    return R,sols
for j in range(4):
    R,sols=enum(j)
    print('piston',j,'target',ps[j][3],'f',ps[j][2],'R',R,'#zero-double covers (<=3 cells):',len(sols))
    seen=set()
    for s in sols[:12]: print('   ',s)
