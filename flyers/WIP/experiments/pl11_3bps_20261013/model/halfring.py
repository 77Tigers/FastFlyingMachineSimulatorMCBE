"""Full 10-segment L0 back loop with rot180 symmetry: free bodies S0..S4, S_{k+5} = R(S_k) (+ same riders).
Ring order S0->S1->...->S9->S0 (S_k carries the spent pushers of S_{k+1}; S_{k+1}'s word = S_k's shifted by D=3).
Each body: first two moves by hopping rider pushers, third move supplied externally (pull by L1).
Bodies are placed in yz boxes around the X axis: S_k centred at angle 36k on a circle of radius rad.
usage: python halfring.py L [--rad 3] [--r 1] [--xr m1:2] [--rxr m3:1] [--rr 2] [--tl 600] [--workers 8] [--maxglue 7]
"""
import sys, pathlib, itertools, argparse, pickle, time, math
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'two_bps_20261007'))
from satflyer5 import FlyerSAT, pinfo, show, to_flyer, Infeasible

NS, D = 5, 3
ROTK = {'D2': 'D3', 'D3': 'D2', 'D4': 'D5', 'D5': 'D4', 'O2': 'O3', 'O3': 'O2', 'O4': 'O5', 'O5': 'O4'}
def R(u): return (u[0], -u[1], -u[2])
def Rk(k): return ROTK.get(k, k)
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def rng(s):
    a, b = (int(z) for z in s.replace('m', '-').split(':')); return range(a, b + 1)


def shiftk(k, d):
    p = pinfo(k)
    if p is None: return k
    return f'{p[0]}{(p[1] + d) % NS}' + ('h' if p[2] == 2 else '')


def build(L, centers, body_r, xr, rxr, rider_r, maxglue=7, kinds=None, word0=(0, 1, 2), extpull=True, sym=True,
          xoff=None):
    """centers: yz centre per body k=0..9 (k>=5 must equal R(center[k-5])). xoff: per-body x offset of box (slot-0)."""
    kinds = kinds or ['g', 'R'] + [f'D{d}' for d in range(6)] + [f'O{d}' for d in range(6)]
    N = 10
    xoff = xoff or [0] * N
    segs = []
    for k in range(N):
        first = [(word0[j] + k * D) % NS for j in range(3)]
        w = tuple(sorted(first))
        cy, cz = centers[k]
        bx = [(x + xoff[k], cy + dy, cz + dz) for x in rng(xr) for dy in range(-body_r, body_r + 1)
              for dz in range(-body_r, body_r + 1)]
        segs.append(dict(name=f'S{k}', k=k, word=w, first=first, box=bx, rider=False, kinds=list(kinds)))
        for j in range(2):
            f = first[j]
            rw = tuple(sorted(s for s in range(NS) if s not in (f, (f + 1) % NS)))
            rb = [(x + xoff[k], cy + dy, cz + dz) for x in rng(rxr) for dy in range(-rider_r, rider_r + 1)
                  for dz in range(-rider_r, rider_r + 1)]
            segs.append(dict(name=f'P{k}{j}', k=k, word=rw, first=None, box=rb, rider=True, kinds=[f'P{f}']))
    names = [s['name'] for s in segs]
    opn = {s['name']: {f"ext_{s['first'][2]}"} for s in segs if not s['rider'] and extpull}
    S = FlyerSAT([s['word'] for s in segs], None, L, NS=NS, kinds=kinds, leaf=True, maxglue=maxglue,
                 boxes=[s['box'] for s in segs], names=names, open_segs=opn,
                 riders=[s['name'] for s in segs if s['rider']], kinds_by_seg={s['name']: s['kinds'] for s in segs})
    if sym:
        # S_{k+5} = R(S_k) at the same time: words identical (5*D = 15 = 0 mod 5), so slot-0 cells map by R.
        for s in segs:
            if s['k'] < 5: continue
            src = names.index(s['name'][0] + str(s['k'] - 5) + s['name'][2:])
            si = names.index(s['name'])
            boxset = set(segs[si]['box'])
            for u in segs[src]['box']:
                ru = R(u)
                for kd in S.kinds_of(src):
                    lit = S.X[src, u, kd]
                    if ru in boxset and (si, ru, Rk(kd)) in S.X:
                        S.m.Add(S.X[si, ru, Rk(kd)] == lit)
                    else:
                        S.m.Add(lit == 0)
            if not s['rider']:
                S.m.Add(S.mat[si] == S.mat[src])
    return S, segs


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('--rad', type=float, default=3.0)
    ap.add_argument('--r', type=int, default=1); ap.add_argument('--rr', type=int, default=2)
    ap.add_argument('--xr', default='m1:2'); ap.add_argument('--rxr', default='m3:1')
    ap.add_argument('--tl', type=float, default=600); ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--maxglue', type=int, default=7); ap.add_argument('--tag', default='')
    ap.add_argument('--layout', default='circle')
    a = ap.parse_args()
    if a.layout == 'circle':
        half = [(round(a.rad * math.cos(math.radians(36 * k + 18))), round(a.rad * math.sin(math.radians(36 * k + 18))))
                for k in range(5)]
    else:  # explicit "y,z;y,z;..." for S0..S4
        half = [tuple(int(z) for z in p.replace('m', '-').split(',')) for p in a.layout.split(';')]
    centers = half + [(-y, -z) for y, z in half]
    print('centers', centers, flush=True)
    t0 = time.time()
    S, segs = build(a.L, centers, a.r, a.xr, a.rxr, a.rr, maxglue=a.maxglue)
    st, dt = S.solve(a.tl, a.workers, objective='maxload')
    print(f'L={a.L} -> {st} {dt:.1f}s (build {time.time() - t0 - dt:.1f}s)', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = S.extract(); ld = S.loads()
        print('maxload', max(ld.values()), ld)
        print(show(sol))
        print(S.causes())
        out = HERE / 'runs_halfring'; out.mkdir(exist_ok=True)
        tag = f'L{a.L}_rad{a.rad}{a.tag}'
        pickle.dump({'sol': sol, 'loads': ld, 'causes': S.causes(), 'centers': centers}, open(out / f'{tag}.pkl', 'wb'))
        to_flyer(sol, max(ld.values()), NS).save(str(out / f'{tag}.flyer'))
