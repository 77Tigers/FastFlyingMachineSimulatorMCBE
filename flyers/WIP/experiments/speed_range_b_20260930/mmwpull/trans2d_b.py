import itertools, json, collections
from sched import X_of, Z_of
from gen import SYMS
FOOT = dict(L1=(0, 0), L2=(1, 1), S=(1, 0), F=(0, 1))
def adj(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1
def d1(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
Vof = {X_of(v): v for v in range(3)}; Uof = {Z_of(u): u for u in range(3)}
R = range(-4, 5)
def foot(s, off):
    return {k: tuple(a + b for a, b in zip(SYMS[s](*c), off)) for k, c in FOOT.items()}
cnt = collections.Counter(); best = []
for s1, s2 in itertools.product(range(8), repeat=2):
    for o1 in itertools.product(R, R):
        f1 = foot(s1, o1); f0 = foot(0, (0, 0))
        if set(f0.values()) & set(f1.values()): continue
        for o2 in itertools.product(R, R):
            fs = [f0, f1, foot(s2, o2)]
            cells = [c for f in fs for c in f.values()]
            if len(set(cells)) < len(cells): continue
            bad = any(adj(fs[b]['S'], fs[c][l]) for b in range(3) for c in range(3) if c != b for l in ('L1', 'L2'))
            cost = sum(d1(fs[b]['S'], fs[Vof[b]]['F']) - 1 + d1(fs[b]['S'], fs[Uof[b]]['F']) - 1 for b in range(3))
            cnt[(bad, cost)] += 1
            if not bad and cost <= 12: best.append((cost, (0, s1, s2), ((0, 0), o1, o2)))
print(sorted(cnt.items())[:20]); print(sorted(k for k in cnt if k[0])[:5])
best.sort()
json.dump(best, open('trans2d.json', 'w'))
print(len(best), best[:5])
