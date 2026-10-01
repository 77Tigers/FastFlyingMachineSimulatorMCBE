"""Generic A/B flyer generator (any word set with L - D == 2; one body per word).

A bodies (honey) are only pulled: sticky Q (faces -X) extends empty at s-1, pulls at s, anchored on a B
resting at s.  B bodies (slime) only pushed: normal P (faces +X) at s anchored on an A resting at s.
Pistons move +1 in every non-frozen slot; carried by lateral glue contacts chosen automatically from
relative-offset tables (see RESUME.md for the hazard rules).  Pistons sit on a YZ grid (even, even);
lateral lines (odd/even) host contacts and triggers; (odd, odd) lines host source holders and routing.
"""
import sys, itertools, random, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from abgen333 import nb, piston_traj
from abworld import World, color_glue
from abcheck import check
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind

SIDES = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Lay2:
    def __init__(self, Aw, Bw):
        self.spec = [('A', w) for w in Aw] + [('B', w) for w in Bw]
        self.bodies = []
        self.w = {}
        cnt = {'A': 0, 'B': 0}
        for t, w in self.spec:
            b = (t, cnt[t]); cnt[t] += 1
            self.bodies.append(b)
            self.w[b] = [1 if ch == 'm' else 0 for ch in w]
        self.L = len(Aw[0]); self.D = sum(self.w[self.bodies[0]])
        self.offs = {}
        for b in self.bodies:
            o = [0]
            for k in range(self.L): o.append(o[-1] + self.w[b][k])
            self.offs[b] = o

    def off(self, b, k):
        return self.offs[b][k % self.L] + (k // self.L) * self.D

    def moves(self, b, k):
        return self.w[b][k % self.L] == 1


def lifecycle(lay):
    P = []
    for b in lay.bodies:
        for s in range(lay.L):
            if not lay.moves(b, s): continue
            if b[0] == 'B':
                anc = [a for a in lay.bodies if a[0] == 'A' and not lay.moves(a, s)]
                P.append(dict(kind='P', s=s, f=s, victim=b, anchors=anc))
            else:
                anc = [a for a in lay.bodies if a[0] == 'B' and not lay.moves(a, s)]
                P.append(dict(kind='Q', s=s, f=(s - 1) % lay.L, victim=b, anchors=anc))
    for p in P:
        p['xrel'] = [0]
        fro = {p['f'], (p['f'] + 1) % lay.L}
        for j in range(lay.L):
            k = (p['f'] + j) % lay.L
            p['xrel'].append(p['xrel'][-1] + (0 if k in fro else 1))
    return P


def rel(lay, p, b, j):
    f = p['f']
    return p['xrel'][j] - (lay.off(b, f + j) - lay.off(b, f))


def contact_options(lay, p):
    """valid lateral glue contacts (b, r) -> set of j touched."""
    L = lay.L; f = p['f']; v = p['victim']
    opts = {}
    # slots where the piston is directly behind a moving victim D (push) -> only victim may touch
    excl = set()
    if p['kind'] == 'P':
        for j in range(1, L):
            if rel(lay, p, v, j) == 0 and lay.moves(v, f + j): excl.add(j)
    for b in lay.bodies:
        rs = {}
        for j in range(L):
            rs.setdefault(rel(lay, p, b, j), set()).add(j)
        for r, J in rs.items():
            okc = True
            if 0 in J and lay.moves(b, f) and not (p['kind'] == 'P' and b == v): okc = False
            for j in excl:
                if j in J and b != v and lay.moves(b, f + j): okc = False
            if okc: opts[(b, r)] = J
    return opts


def choose_contacts(lay, p, rnd, maxn=4):
    L = lay.L; f = p['f']
    opts = contact_options(lay, p)
    fro = {0, 1}
    need = [j for j in range(L) if j not in fro]
    # victim front contact (P: D) carries automatically
    free_carry = set()
    if p['kind'] == 'P':
        v = p['victim']
        for j in range(L):
            if rel(lay, p, v, j) == 0 and lay.moves(v, f + j) and j not in fro: free_carry.add(j)
    anchor_j = 0 if p['kind'] == 'P' else 1
    keys = list(opts); rnd.shuffle(keys)
    sols = []
    for n in range(1, maxn + 1):
        for combo in itertools.combinations(keys, n):
            cov = set(free_carry)
            anch = False
            for (b, r) in combo:
                J = opts[(b, r)]
                for j in J:
                    if lay.moves(b, f + j): cov.add(j)
                if b in p['anchors'] and anchor_j in J: anch = True
            if anch and all(j in cov for j in need):
                sols.append(combo)
        if sols: break
    return sols


def power_options(lay, p):
    """(kind, body, r) triggers touching exactly at j=0 (start of f)."""
    L = lay.L; f = p['f']; out = []
    for b in lay.bodies:
        rs = {}
        for j in range(L):
            rs.setdefault(rel(lay, p, b, j), set()).add(j)
        # redstone: stationary at slot starts; touches set must be {0} and b must move at f
        for r, J in rs.items():
            if J == {0} and lay.moves(b, f): out.append(('rs', b, r))
        # observer/glazed: pulses at j where b moved at j-1; touching at those pulses must be {0}
        for r, J in rs.items():
            pulses = {j for j in range(L) if lay.moves(b, f + j - 1)}
            hit = J & pulses
            if hit == {0}: out.append(('obs', b, r))
    return out


def build(lay, seed, grid_w=4, spacing=2):
    rnd = random.Random(seed)
    P = lifecycle(lay)
    L = lay.L
    # xi: piston x at start of its fire slot ~ mean body offset
    for p in P:
        p['xi'] = round(sum(lay.off(b, p['f']) for b in lay.bodies) / len(lay.bodies))
    order = list(range(len(P))); rnd.shuffle(order)
    req = {b: {} for b in lay.bodies}
    sources = []
    pist = []
    cells_line = {}  # (y,z) -> list of (body, bframe x)
    for n, i in enumerate(order):
        p = P[i]
        gy, gz = (n // grid_w) * spacing, (n % grid_w) * spacing
        p['yz'] = (gy, gz)
        sols = choose_contacts(lay, p, rnd)
        if not sols: return None, ('nocontact', i)
        combo = rnd.choice(sols)
        pw = power_options(lay, p)
        if not pw: return None, ('nopower', i)
        pwc = rnd.choice(pw)
        sides = SIDES[:]; rnd.shuffle(sides)
        f = p['f']
        # place contacts: assign sides (may reuse a side for the same body)
        side_of = {}
        used = []
        for (b, r) in combo:
            s = None
            for sd in sides:
                if sd not in used: s = sd; break
            if s is None: s = rnd.choice(sides)
            used.append(s); side_of[(b, r)] = s
        for (b, r), s in side_of.items():
            c = (p['xi'] + r - lay.off(b, f), gy + s[0], gz + s[1])
            req[b][c] = 'ct'
        # trigger on a remaining side (or random)
        rem = [sd for sd in sides if sd not in used] or sides
        s = rem[0]
        kind, b, r = pwc
        line = (gy + s[0], gz + s[1])
        # holder line: an (odd, odd) neighbour of the trigger line
        hold = (line[0] + (1 if s[0] == 0 else 0), line[1] + (1 if s[1] == 0 else 0))
        bx = p['xi'] + r - lay.off(b, f)
        if kind == 'rs':
            sources.append(dict(kind='rs', body=b, cell=(bx, line[0], line[1]), f=f))
            req[b][(bx, hold[0], hold[1])] = 'hold'
        else:
            sources.append(dict(kind='obs', body=b, cell=(bx - 1, line[0], line[1]), target=(bx, line[0], line[1]), f=f))
            req[b][(bx - 1, hold[0], hold[1])] = 'hold'
        # faces
        v = p['victim']
        if p['kind'] == 'P':
            req[v][(p['xi'] + 1 - lay.off(v, f), gy, gz)] = 'D'
        else:
            req[v][(p['xi'] - 2 - (lay.off(v, f + 1) - lay.off(v, f)) - lay.off(v, f) + 0, gy, gz)] = 'C'
        pist.append(dict(kind=p['kind'], f=f, victim=v, yz=(gy, gz), xi=p['xi']))
    return (req, pist, sources), None


def assemble(lay, req, pist, sources, seed):
    rnd = random.Random(seed)
    col, edges = color_glue(lay, req, rnd)
    if col is None: return None, ('color', None)
    wd = World(lay, req, pist, sources, glue=col)
    bodies = list(lay.bodies); rnd.shuffle(bodies)
    for b in bodies:
        t, why = wd.route(b, rnd)
        if t is None: return None, (b, why[:2])
    return wd, None


def run(Aw, Bw, outdir, seeds, grid_w=5, spacing=4):
    lay = Lay2(Aw, Bw)
    outdir = Path(outdir); outdir.mkdir(exist_ok=True)
    stats = {}
    good = 0
    for seed in seeds:
        r, err = build(lay, seed, grid_w, spacing)
        if err: stats[err[0]] = stats.get(err[0], 0) + 1; continue
        req, pist, sources = r
        wd, err = assemble(lay, req, pist, sources, seed)
        if err:
            key = 'route_' + (err[1][0][1] if err[1] and isinstance(err[1][0], tuple) and len(err[1][0]) > 1 and isinstance(err[1][0][1], str) else str(err[0]))
            stats[key] = stats.get(key, 0) + 1; continue
        pr = check(wd)
        if pr:
            stats['check'] = stats.get('check', 0) + 1
            if len(pr) < stats.get('bestcheck', (999,))[0]: stats['bestcheck'] = (len(pr), seed, pr[:3])
            continue
        f = wd.flyer(limit=100)
        f.save(outdir / ('s%05d.flyer' % seed)); good += 1
    print('good', good, {k: v for k, v in stats.items() if k != 'bestcheck'})
    print('bestcheck', stats.get('bestcheck'))


if __name__ == '__main__':
    Aw = sys.argv[1].split(','); Bw = sys.argv[2].split(',')
    run(Aw, Bw, sys.argv[3], range(int(sys.argv[4]), int(sys.argv[5])))
