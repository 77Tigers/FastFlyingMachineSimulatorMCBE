"""Add a victim-observer pull (planner3 options) onto a snapshot-frame base and delete the replaced pusher.
python build.py BASE OUTDIR PULLER VICTIM SLOT DELX,DELY,DELZ [--conn=3 --oconn=3 --vconn=1 --max=200 --lims=13,14]
DEL is the replaced pusher's planner (base.bodytrack) coordinate; snapshot = planner - 2 in X (nearest non-sticky
piston within +-2 X is deleted, with its arm if extended)."""
import sys, pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']; import planner3x as P3; sys.argv = argv
from fastflyer import Flyer, Block, Kind
a = [x for x in sys.argv[1:] if not x.startswith('--')]
opt = {x.split('=')[0][2:]: x.split('=')[1] for x in sys.argv[1:] if x.startswith('--')}
base, out, Pb, V, s = a[0], pathlib.Path(a[1]), int(a[2]), int(a[3]), int(a[4])
dels = [tuple(int(v) for v in d.split(',')) for d in a[5].split(';')] if len(a) > 5 and a[5] != '-' else []
lims = [int(x) for x in opt.get('lims', '13,14').split(',')]
out.mkdir(parents=True, exist_ok=True)
B = Flyer.load(base); cells = {tuple(p): b for p, b in B.blocks()}
def snap(p): return (p[0] - 2, p[1], p[2])
rm = set()
for d in dels:
    q0 = snap(d); hit = None
    for dx in (0, -1, 1, -2, 2):
        q = (q0[0] + dx, q0[1], q0[2])
        if q in cells and cells[q].kind == Kind.PISTON and not cells[q].sticky: hit = q; break
    print('delete pusher', d, '->', hit, cells.get(hit) if hit else None)
    if hit is None: sys.exit('pusher not found')
    rm.add(hit)
    arm = (hit[0] + 1, hit[1], hit[2])
    if cells[hit].state != 0 and arm in cells and cells[arm].kind == Kind.PISTON_ARM: rm.add(arm)
res = P3.plan_options(Pb, V, s, conn=int(opt.get('conn', 3)), oconn=int(opt.get('oconn', 3)),
                      vconn=int(opt.get('vconn', 1)), limit=int(opt.get('max', 200)))
res.sort(key=lambda r: sum(r['cost'].values()))
print(len(res), 'options')
meta = []
for i, r in enumerate(res):
    add = {}; clash = False
    for (b, x), k in r['cells'].items():
        q = snap(x)
        if q in cells and q not in rm: clash = True; break
        if k == 'sl': add[q] = Block(Kind.SLIME)
        elif k == 'ho': add[q] = Block(Kind.HONEY)
        elif k == 'S': add[q] = Block(Kind.PISTON, direction=1, sticky=True)
        elif k == 'O': add[q] = Block.observer(P3.FACES.index(r['obs_dir']))
        else: raise ValueError(k)
    if clash: continue
    for lim in lims:
        g = Flyer.load(base); g.push_limit = lim
        for q in rm: g.remove(q)
        for q, blk in add.items(): g.set(q, blk)
        name = f'P{Pb}V{V}s{s}{opt.get("tag","")}_o{i:03d}_L{lim}'
        g.save(str(out / f'{name}.flyer'))
    meta.append(dict(i=i, Q=r['Q'], cost={str(k): v for k, v in r['cost'].items()}, via=r['via'],
                     cells=[[b, list(x), k] for (b, x), k in r['cells'].items()]))
json.dump(meta, open(out / 'options.json', 'w'), indent=0)
print('built', len(meta), 'options x', len(lims))
