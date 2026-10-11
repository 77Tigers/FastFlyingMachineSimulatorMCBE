from back6 import *
import back6
def run(L, rw, skip=(), **kw):
    orig = FlyerSAT.__init__
    M = build(L, rw, kw.pop('k1max', 6), **kw) if not skip else None
    if skip:
        import psat
        _b = back6.FlyerSAT
        class F2(_b):
            def __init__(s, *a, **k): k['skip'] = skip; _b.__init__(s, *a, **k)
        back6.FlyerSAT = F2
        try: M = back6.build(L, rw, kw.pop('k1max', 6), **kw)
        finally: back6.FlyerSAT = _b
    st, dt = M.solve(60, 8); print(L, rw, skip, kw, st, round(dt, 1), flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'): print(show(M.extract())); print(report(M))
run(6, (), skip=('power',))
run(9, (), skip=('power',))
run(9, ())
run(9, ('wwmm',))
