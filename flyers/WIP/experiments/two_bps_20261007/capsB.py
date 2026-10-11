"""Chain-B (shift-3) complete 2 bps flyer with caps, 5-slot model (satflyer5).
Segments: R, K0..K{m-1}, F.  K_i word {3i, 3i+1} mod 5.  Paper caps (user):
  rear  R word {b+2,b+4} (b = 0): R pushes K0 at 0, K1 pulls R at 2, K0 pulls R at 4.
  front L = K_{m-1} word {a,a+1}; F word {a+2,a+4}: F pulls L at a+1, L pushes F at a+2, K_{m-2} pushes F at a+4.
Middles come from a chainsym pkl (K0..K4, K_{i+5} = K_i + offs).  Usage:
  python capsB.py TAG L [--pkl v311] [--m 6] [--fix 2,3] [--must 1,4] [--r 2] [--tl 300] [--workers 4]
     [--rwords 24] [--fwords auto] [--riders ...] [--maxload]
--fix: chain indices pinned exactly to the pkl; --must: pkl cells required, extras allowed.
"""
import sys, pathlib, pickle, argparse, itertools, time, json
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from satflyer5 import FlyerSAT, show, to_flyer, pinfo

NS = 5
OFFS0 = None


def chain_offs(words, v, M):
    offs = [(0, 0, 0)]
    for i in range(M - 1):
        c = sum(1 for w in words[i] if w >= NS - 3)
        o = offs[-1]; offs.append((o[0] + v[0] - c, o[1] + v[1], o[2] + v[2]))
    return offs


def sh(c, o): return (c[0] + o[0], c[1] + o[1], c[2] + o[2])


def build(a):
    d = pickle.load(open(HERE / 'runs' / 'chainsym' / f'w01_D3_{a.pkl}_L10.pkl', 'rb'))
    v = d['v']; base = {nm: (w, c, mt) for nm, w, c, mt in d['sol']}
    m = a.m
    words = [tuple(sorted({(3 * i) % NS, (3 * i + 1) % NS})) for i in range(m)]
    offs = chain_offs(words, v, m)
    # pkl segment i (i<5) sits in box offs[i] + box0; segment i>=5 = pkl i-5 shifted by offs[i]-offs[i-5]
    def pkl_cells(i):
        j = i % 5; w, c, mt = base[f'K{j}']
        dd = tuple(offs[i][q] - offs[j][q] for q in range(3))
        return {sh(u, dd): k for u, k in c.items()}, mt
    fixset = {int(x) for x in a.fix.split(',') if x}
    mustset = {int(x) for x in a.must.split(',') if x}
    xa, xb = (int(z) for z in a.xr.replace('m', '-').split(':'))
    box0 = list(itertools.product(range(xa, xb + 1), range(-a.r, a.r + 1), range(-a.r, a.r + 1)))
    names = ['R'] + [f'K{i}' for i in range(m)] + ['F']
    la = (3 * (m - 1)) % NS
    rw = tuple(sorted({2, 4})) if a.rwords == 'paper' else tuple(int(ch) for ch in a.rwords)
    fw = tuple(sorted({(la + 2) % NS, (la + 4) % NS})) if a.fwords == 'paper' else tuple(int(ch) for ch in a.fwords)
    allw = [rw] + words + [fw]
    boxes, fixed, must = [], [], {}
    # rear box: behind K0, front box: ahead of last
    rbox = [sh(u, (-2, 0, 0)) for u in itertools.product(range(xa - 1, xb + 1), range(-a.r, a.r + 1), range(-a.r, a.r + 1))]
    lo = offs[m - 1]
    fbox = [sh(u, sh(lo, (2, 0, 0))) for u in itertools.product(range(xa, xb + 2), range(-a.r, a.r + 1), range(-a.r, a.r + 1))]
    if a.rshift: rbox = [sh(u, tuple(int(z) for z in a.rshift.split(','))) for u in rbox]
    if a.fshift: fbox = [sh(u, tuple(int(z) for z in a.fshift.split(','))) for u in fbox]
    boxes.append(rbox); fixed.append(None)
    for i in range(m):
        b = [sh(u, offs[i]) for u in box0]
        cells, mt = pkl_cells(i)
        if i in fixset:
            fixed.append((cells, mt)); boxes.append(None)
        else:
            fixed.append(None); boxes.append(sorted(set(b) | set(cells)))
            if i in mustset: must[f'K{i}'] = cells
    boxes.append(fbox); fixed.append(None)
    kinds = ['g', 'R'] + [f'D{q}' for q in range(6)] + [f'O{q}' for q in range(6)]
    riders = []
    if a.riders:
        for rd in a.riders.split(';'):
            nm, w = rd.split(':'); names.append(nm); allw.append(tuple(int(ch) for ch in w)); boxes.append(rbox + fbox if nm.startswith('Q') else None)
            fixed.append(None); riders.append(nm)
    # boxes None for riders -> use union of all boxes
    allbox = sorted({u for b in boxes if b for u in b})
    boxes = [b if b is not None or fixed[i] is not None else allbox for i, b in enumerate(boxes)]
    merges = []
    for mg in (a.merges.split(';') if a.merges else []):
        t, x, y = mg.split(','); merges.append((int(t), [x, y]))
    # open flags: nothing open, complete flyer
    drop = set(a.drop.split(',')) if a.drop else set()
    keep = [i for i, nm in enumerate(names) if nm not in drop]
    names = [names[i] for i in keep]; allw = [allw[i] for i in keep]; boxes = [boxes[i] for i in keep]; fixed = [fixed[i] for i in keep]
    flags = {'powmiss', 'Ptarget', 'Starget', 'cause_le1'}
    opn = {nm: flags for nm in (a.open.split(',') if a.open else [])}
    S = FlyerSAT(allw, None, a.L, NS=NS, kinds=kinds, leaf=True, maxglue=a.maxglue, boxes=boxes, fixed=fixed,
                 names=names, must=must, riders=riders, merges=merges, open_segs=opn)
    return S, names, allw


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tag'); ap.add_argument('L', type=int)
    ap.add_argument('--pkl', default='v311'); ap.add_argument('--m', type=int, default=6)
    ap.add_argument('--fix', default='2,3'); ap.add_argument('--must', default='')
    ap.add_argument('--r', type=int, default=2); ap.add_argument('--xr', default='m1:2')
    ap.add_argument('--tl', type=float, default=300); ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--rwords', default='paper'); ap.add_argument('--fwords', default='paper')
    ap.add_argument('--rshift', default=''); ap.add_argument('--fshift', default='')
    ap.add_argument('--riders', default=''); ap.add_argument('--merges', default='')
    ap.add_argument('--drop', default=''); ap.add_argument('--open', default='')
    ap.add_argument('--maxglue', type=int, default=6); ap.add_argument('--obj', default='maxload')
    a = ap.parse_args()
    t0 = time.time()
    S, names, allw = build(a)
    print('words', dict(zip(names, allw)), 'build', round(time.time() - t0, 1), flush=True)
    st, dt = S.solve(a.tl, a.workers, objective=(None if a.obj == 'none' else a.obj))
    print(a.tag, 'L', a.L, st, round(dt, 1), flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = S.extract()
        print(show(sol)); print(S.causes()); ld = S.loads(); print(ld)
        print('maxload', max(ld.values()))
        out = HERE / 'runs' / 'capsB'; out.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': sol, 'riders': [n for n in names if n.startswith(('V', 'Q'))],
                     'merges': [(int(x.split(',')[0]), x.split(',')[1:]) for x in a.merges.split(';') if x], 'args': vars(a)}, open(out / f'{a.tag}.pkl', 'wb'))
        to_flyer(sol, max(ld.values()), NS).save(str(out / f'{a.tag}.flyer'))
        print('saved', out / f'{a.tag}.flyer')
