"""Check the A/B rules on a simulated run.
A = honey bodies (only pulled), B = slime bodies (only pushed).
Every successful action: normal/sticky extension moving blocks must move slime glue only and the
acting piston must touch honey at tick start (anchor A, not the victim); sticky retraction moving
blocks must move honey only and the piston must touch slime (anchor B). Sticky extensions must be empty.
usage: abverify.py FLYER TICKS"""
import subprocess, sys, re
from pathlib import Path
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from fastflyer.research import binary
    return binary(n)
HERE = Path(__file__).resolve().parent
RUN = HERE.parents[3] / 'target' / 'release' / 'fastflyer-research.exe'
DIRS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def states(path, ticks):
    r = subprocess.run([str(_tb('ab-dumpstate')), str(path), str(ticks)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    st = {}
    for line in r.stdout.split('\n'):
        if not line.strip(): continue
        t, x, y, z, k = line.split(); st.setdefault(int(t), {})[(int(x), int(y), int(z))] = k
    return st


def main(path, ticks):
    st = states(path, ticks)
    r = subprocess.run([str(RUN), 'trace', str(path), '0', str(ticks)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    act = None; bad = 0; n = 0
    acts = []
    for line in r.stdout.split('\n'):
        m = re.match(r'ACTION Tick (\d+) · (extend|retract) @ \((-?\d+), (-?\d+), (-?\d+)\).*sources=(\d+) failure=(\S+)', line)
        if m:
            act = dict(t=int(m.group(1)), kind=m.group(2), p=tuple(int(m.group(i)) for i in (3, 4, 5)), n=int(m.group(6)), fail=m.group(7), src=[])
            acts.append(act); continue
        m = re.match(r'SOURCE Coord \{ x: (-?\d+), y: (-?\d+), z: (-?\d+) \} (\w+)', line)
        if m and act is not None:
            act['src'].append(m.group(4))
    probs = []
    for a in acts:
        if a['fail'] != 'None': probs.append(('fail', a['t'], a['kind'], a['p'])); continue
        if a['n'] == 0: continue
        n += 1
        glue = {k for k in a['src'] if k in ('Honey', 'Slime')}
        S = st.get(a['t'])
        touch = set()
        if S:
            for d in DIRS:
                q = (a['p'][0] + d[0], a['p'][1] + d[1], a['p'][2] + d[2])
                if S.get(q) in ('h', 's'): touch.add(S[q])
        if a['kind'] == 'extend':
            if glue != {'Slime'}: probs.append(('push-victim', a['t'], a['p'], glue))
            if 'h' not in touch: probs.append(('push-anchor', a['t'], a['p'], touch))
        else:
            if glue != {'Honey'}: probs.append(('pull-victim', a['t'], a['p'], glue))
            if 's' not in touch: probs.append(('pull-anchor', a['t'], a['p'], touch))
    print('actions', n, 'problems', len(probs))
    for p in probs[:10]: print('  ', p)
    return probs


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
