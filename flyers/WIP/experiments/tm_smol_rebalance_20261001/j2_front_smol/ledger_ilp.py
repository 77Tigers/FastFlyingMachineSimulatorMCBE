"""ledger_ilp.py BT_FILE [rear bodies...]: build the layered.py role model from any bodytrack output (BT_CELLS=1),
validate it (real kinds + real carrier graph must reproduce the simulated per-segment max loads), then solve the
per-segment objective with free kinds on the directed gap-2 graph (+ real edges), K=2, at caps 12/13/14."""
import sys, re, pathlib
sys.argv, ARGS = sys.argv[:1], sys.argv[1:]
import layered as LY

def parse(path):
    hdr, acts = {}, []
    for line in open(path):
        m = re.match(r'\s*(B\d+): n=(\d+) .*?S=(\d+) word=(\w+)(?: box x(\d+)-(\d+) y(\d+)-(\d+) z(\d+)-(\d+))?', line)
        if m and 'piston]' not in line:
            hdr[m[1]] = dict(n=int(m[2]), S=int(m[3]), word=m[4], box=[int(v) for v in m.groups()[4:]] if m[5] else None)
        m = re.match(r'\s*s(\d) (B\d+)\((.*?)\) (push|pull)\s+(\d+)\s+->\s*(.*)', line)
        if m:
            moved = [(b, int(n)) for b, n in re.findall(r'(B\d+)x(\d+)', m[6])]
            acts.append(dict(s=int(m[1]), actor=m[2], kind=m[4], load=int(m[5]), moved=moved))
    return hdr, acts

def build(path):
    hdr, acts = parse(path)
    glue = {b for b, h in hdr.items() if h['box']}
    bodies = {b: (hdr[b]['word'], hdr[b]['n'] - hdr[b]['S']) for b in glue}
    kinds, target, allow = {}, {}, {b: set() for b in glue}
    for a in acts:
        T = max((n, b) for b, n in a['moved'] if b in glue)[1]
        kinds[(T, a['s'])] = a['kind']
        if a['kind'] == 'push': target[a['actor']] = T
        else: allow[T].add(a['actor'])
    for a in acts:
        C = max((n, b) for b, n in a['moved'] if b in glue)[1]
        for b, n in a['moved']:
            if b in target and target[b] != C: allow[target[b]].add(C)
    real = {}
    for a in acts:
        T = max((n, b) for b, n in a['moved'] if b in glue)[1]; real[T] = max(real.get(T, 0), a['load'])
    return bodies, kinds, allow, real, hdr

def order(bodies, hdr):
    return sorted(bodies, key=lambda b: (hdr[b]['box'][0] + hdr[b]['box'][1]) / 2)

if __name__ == '__main__':
    path = ARGS[0]; FIX = [a[4:] for a in ARGS if a.startswith('fix=')]; rear = [a for a in ARGS[1:] if not a.startswith('fix=')]
    bodies, kinds, allow, real, hdr = build(path)
    od = order(bodies, hdr)
    missing = [(b, s) for b in bodies for s in range(5) if bodies[b][0][s] == 'm' and (b, s) not in kinds]
    print('bodies', len(bodies), 'missing kinds', missing)
    print('real  ', [real.get(b) for b in od])
    r = LY.solve(bodies, kinds, rear, allow=allow, cap=20, excess=True)
    segs = lambda r: [max(v for (n, t), v in r['loads'].items() if n == b) for b in od]
    print('model ', segs(r) if r else 'INFEASIBLE', '(real kinds+graph; should match real)')
    DG = {}
    bx = {b: hdr[b]['box'] for b in bodies}
    def dist(a, b): return max(max(a[2*i] - b[2*i+1], b[2*i] - a[2*i+1], 0) for i in range(3))
    for V in bodies:
        NG = {d for d in bodies if d != V and dist(bx[V], bx[d]) <= 2}
        DG[(V, 'pull')] = {d for d in NG if bx[d][1] >= bx[V][1]} | allow[V]
        DG[(V, 'push')] = {d for d in NG if bx[d][0] <= bx[V][1] - 1} | allow[V]
    fix = {k: v for k, v in kinds.items() if k[0] in FIX}
    for cap in (12, 13, 14):
        r = LY.solve(bodies, fix or None, rear, allow=DG, K=2, cap=cap, excess=True, seg=True, front_push_cost=40,
                     time_limit=120, ref_kinds=kinds, ref_allow=allow, c_kind=5, c_edge=3)
        if r is None: print(f'cap{cap}: INFEASIBLE'); continue
        flips = [f'{k[0]}s{k[1]}{k[2]}' for k in r['kinds'] if kinds[(k[0], k[1])] != k[2]]
        fp = sum(1 for k in r['kinds'] if k[0] not in rear and k[2] == 'push')
        print(f'cap{cap}: segs {segs(r)} frontpushers {fp} flips {flips}')
    print('order', od)

def subsets(path, rear, flips, cap=14):
    import itertools
    bodies, kinds, allow, real, hdr = build(path)
    od = order(bodies, hdr)
    bx = {b: hdr[b]['box'] for b in bodies}
    def dist(a, b): return max(max(a[2*i] - b[2*i+1], b[2*i] - a[2*i+1], 0) for i in range(3))
    DG = {}
    for V in bodies:
        NG = {d for d in bodies if d != V and dist(bx[V], bx[d]) <= 2}
        DG[(V, 'pull')] = {d for d in NG if bx[d][1] >= bx[V][1]} | allow[V]
        DG[(V, 'push')] = {d for d in NG if bx[d][0] <= bx[V][1] - 1} | allow[V]
    out = []
    for n in range(len(flips) + 1):
        for sub in itertools.combinations(flips, n):
            kk = dict(kinds)
            for (b, s, k) in sub: kk[(b, s)] = k
            r = LY.solve(bodies, kk, rear, allow=DG, K=2, cap=cap, excess=True, seg=True, time_limit=60, ref_allow=allow, c_edge=3)
            if r is None: continue
            segs = {b: max(v for (nn, t), v in r['loads'].items() if nn == b) for b in od}
            n11 = sum(1 for b in rear[:5] if segs[b] <= 11)
            out.append((n11, -n, sub, [segs[b] for b in od]))
    out.sort(key=lambda x: (-x[0], -x[1]))
    for o in out[:12]: print(o[0], 'back@11 with', -o[1], 'flips', [f'{b}s{s}{k}' for b, s, k in o[2]], o[3])

if __name__ == '__main__' and False: pass
