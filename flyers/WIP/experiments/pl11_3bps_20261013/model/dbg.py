import itertools, sys
from ring10 import build
bb = list(itertools.product(range(-1,3), range(-3,4), range(-3,4)))
rb = list(itertools.product(range(-3,2), range(-3,4), range(-3,4)))
for skip in [(), ('power',), ('power','cause'), ('power','cause','adh'), ('power','cause','adh','move')]:
    S, segs = build(30, (1,0,0), 4, bb, rb, maxglue=8, sym=False)
    S2 = None
    # rebuild with skip
    from satflyer5 import FlyerSAT
    import ring10
    orig = FlyerSAT.__init__
    def patched(self, *a, **k):
        k['skip'] = skip; orig(self, *a, **k)
    FlyerSAT.__init__ = patched
    S, segs = build(30, (1,0,0), 4, bb, rb, maxglue=8, sym=False)
    FlyerSAT.__init__ = orig
    st, dt = S.solve(60, 6)
    print(skip, st, round(dt,1), flush=True)
