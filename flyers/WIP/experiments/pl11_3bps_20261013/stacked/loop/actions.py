import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "extract"))
import xlib as X
def actions(D, order="before_natural", rec="bounded", sample=(0,0,0), cyc=1):
    D = Path(D).resolve()
    c, rows = X.fixture_trace(D, order, rec, sample, 30)
    out = []
    for r in rows:
        if r['tick'] // 10 != cyc: continue
        for s in r['trace']['steps']:
            mv = s.get('movement')
            if s['action'] in ('extend','retract','prescribed move') and mv and mv.get('sources'):
                out.append((r['tick'] % 10, s['action'], tuple(s['active_piston']) if s.get('active_piston') else None, len(mv['sources'])))
    return out
if __name__ == "__main__":
    a = actions(sys.argv[1])
    print(sorted(a))
    print("max natural", max(x[3] for x in a if x[1] != 'prescribed move'), "count at 12:", sum(1 for x in a if x[3]==12 and x[1]!='prescribed move'), "prescribed", [x[3] for x in a if x[1]=='prescribed move'])
