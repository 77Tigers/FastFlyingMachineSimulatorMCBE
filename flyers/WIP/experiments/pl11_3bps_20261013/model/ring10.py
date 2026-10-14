"""Link-module search for the user's 10-segment back loop (3 bps, NS=5) with rot180 symmetry.

Module i = body A_i + its rider pushers. A_{i+1}(slot 0) = R(A_i(slot -D)) + v with R = rot180 about X
(y,z -> -y,-z), D = 3 (= -2 slots: the carrier's successor word). Riders are hopping normal pistons
(satflyer5 riders: own word = complement of {f, f+1}, any moving body may carry them per slot).
Each body gets its first two moves from rider pushes; its third move is supplied externally ('ext_<t>',
the pull that L1 will provide). M modules, ends open (power/targets/causes unchecked); middles fully checked.
usage: python ring10.py L --v vx,vy,vz[;...] [--M 4] [--tl 300] [--workers 6] [--maxglue 6] [--xr m1:2 --r 2]
"""
import sys, pathlib, itertools, argparse, pickle, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'two_bps_20261007'))
from satflyer5 import FlyerSAT, pinfo, show, to_flyer, Infeasible

NS = 5
ROTK = {'D2': 'D3', 'D3': 'D2', 'D4': 'D5', 'D5': 'D4', 'O2': 'O3', 'O3': 'O2', 'O4': 'O5', 'O5': 'O4'}


import os
ROT = os.environ.get('ROT', 'r180')
def R(u): return (u[0], -u[1], -u[2]) if ROT == 'r180' else u
def Rk(k): return ROTK.get(k, k) if ROT == 'r180' else k
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def shiftk(k, d):
    p = pinfo(k)
    if p is None: return k
    return f'{p[0]}{(p[1] + d) % NS}' + ('h' if p[2] == 2 else '')


def build(L, v, M, body_box, rider_box, D=3, word0=(0, 1, 2), maxglue=6, kinds=None, sym=True, extpull=True,
          npush=2, riderS=False):
    kinds = kinds or ['g', 'R'] + [f'D{d}' for d in range(6)] + [f'O{d}' for d in range(6)]
    segs = []  # (name, module, word, kind_list or None, rider?)
    for i in range(M):
        w = tuple(sorted((x + i * D) % NS for x in word0))
        first = [(word0[j] + i * D) % NS for j in range(3)]  # moves in cyclic order
        segs.append((f'A{i}', i, w, None, False, first))
        for j in (range(npush) if i > 0 else []):
            f = first[j]
            rw = tuple(sorted(s for s in range(NS) if s not in (f, (f + 1) % NS)))
            segs.append((f'P{i}{j}', i, rw, [f'P{f}'], True, None))
    names = [s[0] for s in segs]
    words = [s[2] for s in segs]
    # offsets per segment chain
    boxes, offs = [], {}
    for idx, (nm, i, w, kl, rid, first) in enumerate(segs):
        base = rider_box if rid else body_box
        key = nm[0] + (nm[2:] if rid else '')
        if i == 0:
            off = (0, 0, 0)
        elif rid and i == 1:
            off = offs[('A', 1)]
        else:
            po = offs[(key, i - 1)]
            pw = words[names.index(nm[0] + str(i - 1) + (nm[2:] if rid else ''))]
            c = sum(1 for x in pw if x >= NS - D)
            ro = R(po)
            off = (ro[0] + v[0] - c, ro[1] + v[1], ro[2] + v[2])
        offs[(key, i)] = off
        bx = []
        for u in base:
            uu = u
            for _ in range(i): uu = R(uu)
            bx.append(add(uu, off))
        boxes.append(bx)
    flags = {'powmiss', 'Ptarget', 'Starget', 'cause_le1'}
    opn = {}
    for idx, (nm, i, w, kl, rid, first) in enumerate(segs):
        if i in (0, M - 1):
            opn[nm] = set(flags)
        elif not rid and extpull:
            opn[nm] = {f'ext_{first[2]}'}
    kbs = {nm: kl for (nm, i, w, kl, rid, first) in segs if kl}
    if not riderS:
        for (nm, i, w, kl, rid, first) in segs:
            if not rid:
                kbs[nm] = kinds + []  # bodies: no pistons of their own (pushers are riders, pull is external)
    S = FlyerSAT(words, None, L, NS=NS, kinds=kinds, leaf=True, maxglue=maxglue, boxes=boxes, names=names,
                 open_segs=opn, riders=[s[0] for s in segs if s[4]], kinds_by_seg=kbs)
    if sym:
        for idx, (nm, i, w, kl, rid, first) in enumerate(segs):
            if i == 0: continue
            if rid and i == 1: continue
            j0 = names.index(nm[0] + ('1' if rid else '0') + (nm[2:] if rid else ''))
            for a, u in enumerate(boxes[j0]):
                ui = boxes[idx][a]
                for k in S.kinds_of(j0):
                    di = i - (1 if rid else 0)
                    kk = shiftk(k, di * D)
                    for _ in range(di): kk = Rk(kk)
                    if (idx, ui, kk) in S.X:
                        S.m.Add(S.X[idx, ui, kk] == S.X[j0, u, k])
                    else:
                        S.m.Add(S.X[j0, u, k] == 0)
            if not rid:
                S.m.Add(S.mat[idx] == S.mat[j0])
    return S, segs


def rng(s):
    a, b = (int(z) for z in s.replace('m', '-').split(':')); return range(a, b + 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('--v', required=True)
    ap.add_argument('--M', type=int, default=4); ap.add_argument('--tl', type=float, default=300)
    ap.add_argument('--workers', type=int, default=6); ap.add_argument('--maxglue', type=int, default=6)
    ap.add_argument('--xr', default='m1:2'); ap.add_argument('--r', type=int, default=2)
    ap.add_argument('--rxr', default='m3:1'); ap.add_argument('--nosym', action='store_true')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    body_box = list(itertools.product(rng(a.xr), range(-a.r, a.r + 1), range(-a.r, a.r + 1)))
    rider_box = list(itertools.product(rng(a.rxr), range(-a.r, a.r + 1), range(-a.r, a.r + 1)))
    out = HERE / 'runs_ring10'; out.mkdir(exist_ok=True)
    for vs in a.v.split(';'):
        v = tuple(int(z) for z in vs.replace('m', '-').split(','))
        t0 = time.time()
        try:
            S, segs = build(a.L, v, a.M, body_box, rider_box, maxglue=a.maxglue, sym=not a.nosym)
        except Infeasible as e:
            print(f'v={v} TRIVIAL-INF {e}', flush=True); continue
        st, dt = S.solve(a.tl, a.workers, objective='maxload')
        msg = f'v={v} -> {st} {dt:.1f}s build {time.time() - t0 - dt:.1f}s'
        if st in ('OPTIMAL', 'FEASIBLE'):
            sol = S.extract(); ld = S.loads()
            mid = {k: x for k, x in ld.items() if not k[0].endswith('0') and not k[0].endswith(str(a.M - 1))}
            msg += f' midload={max(mid.values()) if mid else None} loads={ld}'
            print(msg, flush=True)
            print(show([s for s in sol if s[0][1] == '1']))
            print([c for c in S.causes() if '1' in c[1] or '1' in c[3]])
            pickle.dump({'sol': sol, 'v': v, 'M': a.M, 'loads': ld, 'causes': S.causes()},
                        open(out / f'v{v[0]}{v[1]}{v[2]}_L{a.L}{a.tag}.pkl', 'wb'))
        else:
            print(msg, flush=True)
