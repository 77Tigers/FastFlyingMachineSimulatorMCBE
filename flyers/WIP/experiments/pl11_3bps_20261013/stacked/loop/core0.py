import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "extract"))
import xlib as X
SRC = 'flyers/bank/pl12/human_3bps_original.flyer'
M = X.Model(SRC, 100)
Ms = [M, X.Model(SRC, 110, base=M), X.Model(SRC, 120, base=M)]
Xs = {'B7','B8','B9','B15','B16'}; Ts = {'B28','B29','B33','B23','B24'}
def sel(Mk):
    out = []
    for e in Mk.ev:
        t = set(e['targets'])
        if t & Xs and not (e['kind']=='pull' and e['actor'] not in Ts): out.append(e)      # back pushes + T pulls of X
        elif t & Ts and e['kind']=='push': out.append(e)                                      # T column pushes
    return out
As = [sel(Mk) for Mk in Ms]
print([len(a) for a in As])
for pas in (False, True):
    pl = X.plan(Ms, As, name='core0', passengers=pas)
    D = HERE / f"core0_{'np' if not pas else 'p'}"
    info = X.build_plan(M, pl, D)
    res = X.evaluate_all(D); ch = X.choose(res)
    print(pas, info['kept'], len(pl['keep']), [(p['name'],p['role'],p['prescribe']) for p in pl['ports']], pl['notes'][:3], '->', ch)
    for k,v in res.items(): print(' ',k, v.get('pass'), str(v.get('first_failure'))[-140:])
