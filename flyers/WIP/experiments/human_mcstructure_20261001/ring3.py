"""3-body push-push-push-pull ring at 3.333 bps (6 slots, +4), inspired by the human c2/c6 extensions.

Bodies X0, X1, X2; front(X0)=X1, front(X1)=X2, front(X2)=X0 (the front body pulls its rear and is 2 slots ahead).
Words (moves per slot): X0 {0,1,2,3}, X1 {4,5,0,1}, X2 {2,3,4,5}. Each body is pushed three times by a
column of three normal pushers clustered round its own redstone block (c6 style: all powered together, they
fire one per slot), then pulled once by its front's sticky. Column of X fires at T[X] = 0/4/2.

Column template around X's redstone A (at slot T[X]); U, V = transverse unit vectors of X's orientation:
  X:          RB A; face glue A+(1,0), A+(1,+-U), A+(1,V)
  pushers:    A+(0,+-U), A+(0,V)  (+X normal pistons; ride rear(X) between bursts)
  rear(X):    sticky S at A+(0,-V) facing -X (powered by A now, pulls rear(rear(X)) next slot);
              carrier glue A+(0,U+V), A+(0,-U+V); sticky holder A+(0,+-U-V)
  rr = rear(rear(X)): pulled glue A+(-2,-V) at slot T+1; arm space A+(-1,-V).
Every feature is moved to t=0 using its owner's movement word, glue is routed per body, simulator decides.
"""
import sys, pathlib, random, itertools, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer, Block, Kind

WORD = {0: [1,1,1,1,0,0], 1: [1,1,0,0,1,1], 2: [0,0,1,1,1,1]}
T = {0: 0, 1: 4, 2: 2}
FRONT = {0: 1, 1: 2, 2: 0}; REAR = {v: k for k, v in FRONT.items()}
def o(b, s): return sum(WORD[b][:s])            # displacement of body b from slot 0 to slot s (0..6)
# pusher (dx from column x at t=0, state) for a column firing at T; 'x' = extended with arm in front
PUSHERS_T0 = {0: [(0,'r')]*3, 2: [(-2,'r')]*3, 4: [(-4,'r'), (-3,'x'), (-2,'r')]}
D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def nb(p): return [add(p, d) for d in D6]
def orient(k):
    """8 transverse orientations: returns (U, V) as (y,z) pairs."""
    rot = k % 4; mir = k // 4
    def f(y, z):
        if mir: y = -y
        for _ in range(rot): y, z = -z, y
        return (y, z)
    return f(1, 0), f(0, 1)
def tv(x, t): return (x, t[0], t[1])

def at(p, b, s): return (p[0] + o(b, s), p[1], p[2])
def time_conflicts(cells, p, Y, m, exempt=()):
    """Would a glue cell of body Y (material m) at t=0 position p collide/stick with foreign glue/RB/sticky
    at any slot start? Also: Y moving into a foreign cell ahead, or a foreign mover pushing into p."""
    for s in range(6):
        q = at(p, Y, s)
        for r, (k, b, _) in cells.items():
            if b == Y or k not in ('G', 'RB', 'S') or r in exempt: continue
            rq = at(r, b, s)
            d = (rq[0]-q[0], rq[1]-q[1], rq[2]-q[2])
            if d == (0, 0, 0): return True
            if abs(d[0]) + abs(d[1]) + abs(d[2]) == 1:
                if k == 'S' and d == (1, 0, 0): continue   # pulled glue resting on the puller's face (intended)
                if k != 'G' or ((k == 'G') and (_mat[b] == m)): return True
            if WORD[Y][s] and d == (1, 0, 0): return True
            if WORD[b][s] and d == (-1, 0, 0): return True
    return False
_mat = {}

class Layout:
    def __init__(self, A, ori, holder_side):
        self.cells = {}      # pos -> (kind, body, extra)
        self.reserved = set()
        self.ok = True
        for X in (0, 1, 2):
            U, V = orient(ori[X]); a = A[X]; t = T[X]
            R = REAR[X]; RR = REAR[R]
            def P(dx, du, dv): return (a[0]+dx, a[1]+du*U[0]+dv*V[0], a[2]+du*U[1]+dv*V[1])
            def put(p, kind, body, at_slot, extra=None):
                q = (p[0] - (o(body, at_slot) - o(body, 0)), p[1], p[2])
                if q in self.cells: self.ok = False
                self.cells[q] = (kind, body, extra)
                return q
            put(P(0,0,0), 'RB', X, t)
            for d in ((1,0,0),(1,1,0),(1,-1,0),(1,0,1)): put(P(*d), 'G', X, t)
            # pushers: positions at t=0 come from PUSHERS_T0 (column x = a[0])
            slots = [(0,1,0),(0,-1,0),(0,0,1)]
            for (dx, st), s in zip(PUSHERS_T0[t], slots):
                p = P(*s); q = (p[0]+dx, p[1], p[2])
                if q in self.cells: self.ok = False
                self.cells[q] = ('PU', X, st)
                if st == 'x':
                    arm = (q[0]+1, q[1], q[2])
                    if arm in self.cells: self.ok = False
                    self.cells[arm] = ('ARM', X, None)
            put(P(0,0,-1), 'S', R, t)
            put(P(0,1,1), 'G', R, t); put(P(0,-1,1), 'G', R, t)
            put(P(0,holder_side[X],-1), 'G', R, t)
            q = P(-1,0,-1); self.reserved.add((q[0]-(o(R,t)), q[1], q[2]))
            put(P(-2,0,-1), 'G', RR, (t+1) % 6 if t+1 < 6 else 6)

    def route(self, mats, rnd, maxlen=10):
        """connect each body's glue+RB+sticky terminals into one glue component. Returns dict or None."""
        cells = dict(self.cells)
        _mat.clear(); _mat.update(mats)
        # template features must already be time-consistent (sticky/RB contacts with intended pistons are not checked)
        for p, (k, b, _) in list(cells.items()):
            if k == 'G' and time_conflicts(cells, p, b, mats[b]): return None
        def sticks(m, other):
            k, b, _ = other
            if k == 'G': return mats[b] == m
            if k in ('ARM',): return False
            return True
        order = [0, 1, 2]; rnd.shuffle(order)
        for Y in order:
            m = mats[Y]
            term = [p for p, (k, b, _) in cells.items() if b == Y and k in ('G', 'RB', 'S')]
            glue = {p for p in term if cells[p][0] == 'G'}
            # components among terminals (glue adjacency; RB/S attach to adjacent own glue)
            def comps():
                pts = set(term)
                seen = set(); out = []
                for p in pts:
                    if p in seen: continue
                    st = [p]; seen.add(p); c = []
                    while st:
                        q = st.pop(); c.append(q)
                        for r in nb(q):
                            if r in pts and r not in seen and (cells[q][0] == 'G' or cells[r][0] == 'G'):
                                seen.add(r); st.append(r)
                    out.append(c)
                return out
            def legal(c):
                if c in cells or c in self.reserved: return False
                if time_conflicts(cells, c, Y, m): return False
                for r in nb(c):
                    if r in cells:
                        k, b, _ = cells[r]
                        if b == Y: continue
                        if sticks(m, cells[r]): return False
                return True
            cs = comps()
            while len(cs) > 1:
                cs.sort(key=len, reverse=True)
                src = set(cs[0]); others = set(p for c in cs[1:] for p in c)
                # BFS from src through legal empty cells to any cell adjacent to another component
                prev = {}; dq = collections.deque()
                for p in src:
                    for r in nb(p):
                        if r in others: pass
                        if legal(r) and r not in prev: prev[r] = None; dq.append(r)
                hit = None
                while dq:
                    q = dq.popleft()
                    if any(r in others for r in nb(q)): hit = q; break
                    depth = 0; z = q
                    while prev[z] is not None: z = prev[z]; depth += 1
                    if depth >= maxlen: continue
                    nbrs = nb(q); rnd.shuffle(nbrs)
                    for r in nbrs:
                        if r not in prev and legal(r): prev[r] = q; dq.append(r)
                if hit is None: return None
                z = hit
                while z is not None:
                    cells[z] = ('G', Y, None); term.append(z); z = prev[z]
                cs = comps()
            # every RB / sticky must touch own glue
            for p in term:
                if cells[p][0] in ('RB', 'S') and not any(r in cells and cells[r][0] == 'G' and cells[r][1] == Y for r in nb(p)):
                    return None
        return cells

    @staticmethod
    def flyer(cells, mats, limit):
        f = Flyer(push_limit=limit)
        for p, (k, b, extra) in cells.items():
            if k == 'G': f.set(p, Block(Kind.SLIME if mats[b] == 'S' else Kind.HONEY))
            elif k == 'RB': f.set(p, Block(Kind.REDSTONE_BLOCK))
            elif k == 'S': f.set(p, Block.piston(1, sticky=True))
            elif k == 'PU': f.set(p, Block.piston(0, state=2 if extra == 'x' else 0))
            elif k == 'ARM': f.set(p, Block(Kind.PISTON_ARM))
        return f

def sample(rnd, span=3):
    A = {0: (0, 0, 0)}
    A[1] = (rnd.randint(2, 7), rnd.randint(-span, span), rnd.randint(-span, span))
    A[2] = (rnd.randint(-2, 4), rnd.randint(-span, span), rnd.randint(-span, span))
    ori = {X: rnd.randrange(8) for X in (0, 1, 2)}
    hs = {X: rnd.choice((1, -1)) for X in (0, 1, 2)}
    return A, ori, hs

if __name__ == '__main__':
    import simtools
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    ticks = int(sys.argv[3]) if len(sys.argv) > 3 else 240
    out = pathlib.Path(sys.argv[4] if len(sys.argv) > 4 else 'work/ring3')
    out.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(seed0)
    vs = {}; meta = {}; tried = 0; geom_ok = 0
    while tried < n:
        tried += 1
        A, ori, hs = sample(rnd)
        L = Layout(A, ori, hs)
        if not L.ok: continue
        geom_ok += 1
        for mats in (('S','H','S'), ('H','S','H'), ('S','H','H'), ('H','S','S'), ('S','S','H'), ('H','H','S')):
            cells = L.route(dict(zip((0,1,2), mats)), rnd)
            if cells is None: continue
            name = f's{seed0}_{tried}_{"".join(mats)}'
            vs[name] = Layout.flyer(cells, dict(zip((0,1,2), mats)), 60)
            meta[name] = (A, ori, hs, mats, len(cells))
            break
    print('sampled', tried, 'geometry ok', geom_ok, 'routed', len(vs))
    res = simtools.screen(vs, ticks)
    good = []
    for k, r in res.items():
        if r['clean'] == 'true' and int(r['distance']) >= ticks * 10 // 30 - 8:
            good.append((int(r['max_successful_action']), k)); vs[k].save(out / f'{k}.flyer')
    good.sort()
    print('working', len(good))
    for l, k in good[:15]: print(k, simtools.brief(res[k]), meta[k])
    dist = collections.Counter(int(r['distance']) for r in res.values())
    print('distance histogram (top):', sorted(dist.items(), key=lambda kv: -kv[0])[:12])
