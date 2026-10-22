import sys, pathlib, pickle
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ring_designer import Ring, ORDER, PREV, NEXT, SYMS, shift, REST
ring = pickle.load(open('ring26.pkl', 'rb'))
def inv(si, y, z):
    for a in range(-15, 16):
        for b in range(-15, 16):
            if SYMS[si](a, b) == (y, z): return (a, b)
U = 'A'; Y = PREV[U]
x0, (oy, oz), si = ring.place[U]
for s in (REST[U],):
    occ = ring.world(s, canon=True)
    for c, lst in sorted(occ.items()):
        y, z = inv(si, c[1] - oy, c[2] - oz); x = c[0] - x0 - shift(U, s)
        for o in lst:
            if o[0] == Y: print('Y=%s' % Y, (x, y, z), o[1])
