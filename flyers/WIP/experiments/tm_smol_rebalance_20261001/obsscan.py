"""Simulator-guided placement of victim observers (after obspower.py proved the mechanism).

python obsscan.py OUTDIR HELPERS(comma) [--support=2] [--limit=12]

Starts from obspower's helper-free start (tick-100 snapshot of 3bps_original minus the given helpers and their
pushers), and for each helper-powered pull (puller F, victim V, ext slot e) enumerates observer cells o (+facing)
that at slot e face F's sticky from a side or hard-power an F glue cell beside it, with <= support victim-material
glue cells linking o to V glue. Only the start state is checked statically (empty cells); the simulator judges the
rest. Variants are screened with loadhist at LIMIT (600 ticks) and at 16; ranked by distance then load.
Single-pull variants first (one helper replaced), written to OUTDIR/<F>_<i>.flyer, results in OUTDIR/results.csv.
"""
import sys, pathlib, itertools, subprocess
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
argv = sys.argv; sys.argv = ['x']
import planner as P
sys.argv = argv
import obspower as O
from fastflyer import Flyer, Block, Kind

FACES = P.FACES; add = P.add; sx = P.sx


def setup(helpers):
    O.HELPERS[:] = helpers
    bodies, ev = P.parse(str(O.BT)); table = P.loads_table(bodies, ev)
    raw = [{tuple(p): b for p, b in Flyer.load(O.SNAPS / f't{100+2*k}.flyer').blocks()} for k in range(5)]
    dx = O.snap_dx(bodies, raw[0]); snaps = [{sx(p, dx): b for p, b in r.items()} for r in raw]
    for b, d in bodies.items():
        if not d['glue']: continue
        best = max(range(-3, 4), key=lambda c: sum(1 for p, k in d['cells'].items() if k in O.KMAP
                   and snaps[0].get(sx(p, c)) is not None and snaps[0][sx(p, c)].kind == O.KMAP[k]))
        if best: d['cells'] = {sx(p, best): k for p, k in d['cells'].items()}
    def at(b, c, k): return sx(c, P.off(bodies[b]['word'], k))
    hp = set()
    for m in table:
        if m['victim'] in helpers: hp.add(m['actor']); hp.update(m['riders'])
    hp -= set(helpers)
    def real_piston(pb, k):
        p0 = at(pb, list(bodies[pb]['cells'])[0], k)
        for d in (0, -1, -2, 1, 2):
            b = snaps[k].get(sx(p0, d))
            if b is not None and b.kind == Kind.PISTON and not b.sticky: return sx(p0, d)
    rem = set()
    for h in helpers:
        for c in bodies[h]['cells']: rem.add(at(h, c, 0))
    for pb in hp:
        p = real_piston(pb, 0)
        if p is None: continue
        rem.add(p)
        if snaps[0][p].state in (1, 2, 3) and snaps[0].get(sx(p, 1)) is not None and snaps[0][sx(p, 1)].kind == Kind.PISTON_ARM:
            rem.add(sx(p, 1))
    start = {p: b for p, b in snaps[0].items() if p not in rem}
    pulls = []
    import re
    for l in open(O.BT).read().splitlines():
        m = re.match(r'\s+s(\d) B(\d+)\(([^|]*)\|([^)]*)\) (\w+)', l)
        if m and m[5] == 'ext0' and m[4].strip().lstrip('B').isdigit() and int(m[4].strip().lstrip('B')) in helpers:
            F = int(m[2]); e = int(m[1])
            pm = [mv for mv in table if mv['actor'] == F and mv['kind'] == 'pull']
            pulls.append((F, pm[0]['victim'], (e + 1) % 5, e))
    base = Flyer.load(O.SNAPS / 't100.flyer')
    return bodies, at, start, pulls, base


def options(bodies, at, start, F, V, e, support):
    stick = [c for c, k in bodies[F]['cells'].items() if k == 'S-x'][0]
    vk = 'sl' if 'sl' in bodies[V]['cells'].values() else 'ho'
    vmat = Kind.SLIME if vk == 'sl' else Kind.HONEY
    dv_e = P.off(bodies[V]['word'], e) - P.off(bodies[F]['word'], e)   # V-frame -> F-frame X shift at slot e
    # positions in the START (slot 0) frame: V cells are at base, F cells at base; at slot e V is shifted by off_V(e)
    s_e = at(F, stick, e)
    fk = Kind.SLIME if 'sl' in bodies[F]['cells'].values() else Kind.HONEY
    targets = [(s_e, None)]
    for f in FACES:
        if f == (-1, 0, 0): continue
        g = add(stick, f)
        if bodies[F]['cells'].get(g) in ('sl', 'ho'): targets.append((at(F, g, e), None))
        elif g not in start and g not in bodies[F]['cells']:
            # one new puller glue cell beside the sticky (hard-powered by the observer); must touch F glue
            if any(bodies[F]['cells'].get(add(g, h)) in ('sl', 'ho') for h in FACES): targets.append((at(F, g, e), g))
    vcells = {c for c, k in bodies[V]['cells'].items() if k in ('sl', 'ho')}
    out = []
    for t, newg in targets:
        for d in range(6):
            dv = FACES[d]
            oa = add(t, (-dv[0], -dv[1], -dv[2]))
            if t == s_e and oa == sx(s_e, -1): continue
            o = sx(oa, -P.off(bodies[V]['word'], e))            # V base frame == start frame for V
            if o in start or o in bodies[V]['cells'] or o == newg: continue
            # support paths (<= support cells) from o to V glue, empty in the start state
            paths = [[]] if any(add(o, f) in vcells for f in FACES) else []
            frontier = [[]]
            for n in range(support):
                nxt = []
                for pth in frontier:
                    last = pth[-1] if pth else o
                    for f in FACES:
                        y = add(last, f)
                        if y in start or y == o or y in pth or y in bodies[V]['cells']: continue
                        npth = pth + [y]
                        if any(add(y, g) in vcells for g in FACES): paths.append(npth)
                        nxt.append(npth)
                frontier = nxt
            for pth in paths[:6]:
                if newg is not None and newg in pth: continue
                out.append(dict(o=o, d=d, path=pth, mat=vmat, cost=1 + len(pth) + (newg is not None),
                                newg=newg, fmat=fk))
    out.sort(key=lambda r: r['cost'])
    return out


def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    helpers = [int(x) for x in sys.argv[2].split(',')]
    opt = {x.split('=')[0][2:]: int(x.split('=')[1]) for x in sys.argv[3:] if x.startswith('--')}
    support = opt.get('support', 2); limit = opt.get('limit', 12); delF = opt.get('delF', 0)
    bodies, at, start, pulls, base = setup(helpers)
    files = []
    allopts = {}
    for F, V, s, e in pulls:
        fg = sorted(c for c, k in bodies[F]['cells'].items() if k in ('sl', 'ho'))
        ops = []
        for n in range(delF + 1):
            for dels in itertools.combinations(fg, n):
                st = {p: b for p, b in start.items() if p not in dels}
                saved = dict(bodies[F]['cells'])
                for c in dels: bodies[F]['cells'].pop(c)
                for op in options(bodies, at, st, F, V, e, support):
                    op['dels'] = dels; ops.append(op)
                bodies[F]['cells'] = saved
        ops.sort(key=lambda r: r['cost'] - len(r['dels']))
        allopts[F] = ops
        print(f'B{F} pulls B{V} @s{s}: {len(ops)} raw placements (delF<={delF})', flush=True)
    keys = list(allopts)
    combos = [()]
    for F in keys:
        combos = [c + ((F, i),) for c in combos for i in range(min(len(allopts[F]), 600 if len(keys) == 1 else 8))]
    import random; random.seed(1); random.shuffle(combos); combos = combos[:600]
    for ci, combo in enumerate(combos):
        cells = dict(start); clash = False
        for F, i in combo:
            op = allopts[F][i]
            for c in op.get('dels', ()): cells.pop(c, None)
            if op['o'] in cells: clash = True; break
            cells[op['o']] = Block.observer(op['d'])
            for y in op['path']:
                if y in cells: clash = True
                cells[y] = Block(op['mat'])
            if op.get('newg') is not None:
                if op['newg'] in cells: clash = True
                cells[op['newg']] = Block(op['fmat'])
        if clash: continue
        g = Flyer(base.phase_x, base.phase_z, base.rng_state, limit)
        for p, b in cells.items(): g.set(p, b)
        name = '_'.join(f'{F}-{i}' for F, i in combo)
        f = out / f'{name}.flyer'; g.save(f); files.append(str(f))
    print(len(files), 'variants; screening at', limit, flush=True)
    res = []
    from concurrent.futures import ThreadPoolExecutor
    chunks = [files[i::6] for i in range(6)]
    def run(ch):
        if not ch: return []
        p = subprocess.run([str(O.LH), '600', '100', str(limit)] + ch, capture_output=True, text=True)
        return [l.split(',') for l in p.stdout.splitlines()[1:]]
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(run, chunks): res += r
    res.sort(key=lambda r: (-int(r[1]), int(r[2]), int(r[4]), int(r[5])))
    with open(out / 'results.csv', 'w') as fh:
        fh.write('name,distance,failures,conserved,max_load,n_at_limit,n_at_limit_m1,hist\n')
        for r in res: fh.write(','.join(r) + '\n')
    for r in res[:10]: print(r)


if __name__ == '__main__':
    main()
