"""Hand-pinned front-cap tests (2026-10-09) for the two lowest-bound untested topology families.

Model: power_riders_20261007/psat.py (= rigid_sat satflyer + power riders + rider leaf loads charged to carriers).
Chain: K2 boundary (BND_BACK), K3 template, K4 template or free, then the family's front parts.

Families (single chain, chain orientation ORIENTS[0]; template origins K4 (8,2,2), K5 (11,2,3), K6 (12,3,3)):
  fam1: F (mmww, K6 position) sticky pulls K5 @3; K5 pushes F @0; rider sticky Q (wwmm) rides K5 @2,@3 and pulls F @1.
  fam2: rider sticky Q (mmww) rides K4 @0,@1 and pulls K5 @3; no F (K5's sticky needs slot-0 power from K4 or a
        power rider).
Variants are named below (VARIANTS); each is a function returning a parts list:
  (name, word, fixed_cells|None, box|None, rider_kinds|None, pins|None, maxsize|None)
usage: python pinfront.py VARIANT L [--obj maxload] [--tl 120] [--wk 4] [--save]
"""
import sys, pathlib, pickle, argparse, time
HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
for p in (str(EXP / 'rigid_chain_20261003'), str(EXP / 'rigid_sat_20261004'), str(EXP / 'power_riders_20261007')):
    if p in sys.path: sys.path.remove(p)
    sys.path.insert(0, p)
from psat import FlyerSAT, Infeasible, show, D6, WORDS
from cfgsat import tcells
from modules import BND_BACK

KPOW = ['R'] + [f'D{i}' for i in range(6)] + [f'O{i}' for i in range(6)]
KALL = ['g', 'P', 'S'] + KPOW


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def nbhd(cells, r=1):
    out = set(cells)
    for _ in range(r):
        out |= {add(u, d) for u in out for d in D6}
    return sorted(out)


def cube(lo, hi):
    return [(x, y, z) for x in range(lo[0], hi[0] + 1) for y in range(lo[1], hi[1] + 1) for z in range(lo[2], hi[2] + 1)]


T = {K: tcells(K)[0] for K in range(2, 9)}
W4, W5 = 'mmww', 'wwmm'


def base(k4='tmpl', k4r=1, k4pins=None, k4max=None):
    parts = [('K2', W4, T[2], None, None, None, None), ('K3', W5, T[3], None, None, None, None)]
    if k4 == 'tmpl': parts.append(('K4', W4, T[4], None, None, None, None))
    else: parts.append(('K4', W4, None, nbhd(list(T[4]), k4r), None, k4pins if k4pins is not None else dict(T[4]), k4max))
    return parts


def strip(d, *cells):
    d = dict(d)
    for c in cells: d.pop(c, None)
    return d


# ------------------------------------------------------------------ family 1
# paper skeleton: K5 = template (R (10,1,3) powers K4's P/S @2; S (11,2,2) pulls K4 @1; g (11,2,3) pushed by K4 @2;
# P (11,3,3) pushes F @0).  F = template K6 minus P: R (11,3,2) powers K5's P,S @0; S (12,2,3) pulls K5's (11,2,3) @3.
# Q (wwmm sticky) at f1 + (3,0,0) for F's pulled glue f1; must touch K5 glue at slots 2,3 (K5 needs an arm forward).
F6 = strip(T[6], (12, 3, 4))           # K6 template minus its pusher


def fam1(k5pins, fpins, k5box, fbox, qbox, k5max=None, fmax=None, k4='tmpl', wpow=None):
    parts = base(k4)
    parts.append(('K5', W5, None, k5box, None, k5pins, k5max))
    parts.append(('F', W4, None, fbox, None, fpins, fmax))
    parts.append(('Q', W5, None, qbox, ['S'], None, None))
    if wpow: parts.append(('W', wpow[0], None, wpow[1], KPOW, None, None))
    return parts


def fam1_free(r5=1, rf=1):
    k5box = nbhd(list(T[5]), r5) + cube((12, 0, 1), (15, 4, 5))
    fbox = nbhd(list(F6), rf)
    return fam1(dict(T[5]), dict(F6), sorted(set(k5box)), fbox, cube((13, 0, 1), (16, 4, 5)))


# ------------------------------------------------------------------ family 2
def fam2(k4pins, k5pins, k4box, k5box, qbox, k4max=None, k5max=None, wpow=None):
    parts = [('K2', W4, T[2], None, None, None, None), ('K3', W5, T[3], None, None, None, None)]
    parts.append(('K4', W4, None, k4box, None, k4pins, k4max))
    parts.append(('K5', W5, None, k5box, None, k5pins, k5max))
    parts.append(('Q', W4, None, qbox, ['S'], None, None))
    if wpow: parts.append(('W', wpow[0], None, wpow[1], KPOW, None, None))
    return parts


K5noP = strip(T[5], (11, 3, 3))


VARIANTS = {
    # family 1: template skeletons pinned, extras free in boxes
    'f1_free': lambda: fam1_free(),
    'f1_free_k4': lambda: fam1(dict(T[5]), dict(F6), sorted(set(nbhd(list(T[5]), 1) + cube((12, 0, 1), (15, 4, 5)))),
                               nbhd(list(F6), 1), cube((13, 0, 1), (16, 4, 5)), k4='free'),
    'f1_wide': lambda: fam1(dict(T[5]), dict(F6), sorted(set(nbhd(list(T[5]), 1) + cube((12, 0, 1), (15, 4, 5)))),
                            sorted(set(nbhd(list(F6), 1) + cube((12, 1, 1), (16, 5, 5)))), cube((12, 0, 0), (16, 5, 5))),
    'f1_wideW': lambda: fam1(dict(T[5]), dict(F6), sorted(set(nbhd(list(T[5]), 1) + cube((12, 0, 1), (15, 4, 5)))),
                             sorted(set(nbhd(list(F6), 1) + cube((12, 1, 1), (16, 5, 5)))), cube((12, 0, 0), (16, 5, 5)),
                             wpow=('mwmw', cube((11, 0, 0), (17, 5, 5)))),
    'f1_loose': lambda: fam1({(11, 2, 3): 'g'}, None, sorted(set(nbhd(list(T[5]), 1) + cube((12, 0, 1), (15, 4, 5)))),
                             sorted(set(nbhd(list(F6), 1) + cube((12, 1, 1), (16, 5, 5)))), cube((12, 0, 0), (16, 5, 5))),
    'f1_back': lambda: fam1({(11, 2, 3): 'g'}, {(12, 2, 3): 'S'}, cube((9, 0, 1), (14, 4, 5)),
                            cube((9, 1, 1), (14, 5, 6)), cube((11, 0, 0), (15, 5, 6))),
    # family 2
    'f2_wide': lambda: fam2({(8, 2, 2): 'g'}, {(11, 2, 3): 'g'}, sorted(set(nbhd(list(T[4]), 1) + cube((9, 0, 0), (12, 4, 5)))),
                            sorted(set(nbhd(list(T[5]), 1) + cube((8, 0, 1), (12, 4, 5)))), cube((8, 0, 0), (13, 5, 6))),
    'f2_free': lambda: fam2(dict(T[4]), K5noP, nbhd(list(T[4]), 2), nbhd(list(K5noP), 2), cube((9, 0, 0), (13, 4, 5))),
}


def build(parts, L, leafrod=True, kinds=KALL, skip=()):
    names, words, fixed, boxes, riders, kbs, must, maxs = [], [], [], [], [], {}, {}, []
    opens = {0: BND_BACK}
    for nm, w, c, b, rk, pins, mx in parts:
        names.append(nm); words.append(WORDS[w] if isinstance(w, str) else tuple(w))
        fixed.append((c, None) if c else None); boxes.append(b); maxs.append(mx)
        if rk: riders.append(nm); kbs[nm] = list(rk)
        if pins:
            if b is not None:
                bs = set(b); assert all(u in bs for u in pins), (nm, [u for u in pins if u not in bs])
            must[nm] = dict(pins)
    M = FlyerSAT(words, None, L, kinds=kinds, leaf=True, maxglue=max(L - 1, 6), fixed=fixed, names=names, boxes=boxes,
                 open_segs=opens, riders=riders, kinds_by_seg=kbs, must=must, maxsize=maxs, leafrod=leafrod, skip=skip)
    return M


def mbuild(mp, d, L, parts, leafrod=True, skip=(), extra=(), opens=None):
    """Mirrored flyer (no shared F): chain 1 = load-7 start cap (K0, N, K1 fixed) + parts; every part gets an image
    under yz map mp + offset d (words shifted by 2 slots, x shifted by the part's slot-2 position).  extra: unmirrored
    parts.  Image boxes = mapped boxes, image cells == mapped cells."""
    from psat import wpos
    from mirror_gen import mapper, START
    from front_mirror import shiftword
    Tm, km = mapper(mp, d)
    half = [(nm, tuple(w), {c: (k if isinstance(k, str) else f'{k[0]}{k[1]}') for c, k in cells.items()}, None, None, None, None)
            for nm, w, cells, m in START if nm in ('K0', 'N', 'K1')]
    half += [(nm, WORDS[w] if isinstance(w, str) else tuple(w), c, b, rk, pins, mx) for nm, w, c, b, rk, pins, mx in parts]
    names, words, fixed, boxes, riders, kbs, must, maxs, img = [], [], [], [], [], {}, {}, [], {}
    for nm, w, c, b, rk, pins, mx in half:
        names.append(nm); words.append(w); fixed.append((c, None) if c else None); boxes.append(b); maxs.append(mx)
        if rk: riders.append(nm); kbs[nm] = list(rk)
        if pins: must[nm] = dict(pins)
    for i, (nm, w, c, b, rk, pins, mx) in enumerate(half):
        p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w)); maxs.append(mx)
        if c: fixed.append(({Tm(u, p): km(k) for u, k in c.items()}, None)); boxes.append(None)
        else: fixed.append(None); boxes.append([Tm(u, p) for u in b]); img[i] = (len(names) - 1, p)
        if rk: riders.append(nm + "'"); kbs[nm + "'"] = sorted({km(k) for k in rk})
    for nm, w, c, b, rk, pins, mx in extra:
        names.append(nm); words.append(WORDS[w] if isinstance(w, str) else tuple(w)); fixed.append((c, None) if c else None)
        boxes.append(b); maxs.append(mx)
        if rk: riders.append(nm); kbs[nm] = list(rk)
        if pins: must[nm] = dict(pins)
    for t in range(4):                                     # fixed skeleton overlap check
        occ = set()
        for w_, fx in zip(words, fixed):
            if fx is None: continue
            for c_ in fx[0]:
                cc = (c_[0] + wpos(w_, t), c_[1], c_[2])
                if cc in occ: return None
                occ.add(cc)
    M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=max(L - 1, 6), fixed=fixed, names=names, boxes=boxes,
                 riders=riders, kinds_by_seg=kbs, must=must, maxsize=maxs, skip=skip, leafrod=leafrod,
                 merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])],
                 open_segs={names.index(k): v for k, v in (opens or {}).items()})
    for i, (j, p) in img.items():
        for u in boxes[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[i, u, k] == M.X[j, Tm(u, p), km(k)])
    return M


def report(M):
    sv = M.solver
    out = ['loads ' + ' '.join(f'{M.names[j] if isinstance(j, int) else "+".join(M.names[x] for x in j)}@{t}={sv.Value(e)}'
                               for (j, t), e in sorted(M.loadexpr.items(), key=lambda kv: str(kv[0])))]
    out.append('riders ' + str([(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if sv.Value(v)]))
    return '\n'.join(out)


def run(parts, L, tl=120, wk=4, obj=None, tag=None, hint=None, skip=()):
    t0 = time.time()
    try:
        M = build(parts, L, skip=skip)
    except Infeasible as e:
        print('TRIVIAL_INFEASIBLE', e, flush=True); return 'TRIVIAL_INFEASIBLE', None, None
    if hint is not None: M.hint(hint)
    st, dt = M.solve(tl, wk, objective=obj)
    print(f'{tag} L={L} obj={obj} -> {st} {dt:.1f}s (build {time.time() - t0 - dt:.1f}s)', flush=True)
    sol = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract(); print(show(sol)); print(report(M))
        if obj == 'maxload': print('max load', int(M.solver.ObjectiveValue()), 'bound', int(M.solver.BestObjectiveBound()))
        if tag:
            od = HERE / 'runs' / 'pin'; od.mkdir(parents=True, exist_ok=True)
            pickle.dump({'sol': sol, 'riders': sorted(M.names[r] for r in M.riders), 'parts': parts},
                        open(od / f'{tag}_L{L}{"_" + obj if obj else ""}.pkl', 'wb'))
    elif obj == 'maxload' and st == 'UNKNOWN':
        print('bound', M.solver.BestObjectiveBound())
    return st, sol, M


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('variant'); ap.add_argument('L', type=int)
    ap.add_argument('--obj', default=None); ap.add_argument('--tl', type=float, default=120)
    ap.add_argument('--wk', type=int, default=4); ap.add_argument('--skip', default='')
    a = ap.parse_args()
    sk = tuple(x for x in a.skip.split(',') if x)
    run(VARIANTS[a.variant](), a.L, a.tl, a.wk, a.obj, tag=None if sk else a.variant, skip=sk)
