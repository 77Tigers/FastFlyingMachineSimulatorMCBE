"""Constructive placement for the all-pull mmmww lifecycle (spec pull3), agent G.

Group y (redstone R_y on body y, fires at slot y) touches A_{y+1}, B_y, C_{y-1}.
Each member is lateral to R (same x) or 'behind' R (same transverse cell, x = R.x - 1), at most one behind.
x: per y,  dAB(h_y) + dCB(h_{y+1}) = la(y+1) + lc(y) + dA[y] + dC[y+1]  and the X chain closes.
Transverse: lane cells (b at body origin, a,c at template offsets) distinct; R_y cell adjacent to the
lateral members' lanes and equal to the behind member's lane; R cells distinct from other lanes.
Outputs random valid placements (gt, places, tmpl) for gen.build.
"""
import random, itertools, pickle, sys
import specs

N = 5
dA = [-1, -1, 0, 0, 0]     # bA - bB at group y (all X = 0, lx = 0)
dC = [0, 1, 1, 0, 0]       # bC - bB at group y
DAB = dict(N=0, A=-1, B=1, C=0)
DCB = dict(N=0, A=0, B=1, C=-1)
TP = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def adj2(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1]) == 1


def x_solutions(rng):
    """yield (h, la, lc, X) consistent assignments, random order."""
    hs = list(itertools.product('NABC', repeat=N))
    rng.shuffle(hs)
    for h in hs:
        for _ in range(30):
            la = [rng.choice((-1, 0, 1)) for _ in range(N)]
            lc = [None] * N
            ok = True
            for y in range(N):
                v = DAB[h[y]] + DCB[h[(y + 1) % N]] - la[(y + 1) % N] - dA[y] - dC[(y + 1) % N]
                if v not in (-1, 0, 1):
                    ok = False; break
                lc[y] = v
            if not ok:
                continue
            X = [0]
            for y in range(N - 1):
                X.append(X[-1] + DAB[h[y]] - la[(y + 1) % N] - dA[y])
            if X[0] != X[-1] + DAB[h[N - 1]] - la[0] - dA[N - 1]:
                continue
            yield h, la, lc, X


def transverse(rng, h, box=3, tries=4000):
    """random backtracking: b-lane positions + a/c template dirs + R cells."""
    for _ in range(tries):
        pos = {}; ta = {}; tc = {}; R = {}
        used = set()
        ok = True
        order = list(range(N))
        for y in order:
            cands = [(bx, bz, a, c) for bx in range(-box, box + 1) for bz in range(-box, box + 1)
                     for a in TP for c in TP if a != c]
            rng.shuffle(cands)
            placed = False
            for bx, bz, a, c in cands[:3000]:
                b = (bx, bz) if y else (0, 0)
                la_ = (b[0] + a[0], b[1] + a[1]); lc_ = (b[0] + c[0], b[1] + c[1])
                cells = {b, la_, lc_}
                if len(cells) < 3 or cells & used:
                    continue
                pos[y], ta[y], tc[y] = b, la_, lc_
                # check groups that become complete
                good = True
                for g in range(N):
                    mem = {'A': (g + 1) % N, 'B': g, 'C': (g - 1) % N}
                    if any(m not in pos for m in mem.values()) or g in R:
                        continue
                    lane = {'A': ta[mem['A']], 'B': pos[mem['B']], 'C': tc[mem['C']]}
                    opts = []
                    for r in {(p[0] + d[0], p[1] + d[1]) for p in lane.values() for d in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))}:
                        fine = True
                        for k, L_ in lane.items():
                            if h[g] == k:
                                if L_ != r: fine = False
                            elif not adj2(L_, r):
                                fine = False
                        if fine and (h[g] != 'N' or r not in used | cells) and r not in R.values():
                            opts.append(r)
                    if not opts:
                        good = False; break
                    R[g] = rng.choice(opts)
                if good:
                    used |= cells
                    placed = True
                    break
                for g in list(R):
                    mem = {'A': (g + 1) % N, 'B': g, 'C': (g - 1) % N}
                    if y in mem.values():
                        del R[g]
                del pos[y], ta[y], tc[y]
            if not placed:
                ok = False; break
        if ok and len(R) == N:
            # R cells must not sit on unrelated lanes
            lanes = {}
            for y in range(N):
                lanes[pos[y]] = ('b', y); lanes[ta[y]] = ('a', y); lanes[tc[y]] = ('c', y)
            bad = False
            for g, r in R.items():
                if r in lanes and h[g] == 'N':
                    bad = True
            if not bad:
                return pos, ta, tc, R
    return None


def placement(rng, gt=None):
    spec = specs.pull3()
    for sol in x_solutions(rng):
        h, la, lc, X = sol
        tr = transverse(rng, h)
        if tr is None:
            continue
        pos, ta, tc, R = tr
        places = []; tmpl = []
        for y in range(N):
            places.append((0, (X[y], pos[y][0], pos[y][1])))
            a = (la[y], ta[y][0] - pos[y][0], ta[y][1] - pos[y][1])
            c = (lc[y], tc[y][0] - pos[y][0], tc[y][1] - pos[y][1])
            tmpl.append(dict(lanes=dict(a=a, b=(0, 0, 0), c=c)))
        gt = gt or tuple(rng.choice('SH') for _ in range(N))
        return (gt, places, tmpl), dict(h=h, la=la, lc=lc, X=X, R=R)
    return None


if __name__ == '__main__':
    import gen
    spec = specs.pull3()
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    for k in range(5):
        pl, info = placement(rng)
        B = gen.Builder(spec, rng, *pl)
        e = B.setup()
        print(info['h'], info['X'], 'setup errs', len(e), e[:2])
        if not e:
            print(' rs feasible', [B.rs_feasible(Y, [B.pidx[((Y + o) % N, kn)] for kn, o in spec['rsgroups']]) for Y in range(N)])


def N4(p):
    return [(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)]


def cheb(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def transverse2(rng, box=3, tries=20000, lim=2):
    """h = all lateral. sample R loop, then per-body lane triples, then distinct matching."""
    for _ in range(tries):
        R = [(0, 0)]
        for y in range(1, N):
            R.append((rng.randint(-box, box), rng.randint(-box, box)))
        if len(set(R)) < N:
            continue
        opts = []
        for y in range(N):
            o = []
            for b in N4(R[y]):
                for a in N4(R[(y - 1) % N]):
                    if cheb(a, b) > lim or a == b:
                        continue
                    for c in N4(R[(y + 1) % N]):
                        if cheb(c, b) > lim or c in (a, b):
                            continue
                        if {a, b, c} & set(R):
                            continue
                        o.append((cheb(a, b) + cheb(c, b) + rng.random(), (a, b, c)))
            if not o:
                break
            o.sort()
            opts.append([t for _, t in o])
        if len(opts) < N:
            continue
        # backtrack distinct
        sol = [None] * N
        def bt(y, used):
            if y == N:
                return True
            for t in opts[y]:
                if set(t) & used:
                    continue
                sol[y] = t
                if bt(y + 1, used | set(t)):
                    return True
            return False
        if bt(0, set()):
            return R, sol
    return None


def placement2(rng, gt=None):
    la = [1, 1, 0, 0, 0]
    rot = rng.randrange(N)
    la = la[-rot:] + la[:-rot]
    lc = [-la[(y + 1) % N] for y in range(N)]
    X = [0]
    for y in range(N - 1):
        X.append(X[-1] - la[(y + 1) % N] - dA[y])
    assert X[0] == X[-1] - la[0] - dA[N - 1]
    tr = transverse2(rng)
    if tr is None:
        return None
    R, sol = tr
    places = []; tmpl = []
    for y in range(N):
        a, b, c = sol[y]
        places.append((0, (X[y], b[0], b[1])))
        tmpl.append(dict(lanes=dict(a=(la[y], a[0] - b[0], a[1] - b[1]), b=(0, 0, 0), c=(lc[y], c[0] - b[0], c[1] - b[1]))))
    gt = gt or tuple(rng.choice('SH') for _ in range(N))
    return (gt, places, tmpl), dict(R=R, la=la, lc=lc, X=X)


def placement3(rng, spec, maxtries=50):
    """placement2 + glue-type colouring with no setup errors."""
    import gen
    for _ in range(maxtries):
        r = placement2(rng)
        if r is None:
            continue
        pl, info = r
        _, places, tmpl = pl
        gts = list(itertools.product('SH', repeat=N))
        rng.shuffle(gts)
        for gt in gts:
            B = gen.Builder(spec, rng, gt, places, tmpl)
            if not B.setup():
                return (gt, places, tmpl), info
    return None
