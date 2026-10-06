"""offsets (dx 0/1) where the image K3' can carry V at slot 1 (hand conditions), for V at (9,y,z), g'=(11,y,z)."""
from subB_lib import *
from satflyer import D6
T3 = tcells(3)[0]
VS = [(9, 0, 3), (9, 1, 4), (9, 2, 4), (9, 3, 3)]
out = []
for mp, d, fd in candidates(list(YZ), 5, 4, range(0, 2)):
    T, km = mapper(mp, d)
    w3 = {}
    for u, k in T3.items():
        c = T(u, 0); w3[(c[0] + 1, c[1], c[2])] = k        # K3' (mmww) at slot 1 = slot-0 + 1
    ok = []
    for v in VS:
        if v in w3: continue
        side = any(w3.get(add3(v, dd)) == 'g' for dd in D6[2:])
        behind = add3(v, (-1, 0, 0)) in w3
        if side or behind: ok.append((v, 'side' if side else 'behind'))
    if ok: out.append((mp, d, fd, ok))
print(len(out))
for o in out: print(o)
