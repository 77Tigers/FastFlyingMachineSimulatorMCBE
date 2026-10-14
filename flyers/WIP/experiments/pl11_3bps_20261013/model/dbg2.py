import itertools
import ring10
from satflyer5 import FlyerSAT
import ring10
bb = list(itertools.product(range(-1,3), range(-2,3), range(-2,3)))
rb = list(itertools.product(range(-3,2), range(-2,3), range(-2,3)))
orig = FlyerSAT.__init__
def patched(self, *a, **k):
    k['skip'] = ('power','softcause'); orig(self, *a, **k)
FlyerSAT.__init__ = patched
S, segs = ring10.build(30, (1,0,0), 3, bb, rb, maxglue=8, sym=False)
st, dt = S.solve(240, 8, objective='softcause')
print(st, dt)
sv = S.solver
for (j,t),b in sorted(S.softcause.items()):
    print(S.names[j], t, sv.Value(b))
print(S.causes())
