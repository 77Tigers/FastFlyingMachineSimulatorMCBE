"""Greedy region adoption from broken B into working A (face-adjacency regions of differing cells).
python hybrid_greedy.py A.flyer B.flyer TICKS LIMIT OUTPREFIX"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer
import simtools, diffalign
D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def regions(a, bt):
    diff = sorted(p for p in set(a) | set(bt) if a.get(p) != bt.get(p))
    S = set(diff); seen = set(); out = []
    for p in diff:
        if p in seen: continue
        st = [p]; seen.add(p); comp = []
        while st:
            q = st.pop(); comp.append(q)
            for d in D6:
                r = (q[0]+d[0], q[1]+d[1], q[2]+d[2])
                if r in S and r not in seen: seen.add(r); st.append(r)
        out.append(sorted(comp))
    return out
def make(A, a, bt, regs, chosen, limit):
    g = Flyer(A.phase_x, A.phase_z, A.rng_state, limit); cells = dict(a)
    for i in chosen:
        for p in regs[i]:
            cells.pop(p, None)
            if p in bt: cells[p] = bt[p]
    for p, bl in cells.items(): g.set(p, bl)
    return g
def works(r, ticks): return r['clean'] == 'true' and int(r['distance']) >= ticks * 3 // 10 - 6
if __name__ == '__main__':
    A = Flyer.load(sys.argv[1]); B = Flyer.load(sys.argv[2]); ticks = int(sys.argv[3]); limit = int(sys.argv[4]); out = sys.argv[5]
    a = dict(A.blocks()); b = dict(B.blocks())
    n, (dx, dy, dz) = diffalign.align(a, b)
    bt = {(p[0]+dx, p[1]+dy, p[2]+dz): bl for p, bl in b.items()}
    regs = regions(a, bt)
    print(len(regs), 'regions')
    single = simtools.screen({f'r{i}': make(A, a, bt, regs, [i], limit) for i in range(len(regs))}, ticks)
    okset = [i for i in range(len(regs)) if works(single[f'r{i}'], ticks)]
    for i in range(len(regs)):
        r = regs[i]; s = single[f'r{i}']
        print(f'R{i:<2} n={len(r):<2} A:{sum(1 for p in r if p in a)} B:{sum(1 for p in r if p in bt)} {r[0]} -> {"OK " if i in okset else "bad"} {simtools.brief(s)}')
    chosen = []
    for i in sorted(okset, key=lambda i: -len(regs[i])):
        trial = chosen + [i]
        r = simtools.screen({'t': make(A, a, bt, regs, trial, limit)}, ticks)['t']
        if works(r, ticks): chosen = trial; print('  keep', i, simtools.brief(r))
    print('adopted B regions:', sorted(chosen), 'B cells adopted:', sum(sum(1 for p in regs[i] if p in bt) for i in chosen))
    make(A, a, bt, regs, chosen, limit).save(out + '.flyer')
