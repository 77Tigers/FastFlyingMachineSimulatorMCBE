"""score2.py FILE...: like ../score.py but simulates at each file's encoded push limit and reports, per load level
>= 12, the number of actions (all / rear) in one 10-tick period.  Rear = glue bodies sharing a cell with tm_smol's
rear chain (start-file coords, as in score.py)."""
import sys, os, re, subprocess, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']
import score as S, planner
sys.argv = argv
from fastflyer import Flyer

DX = 0
def score2(path):
    lim = Flyer.load(path).push_limit
    S.REAR_CELLS = S.REAR_CELLS or {(c[0] + DX, c[1], c[2]) for c in S.rear_cells()}
    lh = subprocess.run([str(S.LH), '600', '100', str(lim), path], capture_output=True, text=True).stdout.splitlines()[1].split(',')
    env = dict(os.environ, BT_CELLS='1')
    out = subprocess.run([str(S.BT), path, '400', '100', '10', str(lim)], capture_output=True, text=True, env=env).stdout
    tmp = HERE / f'_bt_{os.getpid()}.txt'; tmp.write_text(out)
    try: bodies, ev = planner.parse(str(tmp))
    finally: tmp.unlink()
    rear = {b for b, d in bodies.items() if d['glue'] and set(d['cells']) & S.REAR_CELLS}
    cnt = {}
    for e in ev:
        if e['act'] == 'ext0' or e['load'] < 12: continue
        r = any(b in rear for b, _ in e['moved'])
        a, rr = cnt.get(e['load'], (0, 0)); cnt[e['load']] = (a + 1, rr + r)
    lv = ' '.join(f"L{k}:{a}/{r}" for k, (a, r) in sorted(cnt.items()))
    print(f"{pathlib.Path(path).name}: PL{lim} dist600={lh[1]} fail={lh[2]} cons={lh[3]} loads(all/rear) {lv}")

for p in sys.argv[1:]:
    if p.startswith('--dx='): DX = int(p[5:]); continue
    score2(p)
