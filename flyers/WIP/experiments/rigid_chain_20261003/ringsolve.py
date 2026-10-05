"""Geometric builder for closed rigid designs (rings) enumerated by topo4.py.

For a design (words, acts) and x-positions from topo4.solve: DFS lane assignment (each action gets a (y,z) lane;
pistons of one segment must sit at L1 distance 2 when they share x so a single block can power both), exact
minimum glue per body (hop4.min_glue with rigid.reserved_cells), power placement from ANY segment (so duplicated
rings share blocks automatically), then the exact checker. Survivors are saved with their max action load.

usage: python ringsolve.py N MAXP SEED OUTDIR [max_est_load] [maxg]
"""
import itertools, random, sys, pathlib, re, copy, pickle, os
from collections import Counter
from rigid import Seg, check, to_flyer, add, D6, loads, reserved_cells, kind_of
from topo import contact_ok
from topo2 import designs
import topo4
from hop4 import min_glue
from capped4 import power_options2, best_of
DBG = Counter()
X = (1, 0, 0)

def spec_from(words, acts, els):
    ex = []
    for typ, a, t, k in acts:
        U, W, VP, VS = els[a][0], els[a][1], els[t][2], els[t][3]
        ex.append(((U, VP) if typ == 'push' else (W, VS)))
    return ex

def lane_dfs(words, acts, ex, grid, rng, maxsol=6):
    n = len(words); cells = [dict() for _ in range(n)]; sols = []
    lanes = [(y, z) for y in range(grid) for z in range(grid)]
    def place(i, lane):
        typ, a, t, k = acts[i]; xa, xt = ex[i]
        pc = (xa, lane[0], lane[1]); gc = (xt, lane[0], lane[1]); pk = 'P' if typ == 'push' else 'S'
        new = []
        for seg, c, kk in ((a, pc, pk), (t, gc, 'g')):
            if c in cells[seg]:
                if cells[seg][c] != kk or kk != 'g': return None
                continue
            if any(c in cells[j] for j in range(n)): return None
            new.append((seg, c, kk))
        for seg, c, kk in new:
            if kk in 'PS':
                for c2, k2 in cells[seg].items():
                    if k2 in 'PS' and c2[0] == c[0] and sum(abs(u - v) for u, v in zip(c, c2)) != 2: return None
        return new
    nodes = [0]
    def dfs(i):
        if len(sols) >= maxsol or nodes[0] > 20000: return
        if i == len(acts): sols.append([dict(c) for c in cells]); return
        ls = list(lanes); rng.shuffle(ls)
        for lane in ls:
            nodes[0] += 1
            new = place(i, lane)
            if new is None: continue
            for seg, c, kk in new: cells[seg][c] = kk
            dfs(i + 1)
            for seg, c, kk in new: del cells[seg][c]
    dfs(0)
    return sols


def glue_lb(words, cells, i, mats, maxg, rng):
    """Minimum glue for segment i given everything placed so far (lower bound: more placements only add obstacles)."""
    n = len(words)
    segs = [Seg(f'S{j}', words[j], (0, 0, 0), dict(cells[j]), mats[j]) for j in range(n)]
    s = segs[i]
    if not s.cells: return 0
    pist = [c for c, k in s.cells.items() if k in ('P', 'S')]
    reqs = []
    for p in pist:
        fr = add(p, X) if s.cells[p] == 'P' else add(p, (-1, 0, 0))
        reqs.append({add(p, d) for d in D6 if add(p, d) != fr})
    bad = reserved_cells(segs, s)
    for c, k in s.cells.items():
        if k == 'g' and c in bad: bad = bad - {c}
    xs = [c[0] for c in s.cells]; ys = [c[1] for c in s.cells]; zs = [c[2] for c in s.cells]
    box = ((min(xs) - 1, max(xs) + 1), (min(ys) - 1, max(ys) + 1), (min(zs) - 1, max(zs) + 1))
    # glue contacts exist as 'g' cells already; start set must be connected by min_glue
    if not any(k == 'g' for k in s.cells.values()):
        return 0
    sols = min_glue(s, reqs, bad, maxg, box, rng, cap=4000)
    return len(sols[0]) if sols else 99

def lane_dfs2(words, acts, ex, grid, rng, mats, maxg, maxsol=4, maxnodes=3000):
    n = len(words); cells = [dict() for _ in range(n)]; sols = []
    lanes = [(y, z) for y in range(grid) for z in range(grid)]
    order = []
    for i in range(n):
        for j, a in enumerate(acts):
            if (a[1] == i or a[2] == i) and j not in order: order.append(j)
    segacts = {i: [j for j, a in enumerate(acts) if a[1] == i or a[2] == i] for i in range(n)}
    placed = set(); nodes = [0]
    def place(i, lane):
        typ, a, t, k = acts[i]; xa, xt = ex[i]
        pc = (xa, lane[0], lane[1]); gc = (xt, lane[0], lane[1]); pk = 'P' if typ == 'push' else 'S'
        new = []
        for seg, c, kk in ((a, pc, pk), (t, gc, 'g')):
            if c in cells[seg]:
                if cells[seg][c] != kk or kk != 'g': return None
                continue
            if any(c in cells[j] for j in range(n)): return None
            new.append((seg, c, kk))
        for seg, c, kk in new:
            if kk in 'PS':
                for c2, k2 in cells[seg].items():
                    if k2 in 'PS' and c2[0] == c[0] and sum(abs(u - v) for u, v in zip(c, c2)) != 2: return None
        return new
    def dfs(idx):
        if len(sols) >= maxsol or nodes[0] > maxnodes: return
        if idx == len(order): sols.append([dict(c) for c in cells]); return
        i = order[idx]
        ls = list(lanes); rng.shuffle(ls)
        for lane in ls:
            nodes[0] += 1
            new = place(i, lane)
            if new is None: continue
            for seg, c, kk in new: cells[seg][c] = kk
            placed.add(i)
            ok = True
            for sg in {acts[i][1], acts[i][2]}:
                if all(j in placed for j in segacts[sg]):
                    if glue_lb(words, cells, sg, mats, maxg, rng) > maxg: ok = False; break
            if ok: dfs(idx + 1)
            placed.discard(i)
            for seg, c, kk in new: del cells[seg][c]
    dfs(0)
    return sols

def build(words, acts, cells, mats, rng, maxg):
    n = len(words)
    segs = [Seg(f'S{i}', words[i], (0, 0, 0), dict(cells[i]), mats[i]) for i in range(n)]
    for i, s in enumerate(segs):
        pist = [c for c, k in s.cells.items() if k in ('P', 'S')]
        reqs = []
        for p in pist:
            fr = add(p, X) if s.cells[p] == 'P' else add(p, (-1, 0, 0))
            reqs.append({add(p, d) for d in D6 if add(p, d) != fr})
        bad = reserved_cells(segs, s)
        xs = [c[0] for c in s.cells]; ys = [c[1] for c in s.cells]; zs = [c[2] for c in s.cells]
        box = ((min(xs) - 1, max(xs) + 1), (min(ys) - 1, max(ys) + 1), (min(zs) - 1, max(zs) + 1))
        sols = min_glue(s, reqs, bad, maxg, box, rng, cap=8000)
        if not sols: return None, f'glue S{i}'
        for c in rng.choice(sols): s.cells.setdefault(c, 'g')
    for _ in range(10):
        r = check(segs)
        if r is None or 'power missing' not in r: return segs, r
        m = re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        t = int(m.group(1)); si = [i for i, x in enumerate(segs) if x.name == m.group(2)][0]
        pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        opts = []
        for cst, cs in power_options2(segs, si, pw, t, m.group(3), rng, maxlen=2):
            rr = check(cs)
            if rr is None or ('power missing' in rr and rr != r): opts.append((cst, cs))
        st = best_of(opts, rng)
        if st is None: return segs, r
        segs = st
    return segs, check(segs)

if __name__ == '__main__':
    n = int(sys.argv[1]); os.environ['MAXP'] = sys.argv[2]
    seed = int(sys.argv[3]); out = pathlib.Path(sys.argv[4]); out.mkdir(exist_ok=True)
    maxest = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    maxg = int(sys.argv[6]) if len(sys.argv) > 6 else 6
    rng = random.Random(seed)
    os.environ['CONSEC'] = '1'
    import importlib, topo2
    importlib.reload(topo2)
    designs_ok = []
    for words, acts in topo2.designs(n):
        adj = {i: set() for i in range(n)}
        for _, a, t, _ in acts: adj[a].add(t); adj[t].add(a)
        st = [0]; vis = {0}
        while st:
            v = st.pop()
            for y in adj[v]:
                if y not in vis: vis.add(y); st.append(y)
        if len(vis) < n or not contact_ok(words, acts): continue
        r = topo4.solve(n, words, acts)
        if r is None or r[0] > maxest: continue
        designs_ok.append((r[0], words, acts, r[2]))
    designs_ok.sort(key=lambda x: x[0])
    print('designs', len(designs_ok), 'est loads', Counter(d[0] for d in designs_ok), flush=True)
    found = 0
    while True:
        est, words, acts, els = rng.choice(designs_ok[:max(1, len(designs_ok))])
        ex = spec_from(words, acts, els)
        for mt in itertools.product(['slime', 'honey'], repeat=n):
            if mt[0] != 'slime': continue
            mats = list(mt)
            for cells in lane_dfs2(words, acts, ex, 3, rng, mats, maxg):
                segs, why = build(words, acts, cells, mats, rng, maxg)
                if segs is None or why is not None:
                    DBG[re.sub(r'[-0-9(), ]+', '#', str(why))] += 1; continue
                L = loads(segs); found += 1
                tag = f's{os.getpid()}_{found:04d}_L{L}'
                to_flyer(segs, L).save(out / f'ring_{tag}.flyer'); pickle.dump(segs, open(out / f'ring_{tag}.pkl', 'wb'))
                print('FOUND load', L, 'est', est, [(s.name, len(s.cells)) for s in segs], flush=True)
        if sum(DBG.values()) % 20 == 0: print('dbg', dict(DBG.most_common(6)), flush=True)
