# Rigid mmww/wwmm staircase chain builder. Segment K: origin x = 2K (+1 if K odd) at s0, y = K.
# Local template: S(0,0,0) -X, g(0,1,0), P(0,2,0) +X, side glue a(0,1,s), b(-1,1,s), rod(-1,0,s) facing -s.
# s=+1 for even K, -1 for odd K. Rod on K powers K-1 (hard-powers K-1's g) at K-1's fire slot.
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind
def seg_cells(K, mats=('slime','honey'), rod=True):
    s = 1 if K % 2 == 0 else -1
    ox, oy = 2*K + (K % 2), K
    m = Kind.SLIME if mats[K % 2]=='slime' else Kind.HONEY
    c = {(0,0,0): Block.piston(1, sticky=True), (0,1,0): Block(m), (0,2,0): Block.piston(0),
         (0,1,s): Block(m), (-1,1,s): Block(m)}
    if rod: c[(-1,0,s)] = Block.rod(5 if s == 1 else 4)
    return {(ox+x, oy+y, z): b for (x,y,z), b in c.items()}
def build(n, lim, extra=None):
    f = Flyer(); f.push_limit = lim
    for K in range(n):
        for p, b in seg_cells(K).items():
            assert f.get(p) is None, (K, p); f.set(p, b)
    return f
if __name__ == '__main__':
    n, lim, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    build(n, lim).save(out)
