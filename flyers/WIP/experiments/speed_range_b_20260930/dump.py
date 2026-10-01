import sys
from pathlib import Path; sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Kind
f=Flyer.load(sys.argv[1])
print('limit',f.push_limit,'rng',f.rng_state,'phase',f.phase_x,f.phase_z)
bl=f.blocks()
from collections import Counter
print(Counter(b.kind.name+('S' if b.kind==Kind.PISTON and b.sticky else '') for p,b in bl))
sym={Kind.SLIME:'s',Kind.HONEY:'h',Kind.SMOOTH_STONE:'#',Kind.GLASS:'g',Kind.GLAZED_TERRACOTTA:'G',Kind.REDSTONE_BLOCK:'R',Kind.ROD:'r',Kind.PISTON_ARM:'-'}
dirs={0:'E',1:'W',2:'U',3:'D',4:'S',5:'N'}
d={p:b for p,b in bl}
ys=sorted({p[1] for p,_ in bl})
xs=[p[0] for p,_ in bl]; zs=[p[2] for p,_ in bl]
for y in ys:
    print('--- y=%d (rows z, cols x %d..%d)'%(y,min(xs),max(xs)))
    for z in range(min(zs),max(zs)+1):
        row=''
        for x in range(min(xs),max(xs)+1):
            b=d.get((x,y,z))
            if b is None: row+=' . '
            elif b.kind==Kind.PISTON: row+=('P' if not b.sticky else 'Q')+dirs[b.direction]
            elif b.kind==Kind.OBSERVER: row+='o'+dirs[b.direction]
            else: row+=sym.get(b.kind,'?')+(' ' if not b.moving else '*')
            row+=' ' if len(row)%3==2 else ''
        print('%3d '%z+row)
