"""Re-route glue arms of a flyer while keeping their end redstone blocks fixed (keeps power timing).
Arm cells may only touch: their own root body, other cells of the same arm, the RB, air, and blocks
their material does not stick to (honey<->slime, glazed). Combos of both arms are screened."""
import sys, pathlib, random, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer, Block, Kind, DIRECTIONS
import simtools
from perturb import clone
def nb(p): return [(p[0]+d[0],p[1]+d[1],p[2]+d[2]) for d in DIRECTIONS]
def sticks(m, other):
    if other.kind in (Kind.GLAZED_TERRACOTTA, Kind.PISTON_ARM): return False
    if other.kind in (Kind.SLIME, Kind.HONEY) and other.kind != m: return False
    return True
def glue_component(cells, seed, mat):
    st=[seed]; seen={seed}
    while st:
        q=st.pop()
        for r in nb(q):
            if r in cells and r not in seen and cells[r].kind==mat: seen.add(r); st.append(r)
    return seen
def arm_paths(cells, root, mat, rb, banned, maxlen, limit, rng):
    """cells: occupancy without the arm. root: set of root glue cells. Path cells empty, legal neighbours."""
    def legal(c, path):
        if c in cells or c in banned or c == rb: return False
        for r in nb(c):
            if r in root or r == rb or r in path: continue
            o = cells.get(r)
            if o is not None and sticks(mat, o): return False
        return True
    from collections import deque
    goal = [q for q in nb(rb) if legal(q, ())]
    dist = {g:0 for g in goal}; dq = deque(goal)
    while dq:
        q = dq.popleft()
        for r in nb(q):
            if r not in dist and dist[q] < maxlen and legal(r, ()): dist[r] = dist[q]+1; dq.append(r)
    firsts = [c for s in root for c in nb(s) if c in dist]; rng.shuffle(firsts)
    out=[]; seen=set()
    def dfs(path):
        if len(out) >= limit: return
        last = path[-1]
        if dist[last] == 0:
            k = frozenset(path)
            if k not in seen: seen.add(k); out.append(list(path))
            return
        nxt = [r for r in nb(last) if r in dist and r not in path and len(path)+dist[r] <= maxlen and legal(r, path)]
        rng.shuffle(nxt)
        for r in nxt: dfs(path+[r])
    for c in firsts: dfs([c])
    out.sort(key=len)
    return out
