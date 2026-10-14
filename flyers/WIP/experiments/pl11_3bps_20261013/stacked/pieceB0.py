import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "extract"))
import xlib as X
M = X.Model('flyers/bank/pl12/human_3bps_original.flyer', 100)
ev = M.ev
def find(kind, actor, tgt): return [e for e in ev if e['kind'] == kind and e['actor'] == actor and tgt in e['targets']][0]
A = [find('push','B19','B33'), find('push','B25','B33'), find('pull','B33','B9')]
for pas in (True, False):
    for per in (1, 3):
        try:
            Ms = [M] if per == 1 else [M, X.Model(M.src, 110, base=M), X.Model(M.src, 120, base=M)]
            As = [A] if per == 1 else [A]
            if per == 3:
                for Mk in Ms[1:]:
                    a2 = [ [e for e in Mk.ev if e['kind']==x['kind'] and e['targets']==x['targets'] and e['slot']==x['slot']][0] for x in A]
                    As.append(a2)
            pl = X.plan(Ms, As, name='B0', passengers=pas)
            D = HERE / f"B0_work/p{per}{'' if pas else 'np'}"
            info = X.build_plan(M, pl, D)
            res = X.evaluate_all(D); ch = X.choose(res)
            print(per, pas, info['kept'], pl['keep'], [(p['name'], p['role'], p['prescribe']) for p in pl['ports']], pl['notes'][:2], '->', ch)
        except Exception as ex:
            print(per, pas, 'ERR', ex)
