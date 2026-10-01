"""A/B 3.333 bps generator: three A/B pairs with words mmwmmw, mwmmwm, wmmwmm.

A_i (honey) only pulled by stickies anchored on a resting B; B_i (slime) only pushed by pistons anchored
on a resting A. One cross module per fire slot f (see RESUME.md / FINDINGS.md):
  center line: alpha-pair redstone at x=0 (+ glue holder at x=-1);  alpha = pair resting at f+2
  N/E/S/W lines: P(B_alpha), P(B_beta), Q(A_alpha), Q(A_gamma) at x=0 (module frame = start of slot f)
  NE,SW: A_gamma glue at x=0 (P anchor, carry slots f+4,f+5);  gamma = pair resting at f
  SE,NW: B_beta glue at x=-1 (Q anchor, carry slots f+2,f+3);  beta = pair resting at f+1
  P: victim D at x=+1 in line.  Q: arm x=-1, victim C at x=-2 at start of f+1.
Module f+3 = mirror(module f) (z -> -z) with the same x (bodies advance 2 per 3 slots).
World frame = start of slot 0. Bodies are routed with greedy Steiner paths avoiding time-overlap,
same-glue adjacency, foreign-source adjacency and extension hazards. Output: candidate flyers.
"""
import sys, json, random, itertools
from pathlib import Path
from collections import deque
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind

WORDS = ['mmwmmw', 'mwmmwm', 'wmmwmm']
L = 6
DIRS6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
E, W = 0, 1


def nb(c):
    return [(c[0] + d[0], c[1] + d[1], c[2] + d[2]) for d in DIRS6]


class Lay:
    def __init__(self, words=WORDS):
        self.w = [[1 if ch == 'm' else 0 for ch in s] for s in words]
        self.L = len(words[0]); self.D = sum(self.w[0])
        self.bodies = [(t, i) for i in range(len(words)) for t in 'AB']
        self.offs = {}
        for b in self.bodies:
            o = [0]
            for k in range(self.L): o.append(o[-1] + self.w[b[1]][k])
            self.offs[b] = o

    def off(self, b, k):
        return self.offs[b][k % self.L] + (k // self.L) * self.D

    def moves(self, b, k):
        return self.w[b[1]][k % self.L] == 1

    def rest_pair(self, s):
        return [i for i in range(len(self.w)) if not self.w[i][s % self.L]]


def build(lay, params, seed=0):
    rnd = random.Random(seed)
    Lh = lay.L
    # per-module parameters
    items = []   # dict(kind, body(owner for sources) , traj: list of world cells k=0..L-1, ...)
    req = {b: {} for b in lay.bodies}  # body -> {bframe cell: tag}
    pist = []    # piston records
    sources = []  # redstone: (body, bframe cell)
    for f in range(Lh):
        gam = lay.rest_pair(f)[0]; bet = lay.rest_pair(f + 1)[0]; alp = lay.rest_pair(f + 2)[0]
        base = f % 3
        mir = f >= 3
        cy, cz = params['u'][base]
        xi = params['xi'][base] + (2 if mir else 0)
        perm = params['perm'][base]  # order of [P_alpha, P_beta, Q_alpha, Q_gamma] onto N,E,S,W
        holder_body = ('B', alp) if params['holder'][base] == 'B' else ('A', alp)
        hx = params['hx'][base]
        sg = -1 if mir else 1

        def yz(dy, dz):
            return (cy + dy, sg * (cz + dz))
        lines = dict(N=(1, 0), E=(0, 1), S=(-1, 0), W=(0, -1))
        names = ['N', 'E', 'S', 'W']
        roles = [('P', ('B', alp)), ('P', ('B', bet)), ('Q', ('A', alp)), ('Q', ('A', gam))]

        def bcell(body, mx, ycz):
            # module-frame x (start of slot f) -> body frame (world at slot 0)
            return (xi + mx - lay.off(body, f), ycz[0], ycz[1])

        def put(body, cell, tag):
            if cell in req[body] and req[body][cell] != tag:
                pass
            req[body][cell] = tag
        # center: beta-pair B glue at -2, observer at -1 facing +X, glazed terracotta at 0 (pushed along)
        cyz = yz(0, 0)
        if params.get('power', 'obs') == 'obs':
            bb = ('B', bet)
            put(bb, bcell(bb, -2, cyz), 'cglue%d' % f)
            sources.append(dict(kind='obs', body=bb, cell=bcell(bb, -1, cyz), target=bcell(bb, 0, cyz), f=f))
        else:
            sources.append(dict(kind='rs', body=holder_body, cell=bcell(holder_body, 0, cyz), f=f))
            put(holder_body, bcell(holder_body, hx, cyz), 'holder%d' % f)
        # diagonals
        for (dy, dz) in [(1, 1), (-1, -1)]:
            put(('A', gam), bcell(('A', gam), 0, yz(dy, dz)), 'gam%d' % f)
        for (dy, dz) in params.get('betdiag', [(-1, 1), (1, -1)]):
            put(('B', bet), bcell(('B', bet), -1, yz(dy, dz)), 'bet%d' % f)
        for idx, (kind, victim) in enumerate(roles):
            ln = lines[names[perm[idx]]]
            pyz = yz(*ln)
            pist.append(dict(kind=kind, f=f, victim=victim, yz=pyz, xi=xi))
            if kind == 'P':
                put(victim, bcell(victim, 1, pyz), 'D%d' % f)
            else:
                delta = lay.off(victim, f + 1) - lay.off(victim, f)
                put(victim, bcell(victim, -2 - delta, pyz), 'C%d' % f)
    return req, pist, sources


def piston_traj(lay, p):
    """world x at start of slot k=0..L-1 (cycle 0) and state info. Moves +1 every non-frozen slot."""
    f = p['f']; fro = {f % lay.L, (f + 1) % lay.L}
    # position at start of f is xi; walk backwards to slot 0
    x = {f: p['xi']}
    for k in range(f, 0, -1):
        x[k - 1] = x[k] - (0 if (k - 1) % lay.L in fro else 1)
    for k in range(f, lay.L):
        x[k + 1] = x[k] + (0 if k % lay.L in fro else 1)
    return [x[k] for k in range(lay.L + 1)]


def source_traj(lay, body, cell):
    return [cell[0] + lay.off(body, k) for k in range(lay.L + 1)]


def analyse(lay, req, pist, sources):
    """Static checks on required cells: overlaps, power. Returns list of problems."""
    probs = []
    Lh = lay.L
    occ = [dict() for _ in range(Lh)]

    def mark(k, cell, who):
        if cell in occ[k] and occ[k][cell] != who:
            probs.append(('overlap', k, cell, occ[k][cell], who))
        occ[k][cell] = who
    for p in pist:
        p['traj'] = piston_traj(lay, p)
    for b, cells in req.items():
        for c in cells:
            for k in range(Lh):
                mark(k, (c[0] + lay.off(b, k), c[1], c[2]), ('body', b))
    for i, p in enumerate(pist):
        for k in range(Lh):
            mark(k, (p['traj'][k], p['yz'][0], p['yz'][1]), ('pist', i))
        # arms: P arm at +1 at start of f+1; Q arm at -1 at start of f+1 (and arm cell clear at start of f)
        f = p['f']; k1 = (f + 1) % Lh
        dx = 1 if p['kind'] == 'P' else -1
        mark(k1, (p['traj'][k1] + dx, p['yz'][0], p['yz'][1]), ('arm', i))
        if p['kind'] == 'Q':
            mark(f, (p['traj'][f] - 1, p['yz'][0], p['yz'][1]), ('armclr', i))
    for j, sd in enumerate(sources):
        cells = [sd['cell']] + ([sd['target']] if sd['kind'] == 'obs' else [])
        for c in cells:
            for k in range(Lh):
                mark(k, (c[0] + lay.off(sd['body'], k), c[1], c[2]), ('src', j))
    # power per slot start
    for k in range(Lh):
        pw = {}
        for i, p in enumerate(pist):
            pw[(p['traj'][k], p['yz'][0], p['yz'][1])] = i
        hit = set()
        for j, sd in enumerate(sources):
            b = sd['body']
            if sd['kind'] == 'obs':
                if not lay.moves(b, k - 1): continue
                t = sd['target']
            else:
                t = sd['cell']
            w = (t[0] + lay.off(b, k), t[1], t[2])
            for n in nb(w):
                if n in pw:
                    i = pw[n]
                    p = pist[i]
                    infront = (n[0] + (1 if p['kind'] == 'P' else -1), n[1], n[2]) == w
                    if infront: continue
                    hit.add(i)
        want = {i for i, p in enumerate(pist) if p['f'] == k}
        if hit != want:
            probs.append(('power', k, sorted(hit ^ want)))
    return probs, occ


if __name__ == '__main__':
    lay = Lay()
    params = dict(u=[(0, 2), (0, 6), (4, 4)], xi=[0, 1, 1], perm=[(0, 1, 2, 3)] * 3, holder=['B'] * 3, hx=[-1] * 3)
    req, pist, src = build(lay, params)
    probs, occ = analyse(lay, req, pist, src)
    print(len(probs)); print(probs[:20])
