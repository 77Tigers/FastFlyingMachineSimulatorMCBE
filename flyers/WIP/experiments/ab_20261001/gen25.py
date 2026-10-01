"""Structured generator for two-body A/B 2.5 bps flyers (lifecycle of ab25.py).

Frame: world at start of slot 1 (= A-rel = B-rel). Slot-start offsets (S1,S2,S3,S0):
  A [0,0,1,1]  B [0,1,1,2]  G1 [0,0,0,1]  G3 [0,1,2,2] (G3 base = R(G1) - x1).
P1 at origin faces +X (pushes B cell D1 = P1+x at S1); Q2 sticky faces -X (pulls A cell C2 = Q2-2x at S2).
A carries G1 at slot 0 (A-rel = G1), B carries G1 at slot 3 (B-rel = G1 - x).
Bodies are R-symmetric; A honey, B slime. One observer per distinct power cell H (H adjacent to P1 and Q2).
Minimal Steiner trees (Dreyfus-Wagner) connect each body's terminals inside the allowed cells.
"""
import sys, itertools, json, os
from pathlib import Path
from collections import deque
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind

DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
E, W, U, D, S, N = range(6)
OFF = dict(A=[0, 0, 1, 1], B=[0, 1, 1, 2], G1=[0, 0, 0, 1], G3=[0, 1, 2, 2])


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sx(a, k): return (a[0] + k, a[1], a[2])
def nb(c): return [add(c, d) for d in DIRS]


def make_R(kind, c1, c2):
    # c1,c2 are doubled coordinates of the plane/axis
    if kind == 'mz': return lambda p: (p[0], p[1], c1 - p[2])
    if kind == 'my': return lambda p: (p[0], c1 - p[1], p[2])
    if kind == 'rot': return lambda p: (p[0], c1 - p[1], c2 - p[2])
    if kind == 'diag': return lambda p: (p[0], p[2] + c1, p[1] - c1)  # swap y,z (shifted)
    raise ValueError


def steiner(terms, allowed):
    """Min node count connected set containing all terms within allowed (unit weights). Returns set or None."""
    terms = list(dict.fromkeys(terms))
    if any(t not in allowed for t in terms): return None
    k = len(terms)
    if k == 1: return {terms[0]}
    nodes = list(allowed)
    idx = {v: i for i, v in enumerate(nodes)}
    INF = 10 ** 9
    full = (1 << k) - 1
    dp = [[INF] * len(nodes) for _ in range(1 << k)]
    par = [[None] * len(nodes) for _ in range(1 << k)]
    for i, t in enumerate(terms):
        dp[1 << i][idx[t]] = 0
    adj = [[idx[w] for w in nb(v) if w in idx] for v in nodes]
    for m in range(1, full + 1):
        row = dp[m]
        sub = (m - 1) & m
        while sub:
            if sub < (m ^ sub):
                o = m ^ sub
                a, b = dp[sub], dp[o]
                for v in range(len(nodes)):
                    s = a[v] + b[v]
                    if s < row[v]:
                        row[v] = s; par[m][v] = ('m', sub)
            sub = (sub - 1) & m
        # BFS-like relaxation (unit edges) - Dijkstra with buckets
        order = sorted(range(len(nodes)), key=lambda v: row[v])
        dq = deque(v for v in order if row[v] < INF)
        # simple Bellman-Ford style queue relaxation
        inq = [False] * len(nodes)
        for v in dq: inq[v] = True
        while dq:
            v = dq.popleft(); inq[v] = False
            for w in adj[v]:
                if row[v] + 1 < row[w]:
                    row[w] = row[v] + 1; par[m][w] = ('e', v)
                    if not inq[w]: dq.append(w); inq[w] = True
    t0 = idx[terms[0]]
    # tree containing all terms: dp[full][t0]
    if dp[full][t0] >= INF: return None
    out = set()
    stack = [(full, t0)]
    while stack:
        m, v = stack.pop()
        out.add(nodes[v])
        p = par[m][v]
        if p is None: continue
        if p[0] == 'e': stack.append((m, p[1]))
        else: stack.append((p[1], v)); stack.append((m ^ p[1], v))
    return out


def world_items(P1, Q2, R):
    """Return per slot-start dict world cell -> tag for pistons and arms; and piston list."""
    G1 = [(P1, 'P'), (Q2, 'Q')]
    G3 = [(sx(R(c), -1), t) for c, t in G1]
    occ = [dict() for _ in range(4)]
    for s in range(4):
        for c, t in G1: occ[s][sx(c, OFF['G1'][s])] = 'G1' + t
        for c, t in G3: occ[s][sx(c, OFF['G3'][s])] = 'G3' + t
    # arms present at S2 for G1 (fired slot1), at S0 for G3 (fired slot 3)
    occ[1][sx(P1, 1)] = 'armP1'; occ[1][sx(Q2, -1)] = 'armQ2'
    p3, q3 = sx(R(P1), -1 + 2), sx(R(Q2), -1 + 2)  # G3 at S3
    occ[3][sx(p3, 1)] = 'armP3'; occ[3][sx(q3, -1)] = 'armQ0'
    # Q extension cells must be empty at the extension slot start too
    occ[0][sx(Q2, -1)] = occ[0].get(sx(Q2, -1), 'clrQ2')  # S1 is index 0
    occ[2][sx(q3, -1)] = occ[2].get(sx(q3, -1), 'clrQ0')
    return G1, G3, occ


def forbidden_for(body, occ):
    f = set()
    for s in range(4):
        for w in occ[s]:
            f.add(sx(w, -OFF[body][s]))
    return f


def box(cells, pad):
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]; zs = [c[2] for c in cells]
    return [(x, y, z) for x in range(min(xs) - pad, max(xs) + pad + 1)
            for y in range(min(ys) - pad, max(ys) + pad + 1)
            for z in range(min(zs) - pad, max(zs) + pad + 1)]


def candidates(P1, Q2, R):
    G1, G3, occ = world_items(P1, Q2, R)
    # sanity: pistons don't overlap each other at any slot start
    for s in range(4):
        cells = [sx(c, OFF['G1'][s]) for c, _ in G1] + [sx(c, OFF['G3'][s]) for c, _ in G3]
        if len(set(cells)) < 4: return
    fA = forbidden_for('A', occ); fB = forbidden_for('B', occ)
    D1 = sx(P1, 1); C2 = sx(Q2, -2)
    D3 = R(D1); C0 = R(C2)
    if D1 in fB or D3 in fB or C2 in fA or C0 in fA: return
    if D1 == C2: return
    Hs = [h for h in set(nb(P1)) & set(nb(Q2)) if h not in fA]
    Kp = [k for k in nb(sx(P1, -1)) if k not in fB]
    Kq = [k for k in nb(sx(Q2, -1)) if k not in fB]
    for H in Hs:
        HR = R(H)
        Aterm = {H, HR, C2, C0}
        if len(Aterm & {D1, D3}): continue
        # observer cells adjacent to H
        for od in range(6):
            O = add(H, DIRS[od]); OR = R(O)
            if O in fA or OR in fA or O in Aterm or OR in Aterm: continue
            yield dict(H=H, O=O, od=od ^ 1, Aterm=sorted(Aterm), fA=fA, fB=fB, D1=D1, D3=D3, Kp=Kp, Kq=Kq,
                       G1=G1, G3=G3, occ=occ)


def hazards(spec, A, B, R):
    """True if some moving glue touches a movable non-glue item it must not carry (order-dependent drag)."""
    O = spec['O']; obsA = {O, R(O)}
    G1 = spec['G1']; G3 = spec['G3']
    mover = ['B', 'A', 'B', 'A']
    for s in range(4):
        M = B if mover[s] == 'B' else A
        mw = {sx(c, OFF[mover[s]][s]) for c in M}
        bad = set()
        # observers belong to A: B must never touch them while B moves
        if mover[s] == 'B':
            bad |= {sx(o, OFF['A'][s]) for o in obsA}
        # sticky piston extending this tick (S1: Q2 of G1, S3: Q0 of G3)
        if s == 0: bad |= {sx(c, OFF['G1'][s]) for c, t in G1 if t == 'Q'}
        if s == 2: bad |= {sx(c, OFF['G3'][s]) for c, t in G3 if t == 'Q'}
        for w in mw:
            for n in nb(w):
                if n in bad: return True
    return False


def build_flyer(spec, A, B, R, limit=40, rng=5):
    f = Flyer(rng_state=rng, push_limit=limit)
    for c in A: f.set(c, Block(Kind.HONEY))
    for c in B: f.set(c, Block(Kind.SLIME))
    for c, t in spec['G1']:
        f.set(c, Block.piston(E) if t == 'P' else Block.piston(W, sticky=True))
    for c, t in spec['G3']:
        f.set(c, Block.piston(E) if t == 'P' else Block.piston(W, sticky=True))
    obs = {spec['O']: spec['od']}
    # mirrored observer: direction mapped through R
    O, od = spec['O'], spec['od']
    tgt = add(O, DIRS[od]); Ro, Rt = R(O), R(tgt)
    d = (Rt[0] - Ro[0], Rt[1] - Ro[1], Rt[2] - Ro[2])
    obs[Ro] = DIRS.index(d)
    for c, dd in obs.items():
        f.set(c, Block.observer(dd, powered=True))
    return f, len(obs)


def run(outdir, maxload=13, limit_count=4000):
    outdir = Path(outdir); outdir.mkdir(exist_ok=True)
    P1 = (0, 0, 0)
    syms = []
    for c in range(-3, 4): syms.append(('mz', c, 0)); syms.append(('my', c, 0))
    for c1 in range(-3, 4):
        for c2 in range(-3, 4): syms.append(('rot', c1, c2))
    for c1 in range(-2, 3): syms.append(('diag', c1, 0))
    rows = []; seen = set(); n = 0
    for dq in itertools.product((-1, 0, 1), (-2, -1, 0, 1, 2), (-2, -1, 0, 1, 2)):
        if dq == (0, 0, 0): continue
        Q2 = dq
        for (kind, c1, c2) in syms:
            R = make_R(kind, c1, c2)
            for spec in candidates(P1, Q2, R):
                fA, fB = spec['fA'], spec['fB']
                allowedA = set(box(spec['Aterm'] + [P1, Q2], 2)) - fA - {spec['O'], R(spec['O'])}
                Atree = steiner(spec['Aterm'], allowedA)
                if Atree is None: continue
                # symmetric closure
                A = Atree | {R(c) for c in Atree}
                if A & {spec['O'], R(spec['O'])}: continue
                nobs = 1 if R(spec['O']) == spec['O'] else 2
                loadA = len(A) + nobs + 2
                if loadA > maxload: continue
                # B forbidden: A collision lines (B-rel x in {xA, xA-1}) + observers
                fB2 = set(fB)
                for a in list(A) + [spec['O'], R(spec['O'])]:
                    fB2.add(a); fB2.add(sx(a, -1))
                # adhesion hazards: B glue next to observers (S1,S3) or the extending sticky (S1: Q2, S3: Q0)
                for si in (0, 2):
                    bad = [sx(o, OFF['A'][si]) for o in (spec['O'], R(spec['O']))]
                    bad += [sx(c, OFF['G1' if si == 0 else 'G3'][si]) for c, t in (spec['G1'] if si == 0 else spec['G3']) if t == 'Q']
                    for w in bad:
                        for nn in nb(w): fB2.add(sx(nn, -OFF['B'][si]))
                best = None
                kopts = [[k] for k in set(spec['Kp']) & set(spec['Kq'])] + [[a, b] for a in spec['Kp'] for b in spec['Kq']]
                for ks in kopts:
                    if any(k in fB2 for k in ks): continue
                    Bterm = [spec['D1'], spec['D3']] + ks + [R(k) for k in ks]
                    if any(t in fB2 for t in Bterm): continue
                    allowedB = set(box(Bterm + [P1, Q2], 2)) - fB2
                    Bt = steiner(Bterm, allowedB)
                    if Bt is None: continue
                    Bs = Bt | {R(c) for c in Bt}
                    if Bs & fB2: continue
                    if best is None or len(Bs) < len(best): best = Bs
                if best is None: continue
                if hazards(spec, A, best, R): continue
                loadB = len(best) + 2
                key = (frozenset(A), frozenset(best))
                if key in seen: continue
                seen.add(key)
                score = max(loadA, loadB)
                if score > maxload: continue
                f, _ = build_flyer(spec, A, best, R)
                name = f'c{n:05d}'
                f.translate(20, 20, 20)
                f.save(outdir / f'{name}.flyer')
                rows.append(dict(name=name, Q2=Q2, sym=[kind, c1, c2], H=spec['H'], O=spec['O'], loadA=loadA, loadB=loadB))
                n += 1
                if n >= limit_count: break
            if n >= limit_count: break
        print('Q2', Q2, 'cands', n, flush=True)
        if n >= limit_count: break
    (outdir.parent / (outdir.name + '_manifest.json')).write_text(json.dumps(rows, indent=1))
    print('total', n)


if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 13)
