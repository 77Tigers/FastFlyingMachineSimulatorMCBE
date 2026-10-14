import sys, json, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "extract"))
import xlib as X
def describe(D, namesfile, order="before_natural", rec="bounded", sample=(0,0,0), cyc=1):
    D = Path(D).resolve()
    nm = {tuple(json.loads(k.replace('(', '[').replace(')', ']'))): v for k, v in json.load(open(namesfile)).items()}
    c, rows = X.fixture_trace(D, order, rec, sample, 30)
    pos2id = {tuple(q[:3]): tuple(q[:3]) for q in rows[0]['trace']['initial'] if (q[3] & 15) != 10}
    name = lambda i: nm.get(i, ('?' + str(i), ''))[0]
    out = []
    for r in rows:
        for s in r['trace']['steps']:
            mv = s.get('movement')
            if mv and mv.get('sources') and mv.get('destinations') and s['action'] in ('extend', 'retract', 'prescribed move'):
                m = {tuple(a): tuple(b) for a, b in zip(mv['sources'], mv['destinations'])}
                idm = [(pos2id[a], a, b) for a, b in m.items() if a in pos2id]
                if r['tick'] // 10 == cyc:
                    cnt = collections.Counter(name(i) for i, _, _ in idm)
                    ap = tuple(s['active_piston']) if s.get('active_piston') else None
                    actor = name(pos2id.get(ap)) if ap else '-'
                    out.append((r['tick'] % 10, s['action'][:4], actor, len(m), dict(cnt)))
                for i, a, b in idm: pos2id.pop(a)
                for i, a, b in idm: pos2id[b] = i
    return sorted(out, key=lambda x: (x[0], x[2]))
if __name__ == "__main__":
    for o in describe(sys.argv[1], sys.argv[2]): print(o)
