import sys, itertools, time
import construct
from nk import Timing, Ring, SYMS

def racetrack(L, a, b, gy, gz, sym_top, top_shift, half):
    """bottom row +y unrotated; top row -y with orientation sym_top. Module origin = (0,0) corner of its a x b box;
    for rotated modules shift so the rotated box occupies [y, y+a) x [z, z+b)."""
    sy = a + gy; nb = (L + 1) // 2; nt = L - nb
    pts = [((i * sy, 0), 0) for i in range(nb)]
    ys = [(nb - 1 - j) * sy for j in range(nt)] if (nt == nb or not half) else [round((nb - 1.5 - j) * sy) for j in range(nt)]
    # rotated box offset so that the module occupies the same footprint
    ry = [SYMS[sym_top](y, z) for y in (0, a - 1) for z in (0, b - 1)]
    oy = -min(p[0] for p in ry); oz = -min(p[1] for p in ry)
    zt = b + gz
    pts += [((y + oy + top_shift[0], zt + oz + top_shift[1]), sym_top) for y in ys]
    return [(0, p, s) for p, s in pts]

def build(k, lay):
    T = Timing(k); mod = construct.grid_module(k, 'slabP'); a, b = mod['size']
    ring = Ring(T, [mod] * T.L, lay(T.L, a, b))
    for X in range(T.L): ring.route(X)
    return ring

if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    for k in ks:
        res = []
        for sym_top in (0, 2, 4, 5):
            for gz in (0, 1, 2):
                for half in (0, 1):
                    for ts in ((0, 0), (1, 0), (-1, 0)):
                        f = lambda L, a, b: racetrack(L, a, b, 2, gz, sym_top, ts, half)
                        try:
                            r = build(k, f); bad = r.check()
                            if not bad: res.append((max(r.size()), sym_top, gz, half, ts))
                        except Exception as e: pass
        res.sort(); print(k, res[:4], flush=True)
