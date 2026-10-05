"""Join solved back and front modules into complete flyers with straight template chains, check, export.

For each back module (o2, db) and front module (same o2, df) with df = db + (4*(m2-m1), m2*(a2+c2) - m1*(a1+c1)),
chain 1 = A, a1..a(2m1-1), F1 and chain 2 = B, b1..b(2m2-1), F2 (m >= 2 so modules don't share free segments).
Module segments keep their solved cells/materials; the rest are alt templates with materials tried in both phases.
Every assembled flyer is checked with rigid.check (LEAF) and exported to OUTDIR as .flyer + .pkl.

usage: python join.py BACKDIR FRONTDIR OUTDIR [MMAX]
"""
import sys, pathlib, pickle, itertools, os
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
os.environ['LEAF'] = '1'
import rigid
rigid.LEAF = True
from chainflyer import ORIENTS, template, origins
from modules import sub, add


def load_mods(d):
    out = {}
    for p in pathlib.Path(d).glob('*.pkl'):
        r = pickle.load(open(p, 'rb'))
        a = r['args']; out.setdefault((a[1], tuple(a[2])), []).append((p.stem, r['sol']))
    return out


def tmpl_seg(name, K, o, shift):
    cells, word = template(K, *o)
    og = add(origins(K + 1, *o)[K], shift)
    return name, word, {add(og, u): k for u, k in cells.items()}


def assemble(back, front, o2i, db, m1, m2, mats_phase):
    o1, o2 = ORIENTS[0], ORIENTS[o2i]
    L1, L2 = 2 * m1, 2 * m2
    bsol = {nm: (w, c, mt) for nm, w, c, mt in back}
    fsol = {nm: (w, c, mt) for nm, w, c, mt in front}
    T = sub(origins(L1 + 1, *o1)[L1], origins(5, *o1)[4])       # front-module frame -> flyer frame
    tr = lambda cells: {add(c, T): k for c, k in cells.items()}
    segs = []
    # chain 1: K0..K(L1). back module names a1,a2 = K1,K2 ; front module c2,p1,F1 = K(L1-2),K(L1-1),K(L1)
    for K in range(L1 + 1):
        if K == 0: nm, src = 'A', ('b', 'A')
        elif K == L1: nm, src = 'F1', ('f', 'F1')
        elif K == L1 - 1: nm, src = f'a{K}', ('f', 'p1')
        elif K == L1 - 2 and K >= 3: nm, src = f'a{K}', ('f', 'c2')
        elif K in (1, 2): nm, src = f'a{K}', ('b', f'a{K}')
        else: nm, src = f'a{K}', None
        segs.append((nm, K, 1, src))
    org2_1 = origins(2, *o2)[1]
    for K in range(1, L2 + 2):
        if K == 1: nm, src = 'B', ('b', 'B')
        elif K == L2 + 1: nm, src = 'F2', ('f', 'F2')
        elif K == L2: nm, src = f'b{K - 1}', ('f', 'p2')
        elif K == L2 - 1 and K >= 4: nm, src = f'b{K - 1}', ('f', 'd2')
        elif K in (2, 3): nm, src = f'b{K - 1}', ('b', f'b{K - 1}')
        else: nm, src = f'b{K - 1}', None
        segs.append((nm, K, 2, src))
    out = []
    for nm, K, ch, src in segs:
        o = o1 if ch == 1 else o2
        shift = (0, 0, 0) if ch == 1 else sub(db, org2_1)
        if src is None:
            n_, word, cells = tmpl_seg(nm, K, o, shift)
            mat = ('slime', 'honey')[(K + mats_phase[ch - 1]) % 2]
        elif src[0] == 'b':
            word, cells, mat = bsol[src[1]]
        else:
            word, cells, mat = fsol[src[1]]
            cells = tr(cells)
        out.append(rigid.Seg(nm, word, (0, 0, 0), dict(cells), mat))
    return out


def main():
    bd, fd, od = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]); od.mkdir(parents=True, exist_ok=True)
    mmax = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    B, F = load_mods(bd), load_mods(fd)
    print('back modules', sum(len(v) for v in B.values()), 'front modules', sum(len(v) for v in F.values()))
    o1 = ORIENTS[0]; d1 = (o1[0][0] + o1[1][0], o1[0][1] + o1[1][1])
    n_try = n_ok = 0
    for (o2i, db), blist in B.items():
        o2 = ORIENTS[o2i]; d2 = (o2[0][0] + o2[1][0], o2[0][1] + o2[1][1])
        for m1 in range(2, mmax + 1):
            for m2 in range(2, mmax + 1):
                df = (db[0] + 4 * (m2 - m1), db[1] + m2 * d2[0] - m1 * d1[0], db[2] + m2 * d2[1] - m1 * d1[1])
                for ftag, fsol in F.get((o2i, df), []):
                    for btag, bsol in blist:
                        for ph in itertools.product((0, 1), repeat=2):
                            segs = assemble(bsol, fsol, o2i, db, m1, m2, ph)
                            n_try += 1
                            r = rigid.check(segs)
                            if r is None:
                                lo = rigid.loads(segs); n_ok += 1
                                tag = f'J_{btag}__{ftag}__m{m1}{m2}_ph{ph[0]}{ph[1]}_load{lo}'
                                print('OK', tag, flush=True)
                                pickle.dump(segs, open(od / f'{tag}.pkl', 'wb'))
                                rigid.to_flyer(segs, lo).save(str(od / f'{tag}.flyer'))
                                break
                            else:
                                print('fail', btag, ftag, m1, m2, ph, r)
    print('tried', n_try, 'ok', n_ok)


if __name__ == '__main__':
    main()
