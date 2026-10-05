"""Back and front modules of the user's design, solved exactly and enumerated over chain-2 placements.

Back module (placement o2, db = B origin - A origin):
  chain 1 (orientation ORIENTS[0]): A=K0 free, a1=K1, a2=K2, a3=K3 boundary (its pull + push target + power are outside)
  chain 2 (orientation o2):          B=K1 free, b1=K2, b2=K3, b3=K4 boundary
Front module (placement o2, df = F2 origin - F1 origin):
  chain 1: c1=K1 boundary (its push + pull target outside), c2=K2, p1=K3, F1=K4 free (mmww)
  chain 2: d1=K2 boundary, d2=K3, p2=K4, F2=K5 free (wwmm)
FREE_NB=1 also frees a1/b1 (back) or p1/p2 (front). Templates = alt 5-block segments (alt.py), materials free.
Join (straight chains, chain 1 length L1=2*m1, chain 2 length L2=2*m2):
  df = db + (4*(m2-m1), m2*(a2+c2) - m1*(a1+c1))     [see join.py]

usage: python modules.py back|front OUTDIR LOAD TIMELIMIT [NPROC]   (env FREE_NB, KINDS, R, RX)
"""
import sys, pathlib, itertools, os, time, pickle, random
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, Infeasible, show, to_rigid, add
from chainflyer import ORIENTS, template, origins

BND_BACK = {'ext_push', 'Starget'}               # chain continues behind it
BND_FRONT = {'ext_pull', 'Ptarget', 'powmiss'}   # chain continues in front of it


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def chain_segs(o, Ks, shift, names):
    org = origins(max(Ks) + 1, *o)
    out = []
    for K, nm in zip(Ks, names):
        cells, word = template(K, *o)
        og = add(org[K], shift)
        out.append((nm, word, og, {add(og, u): k for u, k in cells.items()}))
    return out


def back_skeleton(o2, db):
    o1 = ORIENTS[0]
    ch1 = chain_segs(o1, [0, 1, 2, 3], (0, 0, 0), ['A', 'a1', 'a2', 'a3'])
    org2 = origins(2, *o2)[1]
    ch2 = chain_segs(o2, [1, 2, 3, 4], sub(db, org2), ['B', 'b1', 'b2', 'b3'])
    return ch1 + ch2, {'a3': BND_FRONT, 'b3': BND_FRONT}, {'A', 'B'}, {'a1', 'b1'}


def front_skeleton(o2, df):
    o1 = ORIENTS[0]
    ch1 = chain_segs(o1, [1, 2, 3, 4], (0, 0, 0), ['c1', 'c2', 'p1', 'F1'])
    f1 = ch1[-1][2]
    org5 = origins(6, *o2)[5]
    ch2 = chain_segs(o2, [2, 3, 4, 5], sub(add(f1, df), org5), ['d1', 'd2', 'p2', 'F2'])
    return ch1 + ch2, {'c1': BND_BACK, 'd1': BND_BACK}, {'F1', 'F2'}, {'p1', 'p2'}


def box_around(org, rx=(-2, 3), r=2):
    return [add(org, (dx, dy, dz)) for dx in range(rx[0], rx[1] + 1) for dy in range(-r, r + 1) for dz in range(-r, r + 1)]


def build(sk, opens, free, load, kinds, leaf=True, r=2, rx=(-2, 3)):
    fixed_cells = {}
    for nm, w, org, cells in sk:
        if nm in free: continue
        for c in cells:
            if c in fixed_cells: return None
            fixed_cells[c] = nm
    names = [x[0] for x in sk]
    fixed = [None if nm in free else (cells, None) for nm, w, org, cells in sk]
    boxes = [box_around(org, rx=rx, r=r) if nm in free else None for nm, w, org, cells in sk]
    of = {names.index(k): v for k, v in opens.items()}
    return FlyerSAT([x[1] for x in sk], None, load, kinds=kinds, leaf=leaf, maxglue=load - 1, fixed=fixed,
                    names=names, boxes=boxes, open_segs=of)


def solve_one(args):
    kind, o2i, d, load, tl, nb, outdir, kinds, r, rx = args
    sk, opens, free, nbs = (back_skeleton if kind == 'back' else front_skeleton)(ORIENTS[o2i], d)
    if nb: free = free | nbs
    t0 = time.time()
    try:
        M = build(sk, opens, free, load, kinds, r=r, rx=rx)
    except Infeasible:
        return (args, 'TRIVIAL_INFEASIBLE', 0, None)
    if M is None: return (args, 'SKEL_OVERLAP', 0, None)
    st, dt = M.solve(tl, int(os.environ.get("WORKERS", "1")))
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract()
        tag = f'{kind}_o{o2i}_{d[0]}_{d[1]}_{d[2]}_load{load}{"_nb" if nb else ""}'
        pickle.dump({'sol': sol, 'args': args, 'free': sorted(free)}, open(pathlib.Path(outdir) / f'{tag}.pkl', 'wb'))
        sizes = {nm: len(c) for nm, w, c, m in sol if nm in free}
        return (args, st, time.time() - t0, (tag, sizes))
    return (args, st, time.time() - t0, None)


def placements(kind):
    out = []
    for o2i in range(8):
        for d in itertools.product(range(-3, 5), range(-4, 5), range(-4, 5)):
            sk = (back_skeleton if kind == 'back' else front_skeleton)(ORIENTS[o2i], d)[0]
            cells = {}
            ok = True
            for nm, w, org, cs in sk:
                if nm in ('A', 'B', 'F1', 'F2'): continue
                for c in cs:
                    if c in cells: ok = False
                    cells[c] = nm
            if ok: out.append((o2i, d))
    return out


if __name__ == '__main__':
    from multiprocessing import Pool
    kind = sys.argv[1]; outdir = pathlib.Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    load, tl = int(sys.argv[3]), float(sys.argv[4])
    nproc = int(sys.argv[5]) if len(sys.argv) > 5 else 15
    nb = bool(int(os.environ.get('FREE_NB', '0')))
    kinds = tuple(os.environ.get('KINDS', 'g,P,S,R').split(','))
    r = int(os.environ.get('R', '2'))
    rx = tuple(int(x) for x in os.environ.get('RX', '-2,3').split(','))
    only = os.environ.get('ONLY')   # optional file with "o2i dx dy dz" lines to restrict placements
    pl = placements(kind)
    if only:
        keep = {tuple(int(v) for v in ln.split()) for ln in open(only) if ln.strip()}
        pl = [(o, d) for o, d in pl if (o,) + d in keep]
    jobs = [(kind, o2i, d, load, tl, nb, str(outdir), kinds, r, rx) for o2i, d in pl]
    random.Random(0).shuffle(jobs)
    print('jobs', len(jobs), flush=True)
    cnt = {}
    log = open(outdir / f'log_{kind}_L{load}{"_nb" if nb else ""}.txt', 'a')
    t0 = time.time()
    with Pool(nproc) as pool:
        for i, (args, st, dt, res) in enumerate(pool.imap_unordered(solve_one, jobs)):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{args[1]} {args[2][0]} {args[2][1]} {args[2][2]} {st} {dt:.1f} {res}\n'); log.flush()
            if res is not None: print('FOUND', args[1], args[2], st, res, flush=True)
            if i % 200 == 0: print(i, f'{time.time() - t0:.0f}s', cnt, flush=True)
    print('done', f'{time.time() - t0:.0f}s', cnt, flush=True)
