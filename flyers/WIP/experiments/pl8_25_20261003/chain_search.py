# Abstract checker: infinite staircase chain of identical rigid bodies, K even = mmww (moves s0,s1; fires s2),
# K odd = wwmm (moves s2,s3; fires s0). Each body: sticky S at origin facing -X (pulls K-1), pusher P facing +X
# (pushes K+1), glue cells, redstone blocks R (power by adjacency). Bodies alternate slime/honey.
import itertools, sys, json
E=(1,0,0); D6=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
DIRS={'O0':(1,0,0),'O1':(-1,0,0),'O2':(0,1,0),'O3':(0,-1,0),'O4':(0,0,1),'O5':(0,0,-1)}
M=[0,1,2,2]; W=[1,1,1,2]
def org(K,t,dl):
    base=2*K+(M[t] if K%2==0 else W[t])
    return (base+K*dl[0],K*dl[1],K*dl[2])
def fire(K): return 2 if K%2==0 else 0
def moves(K,t): return (t in (0,1)) if K%2==0 else (t in (2,3))
def check(T,dl,NB=6,power=True):
    # T: dict local->kind ('S','P','g','R')
    S=(0,0,0); P=[c for c,k in T.items() if k=='P'][0]
    glue={c for c,k in T.items() if k=='g'}
    Ks=range(NB)
    def world(K,t): o=org(K,t,dl); return {add(o,c):(K,k) for c,k in T.items()}
    for t in range(4):
        occ={}
        for K in Ks:
            for c,v in world(K,t).items():
                if c in occ: return 'overlap'
                occ[c]=v
        # arms present at slot start t for pistons that fired at t-1 (about to retract)
        for K in Ks:
            if (fire(K)+1)%4==t:
                o=org(K,t,dl)
                for pc,dd in ((add(o,P),E),):
                    a=add(pc,dd)
                    if a in occ: return 'arm_blocked_t%d'%t
                    occ[a]=(K,'A')
        busy=lambda K:(t==fire(K) or t==(fire(K)+1)%4)
        # push/pull actions
        for K in Ks:
            o=org(K,t,dl)
            if t==fire(K) and K+1 in Ks:
                tgt=add(add(o,P),E)
                v=occ.get(tgt)
                if not v or v[0]!=K+1 or v[1]!='g': return 'push_target'
            if t==fire(K):
                a=add(add(o,S),(-1,0,0))
                if a in occ: return 'sticky_ext_blocked'
                # also must not be entered by a body moving this slot
                for J in Ks:
                    if J!=K and moves(J,t):
                        for c in world(J,t):
                            if add(c,E)==a: return 'sticky_ext_collide'
            if t==(fire(K)+1)%4 and K-1 in Ks:
                tgt=add(add(o,S),(-2,0,0))
                v=occ.get(tgt)
                if not v or v[0]!=K-1 or v[1]!='g': return 'pull_target'
        # moving bodies: destinations + adhesion
        for J in Ks:
            if not moves(J,t): continue
            wj=world(J,t)
            for c,(_,k) in wj.items():
                d=add(c,E); v=occ.get(d)
                if v and v[0]!=J:
                    # allowed: the pusher arm of J-1 is behind, not in front; pushing into another body's cell forbidden
                    return 'dest_blocked'
                if k=='g':
                    for dd in D6:
                        n=add(c,dd); v=occ.get(n)
                        if v and v[0]!=J:
                            kk=v[1]
                            if kk=='A': continue
                            if kk=='g' and (v[0]%2)!=(J%2): continue  # slime vs honey
                            if kk in 'SP' and busy(v[0]): continue
                            if kk=='A': continue
                            return 'adhesion_%s'%kk
        if not power: continue
        pulsing=lambda J: moves(J,(t-1)%4)
        hot=set()
        for J in Ks:
            if not pulsing(J): continue
            o=org(J,t,dl)
            for c,k in T.items():
                if k[0]=='O':
                    f=add(add(o,c),DIRS[k]); v=occ.get(f)
                    if v and v[1]=='g': hot.add(f)
        # power: each piston powered iff t==fire
        for K in Ks:
            o=org(K,t,dl)
            for pc,front in ((add(o,S),add(add(o,S),(-1,0,0))),(add(o,P),add(add(o,P),E))):
                pw=False
                for dd in D6:
                    n=add(pc,dd)
                    if n==front: continue
                    v=occ.get(n)
                    if v and v[1]=='R': pw=True
                    if n in hot: pw=True
                    if v and v[1][0]=='O' and pulsing(v[0]) and add(n,DIRS[v[1]])==pc: pw=True
                want=(t==fire(K))
                if K in (1,2,3,4) and pw!=want and not (busy(K) and t!=fire(K) and False):
                    # extended piston at t_f+1 must be unpowered to retract; others unpowered
                    return 'power_K%d_t%d_%s'%(K,t,'missing' if want else 'extra')
    return 'ok'
def connected(T):
    glue=[c for c,k in T.items() if k=='g']
    if not glue: return False
    seen={glue[0]}; st=[glue[0]]
    while st:
        c=st.pop()
        for dd in D6:
            n=add(c,dd)
            if n in T and T[n]=='g' and n not in seen: seen.add(n); st.append(n)
    if len(seen)!=len(glue): return False
    return all(any(add(c,dd) in seen for dd in D6) for c,k in T.items() if k!='g')
if __name__=='__main__':
    maxg=int(sys.argv[1]); maxr=int(sys.argv[2])
    R=1
    box=[(x,y,z) for x in range(-2,3) for y in range(-2,3) for z in range(-2,3) if (x,y,z)!=(0,0,0)]
    near=[c for c in box if abs(c[0])+abs(c[1])+abs(c[2])<=3]
    found=[]; tried=0; fails={}
    for P in [c for c in near if abs(c[0])+abs(c[1])+abs(c[2])<=2]:
        gcand=[c for c in near if c!=P and max(map(abs,c))<=1]
        for ng in range(1,maxg+1):
            for G in itertools.combinations(gcand,ng):
                T={(0,0,0):'S',P:'P'}
                for g in G: T[g]='g'
                if not connected(T): continue
                # pull target: S_{K+1} - 2e at t pull == glue of K ; solve dl from each glue choice
                for gp in G:
                    # K=1 (odd) pulls K=0 at t=1 : org(1,1)+S-2e == org(0,1)+gp
                    o1=org(1,1,(0,0,0)); o0=org(0,1,(0,0,0))
                    dl=sub(add(o0,gp),add(o1,(-2,0,0)))
                    if check(T,dl,power=False)!='ok': fails['kin']=fails.get('kin',0)+1; continue
                    rest=[c for c in box if c not in T]
                    adj=[c for c in rest if any(add(c,dd) in G for dd in D6)]
                    opts=[]
                    for nr in range(0,min(maxr,1)+1):
                        for Rs in itertools.combinations(adj,nr):
                            opts.append({r:'R' for r in Rs})
                            if nr==0:
                                for oc in adj:
                                    for od in range(6): opts.append({oc:'O%d'%od})
                            if nr==0 and maxr>=2:
                                for oc,oc2 in itertools.combinations(adj,2):
                                    for od in range(6):
                                        for od2 in range(6): opts.append({oc:'O%d'%od,oc2:'O%d'%od2})
                            if nr==1:
                                for oc in adj:
                                    if oc in Rs: continue
                                    for od in range(6): d={r:'R' for r in Rs}; d[oc]='O%d'%od; opts.append(d)
                    for extra in opts:
                            T2=dict(T); T2.update(extra)
                            tried+=1
                            res=check(T2,dl)
                            fails[res]=fails.get(res,0)+1
                            if res=='ok':
                                found.append((len(T2),T2,dl)); print('FOUND',len(T2),dl,sorted(T2.items()),flush=True)
    print('tried',tried); print(sorted(fails.items(),key=lambda x:-x[1])[:12])
