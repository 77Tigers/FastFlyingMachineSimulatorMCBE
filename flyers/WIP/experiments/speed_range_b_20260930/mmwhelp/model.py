"""Abstract model helpers for the planar mmwmmw design (reuses overnight_20260930 generator modules)."""
from pathlib import Path
import sys,json,importlib.util
HERE=Path(__file__).resolve().parent
OV=HERE.parents[1]/'overnight_20260930'
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('mmw_planar',OV/'mmw_planar.py')
mp=importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
m=mp.m; ns=mp.ns
from fastflyer import Flyer,Block,Kind
def load_geometry(path=OV/'trim_planar_mmw'/'geometry.json'):
    d=json.load(open(path))
    ss=[set(map(tuple,s)) for s in d['segments']]
    ps=[(tuple(p),list(dp),f,t,st) for p,dp,f,t,st in d['pistons']]
    src=[(tuple(p),o,ob,dr) for p,o,ob,dr in d['sources']]
    return ss,ps,src
def to_flyer(ss,ps,sources,limit=1000):
    f=Flyer(rng_state=5,push_limit=limit)
    for p,owner,observer,direction in sources:
        f._cells[p]=Block.observer(direction,powered=bool(m.S[owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)
    for pp,dp,phase,target,sticky in ps:
        state=2 if (0-phase)%6==1 else 0
        f._cells[pp]=Block.piston(0,state=state)
        if state:f._cells[m.shift(pp,1)]=Block(Kind.PISTON_ARM)
    for i,s in enumerate(ss):
        for p in s:
            assert p not in f._cells,(p,i)
            f._cells[p]=Block(m.K[i])
    return f
