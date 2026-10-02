import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
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
def view(f, x0,x1,y0,y1,z0,z1):
    cells = dict(f.blocks())
    for y in range(y0,y1+1):
        print(f'--- y={y}')
        print('     ' + ''.join(f'{x:3d}' for x in range(x0, x1 + 1)))
        for z in range(z0, z1 + 1):
            print(f'{z:4d} ' + ''.join((' ' + sym(cells[(x, y, z)])) if (x, y, z) in cells else '  .' for x in range(x0, x1 + 1)))
if __name__ == '__main__':
    f = Flyer.load(sys.argv[1]); a=list(map(int,sys.argv[2:8])); view(f,*a)
