"""Replace a rear body's redstone block by observer power on another (host) body.
For each push of rear body R (extend action at tick T, piston p), an observer on a host H that moved at tick T-2
pulses at T; it either faces p (soft power, not from p's front) or hard-powers a solid cell adjacent to p.
python rbobs.py OUT R [--lim=12] [--hard=1]   base: t100 snapshot (tick 0 = t100)."""
import sys, pathlib, re, itertools, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE.parent))
argv=sys.argv; sys.argv=['x']; import planner as P; sys.argv=argv
from fastflyer import Flyer, Kind, Block
DX = 14
bodies, _ = P.parse(str(HERE.parent/'orig.bodytrack.txt'))
glue = {b: {(c[0]+DX, c[1], c[2]): k for c, k in d['cells'].items()} for b, d in bodies.items() if d['glue']}
snaps = [{tuple(p): blk for p, blk in Flyer.load(str(HERE.parent/'snaps_orig'/f't{100+2*k}.flyer')).blocks()} for k in range(5)]
# t10 = t100 shifted by +3 (one period)
KM = {'sl': Kind.SLIME, 'ho': Kind.HONEY, 'RB': Kind.REDSTONE_BLOCK}
OFF = {b: [P.off(bodies[b]['word'], k) for k in range(6)] for b in glue}
def shift_of(k):
    def score(sh):
        return sum(1 for b, cs in glue.items() for c, kk in cs.items() if kk in KM and
                   snaps[k].get((c[0]+OFF[b][k]+sh, c[1], c[2])) is not None and snaps[k][(c[0]+OFF[b][k]+sh, c[1], c[2])].kind == KM[kk])
    best = max(range(-30, 30), key=score); tot = sum(len(cs) for cs in glue.values())
    print('snapshot', k, 'shift', best, 'match', score(best), '/', tot)
    return best
SH = [shift_of(k) for k in range(5)]
# re-key snapshots into t100 frame
snaps = [{(p[0]-SH[k], p[1], p[2]): v for p, v in snaps[k].items()} for k in range(5)]
def occ_at(k):
    o = {}
    for b, cs in glue.items():
        for c, kk in cs.items(): o[(c[0]+OFF[b][k], c[1], c[2])] = b
    return o
C = lambda s: tuple(int(v) for v in re.findall(r'-?\d+', s)[:3])
def pushes_of(R):
    L = open(HERE/'tr_t100.txt').read().splitlines(); out = []
    for i, l in enumerate(L):
        if l.startswith('ACTION') and ' extend ' in l and 'sources=0' not in l:
            T = int(l.split()[2]); p = C(l.split('piston=Some(')[1])
            if T >= 10: continue
            src = set(); j = i+1
            while j < len(L) and L[j].startswith(('SOURCE', 'LINK')):
                if L[j].startswith('SOURCE'): src.add(C(L[j][7:]))
                j += 1
            Rc = {(c[0]+OFF[R][T//2], c[1], c[2]) for c in glue[R]}
            if (p[0]+1, p[1], p[2]) in Rc: out.append((T, p))
    return out
SOLID = (Kind.SLIME, Kind.HONEY, Kind.REDSTONE_BLOCK, Kind.GLASS) if hasattr(Kind, 'GLASS') else (Kind.SLIME, Kind.HONEY)
HARD = (Kind.SLIME, Kind.HONEY)
FACES = P.FACES
CONN = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--conn=')), 1))
def placements(R, T, p, hard=True):
    k = T//2; kp = (k-1) % 5
    sn = snaps[k]; oc = occ_at(k)
    hosts = [b for b in glue if b != R and (OFF[b][k] - (OFF[b][k-1] if k else OFF[b][4]-3)) == 1]
    res = []
    targets = [(p, None)]
    if hard:
        for f in FACES:
            s = P.add(p, f)
            if f != (1, 0, 0) and s in sn and sn[s].kind in HARD: targets.append((s, f))
    for t, via in targets:
        for d, f in enumerate(FACES):
            q = (t[0]-f[0], t[1]-f[1], t[2]-f[2])   # observer at q facing +f hits t
            if t == p and f == (-1, 0, 0): continue  # source in front of piston
            if q in sn: continue
            if q in occ_at(k): continue
            for H in hosts:
                hk = Kind.SLIME if 'sl' in glue[H].values() else Kind.HONEY
                Hc = {c for c, v in oc.items() if v == H}
                def okglue(c, path):
                    if c in sn or c == q or c in path: return False
                    if (c[0]-OFF[H][k], c[1], c[2]) in snaps[0]: return False
                    for g in FACES:
                        n = P.add(c, g)
                        if n in path: continue
                        b2 = oc.get(n)
                        if b2 is not None and b2 != H and n in sn and sn[n].kind == hk: return False
                    return True
                def grow(path):
                    last = path[-1] if path else q
                    if any(P.add(last, g) in Hc for g in FACES):
                        yield list(path); return
                    if len(path) == CONN: return
                    for g in FACES:
                        n = P.add(last, g)
                        if okglue(n, path): yield from grow(path + [n])
                for path in grow([]):
                    sh = OFF[H][k]
                    q0 = (q[0]-sh, q[1], q[2])
                    if q0 in snaps[0]: continue
                    res.append((q0, d, H, t, via, tuple((c[0]-sh, c[1], c[2]) for c in path), hk))
    return res
if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); R = int(sys.argv[2])
    lim = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--lim=')), 12))
    out.mkdir(parents=True, exist_ok=True)
    pu = pushes_of(R); print('R', R, 'word', bodies[R]['word'], 'offsets', OFF[R], 'pushes', pu)
    opts = [placements(R, T, p) for T, p in pu]
    print('options per push', [len(o) for o in opts])
    rb = [c for c, k in glue[R].items() if k == 'RB']
    cnt = 0
    for combo in itertools.product(*opts):
        qs = [c[0] for c in combo] + [x for c in combo for x in c[5]]
        if len(set(qs)) < len(qs): continue
        g = Flyer.load(str(HERE.parent/'snaps_orig'/'t100.flyer')); g.push_limit = lim
        for c in rb: g.remove(c)
        for q0, d, H, t, via, path, hk in combo:
            g.set(q0, Block.observer(d))
            for c in path: g.set(c, Block(hk))
        name = 'R%d_' % R + '_'.join('o%d.%d.%dd%dH%dc%d' % (c[0]+(c[1],c[2],len(c[5]))) for c in combo)
        g.save(str(out/f'{name}.flyer')); cnt += 1
    print('wrote', cnt)
