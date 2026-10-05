"""Assemble a complete flyer from a start cap and a front cap that share alt-template chain segments, re-check the
whole thing exactly in satflyer (fixed cells, materials re-chosen, planned merges + riders), export .flyer.

usage: python assemble.py START_PKL FRONT_PKL OUT_STEM [EXTRA_MIDDLE]
  START_PKL: runs/caps/*.pkl (endcap.py) or runs/cfg/*.pkl ; FRONT_PKL: runs/cfg/*.pkl
  EXTRA_MIDDLE: number of extra template segments inserted between the caps (even, default 0)
"""
import sys, pathlib, pickle, itertools, os
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, show, to_rigid, add
from cfgsat import tcells, ORG
import rigid


def load(p):
    d = pickle.load(open(p, 'rb'))
    if 'sol' in d: return d
    return {'sol': d}


def kstr(k): return k if isinstance(k, str) else f'{k[0]}{k[1]}'


def assemble(sp, fp, extra=0):
    S, F = load(sp), load(fp)
    segs = {}      # name -> (word, cells, mat)
    order = []
    for nm, w, c, m in S['sol']:
        segs[nm] = (w, c, m); order.append(nm)
    shift = (2 * extra, extra // 2, extra // 2)   # alt chain advances (4, a+c) per 2 segments (orientation ORIENTS[0])
    assert extra % 2 == 0
    fsol = []
    for nm, w, c, m in F['sol']:
        if nm.startswith('K') and nm[1:].isdigit():
            K = int(nm[1:]) + extra
            nm2 = f'K{K}'
        else:
            nm2 = nm
        fsol.append((nm2, w, {add(cc, shift): k for cc, k in c.items()}, m))
    for nm, w, c, m in fsol:
        if nm in segs: continue        # shared template segment: keep the start cap's copy
        segs[nm] = (w, c, m); order.append(nm)
    # fill missing middle templates
    ks = sorted(int(n[1:]) for n in segs if n.startswith('K') and n[1:].isdigit())
    for K in range(ks[0], ks[-1] + 1):
        if f'K{K}' not in segs:
            cells, w = tcells(K); segs[f'K{K}'] = (w, cells, None); order.append(f'K{K}')
    order = sorted(order, key=lambda n: (0, int(n[1:])) if n.startswith('K') and n[1:].isdigit() else (1, n))
    riders = set(F.get('riders', [])) | set(S.get('riders', []))
    merges = []
    for d in (S, F):
        cfg = d.get('cfg') or {}
        merges += list(cfg.get('merges', ()))
    return order, segs, riders, merges


if __name__ == '__main__':
    sp, fp, stem = sys.argv[1], sys.argv[2], sys.argv[3]
    extra = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    order, segs, riders, merges = assemble(sp, fp, extra)
    planned = [tuple(x) for x in os.environ.get('MERGES', '').split(';') if x]
    mg = [(int(p.split(':')[0]), p.split(':')[1].split(',')) for p in os.environ.get('MERGES', '').split(';') if p]
    fixed = [({c: kstr(k) for c, k in segs[n][1].items()}, None) for n in order]
    kinds = sorted({k for f, _ in fixed for k in f.values()} | {'g', 'P', 'S', 'R'})
    M = FlyerSAT([segs[n][0] for n in order], None, None, kinds=kinds, leaf=True, maxglue=20, fixed=fixed, names=order,
                 riders=sorted(riders), merges=mg, automerge=bool(os.environ.get('AUTOMERGE')))
    st, dt = M.solve(300, 16)
    print('assembled', order, 'riders', sorted(riders), 'merges', mg, '->', st)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sv = M.solver
        loads = {f'{j}@{t}': sv.Value(e) for (j, t), e in M.loadexpr.items()}
        print('loads', loads)
        print('auto merges', [(t, M.names[a], M.names[b]) for (t, a, b), v in M.mg.items() if v is True or sv.Value(v)])
        sol = M.extract(); print(show(sol))
        L = max(loads.values())
        out = HERE / 'runs' / 'assembled'; out.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': sol, 'riders': sorted(riders), 'merges': mg}, open(out / f'{stem}.pkl', 'wb'))
        rigid.to_flyer(to_rigid(sol), L).save(str(out / f'{stem}.flyer'))
        print('saved', out / f'{stem}.flyer', 'encoded PL', L)
