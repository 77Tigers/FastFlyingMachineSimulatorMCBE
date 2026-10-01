"""Score a tm_smol-derived 3 bps flyer by real simulated loads.

python score.py FILE [FILE...]      (limit taken as 12; W0=100; one 10-tick period)

Prints: distance over 400 ticks (3 bps = 120), failures/conservation (from loadhist, 600 ticks),
all12 = actions with load >= 12 in one period, rear12 = those whose moved glue body contains a cell of the
original rear chain (tm_smol B9/B10/B11/B15/B18, start-file coordinates in REAR_CELLS), max load.
Progress = runs (distance 180/600, 0 failures, conserved), max <= 12, and rear12 < 8 (or all12 < 12 with rear12 <= 8).
Assumes the rear chain keeps its start-file coordinates (true for edits that leave those bodies in place).
"""
import sys, pathlib, subprocess, os, re
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner
BT = HERE.parent / 'bin' / 'human_bodytrack.exe'
LH = HERE / 'loadhist.exe'
REAR_CELLS = None


def rear_cells():
    bodies, _ = planner.parse(str(HERE / 'base.bodytrack.txt'))
    return {c for b in planner.REAR for c in bodies[b]['cells']}


def score(path, limit=12):
    global REAR_CELLS
    REAR_CELLS = REAR_CELLS or rear_cells()
    lh = subprocess.run([str(LH), '600', '100', str(limit), path], capture_output=True, text=True).stdout.splitlines()[1].split(',')
    env = dict(os.environ, BT_CELLS='1')
    out = subprocess.run([str(BT), path, '400', '100', '10', str(limit)], capture_output=True, text=True, env=env).stdout
    tmp = HERE / f'_bt_{os.getpid()}.txt'; tmp.write_text(out)
    try:
        bodies, ev = planner.parse(str(tmp))
    finally:
        tmp.unlink()
    rear = {b for b, d in bodies.items() if d['glue'] and set(d['cells']) & REAR_CELLS}
    all12 = rear12 = mx = 0
    for e in ev:
        if e['act'] == 'ext0': continue
        mx = max(mx, e['load'])
        if e['load'] >= limit:
            all12 += 1
            if any(b in rear for b, _ in e['moved']): rear12 += 1
    m = re.match(r'distance (\d+)', out)
    return dict(file=path, dist600=int(lh[1]), failures=int(lh[2]), conserved=lh[3] == 'true',
                all12=all12, rear12=rear12, max=mx, dist400=int(m[1]) if m else -1)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = score(p)
        ok = r['dist600'] >= 180 and r['failures'] == 0 and r['conserved'] and r['max'] <= 12
        prog = ok and (r['rear12'] < 8 or (r['all12'] < 12 and r['rear12'] <= 8))
        print(f"{pathlib.Path(p).name}: dist600={r['dist600']} fail={r['failures']} cons={r['conserved']} "
              f"all12={r['all12']} rear12={r['rear12']} max={r['max']} {'PROGRESS' if prog else ('runs' if ok else 'broken')}")
