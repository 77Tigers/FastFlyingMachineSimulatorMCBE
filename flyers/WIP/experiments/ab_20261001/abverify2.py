"""Label-free A/B check. Bodies = same-glue connected components, identified by shape (translation-free).
Every moving action must move exactly one body (plus non-glue riders). A body moved by an extension is
'B'; by a sticky retraction 'A'. A body may not be both. Every extension's piston must touch (at tick
start) a body labelled A (or later labelled A) other than its victim; every retraction's piston a body
labelled B. usage: abverify2.py FLYER TICKS"""
import subprocess, sys, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
RUN = HERE.parent / 'bin' / 'research_runner.exe'
DIRS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def states(path, ticks):
    r = subprocess.run([str(HERE / 'bin' / 'dumpstate.exe'), str(path), str(ticks)], capture_output=True, text=True)
    st = {}
    for line in r.stdout.split('\n'):
        if not line.strip(): continue
        t, x, y, z, k = line.split(); st.setdefault(int(t), {})[(int(x), int(y), int(z))] = k
    return st


def comps(S):
    seen = {}; out = []
    for c, k in S.items():
        if k not in 'hs' or c in seen: continue
        st = [c]; seen[c] = len(out); comp = [c]
        while st:
            u = st.pop()
            for d in DIRS:
                v = (u[0]+d[0], u[1]+d[1], u[2]+d[2])
                if S.get(v) == k and v not in seen: seen[v] = len(out); st.append(v); comp.append(v)
        out.append(comp)
    return out, seen


SHAPE_S = None


def shape(comp):
    mx = min(c[0] for c in comp); my = min(c[1] for c in comp); mz = min(c[2] for c in comp)
    return (SHAPE_S[comp[0]],) + tuple(sorted((c[0]-mx, c[1]-my, c[2]-mz) for c in comp))


def main(path, ticks):
    st = states(path, ticks)
    r = subprocess.run([str(RUN), 'trace', str(path), '0', str(ticks)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    acts = []; act = None
    for line in r.stdout.split('\n'):
        m = re.match(r'ACTION Tick (\d+) .{1,3} (extend|retract) @ \((-?\d+), (-?\d+), (-?\d+)\).*sources=(\d+) failure=(\S+)', line)
        if m:
            act = dict(t=int(m.group(1)), kind=m.group(2), p=tuple(int(m.group(i)) for i in (3, 4, 5)), n=int(m.group(6)), fail=m.group(7), src=[])
            acts.append(act); continue
        m = re.match(r'SOURCE Coord \{ x: (-?\d+), y: (-?\d+), z: (-?\d+) \} (\w+)', line)
        if m and act is not None:
            act['src'].append(((int(m.group(1)), int(m.group(2)), int(m.group(3))), m.group(4)))
    label = {}; probs = []; anchors = []
    for a in acts:
        if a['fail'] != 'None': probs.append(('fail', a['t'])); continue
        if a['n'] == 0: continue
        S = st[a['t']]
        global SHAPE_S
        SHAPE_S = S
        cs, idx = comps(S)
        vict = {idx[c] for c, k in a['src'] if c in idx}
        if len(vict) != 1: probs.append(('multi-victim', a['t'], a['p'], len(vict))); continue
        v = next(iter(vict)); sv = shape(cs[v])
        want = 'B' if a['kind'] == 'extend' else 'A'
        if label.get(sv, want) != want: probs.append(('both', a['t'], sv[:2]))
        label[sv] = want
        touch = set()
        for d in DIRS:
            q = (a['p'][0]+d[0], a['p'][1]+d[1], a['p'][2]+d[2])
            if q in idx and idx[q] != v: touch.add(shape(cs[idx[q]]))
        anchors.append((a['t'], a['kind'], touch))
    for t, kind, touch in anchors:
        need = 'A' if kind == 'extend' else 'B'
        if not any(label.get(s) == need for s in touch): probs.append(('anchor', t, kind, [label.get(s) for s in touch]))
    print('actions', len(anchors), 'bodies labelled', len(label), 'A', sum(1 for v in label.values() if v == 'A'), 'B', sum(1 for v in label.values() if v == 'B'), 'problems', len(probs))
    for p in probs[:8]: print('  ', p)
    return probs


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
