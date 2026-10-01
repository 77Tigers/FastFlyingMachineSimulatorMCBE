"""Compare simulator state with the model's expected state at each slot start."""
import subprocess, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent


def expected(wd, k, T=(30, 30, 30)):
    lay = wd.lay; L = lay.L
    out = {}
    kk = k % L; cyc = k // L
    for b in lay.bodies:
        for c in wd.cells[b]:
            out[(c[0] + lay.off(b, k) + T[0], c[1] + T[1], c[2] + T[2])] = ('glue', b)
    for i, p in enumerate(wd.pist):
        x = p['traj'][kk] + cyc * lay.D
        out[(x + T[0], p['yz'][0] + T[1], p['yz'][1] + T[2])] = ('pist', i, p['kind'], p['f'])
    for j, sd in enumerate(wd.sources):
        b = sd['body']
        for key in ('cell', 'target'):
            if key in sd:
                c = sd[key]
                out[(c[0] + lay.off(b, k) + T[0], c[1] + T[1], c[2] + T[2])] = (key, j, b)
    return out


def actual(path, ticks):
    r = subprocess.run([str(HERE / 'bin' / 'dumpstate.exe'), str(path), str(ticks)], capture_output=True, text=True)
    st = defaultdict(dict)
    for line in r.stdout.split('\n'):
        if not line.strip(): continue
        t, x, y, z, kd = line.split()
        st[int(t)][(int(x), int(y), int(z))] = kd
    return st


def compare(wd, path, slots=12, T=None):
    st = actual(path, 2 * slots)
    if T is None:
        e0 = expected(wd, 0, (0, 0, 0)); a0 = [c for c, v in st[0].items()]
        T = tuple(min(c[a] for c in a0) - min(c[a] for c in e0) for a in range(3))
    for k in range(slots):
        exp = expected(wd, k, T)
        act = {c: v for c, v in st[2 * k].items() if v != '-'}
        miss = [(c, exp[c]) for c in exp if c not in act]
        extra = [(c, act[c]) for c in act if c not in exp]
        if miss or extra:
            print('slot', k, 'missing', len(miss), 'extra', len(extra))
            for m in miss[:12]: print('  miss', m)
            for e in extra[:12]: print('  extra', e)
            return k
    print('all', slots, 'slots match')
    return None
