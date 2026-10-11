"""Pinned-skeleton search for the closed 2-body 2 bps engine (NS=5):
  B0 word {0,1}: pusher P2 at Bp pushes B1 at slot 2, sticky S3 at T pulls B1 at slot 4.
  B1 word {2,4}: pusher P0 at A=(0,0,0) pushes B0 at slot 0, sticky S0 at Sp pulls B0 at slot 1.
Target glue (slot-0 world frame): q0 = A+E, g0 = Sp-3E (B0);  q1 = Bp+3E, g1 = T-E (B1).
Skeleton = (Sp, Bp, T); each pinned with `must`, glue/power free in small boxes around it.
usage: python skel2.py L [--gb0 4] [--gb1 3] [--tl 20] [--workers 2] [--part i/n] [--out tag]
"""
import sys, pathlib, itertools, pickle, argparse, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from satflyer5 import FlyerSAT, show, to_flyer, Infeasible, D6, add

NS = 5
E = (1, 0, 0)


def d1(a, b): return sum(abs(a[i] - b[i]) for i in range(3))


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def nbrs(c): return [add(c, d) for d in D6]


def bbox(cells, ex):
    lo = [min(c[i] for c in cells) - ex for i in range(3)]
    hi = [max(c[i] for c in cells) + ex for i in range(3)]
    return list(itertools.product(*[range(lo[i], hi[i] + 1) for i in range(3)]))


def skeletons(gb0, gb1, R=3):
    A = (0, 0, 0); q0 = (1, 0, 0)
    rng = list(itertools.product(range(-R, R + 3), range(-2, 3), range(-2, 3)))
    out = []
    for Sp in rng:
        g0 = sub(Sp, (3, 0, 0))
        if Sp == A or d1(g0, q0) > gb0 - 1: continue
        if d1(A, Sp) > gb1 + 1: continue          # both attach to <= gb1 connected glue
        for Bp in rng:
            q1 = add(Bp, (3, 0, 0))
            if d1(Bp, q0) > gb0 or d1(Bp, g0) > gb0: continue
            if d1(q1, A) > gb1 or d1(q1, Sp) > gb1: continue
            for T in rng:
                g1 = sub(T, E)
                if d1(T, q0) > gb0 or d1(T, g0) > gb0: continue
                if d1(g1, q1) > gb1 - 1 or d1(g1, A) > gb1 or d1(g1, Sp) > gb1: continue
                cells = [A, Sp, q0, g0, Bp, T, q1, g1]
                if len(set(cells)) < 8: continue
                # y/z symmetry: canonical under y<->z swap and sign flips of y, z
                out.append((Sp, Bp, T))
    # canonicalise under the 8 yz symmetries (A fixed at origin, x unchanged)
    def tr(c, k):
        y, z = c[1], c[2]
        if k & 4: y, z = z, y
        if k & 1: y = -y
        if k & 2: z = -z
        return (c[0], y, z)
    canon = {}
    for s in out:
        key = min(tuple(tr(c, k) for c in s) for k in range(8))
        canon.setdefault(key, s)
    return sorted(canon)


def solve(sk, L, tl, workers, kinds):
    Sp, Bp, T = sk
    A = (0, 0, 0); q0 = (1, 0, 0); g0 = sub(Sp, (3, 0, 0)); q1 = add(Bp, (3, 0, 0)); g1 = sub(T, E)
    must = {'B0': {q0: 'g', g0: 'g', Bp: 'P2', T: 'S3'}, 'B1': {A: 'P0', Sp: 'S0', q1: 'g', g1: 'g'}}
    b0 = bbox([q0, g0, Bp, T] + nbrs(A) + nbrs(Sp), 0)
    b0 = sorted(set(b0) | set(bbox([q0, g0, Bp, T], 1)))
    b1 = sorted(set(bbox([A, Sp, q1, g1] + nbrs(add(Bp, (2, 0, 0))) + nbrs(add(T, E)), 0)) | set(bbox([A, Sp, q1, g1], 1)))
    try:
        S = FlyerSAT([(0, 1), (2, 4)], None, L, NS=NS, kinds=kinds, leaf=True, maxglue=8, names=['B0', 'B1'],
                     boxes=[b0, b1], must=must)
    except (Infeasible, KeyError) as e:
        return 'TRIV', 0, None
    st, dt = S.solve(tl, workers)
    return st, dt, S


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('--gb0', type=int, default=4); ap.add_argument('--gb1', type=int, default=3)
    ap.add_argument('--tl', type=float, default=20); ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--part', default='0/1'); ap.add_argument('--out', default='skel')
    ap.add_argument('--count', action='store_true')
    a = ap.parse_args()
    sks = skeletons(a.gb0, a.gb1)
    print(len(sks), 'skeletons', flush=True)
    if a.count: sys.exit()
    i, n = (int(z) for z in a.part.split('/'))
    kinds = ['g', 'R'] + [f'D{q}' for q in range(6)] + [f'O{q}' for q in range(6)]
    odir = HERE / 'runs' / 'skel2'; odir.mkdir(parents=True, exist_ok=True)
    cnt = {}
    for j, sk in enumerate(sks):
        if j % n != i: continue
        st, dt, S = solve(sk, a.L, a.tl, a.workers, kinds)
        cnt[st] = cnt.get(st, 0) + 1
        if st not in ('INFEASIBLE', 'TRIV'):
            print(j, sk, st, round(dt, 1), flush=True)
        if st in ('OPTIMAL', 'FEASIBLE'):
            sol = S.extract(); ld = S.loads(); ml = max(ld.values())
            print(show(sol)); print(S.causes()); print(ld, flush=True)
            tag = f'{a.out}_L{ml}_{j}'
            pickle.dump({'sol': sol, 'riders': [], 'merges': [], 'sk': sk}, open(odir / f'{tag}.pkl', 'wb'))
            to_flyer(sol, ml, NS).save(str(odir / f'{tag}.flyer'))
            print('saved', tag, flush=True)
        if j % 50 == 0: print('progress', j, cnt, flush=True)
    print('done', cnt, flush=True)
