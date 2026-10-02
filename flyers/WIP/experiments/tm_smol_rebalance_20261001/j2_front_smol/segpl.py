"""segpl.py [--dx=N] FILE...: per glue segment (back->front by x), the max load of the actions that move it."""
import sys, os, subprocess, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']
import score as S, planner
sys.argv = argv
from fastflyer import Flyer
DX = 0
for path in sys.argv[1:]:
    if path.startswith('--dx='): DX = int(path[5:]); continue
    lim = Flyer.load(path).push_limit
    rc = {(c[0] + DX, c[1], c[2]) for c in S.rear_cells()}
    out = subprocess.run([str(S.BT), path, '400', '100', '10', str(lim)], capture_output=True, text=True,
                         env=dict(os.environ, BT_CELLS='1')).stdout
    tmp = HERE / f'_bt_{os.getpid()}.txt'; tmp.write_text(out)
    try: bodies, ev = planner.parse(str(tmp))
    finally: tmp.unlink()
    glue = {b: d for b, d in bodies.items() if d['glue']}
    mx = {}
    for e in ev:
        if e['act'] == 'ext0': continue
        g = [(n, b) for b, n in e['moved'] if b in glue]
        if not g: continue
        b = max(g)[1]; mx[b] = max(mx.get(b, 0), e['load'])
    order = sorted(glue, key=lambda b: sum(c[0] for c in glue[b]['cells']) / len(glue[b]['cells']))
    rear = [b for b in order if set(glue[b]['cells']) & rc]
    front = [b for b in order if b not in rear]
    print(f"{pathlib.Path(path).name} (PL{lim}): back {[mx.get(b) for b in rear]}  front {[mx.get(b) for b in front]}")
