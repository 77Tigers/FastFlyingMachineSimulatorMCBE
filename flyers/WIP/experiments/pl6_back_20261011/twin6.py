"""Twin start caps (user idea 2026-10-11: backs near each other share glue/power).
Chain A = pinned load-6 cap skeleton: K0 (4 blocks, 7b minus relay), N (2), K1 (template glue/pistons + free power,
<= K1MAX), K2 template (front boundary).  Chain B = image of A under yz map MP + offset d, words shifted by 2 slots
(mirror_gen convention), K1' constrained equal to the image of K1.  Merges K0+N at slot 1 and K0'+N' at slot 3.
Law (FINDINGS): K0's N-pusher can be powered only by K0/N blocks or by opposite-material glue of a body standing still
in slot 1 -> the twin (honey vs slime) can supply it for free.
usage: python twin6.py L MAPS [--dx -3:3] [--dy -4:4] [--dz -4:4] [--tl 60] [--wk 3] [--mat opp|free] [--skip power]
"""
import sys, pathlib, itertools, pickle, time, argparse
from back6 import FlyerSAT, Infeasible, WORDS, show, tcells, report, BND_FRONT, KPOW, KALL, add, cube, HERE, K0, N
from psat import wpos
sys.path.insert(0, str(HERE.parent / 'rigid_sat_20261004'))
from front_mirror import shiftword
from mirror_gen import mapper


def build(mp, d, L, k1max=6, mat='opp', skip=(), k1r=2, powmiss=()):
    T, km = mapper(mp, d)
    k1c = {u: k for u, k in tcells(1)[0].items() if k in 'gSP'}
    k1box = sorted(set(cube((2, 0, 0), range(-1, 3), k1r)) | set(k1c))
    half = [('K0', WORDS['mmww'], K0, None), ('N', WORDS['wmmw'], N, None), ('K1', WORDS['wwmm'], None, k1box),
            ('K2', tcells(2)[1], tcells(2)[0], None)]
    names, words, fixed, boxes, img = [], [], [], [], {}
    for nm, w, c, b in half:
        names.append(nm); words.append(tuple(w)); fixed.append((c, None) if c else None); boxes.append(b)
    for i, (nm, w, c, b) in enumerate(half):
        p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w))
        if c: fixed.append(({T(u, p): km(k) for u, k in c.items()}, None)); boxes.append(None)
        else: fixed.append(None); boxes.append([T(u, p) for u in b]); img[i] = (len(names) - 1, p)
    # skeleton overlap prefilter (fixed cells at every slot)
    for t in range(4):
        occ = set()
        for w_, fx in zip(words, fixed):
            if fx is None: continue
            for c_ in fx[0]:
                cc = (c_[0] + wpos(w_, t), c_[1], c_[2])
                if cc in occ: return 'SKEL_OVERLAP'
                occ.add(cc)
    # necessary: P2 = K0 (0,-1,-1) at slot-2 start sits at (2,-1,-1); a twin glue cell (opposite material, standing
    # still or co-moving in slot 1) must be one of its free side cells at slot 2 (FINDINGS law)
    Q = {(2, -2, -1), (2, -1, 0), (2, -1, -2)}
    hit = False
    for j in range(4, 8):
        cells = fixed[j][0] if fixed[j] else {u: 'g' for u in boxes[j]}
        for u, k in cells.items():
            if k == 'g' and (u[0] + wpos(words[j], 2), u[1], u[2]) in Q: hit = True
    if not hit: return 'NO_RELAY'
    must = {'K1': k1c, "K1'": {T(u, wpos(WORDS['wwmm'], 2)): km(k) for u, k in k1c.items()}}
    maxsize = [None, None, k1max, None] * 2
    try:
        M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=max(L - 1, 1), fixed=fixed, names=names,
                     boxes=boxes, open_segs={3: BND_FRONT, 7: BND_FRONT, **{i: {'powmiss'} for i in powmiss}}, merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])],
                     must=must, maxsize=maxsize, leafrod=True, skip=skip)
    except Infeasible:
        return 'TRIV_INFEASIBLE'
    for i, (j, p) in img.items():
        for u in boxes[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[j, T(u, p), km(k)] == M.X[i, u, k])
    for s in range(4):        # chain A one material, chain B one material
        M.m.Add(M.mat[s] == M.mat[0]); M.m.Add(M.mat[s + 4] == M.mat[4])
    if mat == 'opp': M.m.Add(M.mat[0] != M.mat[4])
    return M


def rng(s):
    a, b = s.replace('m', '-').split(':'); return range(int(a), int(b) + 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('maps')
    ap.add_argument('--dx', default='m3:3'); ap.add_argument('--dy', default='m4:4'); ap.add_argument('--dz', default='m4:4')
    ap.add_argument('--tl', type=float, default=60); ap.add_argument('--wk', type=int, default=3)
    ap.add_argument('--mat', default='opp'); ap.add_argument('--skip', default=''); ap.add_argument('--k1max', type=int, default=6)
    a = ap.parse_args()
    skip = tuple(x for x in a.skip.split(',') if x)
    done = set()
    for f in (HERE / 'runs').glob('twin_*.log'):
        for line in open(f):
            parts = line.split(' (', 1)
            if len(parts) == 2 and ')' in parts[1]: done.add((parts[0], tuple(int(v) for v in parts[1].split(')')[0].split(','))))
    for mp in a.maps.split(','):
        for d in itertools.product(rng(a.dx), rng(a.dy), rng(a.dz)):
            if (mp, d) in done: continue
            M = build(mp, d, a.L, a.k1max, a.mat, skip)
            if isinstance(M, str):
                continue
            st, dt = M.solve(a.tl, a.wk)
            print(mp, d, st, f'{dt:.1f}s', flush=True)
            if st in ('OPTIMAL', 'FEASIBLE'):
                sol = M.extract(); print(show(sol)); print(report(M), flush=True)
                tag = f"twin_L{a.L}_{mp}_{'_'.join(map(str, d))}{'_np' if skip else ''}"
                pickle.dump({'sol': sol, 'map': mp, 'd': d}, open(HERE / 'runs' / f'{tag}.pkl', 'wb'))
