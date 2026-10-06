"""Sub-question A helpers (2026-10-06): twin-pull mirrored front (mirror_gen mode 'none') with custom boxes and
assumption-guarded pins.  Same model as mirror_gen.build (imports it), but every free segment gets an explicit box,
F gets an explicit box, and pins are added behind assumption literals so CP-SAT can report a conflicting pin subset.
"""
import sys, pathlib, pickle, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mirror_gen as G
from mirror_gen import mapper, START, ks
from front_mirror import YZ, dmap, shiftword
from cfgsat import tcells, ORG, KALL, report, HERE as _H
from satflyer import FlyerSAT, Infeasible, wpos, WORDS, show, add
from ortools.sat.python import cp_model

MERGES = [(1, ['K0', 'N']), (3, ["K0'", "N'"])]


def cube(o, xr, yr, zr):
    return [add(o, (a, b, e)) for a in range(xr[0], xr[1] + 1) for b in range(yr[0], yr[1] + 1)
            for e in range(zr[0], zr[1] + 1)]


def build(mp, d, L, boxes, fbox, kinds=KALL, skip=(), maxsize=None, last=5, powmiss=(), noF=False):
    """boxes: {K: list of cells} for the free chain-1 segments (others = templates); fbox: F's cells."""
    T, km = mapper(mp, d)
    half = []
    for nm, w, cells, m in START:
        if nm in ('K0', 'N', 'K1'):
            half.append((nm, tuple(w), {c: ks(k) for c, k in cells.items()}, None))
    for K in range(2, last + 1):
        c, w = tcells(K)
        if K in boxes: half.append((f'K{K}', w, None, list(boxes[K])))
        else: half.append((f'K{K}', w, c, None))
    names, words, fixed, bxs, img = [], [], [], [], {}
    for nm, w, c, b in half:
        names.append(nm); words.append(w); fixed.append((c, None) if c else None); bxs.append(b)
    n1 = len(names)
    for i, (nm, w, c, b) in enumerate(half):
        p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w))
        if c: fixed.append(({T(u, p): km(k) for u, k in c.items()}, None)); bxs.append(None)
        else: fixed.append(None); bxs.append([T(u, p) for u in b]); img[i] = (n1 + i, p)
    for t in range(4):
        occ = set()
        for w_, fx in zip(words, fixed):
            if fx is None: continue
            for c_ in fx[0]:
                cc = (c_[0] + wpos(w_, t), c_[1], c_[2])
                if cc in occ: return 'SKEL_OVERLAP'
                occ.add(cc)
    if not noF:
        names.append('F'); words.append(WORDS['mwmw']); fixed.append(None); bxs.append(list(fbox))
    # powmiss segments: power may come from outside (open_segs flag; satflyer then skips their load cap, so cap size)
    ms = [maxsize.get(nm.rstrip("'")) if maxsize else None for nm in names]
    for i, nm in enumerate(names):
        if nm.rstrip("'") in powmiss: ms[i] = min(ms[i] or L, L)
    opens = {names.index(nm): {'powmiss'} for nm in names if nm.rstrip("'") in powmiss}
    try:
        M = FlyerSAT(words, None, L, kinds=kinds, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=bxs,
                     merges=MERGES, maxsize=ms, skip=skip, open_segs=opens)
    except Infeasible:
        return 'TRIV_INFEASIBLE'
    for i, (j, p) in img.items():
        for u in bxs[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[i, u, k] == M.X[j, T(u, p), km(k)])
    M.T = T; M.km = km
    return M


def pin(M, pins, assume=True, absent=()):
    """pins: [(seg, cell, kind)] -> X == 1; absent: [(seg, cell)] -> cell empty.  Returns {literal: description}."""
    lits = {}
    for nm, c, k in pins:
        i = M.names.index(nm)
        if (i, c, k) not in M.X:
            raise KeyError(f'pin outside box: {nm} {c} {k}')
        if assume:
            b = M.m.NewBoolVar(f'pin_{nm}_{c}_{k}')
            M.m.Add(M.X[i, c, k] == 1).OnlyEnforceIf(b); lits[b] = f'{nm} {c} {k}'
        else:
            M.m.Add(M.X[i, c, k] == 1)
    for nm, c in absent:
        i = M.names.index(nm)
        if (i, c) not in M.OCC: continue
        if assume:
            b = M.m.NewBoolVar(f'abs_{nm}_{c}')
            M.m.Add(M.OCC[i, c] == 0).OnlyEnforceIf(b); lits[b] = f'{nm} {c} EMPTY'
        else:
            M.m.Add(M.OCC[i, c] == 0)
    if assume and lits:
        M.m.AddAssumptions(list(lits))
    return lits


def solve(M, tl=60, wk=4):
    return M.solve(tl, wk)


def core(M, lits, tl=120):
    """1-worker solve; on INFEASIBLE return the sufficient subset of pin literals."""
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = tl
    sv.parameters.num_search_workers = 1
    t0 = time.time()
    st = sv.Solve(M.m)
    name = sv.StatusName(st)
    out = None
    if name == 'INFEASIBLE':
        idx = sv.SufficientAssumptionsForInfeasibility()
        bylit = {l.Index(): s for l, s in lits.items()}
        out = [bylit.get(i, f'?{i}') for i in idx]
    M.solver = sv
    return name, time.time() - t0, out


def save(M, mp, d, tag):
    sol = M.extract()
    od = HERE / 'runs' / 'subA'; od.mkdir(parents=True, exist_ok=True)
    pickle.dump({'sol': sol, 'map': mp, 'd': d, 'riders': [], 'merges': MERGES}, open(od / f'{tag}.pkl', 'wb'))
    return od / f'{tag}.pkl', sol
