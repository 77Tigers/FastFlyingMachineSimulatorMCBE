import itertools
import ring10
from satflyer5 import FlyerSAT
bb = list(itertools.product(range(-1,3), range(-2,3), range(-2,3)))
rb = list(itertools.product(range(-3,2), range(-2,3), range(-2,3)))
orig = FlyerSAT.__init__
for skip in [('power','cause','adh','move','conn','targets'), ('power','cause','adh','move','targets'), ('power','cause','targets'),('power','cause','adh','move','conn')]:
    def patched(self, *a, _s=skip, **k):
        k['skip'] = _s; orig(self, *a, **k)
    FlyerSAT.__init__ = patched
    S, segs = ring10.build(30, (1,0,0), 3, bb, rb, maxglue=8, sym=True)
    st, dt = S.solve(60, 8)
    print(skip, st, round(dt,1), flush=True)
