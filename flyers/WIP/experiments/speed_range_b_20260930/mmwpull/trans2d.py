"""2D transverse arrangement search: spine of b adjacent to foreign column F of V(b) (b=X_of(V)) and U(b) (b=Z_of(U))."""
import itertools, json
from sched import X_of, Z_of
from gen import SYMS
FOOT = dict(L1=(0, 0), L2=(1, 1), S=(1, 0), F=(0, 1))
OPOS = [(2, 0), (1, -1)]
def adj(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1
Vof = {X_of(v): v for v in range(3)}; Uof = {Z_of(u): u for u in range(3)}
sols = []
R = range(-4, 5)
def foot(s, off, oo):
    m = {k: tuple(a + b for a, b in zip(SYMS[s](*c), off)) for k, c in FOOT.items()}
    m['O'] = tuple(a + b for a, b in zip(SYMS[s](*OPOS[oo]), off))
    return m
for s1, s2 in itertools.product(range(8), repeat=2):
    for o1 in itertools.product(R, R):
        for o2 in itertools.product(R, R):
            for oo in itertools.product((0, 1), repeat=3):
                fs = [foot(0, (0, 0), oo[0]), foot(s1, o1, oo[1]), foot(s2, o2, oo[2])]
                cells = [c for f in fs for c in f.values()]
                if len(set(cells)) < len(cells): continue
                ok = True
                for b in range(3):
                    if not adj(fs[b]['S'], fs[Vof[b]]['F']) or not adj(fs[b]['S'], fs[Uof[b]]['F']): ok = False; break
                    for c in range(3):
                        if c == b: continue
                        if adj(fs[b]['S'], fs[c]['L1']) or adj(fs[b]['S'], fs[c]['L2']): ok = False; break
                    if not ok: break
                if ok:
                    sols.append(((0, s1, s2), ((0, 0), o1, o2), oo))
print(len(sols))
json.dump(sols, open('trans2d.json', 'w'))
for s in sols[:10]: print(s)
