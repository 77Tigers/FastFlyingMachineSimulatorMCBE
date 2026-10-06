"""subB helpers: build mirror_gen models (mode V / S / none) with pins as assumption literals, solve, diagnose."""
import sys, time, pickle, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
import mirror_gen as G
from mirror_gen import mapper, fbox, candidates
from cfgsat import tcells, ORG, report, KALL
from satflyer import show, wpos, D6, to_rigid
from front_mirror import YZ, dmap, shiftword
from ortools.sat.python import cp_model

OUT = HERE / 'runs' / 'subB'; OUT.mkdir(parents=True, exist_ok=True)


def build(mp, d, mode, L=7, free=(5,), pin=None, maxsize=None, skip=(), r=2, vr=2):
    G.PIN = pin; G.VR = vr
    return G.build(mp, d, mode, L, 5, free, r, maxsize=maxsize, skip=skip)


class Pins:
    """collect pin literals; hard (Add) or as assumptions (for SufficientAssumptionsForInfeasibility)."""
    def __init__(self, M, assume=False):
        self.M, self.assume, self.lits = M, assume, []

    def lit(self, name, l):
        M = self.M
        if self.assume:
            b = M.m.NewBoolVar(name); M.m.AddImplication(b, l); self.lits.append((name, b))
        else:
            M.m.Add(l == 1)

    def cells(self, seg, cells):
        M = self.M; i = M.names.index(seg)
        for u, k in cells.items():
            key = (i, u, k)
            if key not in M.X:
                raise KeyError(f'{seg} {u} {k} not in box')
            self.lit(f'{seg}{u}{k}', M.X[key])

    def only(self, seg, cells):
        """seg consists of exactly these cells (others 0)"""
        M = self.M; i = M.names.index(seg)
        self.cells(seg, cells)
        for u in M.boxes[i]:
            if u not in cells: M.m.Add(M.OCC[i, u] == 0)

    def ride(self, slot, rider, carrier):
        M = self.M
        self.lit(f'ride{slot}_{rider}_{carrier}', M.rc[slot, M.names.index(rider), M.names.index(carrier)])

    def finish(self):
        if self.assume: self.M.m.AddAssumptions([b for _, b in self.lits])


def solve(M, tl=60, wk=4, pins=None):
    st, dt = M.solve(tl, wk)
    core = None
    if st == 'INFEASIBLE' and pins is not None and pins.assume:
        idx = M.solver.SufficientAssumptionsForInfeasibility()
        names = {b.Index(): n for n, b in pins.lits}
        core = [names.get(i, i) for i in idx]
    return st, dt, core


def save(M, mp, d, tag):
    sol = M.extract()
    pickle.dump({'sol': sol, 'map': mp, 'd': d, 'riders': sorted(M.names[x] for x in M.riders),
                 'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]}, open(OUT / f'{tag}.pkl', 'wb'))
    return sol


def world(M, seg, u, t):
    i = M.names.index(seg); return (u[0] + M.sh[i][t], u[1], u[2])


def nbhd(cells, r=1):
    """cells plus all cells within L1 distance r (no x restriction)"""
    out = set(cells)
    for _ in range(r):
        out |= {add3(u, dd) for u in out for dd in D6}
    return sorted(out)


def add3(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def build2(mp, d, mode, L=7, segs=None, vbox=None, maxsize=None, skip=(), extra=None):
    """segs: {'K4': ('fixed', cells) | ('box', cells), 'K5': ...}; other chain segments = templates.
    vbox: rider box (default mirror_gen's). extra: list of additional (name, word, fixed|None, box|None, riderkind)
    chain-1 parts (imaged automatically)."""
    segs = segs or {}
    def chain(last, free, r, mode_):
        half = []
        for nm, w, cells, m in G.START:
            if nm in ('K0', 'N', 'K1'):
                half.append((nm, tuple(w), {c: G.ks(k) for c, k in cells.items()}, None, None))
        for K in range(2, 6):
            c, w = tcells(K); nm = f'K{K}'
            if nm in segs and segs[nm][0] == 'fixed': half.append((nm, w, dict(segs[nm][1]), None, None))
            elif nm in segs: half.append((nm, w, None, list(segs[nm][1]), None))
            else: half.append((nm, w, c, None, None))
        wl = tcells(5)[1]; k = G.second_slot(wl)
        if mode_ in ('V', 'S'):
            rw = tuple(sorted(((k + 2) % 4, (k + 3) % 4))) if mode_ == 'V' else tuple(sorted(((k + 1) % 4, (k + 2) % 4)))
            o = ORG[5]; xr = range(-3, 2) if mode_ == 'V' else range(-1, 4)
            vb = vbox or [add3(o, (a, b, e)) for a in xr for b in range(-2, 3) for e in range(-2, 3)]
            half.append(('V', rw, None, vb, 'P' if mode_ == 'V' else 'S'))
        for e in (extra or []): half.append(e)
        return half
    old = G.chain; G.chain = chain; G.PIN = None
    try:
        return G.build(mp, d, mode, L, 5, (), 2, maxsize=maxsize, skip=skip)
    finally:
        G.chain = old
