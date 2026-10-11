"""Unmerged start caps on psat: free rear bodies with given words (no planned merges), K1 keeps the template
glue/pistons that interface with K2, K2..K4 templates (K4 = front boundary), optional power/piston riders.
Motivation (FINDINGS law): in the merged double-pull cap, K0's N-pusher can only be powered by K0/N blocks, so the cap
costs >= 7.  Here N's slot-2 move comes from an extra body M (mwwm) and N's slot-1 move from K1, so nothing merges.
usage: python back6b.py L SPEC [--tl S] [--wk N] [--automerge] [--riders w1:K,w2:K]
  SPEC: comma list of name:word:cx:cy:cz:x0:x1:r[:max]  (box centre, x range, yz radius, optional max blocks)
  default rear: K0:mmww:0:0:0:-1:1:2,N:wmmw:2:0:0:-1:2:2,M:mwwm:4:0:0:-2:2:2
"""
import sys, pathlib, itertools, pickle, time, argparse
from back6 import FlyerSAT, Infeasible, WORDS, show, tcells, report, BND_FRONT, KPOW, KALL, add, cube, HERE

DEFAULT = 'K0:mmww:0:0:0:-1:1:2,N:wmmw:2:0:0:-1:2:2,M:mwwm:4:0:0:-2:2:2'


def build(L, spec, automerge=False, riders=(), k1max=6, k1keep=True, k1r=2, skip=()):
    names, words, fixed, boxes, maxsize, must = [], [], [], [], [], {}
    for item in spec.split(','):
        f = item.split(':')
        nm, w = f[0], f[1]; c = tuple(int(v) for v in f[2:5]); x0, x1, r = (int(v) for v in f[5:8])
        names.append(nm); words.append(WORDS[w]); fixed.append(None); boxes.append(cube(c, range(x0, x1 + 1), r))
        maxsize.append(int(f[8]) if len(f) > 8 else None)
    k1c = {u: k for u, k in tcells(1)[0].items() if k in 'gSP'}
    names.append('K1'); words.append(WORDS['wwmm']); fixed.append(None)
    boxes.append(sorted(set(cube((2, 0, 0), range(-1, 3), k1r)) | set(k1c))); maxsize.append(k1max)
    if k1keep: must['K1'] = k1c
    for K in (2, 3, 4):
        names.append(f'K{K}'); words.append(tcells(K)[1]); fixed.append((tcells(K)[0], None)); boxes.append(None)
        maxsize.append(None)
    rid, kbs = [], {}
    for i, rw in enumerate(riders):
        w, kind = rw.split(':')
        nm = f'W{i + 1}'
        names.append(nm); words.append(WORDS[w]); fixed.append(None); boxes.append(cube((2, 0, 0), range(-2, 5), 2))
        maxsize.append(None); rid.append(nm)
        kbs[nm] = KPOW if kind == 'pow' else [kind]
    M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=max(L - 1, 1), fixed=fixed, names=names, boxes=boxes,
                 open_segs={names.index('K4'): BND_FRONT}, riders=rid, kinds_by_seg=kbs, automerge=automerge,
                 must=must, maxsize=maxsize, leafrod=True, skip=skip)
    return M


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('spec', nargs='?', default=DEFAULT)
    ap.add_argument('--tl', type=float, default=600); ap.add_argument('--wk', type=int, default=4)
    ap.add_argument('--automerge', action='store_true'); ap.add_argument('--riders', default='')
    ap.add_argument('--skip', default=''); ap.add_argument('--tag', default='b6b')
    ap.add_argument('--obj', default=None)
    a = ap.parse_args()
    rid = [r for r in a.riders.split(',') if r]
    t0 = time.time()
    try:
        M = build(a.L, a.spec, a.automerge, rid, skip=tuple(x for x in a.skip.split(',') if x))
    except Infeasible as e:
        print('TRIV_INFEASIBLE', e); sys.exit()
    print('built', round(time.time() - t0, 1), flush=True)
    st, dt = M.solve(a.tl, a.wk, objective=a.obj)
    print(a.L, a.spec, rid, 'automerge' if a.automerge else '', st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract(); print(show(sol)); print(report(M), flush=True)
        out = HERE / 'runs' / f'{a.tag}_L{a.L}_{int(time.time())}.pkl'
        pickle.dump({'sol': sol, 'riders': sorted(M.names[r] for r in M.riders), 'spec': a.spec}, open(out, 'wb'))
        print('saved', out, flush=True)
