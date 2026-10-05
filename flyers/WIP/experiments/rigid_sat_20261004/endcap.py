"""Single-chain end caps solved exactly (roles free, extra segments of any word, leaf + leaf-push races allowed).

back cap ('start'): A = K0 (mmww) free + extra free segments; chain K1..K4 alt templates, K4 boundary (its pull, push
                    target and power come from the chain in front). NB=1 also frees K1.
front cap ('end'):  chain K1..K3 templates (K1 boundary: pushed/pulls outside), F = K4 (mmww) free + extra segments.
                    NB=1 also frees K3.
All free segments share one candidate box around the chain end. If a start cap and an end cap both fit under LOAD, any
alt chain between them gives a complete flyer (join_caps in this file).

usage: python endcap.py start|end LOAD TL WORKERS EXTRA_WORDS [OUTDIR]     EXTRA_WORDS e.g. wmmw or mwwm,wwmm or -
env: NB=1, KINDS=g,P,S,R[,D0..D5,O0..O5], LEAF=1 (default 1), BOX="x0,x1,r", MERGE="1:K0,E0[;t:a,b]"
"""
import sys, pathlib, itertools, os, time, pickle
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, Infeasible, show, to_rigid, add
from chainflyer import ORIENTS, template, origins
from modules import BND_BACK, BND_FRONT

O1 = ORIENTS[0]


def chain(Ks):
    org = origins(max(Ks) + 1, *O1)
    out = []
    for K in Ks:
        cells, word = template(K, *O1)
        out.append((f'K{K}', word, org[K], {add(org[K], u): k for u, k in cells.items()}))
    return out


def setup(side, extra, nb, box):
    x0, x1, r = box
    if side == 'start':
        ch = chain([0, 1, 2, 3, 4])
        center = ch[0][2]
        free = {'K0'} | ({'K1'} if nb else set())
        opens = {'K4': BND_FRONT}
    else:
        ch = chain([1, 2, 3, 4])
        center = ch[-1][2]
        free = {'K4'} | ({'K3'} if nb else set())
        opens = {'K1': BND_BACK}
    region = [add(center, (dx, dy, dz)) for dx in range(x0, x1 + 1) for dy in range(-r, r + 1) for dz in range(-r, r + 1)]
    segs = [(nm, w, cells) for nm, w, org, cells in ch]
    for i, w in enumerate(extra):
        segs.append((f'E{i}', w, None)); free.add(f'E{i}')
    names = [s[0] for s in segs]
    words = [s[1] for s in segs]
    fixed = [None if nm in free else (cells, None) for nm, w, cells in segs]
    boxes = [region if nm in free else None for nm, w, cells in segs]
    of = {names.index(k): v for k, v in opens.items()}
    return names, words, fixed, boxes, of


def solve(side, load, tl, workers, extra, nb=False, kinds=('g', 'P', 'S', 'R'), leaf=True, box=(-4, 4, 3), log=False,
          objective=None, skip=(), merges=(), keep=()):
    """keep: names of free chain segments whose alt-template cells are REQUIRED (solver may add blocks)."""
    names, words, fixed, boxes, of = setup(side, extra, nb, box)
    must = {}
    for nm in keep:
        K = int(nm[1:]); cells, _ = template(K, *O1); org = origins(K + 1, *O1)[K]
        cl = {add(org, u): k for u, k in cells.items()}
        if side == 'start' and K == 0: cl = {c: k for c, k in cl.items() if k in ('g', 'P') and c[0] == org[0]}
        if side == 'end' and K == 4: cl = {c: k for c, k in cl.items() if k != 'P'}
        must[nm] = cl
    M = FlyerSAT(words, None, load, kinds=kinds, leaf=leaf, maxglue=load - 1, fixed=fixed, names=names, boxes=boxes,
                 open_segs=of, skip=skip, merges=merges, must=must)
    st, dt = M.solve(tl, workers, log=log, objective=objective)
    sol = M.extract() if st in ('OPTIMAL', 'FEASIBLE') else None
    return st, dt, sol, M


if __name__ == '__main__':
    side, load, tl, workers = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    extra = [] if sys.argv[5] == '-' else sys.argv[5].split(',')
    outdir = pathlib.Path(sys.argv[6]) if len(sys.argv) > 6 else HERE / 'runs' / 'caps'
    outdir.mkdir(parents=True, exist_ok=True)
    nb = bool(int(os.environ.get('NB', '0')))
    kinds = tuple(os.environ.get('KINDS', 'g,P,S,R').split(','))
    leaf = bool(int(os.environ.get('LEAF', '1')))
    box = tuple(int(v) for v in os.environ.get('BOX', '-4,4,3').split(','))
    merges = []
    for mg in filter(None, os.environ.get('MERGE', '').split(';')):
        t, g = mg.split(':'); merges.append((int(t), g.split(',')))
    t0 = time.time()
    keep = tuple(filter(None, os.environ.get('KEEP', '').split(',')))
    obj = os.environ.get('OBJ') or None
    st, dt, sol, M = solve(side, load, tl, workers, extra, nb, kinds, leaf, box, merges=merges, keep=keep, objective=obj)
    if sol: print('loads', {f'{M.names[j] if isinstance(j, int) else "+".join(M.names[x] for x in j)}@{t}': M.solver.Value(e)
                            for (j, t), e in M.loadexpr.items()})
    if sol: print('merges', [(t, M.names[a], M.names[b]) for (t, a, b), v in M.mg.items() if v is True or M.solver.Value(v)],
                  'riders', [(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if M.solver.Value(v)])
    tag = (f'{side}_L{load}_{"-".join(extra) or "none"}{"_nb" if nb else ""}{"_k" + str(len(kinds)) if len(kinds) > 4 else ""}'
           + ''.join(f'_m{t}{"".join(g)}' for t, g in merges) + (f'_keep{"".join(keep)}' if keep else ''))
    print(tag, st, f'{dt:.1f}s', flush=True)
    if sol:
        print(show(sol))
        pickle.dump({'sol': sol, 'side': side, 'extra': extra, 'load': load}, open(outdir / f'{tag}.pkl', 'wb'))
