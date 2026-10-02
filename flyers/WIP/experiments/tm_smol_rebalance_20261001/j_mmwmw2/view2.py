import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from fastflyer import Flyer, Kind
from view import sym
MOVED=[0,1,2,2,3]
def load_slot(k, d='snap'):
    f=Flyer.load(str(pathlib.Path(__file__).parent/d/f's{100+2*k}.flyer'))
    cells=dict(f.blocks())
    xs=[p[0] for p,b in cells.items() if p[1]==7 and p[2]==9 and b.kind==Kind.HONEY]
    off=min(xs)-5-MOVED[k]
    return {(p[0]-off,p[1],p[2]):b for p,b in cells.items()}
def show(cells,x0,x1,y0,y1,z0,z1):
    for y in range(y0,y1+1):
        print(f'--- y={y}')
        print('     '+''.join(f'{x:3d}' for x in range(x0,x1+1)))
        for z in range(z0,z1+1):
            print(f'{z:4d} '+''.join((' '+sym(cells[(x,y,z)])) if (x,y,z) in cells else '  .' for x in range(x0,x1+1)))
if __name__=='__main__':
    k=int(sys.argv[1]); a=list(map(int,sys.argv[2:8]))
    show(load_slot(k),*a)
