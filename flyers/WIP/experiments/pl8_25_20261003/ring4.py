# 4-segment rigid ring at 2.5 bps (all mmww/wwmm, no hopping): A,B1 move s0,s1; B,A1 move s2,s3.
# B pushes A,B1 at s0; A1's stickies pull A,B1 at s1. A pushes B,A1 at s2; B1's stickies pull B,A1 at s3.
# Each pushed segment carries redstone blocks touching (from the side) its pusher and its puller at the push slot.
import sys, itertools, random, pathlib
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind
D6=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a,b): return tuple(x+y for x,y in zip(a,b))
MOV={'A':[0,1,2,2],'B1':[0,1,2,2],'B':[0,0,0,1],'A1':[0,0,0,1]}
def gen(lanes,u,up,rng,lim):
    al,be,ga,de=lanes
    L=lambda x,l:(x,l[0],l[1])
    body={k:{} for k in MOV}   # s0 absolute coords -> (kind)
    body['B'][L(0,al)]='P'; body['A'][L(1,al)]='g'; body['A1'][L(4,al)]='S'
    body['B'][L(0,be)]='P'; body['B1'][L(1,be)]='g'; body['A1'][L(4,be)]='S'
    # lanes at s2 (M bodies +2): pusher at u (s2) => s0 u-2
    body['A'][L(u-2,ga)]='P'; body['B'][L(u+1,ga)]='g'; body['B1'][L(u+2,ga)]='S'
    body['A'][L(up-2,de)]='P'; body['A1'][L(up+1,de)]='g'; body['B1'][L(up+2,de)]='S'
    # RB: for M segment X pushed at s0 by pusher at c (s0) and pulled by sticky at s (s0): RB side of each at s0.
    pushers={'A':L(0,al),'B1':L(0,be),'B':L(u,ga),'A1':L(up,de)}   # pusher pos at push slot (s0 or s2), absolute at that slot
    stickies={'A':L(4,al),'B1':L(4,be),'B':L(u+4,ga),'A1':L(up+4,de)}
    shift={'A':0,'B1':0,'B':-2,'A1':-2}  # segment frame at its push slot vs s0: W pushed at s2, M bodies moved +2 by then; W at s2 same as s0
    # Express W push slot (s2): W bodies unmoved since s0 -> RB cell at s2 abs = s0 abs. Pusher (on M body) at s2 abs given.
    for X in body:
        for tgt in (pushers[X],stickies[X]):
            sides=[add(tgt,d) for d in D6[2:]]
            rng.shuffle(sides)
            for c in sides:
                if all(c not in body[Y] for Y in body): body[X][c]='R'; break
            else: return None
    # swept cells of each body relative to its own frame: other bodies' cells at all 4 slots
    def at(Y,t): m=MOV[Y][t]; return {add(c,(m,0,0)) for c in body[Y]}
    def blocked_for(X):
        bad=set()
        for t in range(4):
            mx=MOV[X][t]
            for Y in body:
                if Y==X: continue
                for c in at(Y,t):
                    for dx in (0,1,-1):  # include movement sweep
                        bad.add(add(c,(dx-mx,0,0)))
        # arms of pushers / stickies in their lanes
        return bad
    out={}
    for X in body:
        bad=blocked_for(X); cells=dict(body[X])
        comps=[c for c in cells]
        # connect all components with BFS glue (Steiner greedy from first glue cell)
        start=[c for c,k in cells.items() if k=='g'][0]
        tree={start}
        for c in comps:
            if c in tree: continue
            if any(add(c,d) in tree and cells.get(add(c,d))=='g' for d in D6) or any(add(c,d) in tree and cells.get(add(c,d),'g')=='g' and add(c,d) not in cells for d in D6):
                tree.add(c); continue
            # BFS from tree glue cells to a free cell adjacent to c
            q=deque(); prev={}
            for s in tree:
                if cells.get(s,'g')=='g': q.append(s); prev[s]=None
            goal=None
            while q:
                p=q.popleft()
                if any(add(p,d)==c for d in D6): goal=p; break
                for d in D6:
                    n=add(p,d)
                    if n in prev or n in bad or (n in cells and cells[n]!='g') : continue
                    if max(abs(n[1]),abs(n[2]))>3 or n[0]<-4 or n[0]>9: continue
                    if any(n in body[Y] for Y in body if Y!=X): continue
                    prev[n]=p; q.append(n)
            if goal is None: return None
            p=goal
            while p is not None:
                if p not in cells: cells[p]='g'
                tree.add(p); p=prev[p]
            tree.add(c)
        out[X]=cells
    f=Flyer(); f.push_limit=lim
    mat={'A':Kind.SLIME,'B':Kind.HONEY,'A1':Kind.SLIME,'B1':Kind.HONEY}
    occ=set()
    for X,cells in out.items():
        for c,k in cells.items():
            if c in occ: return None
            occ.add(c)
            if k=='g': f.set(c,Block(mat[X]))
            elif k=='R': f.set(c,Block(Kind.REDSTONE_BLOCK))
            elif k=='P': f.set(c,Block.piston(0))
            elif k=='S': f.set(c,Block.piston(1,sticky=True))
    return f,{X:len(c) for X,c in out.items()}
if __name__=='__main__':
    out=pathlib.Path(sys.argv[1]); out.mkdir(exist_ok=True); n=int(sys.argv[2]); lim=int(sys.argv[3])
    rng=random.Random(0); grid=[(y,z) for y in range(-1,2) for z in range(-1,2)]
    k=0; tries=0
    while k<n and tries<200000:
        tries+=1
        lanes=rng.sample(grid,4); u=rng.randint(0,4); up=rng.randint(0,4)
        if rng.random()<0.5: matswap=True
        r=gen(lanes,u,up,rng,lim)
        if not r: continue
        f,sz=r
        k+=1; f.save(out/f'r{k:04d}_{max(sz.values())}.flyer')
    print(k,'built of',tries)
