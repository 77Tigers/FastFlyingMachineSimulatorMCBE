"""Free search of small CLOSED 2 bps flyers (NS=5): n bodies (2 moves each), optional riders, small box.
usage: python small5.py L WORDS [--box m2:3,m1:1,m1:1] [--riders P:wd,S:wd] [--tl 60] [--workers 1] [--obj maxload]
       python small5.py L enum N [...]   -> all canonical word combos for N bodies (body 0 word fixed up to rotation)
WORDS like 01,24 (slots each body moves).  Saves feasible designs to runs/small5/.
"""
import sys, pathlib, itertools, pickle, argparse, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from satflyer5 import FlyerSAT, show, to_flyer, Infeasible

NS = 5
ALLW = sorted({tuple(sorted(c)) for c in itertools.combinations(range(NS), 2)})


def rng(s):
    a, b = (int(z) for z in s.replace('m', '-').split(':')); return range(a, b + 1)


def canon(ws):
    best = None
    for r in range(NS):
        rot = sorted(tuple(sorted((x + r) % NS for x in w)) for w in ws)
        if best is None or rot < best: best = rot
    return tuple(best)


def run(L, words, a, tag=None):
    box = list(itertools.product(*[rng(r) for r in a.box.split(',')]))
    names = [f'B{i}' for i in range(len(words))]
    allw = list(words); kbs = {}; riders = []
    for i, rd in enumerate(a.riders.split(',') if a.riders else []):
        k, w = rd.split(':'); nm = f'Q{i}'; names.append(nm); w = tuple(int(c) for c in w); allw.append(w)
        riders.append(nm)
        from satflyer5 import piston_kinds
        kbs[nm] = [pk for pk in piston_kinds(w, NS) if pk[0] == k]
    kinds = ['g', 'R'] + [f'D{q}' for q in range(6)] + [f'O{q}' for q in range(6)]
    if a.kinds: kinds = a.kinds.split(',')
    exact = {}
    if a.pk:   # exact piston plan, e.g. "0:P0;1:P2,P3,S3"
        for part in a.pk.split(';'):
            i, ks = part.split(':'); ks = ks.split(',') if ks else []
            kbs[names[int(i)]] = kinds + ks; exact[int(i)] = ks
    try:
        S = FlyerSAT(allw, box, L, NS=NS, kinds=kinds, leaf=True, maxglue=a.maxglue, names=names, riders=riders,
                     anchor=(0, 0, 0), kinds_by_seg=kbs)
    except Infeasible as e:
        return 'TRIVIAL-INF', 0, None
    for i, ks in exact.items():
        for k in ks: S.m.Add(sum(S.X[i, u, k] for u in S.boxes[i]) == 1)
    if a.hint:
        S.hint(pickle.load(open(a.hint, 'rb'))['sol'])
    st, dt = S.solve(a.tl, a.workers, objective=(None if a.obj == 'none' else a.obj))
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = S.extract(); ld = S.loads(); ml = max(ld.values())
        out = HERE / 'runs' / 'small5'; out.mkdir(parents=True, exist_ok=True)
        tag = tag or ('w' + '-'.join(''.join(map(str, w)) for w in allw) + (f'_r{a.riders.replace(":", "").replace(",", "-")}' if a.riders else '') + f'_L{ml}')
        pickle.dump({'sol': sol, 'riders': riders, 'merges': []}, open(out / f'{tag}.pkl', 'wb'))
        to_flyer(sol, ml, NS).save(str(out / f'{tag}.flyer'))
        return st, ml, (sol, S.causes(), ld, tag)
    return st, dt, None


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('words'); ap.add_argument('N', nargs='?', type=int, default=2)
    ap.add_argument('--box', default='m2:3,m1:1,m1:1'); ap.add_argument('--riders', default='')
    ap.add_argument('--tl', type=float, default=60); ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--obj', default='maxload'); ap.add_argument('--maxglue', type=int, default=6)
    ap.add_argument('--kinds', default=''); ap.add_argument('--pk', default=''); ap.add_argument('--hint', default='')
    a = ap.parse_args()
    if a.words == 'enum':
        combos = sorted({canon(c) for c in itertools.combinations_with_replacement(ALLW, a.N)})
        print(len(combos), 'combos', flush=True)
        for c in combos:
            st, x, res = run(a.L, c, a)
            print(c, st, x if res else f'{x:.1f}s' if isinstance(x, float) else x, flush=True)
            if res: print('  ', res[3], res[1])
    else:
        words = [tuple(int(ch) for ch in w) for w in a.words.split(',')]
        st, x, res = run(a.L, words, a)
        print(words, st, x, flush=True)
        if res:
            sol, causes, ld, tag = res
            print(show(sol)); print(causes); print(ld); print('saved', tag)
