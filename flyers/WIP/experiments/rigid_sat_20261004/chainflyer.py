"""User's design as ONE exact model: back loop A>B, B>A + one alt 5-block chain per loop segment + front pair.

chain 1: A=K0 (mmww), K1..K(L1-1) template, F1=K(L1)            (origin x = 2K + K%2, yz staircase a/c)
chain 2: B=K1 (wwmm), K2..K(L2) template, F2=K(L2+1)            (orientation o2, shifted by offset)
Free segments (default A, B, F1, F2; FREE_NB=1 also frees each free segment's chain neighbour) get a box around
their template origin; template segments are fixed cells, materials free. Roles are NOT fixed: the solver only
needs every move to have exactly one cause (see satflyer.py), so any working layout in the boxes is found.

usage: python chainflyer.py OUTDIR SHARD NSHARDS [L1 L2 LOAD TIMELIMIT]
"""
import sys, pathlib, itertools, os, time, pickle, random
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, Infeasible, show, to_rigid, add

ORIENTS = [((1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, 1)), ((-1, 0), (0, -1)),
           ((0, 1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (1, 0)), ((0, -1), (-1, 0))]


def template(K, a, c):
    neg = lambda v: (-v[0], -v[1])
    if K % 2 == 0: S, P, att = neg(a), c, neg(c)
    else: S, P, att = neg(c), a, neg(a)
    cells = {(0,) + S: 'S', (0, 0, 0): 'g', (0,) + P: 'P', (0,) + att: 'g', (-1,) + att: 'R'}
    return cells, ((0, 1) if K % 2 == 0 else (2, 3))


def origins(n, a, c):
    Y = (0, 0); out = []
    for K in range(n):
        out.append((2 * K + (K % 2), Y[0], Y[1]))
        d = c if K % 2 == 0 else a
        Y = (Y[0] + d[0], Y[1] + d[1])
    return out


def skeleton(L1, L2, o2, off, o1=ORIENTS[0]):
    """list of (name, K, word, world_origin, template_cells_world, a, c)"""
    segs = []
    for K, org in enumerate(origins(L1 + 1, *o1)):
        cells, word = template(K, *o1)
        nm = 'A' if K == 0 else ('F1' if K == L1 else f'a{K}')
        segs.append((nm, word, org, {add(org, u): k for u, k in cells.items()}))
    for K, org in enumerate(origins(L2 + 2, *o2)):
        if K == 0: continue
        org = add(org, off)
        cells, word = template(K, *o2)
        nm = 'B' if K == 1 else ('F2' if K == L2 + 1 else f'b{K - 1}')
        segs.append((nm, word, org, {add(org, u): k for u, k in cells.items()}))
    return segs


def free_names(L1, L2, nb):
    f = {'A', 'B', 'F1', 'F2'}
    if nb:
        f |= {'a1', f'a{L1 - 1}', 'b1', f'b{L2 - 1}'}
    return f


def box_around(org, rx=(-2, 3), r=2):
    return [add(org, (dx, dy, dz)) for dx in range(rx[0], rx[1] + 1) for dy in range(-r, r + 1) for dz in range(-r, r + 1)]


def instance(L1, L2, o2, off, load, free, kinds=('g', 'P', 'S', 'R'), leaf=True, r=2):
    sk = skeleton(L1, L2, o2, off)
    # template-only sanity: fixed segments must not overlap each other at slot 0
    fixed_cells = {}
    for nm, w, org, cells in sk:
        if nm in free: continue
        for c in cells:
            if c in fixed_cells: return None
            fixed_cells[c] = nm
    words = [w for nm, w, org, cells in sk]
    names = [nm for nm, w, org, cells in sk]
    fixed = [None if nm in free else (cells, None) for nm, w, org, cells in sk]
    boxes = [box_around(org, r=r) if nm in free else None for nm, w, org, cells in sk]
    return FlyerSAT(words, None, load, kinds=kinds, leaf=leaf, maxglue=load - 1, fixed=fixed, names=names, boxes=boxes)


def solve_one(args):
    L1, L2, o2i, off, load, tl, nb, outdir, kinds, r = args
    free = free_names(L1, L2, nb)
    t0 = time.time()
    try:
        M = instance(L1, L2, ORIENTS[o2i], off, load, free, kinds=kinds, r=r)
    except Infeasible:
        return (args, 'TRIVIAL_INFEASIBLE', 0, None)
    if M is None: return (args, 'SKEL_OVERLAP', 0, None)
    st, dt = M.solve(tl, 1)
    sol = M.extract() if st in ('OPTIMAL', 'FEASIBLE') else None
    if sol is not None:
        import rigid
        rigid.LEAF = True
        segs = to_rigid(sol)
        rc = rigid.check(segs); lo = rigid.loads(segs)
        tag = f'L{L1}{L2}_o{o2i}_{off[0]}_{off[1]}_{off[2]}_load{load}'
        pickle.dump(sol, open(pathlib.Path(outdir) / f'{tag}.pkl', 'wb'))
        rigid.to_flyer(segs, load).save(str(pathlib.Path(outdir) / f'{tag}.flyer'))
        return (args, st, time.time() - t0, (rc, lo, tag))
    return (args, st, time.time() - t0, None)


def near(sk, a, b, lim):
    pa = [o for nm, w, o, c in sk if nm == a][0]; pb = [o for nm, w, o, c in sk if nm == b][0]
    return max(abs(pa[i] - pb[i]) for i in range(3)) <= lim


if __name__ == '__main__':
    from multiprocessing import Pool
    outdir = pathlib.Path(sys.argv[1]); outdir.mkdir(parents=True, exist_ok=True)
    L1, L2, load, tl = (int(x) for x in sys.argv[2:6])
    nproc = int(sys.argv[6]) if len(sys.argv) > 6 else 15
    nb = bool(int(os.environ.get('FREE_NB', '0')))
    kinds = tuple(os.environ.get('KINDS', 'g,P,S,R').split(','))
    r = int(os.environ.get('R', '2'))
    jobs = []
    for o2i in range(8):
        for off in itertools.product(range(-3, 4), range(-4, 5), range(-4, 5)):
            sk = skeleton(L1, L2, ORIENTS[o2i], off)
            if not near(sk, 'A', 'B', 4) or not near(sk, 'F1', 'F2', 4): continue
            jobs.append((L1, L2, o2i, off, load, tl, nb, str(outdir), kinds, r))
    random.Random(0).shuffle(jobs)
    print('jobs', len(jobs), flush=True)
    cnt = {}
    log = open(outdir / 'log.txt', 'a')
    with Pool(nproc) as pool:
        for i, (args, st, dt, res) in enumerate(pool.imap_unordered(solve_one, jobs)):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{args[2]} {args[3]} {st} {dt:.1f} {res}\n'); log.flush()
            if res is not None: print('FOUND', args[2], args[3], st, res, flush=True)
            if i % 100 == 0: print(i, cnt, flush=True)
    print('done', cnt, flush=True)
