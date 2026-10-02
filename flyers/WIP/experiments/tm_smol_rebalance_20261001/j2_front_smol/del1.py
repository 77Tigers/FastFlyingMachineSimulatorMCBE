import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from fastflyer import Flyer, Kind
src, outd = sys.argv[1], pathlib.Path(sys.argv[2]); outd.mkdir(exist_ok=True)
f = Flyer.load(src)
for lim in map(int, sys.argv[3:]):
    for p, b in f.blocks():
        if b.kind not in (Kind.SLIME, Kind.HONEY, Kind.REDSTONE_BLOCK): continue
        g = Flyer(f.phase_x, f.phase_z, f.rng_state, lim)
        for q, c in f.blocks():
            if q != p: g.set(q, c)
        g.save(str(outd / f'L{lim}_{p[0]}_{p[1]}_{p[2]}.flyer'))
