"""Role-level pull planner for 5-slot (3 bps) human flyers.

python planner.py BODYTRACK.txt [--newrb] [--all]

Input: `BT_CELLS=1 human_bodytrack.exe FILE TICKS W0 10 LIMIT` output, where W0 is a cycle start whose positions
equal the start file's (checked for tm_smol: tick 100). Model (verified on B19's sticky with tick snapshots):
at slot k start, a body sits at base + (#m in word[:k]) in X; power is evaluated at slot starts; a -X sticky that is
powered at slot s-1 extends, and if unpowered at slot s it retracts and pulls the victim cell at sticky-2X.

For every (puller P, victim glue body V, slot s) with V moving at s and P resting at s-1 and s, it lists cells c for
a new -X sticky on P that:
  - never overlaps another cell, touches P glue (not on its front), has its arm cell free at s-1;
  - pulls a V glue cell at slot s;
  - is powered (existing RB of another body, or with --newrb a new RB on a glue body) at slot s-1 only;
  - is not dragged by foreign moving glue, is not shoved by a foreign mover, and does not shove a resting cell.
The victim's old pusher at slot s (the actor) is assumed removed. It prints the predicted load table change:
rear-chain and total counts of load-12 actions.
"""
import re, sys, collections, itertools

FACES = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def sx(a, d): return (a[0]+d, a[1], a[2])
REAR = {9, 10, 11, 15, 18}
RBCONN = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--rbconn=')), 2))
MAXCONN = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--conn=')), 2))
LIMIT = 12


def parse(path):
    L = open(path).read().splitlines()
    bodies = {}
    for i, l in enumerate(L):
        m = re.match(r'\s+B(\d+): n=(\d+)\s+(\S+).*word=(\w+)', l)
        if not m: continue
        b = int(m[1]); w = m[4]
        pm = re.search(r'at\((-?\d+),(-?\d+),(-?\d+)\) \[(\w+) piston', l)
        if pm:
            bodies[b] = dict(word=w, cells={(int(pm[1]), int(pm[2]), int(pm[3])): 'P'}, glue=False)
        else:
            cl = L[i+1]
            cells = {(int(x), int(y), int(z)): k for x, y, z, k in re.findall(r'\((-?\d+),(-?\d+),(-?\d+)\)(\S+?)(?= |$)', cl)}
            bodies[b] = dict(word=w, cells=cells, glue=True)
    ev = []
    for l in L:
        m = re.match(r'\s+s(\d) B(\d+)\(([^|]*)\|([^)]*)\) (\w+)\s+(\d+)\s+->\s*(.*)', l)
        if m:
            ev.append(dict(s=int(m[1]), actor=int(m[2]), act=m[5], load=int(m[6]),
                           moved=[(int(a), int(c)) for a, c in re.findall(r'B(\d+)x(\d+)', m[7])]))
    return bodies, ev


def off(word, k):  # X offset at slot-k start (k may be 0..5)
    return word[:k].count('m') if k <= 5 else None


def occupancy(bodies, k):
    occ = {}
    for b, d in bodies.items():
        o = off(d['word'], k)
        for c, kind in d['cells'].items(): occ[sx(c, o)] = (b, kind)
    return occ


def moves(word, k): return word[k % 5] == 'm'


def loads_table(bodies, ev):
    """Return list of moves: (slot, kind, victim, actor, riders(list))."""
    out = []
    for e in ev:
        if e['act'] == 'ext0': continue
        g = [b for b, c in e['moved'] if bodies[b]['glue']]
        if not g: continue
        out.append(dict(s=e['s'], kind=e['act'], victim=g[0], actor=e['actor'],
                        riders=[b for b, c in e['moved'] if not bodies[b]['glue']]))
    return out


def size(bodies, b): return len(bodies[b]['cells'])


def count12(bodies, table, extra=None, removed=(), limit=LIMIT):
    extra = extra or {}
    n12 = rear12 = 0; mx = 0; loads = []
    for mv in table:
        l = size(bodies, mv['victim']) + extra.get(mv['victim'], 0) + sum(1 for r in mv['riders'] if r not in removed)
        loads.append(l); mx = max(mx, l)
        if l >= limit:
            n12 += 1; rear12 += mv['victim'] in REAR
    return n12, rear12, mx


def plan(path, newrb=False, show_all=False):
    bodies, ev = parse(path)
    table = loads_table(bodies, ev)
    occ = [occupancy(bodies, k) for k in range(6)]
    base = count12(bodies, table)
    print(f'baseline: load>=12 actions {base[0]}, rear-chain {base[1]}, max {base[2]}')
    glue_ids = [b for b in bodies if bodies[b]['glue']]
    results = []
    for P in glue_ids:
        wp = bodies[P]['word']
        for V in glue_ids:
            if V == P: continue
            wv = bodies[V]['word']
            for s in range(5):
                sm1 = (s - 1) % 5
                if not (moves(wv, s) and not moves(wp, s) and not moves(wp, sm1)): continue
                # current move of V at slot s
                cur = [mv for mv in table if mv['victim'] == V and mv['s'] == s]
                if not cur or cur[0]['kind'] != 'push': continue
                actor = cur[0]['actor']
                # slot index for positions: extension at slot sm1 start, pull at slot s start.
                ks = s; km = sm1 if s > 0 else 4  # positions within the same cycle frame
                dP = lambda k: off(wp, k)
                # victim glue cells at pull slot
                vcells = [sx(v, off(wv, ks)) for v, kind in bodies[V]['cells'].items() if kind in ('sl', 'ho')]
                for vc in vcells:
                    cabs = sx(vc, 2)             # sticky position at slot s (absolute)
                    c = sx(cabs, -dP(ks))        # base frame of P
                    if s == 0:                   # extension happened in previous cycle's slot 4: P frame there is -3 cycle
                        pass
                    ok, why = check(bodies, occ, P, V, c, s, km, newrb)
                    if not ok:
                        if show_all: print('  reject', P, V, s, c, why)
                        continue
                    for pw in why:  # power options
                        extra = {P: 1 + len(pw[-1])}
                        if pw[0] == 'new': extra[pw[1]] = extra.get(pw[1], 0) + 1 + len(pw[3])
                        t = [dict(mv) for mv in table]
                        for mv in t:
                            if mv['victim'] == V and mv['s'] == s: mv['kind'] = 'pull'; mv['actor'] = P
                        n12, r12, mx = count12(bodies, t, extra, removed={actor})
                        results.append((r12, n12, mx, P, V, s, c, actor, pw))
    results.sort(key=lambda r: (r[2] > LIMIT, r[0], r[1]))
    seen = set()
    print('rear12 all12 max | puller victim slot sticky(base frame) removed-pusher power')
    for r in results:
        key = (r[3], r[4], r[5], r[6], r[8][0])
        if key in seen: continue
        seen.add(key)
        print(f'{r[0]:6} {r[1]:5} {r[2]:3} | B{r[3]} pulls B{r[4]} @s{r[5]} sticky {r[6]} drop B{r[7]} power {r[8]}')
    return results


def sticks(a, b):
    """Does a glue cell of kind a stick to neighbour kind b? (slime/honey don't stick to each other)."""
    g = ('sl', 'ho')
    if a not in g or b is None: return False
    if b in g: return a == b
    return True


def cell_ok(bodies, occ, P, V, s, x, kind, extra_cells):
    """Can P carry a new cell of `kind` at base-frame x? Checks overlap, unwanted drag/carry and shoves."""
    wp = bodies[P]['word']
    for k in range(5):
        a = pos(bodies, P, x, k)
        if a in occ[k] and occ[k][a][0] != P: return False
        pm = moves(wp, k)
        for f in FACES:
            q = add(a, f)
            if q not in occ[k] or occ[k][q][0] == P: continue
            Q, qk = occ[k][q]
            qm = moves(bodies[Q]['word'], k)
            if qm and not pm and not (Q == V and k == s) and (sticks(qk, kind) or sticks(kind, qk)): return False
            if pm and not qm and sticks(kind, qk): return False   # would carry a foreign cell
            if f == (-1,0,0) and qm and not pm: return False
            if f == (1,0,0) and pm and not qm: return False
    return True


def connect(bodies, occ, P, V, s, c, maxn=2):
    """Shortest glue path (<= maxn cells) from sticky cell c to P glue. Returns list of (cell, kind) or None."""
    pcells = bodies[P]['cells']
    def attached(x, kind):
        return any(f != (-1,0,0) or x != c for f in FACES) and any(sticks(kind, pcells.get(add(x, f))) for f in FACES)
    if any(f != (-1,0,0) and pcells.get(add(c, f)) in ('sl', 'ho') for f in FACES): return []
    frontier = [[]]
    for n in range(1, maxn + 1):
        nxt = []
        for path in frontier:
            last = path[-1][0] if path else c
            for f in FACES:
                x = add(last, f)
                if x == sx(c, -1) or x == c or x in pcells or any(x == p[0] for p in path): continue
                for kind in ('sl', 'ho'):
                    if path and path[-1][1] != kind: continue   # connector chain must stick to itself
                    if not cell_ok(bodies, occ, P, V, s, x, kind, path): continue
                    np = path + [(x, kind)]
                    if any(sticks(kind, pcells.get(add(x, g))) for g in FACES): return np
                    nxt.append(np)
        frontier = nxt
    return None


def rb_ok(bodies, occ, P, c, km, Q, rq):
    """New RB on Q at base-frame rq: free at every slot, powers our sticky only at km and no other piston ever."""
    for k in range(5):
        rk = pos(bodies, Q, rq, k)
        if rk in occ[k] and occ[k][rk][0] != Q: return False
        if rk == pos(bodies, P, c, k): return False
        for g in FACES:
            n = add(rk, g)
            if n in occ[k] and occ[k][n][1] in ('P', 'S-x') and occ[k][n][0] != Q: return False
            if k != km and n == pos(bodies, P, c, k): return False
    return True


def connect_to(bodies, occ, Q, x0, maxn):
    """Glue path (<= maxn cells) from a new non-glue cell x0 to Q glue (x0 itself must be carried by glue)."""
    qc = bodies[Q]['cells']
    if any(qc.get(add(x0, f)) in ('sl', 'ho') for f in FACES): return []
    frontier = [[]]
    for n in range(1, maxn + 1):
        nxt = []
        for path in frontier:
            last = path[-1][0] if path else x0
            for f in FACES:
                x = add(last, f)
                if x == x0 or x in qc or any(x == p[0] for p in path): continue
                for kind in ('sl', 'ho'):
                    if path and path[-1][1] != kind: continue
                    if not cell_ok(bodies, occ, Q, None, -1, x, kind, path): continue
                    np = path + [(x, kind)]
                    if any(sticks(kind, qc.get(add(x, g))) for g in FACES): return np
                    nxt.append(np)
        frontier = nxt
    return None


def pos(bodies, b, c, k):
    return sx(c, off(bodies[b]['word'], k))


def check(bodies, occ, P, V, c, s, km, newrb):
    wp = bodies[P]['word']
    if c in bodies[P]['cells']: return False, 'on P'
    # occupancy at all slot starts (P frame moves with P)
    for k in range(5):
        a = pos(bodies, P, c, k)
        if a in occ[k] and occ[k][a][0] != P: return False, f'overlap s{k} B{occ[k][a][0]}'
    # attachment: P glue on a non-front face
    conn = connect(bodies, occ, P, V, s, c, MAXCONN)
    if conn is None: return False, 'unattached'
    # arm cell free at extension slot km (P resting, so frame offset constant between km and s)
    arm = pos(bodies, P, sx(c, -1), km)
    if arm in occ[km]: return False, f'arm blocked by B{occ[km][arm][0]}'
    # dragging / shoving per slot
    for k in range(5):
        a = pos(bodies, P, c, k)
        pm = moves(wp, k)
        for f in FACES:
            q = add(a, f)
            if q in occ[k]:
                Q, kind = occ[k][q]
                if Q == P: continue
                qm = moves(bodies[Q]['word'], k)
                if kind in ('sl', 'ho') and qm and not pm and not (Q == V and k == s):
                    return False, f'dragged by B{Q} s{k}'
                if f == (-1,0,0) and qm and not pm: return False, f'shoved by B{Q} s{k}'
                if f == (1,0,0) and pm and not qm: return False, f'shoves B{Q} s{k}'
    # power: adjacency to RB cells at slot starts (not on the front face)
    def powered_by(k, rbs):
        a = pos(bodies, P, c, k)
        return [r for r in rbs if r[1] != sx(a, -1) and any(add(a, f) == r[1] for f in FACES)]
    rbs_k = [[(Q, q) for q, (Q, kind) in occ[k].items() if kind == 'RB' and Q != P] for k in range(5)]
    own = [sx(q, off(wp, 0)) for q, kind in bodies[P]['cells'].items() if kind == 'RB']
    a0 = pos(bodies, P, c, 0)
    if any(add(a0, f) == q for q in own for f in FACES if f != (-1,0,0)): return False, 'own RB always powers'
    others = [k for k in range(5) if k != km and powered_by(k, rbs_k[k])]
    if others: return False, f'powered at wrong slot {others}'
    opts = []
    if powered_by(km, rbs_k[km]): opts.append(('existing', powered_by(km, rbs_k[km])[0][0]))
    if newrb:
        a = pos(bodies, P, c, km)
        for f in FACES:
            r = add(a, f)
            if f == (-1,0,0) or r in occ[km]: continue
            for Q in bodies:
                if not bodies[Q]['glue'] or Q == P: continue
                rq = sx(r, -off(bodies[Q]['word'], km))  # base frame of Q
                if not rb_ok(bodies, occ, P, c, km, Q, rq): continue
                path = connect_to(bodies, occ, Q, rq, RBCONN)
                if path is not None: opts.append(('new', Q, rq, tuple(path)))
    if not opts: return False, 'no power'
    return True, [o + (tuple(conn),) for o in opts]


if __name__ == '__main__':
    plan(sys.argv[1], newrb='--newrb' in sys.argv, show_all='--all' in sys.argv)
