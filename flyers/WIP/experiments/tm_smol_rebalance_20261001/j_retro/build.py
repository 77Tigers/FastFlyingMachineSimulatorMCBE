import sys, pathlib, subprocess
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
BASE = HERE.parent / 'base.flyer'
def load():
    f = Flyer.load(str(BASE)); return f
def build(sticky=(), glue=(), rb=(), remove=(), conn=()):
    """sticky: [(x,y,z)] -X sticky; glue: [(x,y,z,'sl'|'ho')]; rb: [(x,y,z)]; remove: cells (pistons etc.)"""
    f = load()
    for c in remove: f.remove(tuple(c))
    for c in sticky: f.set(tuple(c), Block.piston(1, sticky=True, state=0))
    for x,y,z,k in glue: f.set((x,y,z), Block(Kind.SLIME if k=='sl' else Kind.HONEY))
    for c in rb: f.set(tuple(c), Block(Kind.REDSTONE_BLOCK))
    return f
def run(f, name, limit=12, ticks=600):
    p = HERE / 'cand' / f'{name}.flyer'; p.parent.mkdir(exist_ok=True)
    f.save(str(p))
    out = subprocess.run([str(HERE.parent/'loadhist.exe'), str(ticks), '100', str(limit), str(p)], capture_output=True, text=True).stdout.splitlines()[1]
    return out
