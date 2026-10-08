"""Score 3bps_original-derived candidates: dist, failures, all12, rear12 (rear = bodies containing an
orig rear cell, ../orig_rear_cells.txt), per-rear-body move loads, max load.
python oscore.py [--lim=N] FILE...   (lim = load threshold counted as '12'; default 12; flyer limit taken from --run=)
"""
import sys, pathlib, subprocess, os, re
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
    from fastflyer.research import binary
    return binary(n)
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
argv = sys.argv; sys.argv = ['x']; import planner; sys.argv = argv
BT = _tb('bodytrack')
LH = _tb('loadhist')
REAR = {tuple(int(v) for v in l.split(',')) for l in open(HERE.parent / 'orig_rear_cells.txt').read().split()}

def score(path, run=12, thr=12, w0=100):
    lh = subprocess.run([str(LH), '600', str(w0), str(run), path], capture_output=True, text=True).stdout.splitlines()[1].split(',')
    env = dict(os.environ, BT_CELLS='1')
    out = subprocess.run([str(BT), path, '400', str(w0), '10', str(run)], capture_output=True, text=True, env=env).stdout
    tmp = HERE / f'_bt_{os.getpid()}.txt'; tmp.write_text(out)
    try: bodies, ev = planner.parse(str(tmp))
    finally: tmp.unlink()
    rear = {b for b, d in bodies.items() if d['glue'] and set(d['cells']) & REAR}
    all12 = rear12 = mx = rmx = 0; rl = {}
    for e in ev:
        if e['act'] == 'ext0': continue
        mx = max(mx, e['load'])
        isr = any(b in rear for b, _ in e['moved'])
        if isr:
            rmx = max(rmx, e['load'])
            v = [b for b, _ in e['moved'] if b in rear][0]; rl.setdefault(v, []).append(e['load'])
        if e['load'] >= thr:
            all12 += 1; rear12 += isr
    m = re.match(r'distance (\d+)', out)
    return dict(dist600=int(lh[1]), fail=int(lh[2]), cons=lh[3] == 'true', all12=all12, rear12=rear12, max=mx,
                rearmax=rmx, rl={k: sorted(v) for k, v in rl.items()}, nrear=len(rear))

if __name__ == '__main__':
    run = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--run=')), 12))
    thr = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--thr=')), 12))
    for p in [a for a in sys.argv[1:] if not a.startswith('--')]:
        r = score(p, run, thr)
        print(pathlib.Path(p).name, r)
