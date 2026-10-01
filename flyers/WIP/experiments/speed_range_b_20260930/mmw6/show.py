import sys
from pathlib import Path; sys.path.insert(0,str(Path(__file__).resolve().parents[5]))
from fastflyer import Flyer, Kind
f=Flyer.load(sys.argv[1]); which=[int(x) for x in sys.argv[2:]]
d={p:b for p,b in f.blocks()}
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
seen=set();comps=[]
for p,b in sorted(d.items()):
    if p in seen or b.kind not in (Kind.SLIME,Kind.HONEY):continue
    st=[p];seen.add(p);c=[p]
    while st:
        q=st.pop()
        for dd in D:
            r=(q[0]+dd[0],q[1]+dd[1],q[2]+dd[2])
            if r in d and r not in seen and d[r].kind==b.kind:seen.add(r);st.append(r);c.append(r)
    comps.append(c)
for i in which:
    c=comps[i];cs=set(c)
    att=set()
    for q in c:
        for dd in D:
            r=(q[0]+dd[0],q[1]+dd[1],q[2]+dd[2])
            if r in d and d[r].kind not in (Kind.SLIME,Kind.HONEY,Kind.PISTON_ARM,Kind.GLAZED_TERRACOTTA):att.add(r)
    allp=cs|att
    xs=[p[0] for p in allp];ys=[p[1] for p in allp];zs=[p[2] for p in allp]
    print('body',i,len(c),d[c[0]].kind.name,'x',min(xs),max(xs))
    sym={Kind.SLIME:'s',Kind.HONEY:'h',Kind.REDSTONE_BLOCK:'R'}
    dirs={0:'E',1:'W',2:'U',3:'D',4:'S',5:'N'}
    for y in range(min(ys),max(ys)+1):
        rows=[]
        for z in range(min(zs),max(zs)+1):
            row=''
            for x in range(min(xs),max(xs)+1):
                p=(x,y,z);b=d.get(p)
                if p not in allp: row+=' . ' if not (b is not None and b.kind!=Kind.PISTON_ARM) else ' + '
                elif b.kind==Kind.PISTON: row+='P'+dirs[b.direction]+' '
                elif b.kind==Kind.OBSERVER: row+='o'+dirs[b.direction]+' '
                else: row+=sym.get(b.kind,'?')+'  '
            rows.append(row)
        if any(set(r)-set(' .') for r in rows):
            print('y=%d'%y)
            for z,r in zip(range(min(zs),max(zs)+1),rows):print('%3d '%z+r)
