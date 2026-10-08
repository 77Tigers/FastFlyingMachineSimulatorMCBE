"""Gull-wing bird: the stretched PL8 mirrored bird (stretch.py) with an ELBOW in each arm.
Chain 1 = start cap + o0 templates up to K_j (wing rises in y toward the elbow), joint segment K_{j+1} (joint.py,
o0 -> o2), then everything in front (o2 templates, front cap K_{last-1}, K_last, rider V, shared F) = the straight
bird's front part mirrored in y (G: y -> ty - y, ty = 2 * ORG[j+1].y), so the inner wing descends to the body.
Chain 2 = flipz image as in the straight bird (G commutes with the flipz map, so the front region is just G of the
banked front region). Whole design re-checked exactly in satflyer (all cells fixed), then exported.
usage: python gull.py LAST JOINT_PKL [--tag NAME]   (the joint pkl was solved at j = 6; it is moved to j = 6 + 2i
       with --i I by the alt-chain period shift (4,1,1))
"""
import sys, pathlib, pickle, time, argparse
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stretch                                   # extends ORG, imports satflyer/mirror_gen
from stretch import add, wpos, shiftword, mg, check, to_rigid, rigid
from front_mirror import YZ, dmap
from cfgsat import ORG

ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'


def gull(last, joint_pkl, i=0):
    segs, d, mp = stretch.design(last)
    J = pickle.load(open(joint_pkl, 'rb'))
    j0 = J['j']; j = j0 + 2 * i
    assert J['OA'] == 0 and J['OB'] == 2 and tuple(J['off']) == (0, 0) and J['nf'] == 1
    assert j + 2 <= last - 2, 'joint must sit behind the front cap'
    jc = {nm: c for nm, w, c, m in J['sol']}[f'K{j0 + 1}']
    jcells = {add(u, (4 * i, i, i)): ks(k) for u, k in jc.items()}
    ty = 2 * ORG[j + 1][1]
    dm = dmap('flipy')
    gk = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
    G = lambda c: {(u[0], ty - u[1], u[2]): gk(k) for u, k in c.items()}
    half, F = [], None
    for nm, w, c in segs:
        if nm.endswith("'"): continue
        if nm == 'F': F = (nm, w, G(c)); continue
        if nm.startswith('K') and nm[1:].isdigit():
            K = int(nm[1:])
            if K == j + 1: half.append((nm, w, jcells)); continue
            if K >= j + 2: half.append((nm, w, G(c))); continue
            half.append((nm, w, c)); continue
        if nm == 'V': half.append((nm, w, G(c))); continue
        half.append((nm, w, c))                  # N
    T, km = mg.mapper(mp, d)
    out = list(half)
    for nm, w, c in half:
        p = wpos(w, 2)
        out.append((nm + "'", shiftword(w), {T(u, p): km(k) for u, k in c.items()}))
    out.append(F)
    return out, d, mp, j


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('last', type=int); ap.add_argument('joint')
    ap.add_argument('--i', type=int, default=0); ap.add_argument('--tag', default=None)
    a = ap.parse_args()
    segs, d, mp, j = gull(a.last, a.joint, a.i)
    for t in range(4):
        seen = {}
        for nm, w, c in segs:
            for u in c:
                cc = (u[0] + wpos(w, t), u[1], u[2])
                if cc in seen: print('OVERLAP slot', t, cc, seen[cc], nm)
                seen[cc] = nm
    t0 = time.time()
    M, st, dt = check(segs, 300, 4)
    print('gull last', a.last, 'joint K%d' % (j + 1), 'd', d, 'segments', len(segs), 'blocks',
          sum(len(s[2]) for s in segs), '->', st, f'{time.time() - t0:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sv = M.solver
        loads = {f'{M.names[x] if isinstance(x, int) else x}@{t}': sv.Value(e) for (x, t), e in M.loadexpr.items()}
        PL = max(loads.values())
        print('max load', PL, 'loads>=7', sorted((v, k) for k, v in loads.items() if v >= 7))
        sol = M.extract()
        tag = a.tag or f'gull_last{a.last}_j{j + 1}'
        pickle.dump({'sol': sol, 'map': mp, 'd': d, 'last': a.last, 'joint': j + 1, 'riders': ['V', "V'"],
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])], 'loads': loads},
                    open(HERE / 'runs' / f'{tag}.pkl', 'wb'))
        rigid.to_flyer(to_rigid(sol), PL).save(str(HERE / 'runs' / f'{tag}.flyer'))
        print('saved', HERE / 'runs' / f'{tag}.flyer', 'encoded PL', PL)
