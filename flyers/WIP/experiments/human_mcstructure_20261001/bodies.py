"""Rigid-body decomposition of a Flyer by slime/honey adhesion (initial state, ignores arm cells' ownership).
Edges: a slime/honey block sticks to every face neighbour except the opposite material and glazed terracotta;
observers/pistons/redstone etc. adjacent to slime/honey are carried. Arms stick to nothing here."""
import sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Kind, DIRECTIONS
def bodies(f):
    cells = dict(f.blocks())
    glue = (Kind.SLIME, Kind.HONEY)
    adj = collections.defaultdict(set)
    for p, b in cells.items():
        if b.kind not in glue: continue
        for d in DIRECTIONS:
            q = (p[0]+d[0], p[1]+d[1], p[2]+d[2])
            c = cells.get(q)
            if c is None or c.kind == Kind.GLAZED_TERRACOTTA or c.kind == Kind.PISTON_ARM: continue
            if c.kind in glue and c.kind != b.kind: continue
            adj[p].add(q); adj[q].add(p)
    seen = set(); out = []
    for p in sorted(cells):
        if p in seen: continue
        comp = []; st = [p]; seen.add(p)
        while st:
            q = st.pop(); comp.append(q)
            for r in adj[q]:
                if r not in seen: seen.add(r); st.append(r)
        out.append(comp)
    return cells, out
def describe(f):
    cells, comps = bodies(f)
    rows = []
    for c in comps:
        cnt = collections.Counter()
        for p in c:
            b = cells[p]
            k = {Kind.SLIME:'sl',Kind.HONEY:'ho',Kind.REDSTONE_BLOCK:'RB',Kind.PISTON_ARM:'arm',Kind.OBSERVER:'obs',Kind.ROD:'rod',Kind.GLASS:'gl'}.get(b.kind)
            if b.kind == Kind.PISTON: k = ('S' if b.sticky else 'P') + 'xyz'[b.direction//2 if False else 0]
            if b.kind == Kind.PISTON: k = ('stk' if b.sticky else 'pst') + ('+x' if b.direction==0 else '-x' if b.direction==1 else '?')
            cnt[k] += 1
        xs=[p[0] for p in c]; ys=[p[1] for p in c]; zs=[p[2] for p in c]
        rows.append((min(xs), len(c), (min(xs),max(xs)),(min(ys),max(ys)),(min(zs),max(zs)), dict(cnt)))
    return sorted(rows)
if __name__ == '__main__':
    f = Flyer.load(sys.argv[1])
    for r in describe(f): print(r[1:], )
