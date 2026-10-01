"""Region-wise hybrids between a working flyer A and a broken variant B (aligned by diffalign).
Differing cells are clustered (26-adjacency) into regions; each region is taken wholly from A or B.
python hybrid.py A.flyer B.flyer TICKS LIMIT [MAXREGIONS]"""
import sys, pathlib, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer, Block, Kind
import simtools, diffalign
def regions(a, bt):
    diff = sorted(p for p in set(a) | set(bt) if a.get(p) != bt.get(p))
    S = set(diff); seen = set(); out = []
    for p in diff:
        if p in seen: continue
        st = [p]; seen.add(p); comp = []
        while st:
            q = st.pop(); comp.append(q)
            for d in itertools.product((-1,0,1), repeat=3):
                r = (q[0]+d[0], q[1]+d[1], q[2]+d[2])
                if r in S and r not in seen: seen.add(r); st.append(r)
        out.append(sorted(comp))
    return out
if __name__ == '__main__':
    A = Flyer.load(sys.argv[1]); B = Flyer.load(sys.argv[2]); ticks = int(sys.argv[3]); limit = int(sys.argv[4])
    a = dict(A.blocks()); b = dict(B.blocks())
    n, (dx, dy, dz) = diffalign.align(a, b)
    bt = {(p[0]+dx, p[1]+dy, p[2]+dz): bl for p, bl in b.items()}
    regs = regions(a, bt)
    for i, r in enumerate(regs):
        print(f'R{i}: {len(r)} cells  A:{sum(1 for p in r if p in a)} B:{sum(1 for p in r if p in bt)}  {r[0]}..{r[-1]}')
    k = len(regs)
    vs = {}
    for mask in range(1 << k):
        g = Flyer(A.phase_x, A.phase_z, A.rng_state, limit)
        cells = dict(a)
        for i, r in enumerate(regs):
            if mask >> i & 1:
                for p in r:
                    cells.pop(p, None)
                    if p in bt: cells[p] = bt[p]
        for p, bl in cells.items(): g.set(p, bl)
        vs[f'm{mask:0{k}b}'] = g
    print(len(vs), 'hybrids; bit i=1 means region i from B')
    res = simtools.screen(vs, ticks)
    ok = [(m, r) for m, r in res.items() if int(r['distance']) >= ticks * 3 // 10 - 6 and r['clean'] == 'true']
    ok.sort(key=lambda mr: (-mr[0].count('1'), int(mr[1]['max_successful_action'])))
    print(len(ok), 'run at ~3 bps; most-B first:')
    for m, r in ok[:20]: print(m, simtools.brief(r))
