"""ASCII layer viewer for .flyer files, in flyer coordinates (+X right = travel, +Z down).
Usage: python fview.py FILE [y ...]
 sl=slime ho=honey RB=redstone  P>/S> normal/sticky piston facing (>,<,^=-z,v=+z,U,D); trailing x = extended;
 ~~ piston arm; O> observer output direction (* if powered); |> rod; GL glass; ST stone; GZ glazed."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Kind
ARROW = {0: '>', 1: '<', 2: 'U', 3: 'D', 4: 'v', 5: '^'}
def sym(b):
    k = b.kind
    s = {Kind.SLIME: 'sl', Kind.HONEY: 'ho', Kind.REDSTONE_BLOCK: 'RB', Kind.GLASS: 'GL',
         Kind.SMOOTH_STONE: 'ST', Kind.GLAZED_TERRACOTTA: 'GZ', Kind.PISTON_ARM: '~~'}.get(k)
    if s: return s + ('m' if b.moving else ' ')
    if k == Kind.PISTON:
        return ('S' if b.sticky else 'P') + ARROW[b.direction] + ('x' if b.state == 2 else 'e' if b.state == 1 else 'r' if b.state == 3 else '') + ('' if b.state else ' ')
    if k == Kind.OBSERVER: return 'O' + ARROW[b.direction] + ('*' if b.powered else ' ')
    if k == Kind.ROD: return '|' + ARROW[b.direction] + ' '
    return '??'
def view(f, ys=None, out=sys.stdout):
    cells = dict(f.blocks())
    xs = [p[0] for p in cells]; ys_ = [p[1] for p in cells]; zs = [p[2] for p in cells]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    for y in range(min(ys_), max(ys_) + 1):
        if ys and y not in ys: continue
        layer = {p: b for p, b in cells.items() if p[1] == y}
        if not layer: continue
        print(f'--- y={y}  (x {x0}..{x1} right, z {z0}..{z1} down)', file=out)
        print('     ' + ''.join(f'{x:3d}' for x in range(x0, x1 + 1)), file=out)
        for z in range(z0, z1 + 1):
            print(f'{z:4d} ' + ''.join((' ' + sym(layer[(x, y, z)])) if (x, y, z) in layer else '  .' for x in range(x0, x1 + 1)), file=out)
if __name__ == '__main__':
    f = Flyer.load(sys.argv[1]); view(f, set(map(int, sys.argv[2:])) or None)
