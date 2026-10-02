"""seg2.py [--dx=N] FILE: per glue segment back->front: id, cells, word, loads of its moves (kind:load) and riders."""
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
    glue = {b: d for b, d in bodies.items() if d['glue'] and d['cells']}
    mv = {}
    for e in ev:
        if e['act'] == 'ext0': continue
        g = [(n, b) for b, n in e['moved'] if b in glue]
        if not g: continue
        b = max(g)[1]
        mv.setdefault(b, []).append(f"s{e['s']}{e['act'][:2]}{e['load']}(B{e['actor']}:" + ','.join(f'B{x}' for x, n in e['moved'] if x != b) + ')')
    rear = {b for b in glue if set(glue[b]['cells']) & rc}
    fpush = set(); fpushn = 0; fpull = 0; fpullback = 0; actors = {}
    for e in ev:
        if e['act'] == 'ext0': continue
        g = [(n, b) for b, n in e['moved'] if b in glue]
        if not g: continue
        v = max(g)[1]
        if e['act'] == 'push' and v not in rear: fpushn += 1; fpush.add(e['actor'])
        if e['act'] == 'pull':
            pb = [b for b in glue if e['actor'] == b]
            if e['actor'] in glue and e['actor'] not in rear:
                fpull += 1; fpullback += v in rear
    print(f"front-seg pushes/period={fpushn} distinct pushers={len(fpush)}; pulls by front pullers={fpull} (of rear victims {fpullback})")
    order = sorted(glue, key=lambda b: sum(c[0] for c in glue[b]['cells']) / len(glue[b]['cells']))
    print(pathlib.Path(path).name, 'PL', lim)
    for b in order:
        print(('R ' if set(glue[b]['cells']) & rc else '  ') + f"B{b} n={len(glue[b]['cells'])} {glue[b]['word']} " + ' '.join(sorted(mv.get(b, []))))
