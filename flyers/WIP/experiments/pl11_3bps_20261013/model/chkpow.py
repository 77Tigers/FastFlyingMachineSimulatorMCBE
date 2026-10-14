import sys,pickle
sys.path.insert(0,'../../two_bps_20261007')
import satflyer5 as S
d=pickle.load(open(sys.argv[1],'rb')); sol=d['sol']; NS=5
D6=S.D6
def pos(c,w,t): return (c[0]+S.wpos(w,t),c[1],c[2])
# carriers: ride causes
ride={(t,r):j for (t,r,k,j,_) in [(c[0],c[1],c[2],c[3],c[4]) for c in d['causes']] if k=='ride'} if False else {}
for c in d['causes']:
    if c[2]=='ride': ride[(c[0],c[1])]=c[3]
w_of={n:w for n,w,_,_ in sol}
for t in range(NS):
    cells={}   # position -> (name,kind)
    for n,w,cs,m in sol:
        for c,k in cs.items():
            # riders: position follows the carrier's moves when they ride; use body's own word (single-piston rider word)
            cells[pos(c,w,t)]=(n,k)
    soft=set(); hot=set(); obs={}
    for p,(n,k) in cells.items():
        if k=='R' or k[0]=='D': soft.add(p)
        if k[0]=='D': hot.add((p[0]+D6[int(k[1])][0],p[1]+D6[int(k[1])][1],p[2]+D6[int(k[1])][2]))
        if k[0]=='O' and (t-1)%NS in w_of[n]:
            f=tuple(p[i]+D6[int(k[1])][i] for i in range(3)); hot.add(f); obs[f]=p
    hot={h for h in hot if h in cells and cells[h][1]=='g'}
    for p,(n,k) in sorted(cells.items()):
        if k[0] in 'PS' and k[1:2].isdigit():
            ph=S.kphase(k,t,NS); fd=(1,0,0) if k[0]=='P' else (-1,0,0)
            front=(p[0]+fd[0],p[1],p[2]); src=[]
            for dd in D6:
                nb=(p[0]+dd[0],p[1]+dd[1],p[2]+dd[2])
                if nb==front: continue
                if nb in soft: src.append(('soft',nb,cells[nb]))
                if nb in hot: src.append(('hot',nb))
            if p in obs and obs[p]!=front: src.append(('obs',obs[p]))
            print(t,n,k,p,ph,src)
