"""c5-concept repair: delete a helper body (+its pushers) and re-supply its redstone block from a glue arm
rooted on a body with the same movement word (constant relative offset => identical power timing).
python armsearch.py  (configuration below; writes candidates to work/arms/, prints screen results)"""
import sys, pathlib, random, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer, Block, Kind, DIRECTIONS
import simtools
from perturb import clone

def body_cells(f, box, kinds=(Kind.SLIME, Kind.HONEY)):
    x0,x1,y0,y1,z0,z1 = box
    return [p for p,b in f.blocks() if x0<=p[0]<=x1 and y0<=p[1]<=y1 and z0<=p[2]<=z1 and b.kind in kinds]

def nb(p): return [(p[0]+d[0],p[1]+d[1],p[2]+d[2]) for d in DIRECTIONS]

def paths(occ, starts, goal_adj, maxlen, limit, rng):
    """Random-order DFS for simple paths of empty cells; path[0] adjacent to a start glue cell, last cell adjacent to goal."""
    out = []; seen_paths = set()
    # BFS distance-to-goal for pruning
    from collections import deque
    dist = {}; dq = deque()
    for g in goal_adj:
        if g not in occ: dist[g] = 0; dq.append(g)
    while dq:
        q = dq.popleft()
        for r in nb(q):
            if r not in occ and r not in dist and abs(r[0])<40 and -3<=r[1]<=12 and abs(r[2])<40 and dist[q] < maxlen:
                dist[r] = dist[q]+1; dq.append(r)
    firsts = [c for s in starts for c in nb(s) if c in dist]
    rng.shuffle(firsts)
    def dfs(path):
        if len(out) >= limit: return
        last = path[-1]
        if dist.get(last) == 0:
            key = tuple(path)
            if key not in seen_paths: seen_paths.add(key); out.append(list(path))
            return
        n = [r for r in nb(last) if r in dist and r not in path and dist[r] < dist[last] + 1 and len(path) + dist[r] <= maxlen]
        rng.shuffle(n)
        for r in n: dfs(path + [r])
    for c in firsts:
        dfs([c])
    return out

def build(base, remove, anchor_mat, path, rb):
    g = clone(base)
    for p in remove: g.remove(p)
    for c in path: g.set(c, Block(anchor_mat))
    g.set(rb, Block(Kind.REDSTONE_BLOCK))
    return g

if __name__ == '__main__':
    rng = random.Random(1)
    base = Flyer.load('converted/human_tm_smol_3bps_pl12.flyer'); base.push_limit = 40
    cells = dict(base.blocks())
    B41 = [(12,4,7),(12,4,8),(12,5,7),(12,5,8),(12,5,9),(13,4,7),(13,4,8),(13,5,7),(13,5,8),(13,5,9)]
    B45 = [(13,3,1),(14,3,1),(14,3,2),(14,3,3),(14,4,2),(14,4,3),(15,3,1),(15,3,2),(15,3,3),(15,4,2),(15,4,3)]
    jobs = {
      'B41': (B41, (12,5,8), {'B15': (2,7,3,5,3,4), 'B24': (7,8,0,2,3,6)}),
      'B45': (B45, (14,3,2), {'B11': (4,5,2,3,5,8), 'B29': (8,9,5,7,5,8)}),
    }
    which = sys.argv[1:] or list(jobs)
    vs = {}
    for job in which:
        remove, rb, anchors = jobs[job]
        occ = set(cells) - set(remove)
        for an, box in anchors.items():
            glue = body_cells(base, box)
            for mat in (Kind.SLIME, Kind.HONEY):
                starts = [p for p in glue if cells[p].kind == mat]
                if not starts: continue
                ps = paths(occ | {rb}, starts, [q for q in nb(rb)], maxlen=12, limit=150, rng=rng)
                for i, pth in enumerate(ps):
                    vs[f'{job}_{an}_{mat.name[0]}_{len(pth)}_{i}'] = build(base, remove, mat, pth, rb)
    print(len(vs), 'candidates')
    res = simtools.screen(vs, 300)
    good = sorted(res.items(), key=lambda kv: (-int(kv[1]['distance']), int(kv[1]['max_successful_action'])))
    for n, r in good[:15]: print(f'{n:<26}', simtools.brief(r))
    import json; json.dump({n: r for n, r in res.items()}, open('work/armsearch_last.json', 'w'))
