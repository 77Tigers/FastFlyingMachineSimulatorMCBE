"""Assemble a complete symmetric two-chain flyer from a symcaps back solution and a symcaps front solution that use
the SAME offset d (they share the template middles K2..K4 and their images). Re-checks the whole flyer exactly in
satflyer (all cells fixed, planned merges, riders) and exports .flyer for the real simulator.

usage: python assemble_sym.py BACK_PKL FRONT_PKL OUT_STEM
"""
import sys, pathlib, pickle
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, show, to_rigid
import rigid


def kstr(k): return k if isinstance(k, str) else f'{k[0]}{k[1]}'


if __name__ == '__main__':
    B, F = pickle.load(open(sys.argv[1], 'rb')), pickle.load(open(sys.argv[2], 'rb'))
    assert tuple(B['d']) == tuple(F['d']), (B['d'], F['d'])
    segs, order = {}, []
    for nm, w, c, m in B['sol'] + F['sol']:
        if nm in segs: continue
        segs[nm] = (w, c, m); order.append(nm)
    riders = sorted(set(B.get('riders', [])) | set(F.get('riders', [])))
    merges = [(1, ['K0', 'N']), (3, ["K0'", "N'"])] if 'N' in segs else []
    fixed = [({c: kstr(k) for c, k in segs[n][1].items()}, None) for n in order]
    kinds = sorted({k for f, _ in fixed for k in f.values()} | {'g', 'P', 'S', 'R'})
    M = FlyerSAT([segs[n][0] for n in order], None, None, kinds=kinds, leaf=True, maxglue=20, fixed=fixed,
                 names=order, riders=riders, merges=merges)
    st, dt = M.solve(600, 16)
    print('assembled', order, 'riders', riders, 'merges', merges, '->', st)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sv = M.solver
        loads = {f'{j}@{t}': sv.Value(e) for (j, t), e in M.loadexpr.items()}
        print('loads', loads)
        sol = M.extract()
        L = max(loads.values())
        out = HERE / 'runs' / 'assembled'; out.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': sol, 'riders': riders, 'merges': merges}, open(out / f'{sys.argv[3]}.pkl', 'wb'))
        rigid.to_flyer(to_rigid(sol), L).save(str(out / f'{sys.argv[3]}.flyer'))
        print('saved', out / f'{sys.argv[3]}.flyer', 'encoded PL', L)
