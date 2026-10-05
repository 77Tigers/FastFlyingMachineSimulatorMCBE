# One glue deletion per body of pulling_loop4 (bodies from bodytrack boxes), encoded PL8.
import sys, itertools, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Kind
base = '../../../bank/pl9/pulling_loop4.flyer'
f0 = Flyer.load(base); cells = dict(f0.blocks())
glue = {p for p, b in cells.items() if b.kind in (Kind.SLIME, Kind.HONEY)}
D = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
seen=set(); bodies=[]
for g in sorted(glue):
    if g in seen: continue
    comp=[g]; seen.add(g); i=0
    while i<len(comp):
        p=comp[i]; i+=1
        for d in D:
            q=(p[0]+d[0],p[1]+d[1],p[2]+d[2])
            if q in glue and q not in seen and cells[q].kind==cells[p].kind: seen.add(q); comp.append(q)
    bodies.append(comp)
print([len(b) for b in bodies])
out = pathlib.Path(sys.argv[1]); out.mkdir(exist_ok=True)
lim = int(sys.argv[2]) if len(sys.argv)>2 else 8
for combo in itertools.product(*bodies):
    f = Flyer.load(base)
    for p in combo: f.remove(p)
    f.push_limit = lim
    f.save(out / ('d_' + '_'.join(f'{p[0]}.{p[1]}.{p[2]}' for p in combo) + '.flyer'))
