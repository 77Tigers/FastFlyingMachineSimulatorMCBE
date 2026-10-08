"""Mirrored-front builder on psat (power riders allowed).  Same design family as rigid_sat_20261004/mirror_gen.py:
chain 1 = load-7 start cap (K0, N, K1 fixed) + K2.. + front parts; chain 2 = image under yz map `mp` + offset d with
words shifted by 2 slots; shared passive mwmw front F (free in fbox or fixed).
parts: list of (name, word, fixed_cells | None, box | None, rider_kinds | None) for chain 1 AFTER K1 (K2, K3, ...,
V, W, ...); every part gets an image (name + "'") unless name starts with '!' (then it is a single, unmirrored part).
Rider kinds: e.g. ['P'] (hand-off pusher V) or KPOW (power rider W: redstone / rod / observer, one block, no glue).
"""
import sys, pathlib, pickle
HERE = pathlib.Path(__file__).resolve().parent
RS = HERE.parent / 'rigid_sat_20261004'
for p in (str(HERE.parent / 'rigid_chain_20261003'), str(RS), str(HERE)):
    if p in sys.path: sys.path.remove(p)
    sys.path.insert(0, p)
from psat import FlyerSAT, Infeasible, wpos, WORDS, show, D6
import mirror_gen as G
from mirror_gen import mapper, fbox, second_slot, START
from front_mirror import shiftword, YZ
from cfgsat import tcells, ORG

KPOW = ['R'] + [f'D{i}' for i in range(6)] + [f'O{i}' for i in range(6)]
KALL = ['g', 'P', 'S'] + KPOW
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
BANK = pickle.load(open(RS / 'runs' / 'assembled' / 'mirror_freeF_L8.pkl', 'rb'))
BANKC = {nm: (tuple(w), {c: ks(k) for c, k in cells.items()}) for nm, w, cells, m in BANK['sol']}


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def nbhd(cells, r=1):
    out = set(cells)
    for _ in range(r):
        out |= {add(u, dd) for u in out for dd in D6}
    return sorted(out)


def cube(c, xr, r):
    return [add(c, (a, b, e)) for a in xr for b in range(-r, r + 1) for e in range(-r, r + 1)]


def build(mp, d, L, parts, F=None, leafrod=True, maxsize=None, skip=(), fixF=None):
    T, km = mapper(mp, d)
    half = []
    for nm, w, cells, m in START:
        if nm in ('K0', 'N', 'K1'):
            half.append((nm, tuple(w), {c: ks(k) for c, k in cells.items()}, None, None))
    half += list(parts)
    names, words, fixed, boxes, riders, kbs, img = [], [], [], [], [], {}, {}
    for nm, w, c, b, rk in half:
        names.append(nm.lstrip('!')); words.append(tuple(w)); fixed.append((c, None) if c else None); boxes.append(b)
        if rk: riders.append(nm.lstrip('!')); kbs[nm.lstrip('!')] = list(rk)
    n1 = len(names)
    for i, (nm, w, c, b, rk) in enumerate(half):
        if nm.startswith('!'): continue
        p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w))
        if c: fixed.append(({T(u, p): km(k) for u, k in c.items()}, None)); boxes.append(None)
        else: fixed.append(None); boxes.append([T(u, p) for u in b]); img[i] = (len(names) - 1, p)
        if rk: riders.append(nm + "'"); kbs[nm + "'"] = sorted({km(k) for k in rk})
    for t in range(4):
        occ = set()
        for w_, fx in zip(words, fixed):
            if fx is None: continue
            for c_ in fx[0]:
                cc = (c_[0] + wpos(w_, t), c_[1], c_[2])
                if cc in occ: return 'SKEL_OVERLAP'
                occ.add(cc)
    names.append('F'); words.append(WORDS['mwmw'])
    if fixF is not None: fixed.append((fixF, None)); boxes.append(None)
    else: fixed.append(None); boxes.append(F if F is not None else fbox(mp, d, 5)[0])
    ms = None
    if maxsize: ms = [maxsize.get(nm, maxsize.get(nm.rstrip("'"))) for nm in names]
    try:
        M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=max(L - 1, 1) if L else 12, fixed=fixed,
                     names=names, boxes=boxes, riders=riders, kinds_by_seg=kbs, maxsize=ms, skip=skip,
                     merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])], leafrod=leafrod)
    except Infeasible:
        return 'TRIV_INFEASIBLE'
    for i, (j, p) in img.items():
        for u in boxes[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[i, u, k] == M.X[j, T(u, p), km(k)])
    M.mp, M.d = mp, d
    return M


class Pins:
    def __init__(self, M): self.M = M

    def cells(self, seg, cells):
        M = self.M; i = M.names.index(seg)
        for u, k in cells.items(): M.m.Add(M.X[i, u, k] == 1)

    def only(self, seg, cells):
        M = self.M; i = M.names.index(seg); self.cells(seg, cells)
        for u in M.boxes[i]:
            if u not in cells: M.m.Add(M.OCC[i, u] == 0)

    def ride(self, t, r, c):
        M = self.M; M.m.Add(M.rc[t, M.names.index(r), M.names.index(c)] == 1)


def report(M):
    sv = M.solver
    loads = {f'{M.names[j] if isinstance(j, int) else j}@{t}': sv.Value(e) for (j, t), e in M.loadexpr.items()}
    out = ['max load %d; loads>=6: %s' % (max(loads.values()), sorted((v, k) for k, v in loads.items() if v >= 6))]
    out.append('riders ' + str([(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if sv.Value(v)]))
    return '\n'.join(out)


def save(M, path):
    sol = M.extract()
    pickle.dump({'sol': sol, 'map': M.mp, 'd': M.d, 'riders': sorted(M.names[x] for x in M.riders),
                 'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]}, open(path, 'wb'))
    return sol
