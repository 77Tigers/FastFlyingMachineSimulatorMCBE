import model, itertools
m=model.m;S=m.S;DISP=m.DISP
ss,ps,src=model.load_geometry()
def rec(f): return [t for t in range(6) if (t-f)%6 not in (0,1)]
KINDS=(('beside',0),('front',1))
def analyse(j):
    pp,dp,f,tg,st=ps[j]
    R=rec(f)
    # options per body X: (cx,kind) -> covered slots
    opts={}
    for X in range(3):
        o=[]
        for cx in range(-8,9):
            for kind,dl in KINDS:
                cov=frozenset(t for t in R if S[X][t] and (cx+DISP[X][t])==(pp[0]+dp[t]+dl))
                if cov: o.append(((cx,kind),cov))
        opts[X]=o
    best=None
    # choose up to 1..2 cells per body, total <=4
    allo=[(X,k,c) for X in range(3) for k,c in opts[X]]
    for n in range(1,5):
        for combo in itertools.combinations(allo,n):
            cov=set()
            per={}
            for X,k,c in combo:
                cov|=c
                per.setdefault(X,set()).update(c)
            if cov!=set(R): continue
            dbl=sum(1 for t in R if sum(1 for X in per if t in per[X])>1)
            # distinct bodies count
            key=(dbl,n,len(per))
            if best is None or key<best[0]: best=(key,combo)
        if best and best[0][0]==0 and n>=1 and best[0][1]==n: break
    return R,best
for j in range(4):
    R,b=analyse(j)
    print('piston',j,'f',ps[j][2],'R',R,'best (doubles,ncells,nbodies)',b[0],[(X,k) for X,k,c in b[1]])
