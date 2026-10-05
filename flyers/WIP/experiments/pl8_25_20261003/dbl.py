import sys, random, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind
base='../../../bank/pl9/human_observer_hop.flyer'; out=pathlib.Path('e3'); out.mkdir(exist_ok=True)
f0=Flyer.load(base); cells=dict(f0.blocks())
glue=[p for p,b in cells.items() if b.kind in (Kind.SLIME,Kind.HONEY)]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
random.seed(1); seen=set()
while len(seen)<6000:
    f=Flyer.load(base); occ=dict(cells); tag=[]
    for _ in range(2):
        g=random.choice([p for p in occ if occ[p].kind in (Kind.SLIME,Kind.HONEY)])
        del occ[g]; f.remove(g)
        em=sorted({(p[0]+d[0],p[1]+d[1],p[2]+d[2]) for p in occ for d in D}-set(occ))
        e=random.choice(em); b=Block(random.choice([Kind.SLIME,Kind.SLIME,Kind.HONEY]))
        occ[e]=b; f.set(e,b); tag.append(f'{g}{e}{b.kind.name[0]}')
    k=''.join(tag)
    if k in seen: continue
    seen.add(k); f.push_limit=8; f.save(out/f'c{len(seen):05d}.flyer')
