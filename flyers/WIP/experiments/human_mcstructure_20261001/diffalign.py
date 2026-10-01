"""Align flyer B onto flyer A by the translation maximizing identical cells; print differences.
Usage: python diffalign.py A.flyer B.flyer"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Kind
def s(bl):
    if bl is None: return '.'
    k = bl.kind.name.lower()
    if bl.kind == Kind.PISTON:
        k = ('sticky' if bl.sticky else 'piston') + ['+x','-x','+y','-y','+z','-z'][bl.direction] + (' ext' if bl.state == 2 else '')
    if bl.kind == Kind.OBSERVER: k = 'obs' + ['+x','-x','+y','-y','+z','-z'][bl.direction]
    return k
def align(a, b, r=20):
    best = None
    for dx in range(-r, r+1):
        for dy in range(-10, 11):
            for dz in range(-r, r+1):
                n = sum(1 for p, bl in b.items() if a.get((p[0]+dx, p[1]+dy, p[2]+dz)) == bl)
                if best is None or n > best[0]: best = (n, (dx, dy, dz))
    return best
if __name__ == '__main__':
    a = dict(Flyer.load(sys.argv[1]).blocks()); b = dict(Flyer.load(sys.argv[2]).blocks())
    n, (dx, dy, dz) = align(a, b)
    print(f'overlap {n} of A={len(a)} B={len(b)} at B+({dx},{dy},{dz})')
    bt = {(p[0]+dx, p[1]+dy, p[2]+dz): bl for p, bl in b.items()}
    for p in sorted(set(a) | set(bt)):
        if a.get(p) != bt.get(p): print(f'  {p}: A={s(a.get(p)):<14} B={s(bt.get(p))}')
