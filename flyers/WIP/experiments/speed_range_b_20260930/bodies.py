import sys
from pathlib import Path; sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Kind
f=Flyer.load(sys.argv[1])
d={p:b for p,b in f.blocks()}
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def sticks(a,b):
    # slime/honey adhere to neighbours, but not slime<->honey nor glazed; pistons arms etc ignore
    ka,kb=a.kind,b.kind
    if ka in (Kind.SLIME,Kind.HONEY):
        if kb in (Kind.SLIME,Kind.HONEY): return ka==kb
        if kb==Kind.GLAZED_TERRACOTTA: return False
        return True
    return False
seen={};comps=[]
for p,b in d.items():
    if p in seen or b.kind==Kind.PISTON_ARM: continue
    if b.kind not in (Kind.SLIME,Kind.HONEY): continue
    stack=[p];seen[p]=len(comps);c=[p]
    while stack:
        q=stack.pop()
        for dd in D:
            r=(q[0]+dd[0],q[1]+dd[1],q[2]+dd[2])
            if r in d and d[r].kind in (Kind.SLIME,Kind.HONEY) and r not in seen and d[r].kind==d[q].kind:
                seen[r]=len(comps);stack.append(r);c.append(r)
    comps.append(c)
from collections import Counter
for i,c in enumerate(comps):
    att=set()
    for q in c:
        for dd in D:
            r=(q[0]+dd[0],q[1]+dd[1],q[2]+dd[2])
            if r in d and d[r].kind not in (Kind.SLIME,Kind.HONEY,Kind.PISTON_ARM,Kind.GLAZED_TERRACOTTA): att.add(r)
    cnt=Counter(d[p].kind.name+('S' if d[p].kind==Kind.PISTON and d[p].sticky else '') for p in att)
    xs=[p[0] for p in c]
    print(i,d[c[0]].kind.name,len(c),'attached',dict(cnt),'load',len(c)+len(att),'x',min(xs),max(xs))
