"""Body-labelled layer view: each cell = adhesion-body letter + fview symbol.  python bview.py FILE"""
import sys, pathlib, string
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer
import bodies, fview
def view(f, out=sys.stdout):
    cells, comps = bodies.bodies(f)
    comps = sorted(comps, key=lambda c: (-len(c), min(c)))
    lab = {}
    letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    for i, c in enumerate(comps):
        for p in c: lab[p] = letters[i] if len(c) > 1 else '-'
    xs = [p[0] for p in cells]; ys = [p[1] for p in cells]; zs = [p[2] for p in cells]
    for y in range(min(ys), max(ys)+1):
        print(f'--- y={y}', file=out)
        print('     ' + ''.join(f'{x:5d}' for x in range(min(xs), max(xs)+1)), file=out)
        for z in range(min(zs), max(zs)+1):
            print(f'{z:4d} ' + ''.join(('  ' + lab[(x,y,z)] + fview.sym(cells[(x,y,z)])[:2]) if (x,y,z) in cells else '    .' for x in range(min(xs), max(xs)+1)), file=out)
if __name__ == '__main__':
    view(Flyer.load(sys.argv[1]))
