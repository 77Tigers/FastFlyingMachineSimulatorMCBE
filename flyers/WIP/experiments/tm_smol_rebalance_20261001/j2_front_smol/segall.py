"""segall.py FILE: every glue segment back->front (mean x): word, cells, max load of actions moving it, #pushes, #pulls."""
import sys, os, subprocess, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']
import score as S, planner
sys.argv = argv
from fastflyer import Flyer
for path in argv[1:]:
    lim = Flyer.load(path).push_limit
    out = subprocess.run([str(S.BT), path, '400', '100', '10', str(lim)], capture_output=True, text=True,
                         env=dict(os.environ, BT_CELLS='1')).stdout
    tmp = HERE / f'_bt_{os.getpid()}.txt'; tmp.write_text(out)
    try: bodies, ev = planner.parse(str(tmp))
    finally: tmp.unlink()
    glue = {b: d for b, d in bodies.items() if d['glue']}
    st = {b: [0, 0, 0] for b in glue}
    for e in ev:
        if e['act'] == 'ext0': continue
        g = [(n, b) for b, n in e['moved'] if b in glue]
        if not g: continue
        b = max(g)[1]; st[b][0] = max(st[b][0], e['load'])
        st[b][1 if 'pull' not in e['act'] else 2] += 1
    order = sorted(glue, key=lambda b: sum(c[0] for c in glue[b]['cells']) / len(glue[b]['cells']))
    print(f"{pathlib.Path(path).name} PL{lim}")
    for b in order:
        mx = sum(c[0] for c in glue[b]['cells']) / len(glue[b]['cells'])
        print(f"  B{b:<3} x~{mx:5.1f} {glue[b]['word']} cells {len(glue[b]['cells']):2d} maxload {st[b][0]:2d} push {st[b][1]} pull {st[b][2]}")
