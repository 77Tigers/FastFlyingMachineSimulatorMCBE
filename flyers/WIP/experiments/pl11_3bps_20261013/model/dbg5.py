import itertools, math
import halfring
from satflyer5 import FlyerSAT
rad=5
half=[(round(rad*math.cos(math.radians(36*k+18))), round(rad*math.sin(math.radians(36*k+18)))) for k in range(5)]
centers=half+[(-y,-z) for y,z in half]
orig = FlyerSAT.__init__
for skip in [('power','cause'),('power','targets'),('cause','targets')]:
    def patched(self, *a, _s=skip, **k):
        k['skip'] = _s; orig(self, *a, **k)
    FlyerSAT.__init__ = patched
    S, segs = halfring.build(40, centers, 1, 'm2:2', 'm4:1', 2, maxglue=7)
    print(skip, S.solve(60, 12), flush=True)
