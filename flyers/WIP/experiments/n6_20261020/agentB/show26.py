"""Rebuild the PL26 V9 screw ring and print per body: module place, glue cells in each module's frame."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from close_ring import chain
from ring_designer import Ring, route_all, V9, ORDER, PREV, NEXT, SYMS, shift, local, REST
place, _ = chain([(d, (5, 4), 1) for d in (-1, 0, -1, 2)])
ring = Ring(V9, {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()})
print(route_all(ring), 'check', ring.check())
print(ring.place)
import pickle
pickle.dump(ring, open('ring26.pkl', 'wb'))
# inverse sym
def inv(si, y, z):
    for a in range(-12, 13):
        for b in range(-12, 13):
            if SYMS[si](a, b) == (y, z): return (a, b)
for U in ORDER:
    x0, (oy, oz), si = ring.place[U]
    s = REST[U]       # U-local 0
    print(f'=== module {U} frame at U-local 0 (global {s}); hole cells (1,1),(1,2),(2,1),(2,2)')
    occ = ring.world(s, canon=True)
    rows = []
    for c, lst in occ.items():
        y, z = inv(si, c[1] - oy, c[2] - oz)
        x = c[0] - x0 - shift(U, s)
        if -1 <= y <= 4 and -1 <= z <= 4 and -4 <= x <= 5:
            rows.append(((x, y, z), [(o[0], o[1]) for o in lst]))
    for r in sorted(rows): print(r)
