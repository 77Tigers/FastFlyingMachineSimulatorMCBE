import itertools, math
import halfring
from satflyer5 import FlyerSAT
rad=5
half=[(round(rad*math.cos(math.radians(36*k+18))), round(rad*math.sin(math.radians(36*k+18)))) for k in range(5)]
centers=half+[(-y,-z) for y,z in half]
orig = FlyerSAT.__init__
def patched(self, *a, **k):
    k['skip'] = ('power','softcause','targets'); orig(self, *a, **k)
FlyerSAT.__init__ = patched
for sym in (True, False):
    S, segs = halfring.build(40, centers, 1, 'm2:2', 'm4:1', 2, maxglue=7, sym=sym)
    st = S.solve(120, 12, objective='softcause')
    sv = S.solver
    print(sym, st, sv.ObjectiveValue() if st[0] in ('OPTIMAL','FEASIBLE') else None, len(S.softcause))
    if st[0] in ('OPTIMAL','FEASIBLE'):
        print([ (S.names[j],t) for (j,t),b in S.softcause.items() if not sv.Value(b)])
