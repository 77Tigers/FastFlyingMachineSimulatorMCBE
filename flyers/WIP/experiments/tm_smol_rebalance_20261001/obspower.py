"""Replace helper-helper power by victim-observer power in a human 3 bps flyer (role-level change).

python obspower.py OUTDIR [--conn=1] [--max=6]

Default target: bank/pl12/human_3bps_original.flyer (orig.flyer here, bodytrack orig.bodytrack.txt, snapshots
snaps_orig/t100..t108). Its five front pullers (B41,B48,B42,B43,B56) have -X stickies powered at the extension slot
by tiny helpers (B55,B64,B65,B66,B69) whose 15 pushers ride the front pullers. Victim-observer principle: the victim
of a pull on its last move s moved at s-2, so an observer on the victim pulses at s-1 = the extension slot; at its
other pulses the victim has moved relative to the resting puller. So: delete the helpers and their pushers, add one
observer (+<=conn glue) on each victim, facing the sticky from a side or hard-powering a puller glue cell beside it.

Placement checks per slot start (exact occupancy from the tick snapshots, removed blocks excluded): free cell, held
by victim glue, not dragged by foreign moving glue, no shoves, other pulses power no piston. Candidates are
combined (one option per pull), built from the tick-100 snapshot, and scored (loadhist, score metrics).
"""
import sys, pathlib, itertools, collections, re, random
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
argv = sys.argv; sys.argv = ['x']
import planner as P
sys.argv = argv
from fastflyer import Flyer, Block, Kind
import subprocess
DBG = collections.Counter()

FACES = P.FACES; add = P.add; sx = P.sx
BT = HERE / 'orig.bodytrack.txt'; SNAPS = HERE / 'snaps_orig'; BASE = HERE / 'orig.flyer'
HELPERS = [int(x) for x in next((a.split('=')[1] for a in sys.argv if a.startswith('--helpers=')), '55,64,65,66,69').split(',')]
LH = HERE / 'loadhist.exe'


KMAP = {'sl': Kind.SLIME, 'ho': Kind.HONEY, 'RB': Kind.REDSTONE_BLOCK}


def snap_dx(bodies, snap0):
    """Shift that maps snapshot coordinates into the bodytrack (start-file) frame (kind-matched vote)."""
    votes = collections.Counter()
    for b, d in bodies.items():
        if not d['glue']: continue
        for c, k in d['cells'].items():
            if k not in KMAP: continue
            for dx in range(-40, 40):
                q = sx(c, dx)
                if q in snap0 and snap0[q].kind == KMAP[k]: votes[dx] += 1
    return -votes.most_common(1)[0][0]


def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    opt = {x.split('=')[0][2:]: int(x.split('=')[1]) for x in sys.argv[2:] if x.startswith('--') and ',' not in x and 'helpers' not in x}
    conn = opt.get('conn', 1); kmax = opt.get('max', 6)
    bodies, ev = P.parse(str(BT))
    table = P.loads_table(bodies, ev)
    raw = [{tuple(p): b for p, b in Flyer.load(SNAPS / f't{100+2*k}.flyer').blocks()} for k in range(5)]
    dx = snap_dx(bodies, raw[0])
    snaps = [{sx(p, dx): b for p, b in r.items()} for r in raw]   # into bodytrack (start-file) frame
    print('snapshot frame dx', dx)
    # per-body correction: bodytrack cells can be off by a cell for bodies whose start transient differs
    fixed = 0
    for b, d in bodies.items():
        if not d['glue']: continue
        best = max(range(-3, 4), key=lambda c: sum(1 for p, k in d['cells'].items() if k in KMAP
                   and snaps[0].get(sx(p, c)) is not None and snaps[0][sx(p, c)].kind == KMAP[k]))
        if best:
            d['cells'] = {sx(p, best): k for p, k in d['cells'].items()}; fixed += 1
    print('bodies re-aligned to the snapshot:', fixed)
    def at(b, c, k): return sx(c, P.off(bodies[b]['word'], k))
    def moves(b, k): return bodies[b]['word'][k % 5] == 'm'
    # helper pushers: actors/riders of helper moves
    hp = set()
    for m in table:
        if m['victim'] in HELPERS: hp.add(m['actor']); hp.update(m['riders'])
    hp -= set(HELPERS)
    def real_piston(pb, k):
        p0 = at(pb, list(bodies[pb]['cells'])[0], k)
        for d in (0, -1, -2, 1, 2):
            b = snaps[k].get(sx(p0, d))
            if b is not None and b.kind == Kind.PISTON and not b.sticky: return sx(p0, d)
    removed = []   # per slot: set of removed positions (helper glue/RB + helper pushers + their arms)
    for k in range(5):
        r = set()
        for h in HELPERS:
            for c in bodies[h]['cells']: r.add(at(h, c, k))
        for pb in hp:
            p = real_piston(pb, k)
            if p is None: continue
            r.add(p)
            if snaps[k][p].state in (1, 2, 3) and snaps[k].get(sx(p, 1)) is not None and snaps[k][sx(p, 1)].kind == Kind.PISTON_ARM:
                r.add(sx(p, 1))
        removed.append(r)
    own = []
    for k in range(5):
        o = {}
        for b, d in bodies.items():
            if d['glue']:
                for c, kind in d['cells'].items(): o[at(b, c, k)] = (b, kind)
        occ = {}
        for p, blk in snaps[k].items():
            if p in removed[k]: continue
            occ[p] = o.get(p, (None, 'P' if blk.kind in (Kind.PISTON, Kind.PISTON_ARM) else blk.kind.name))
        own.append(occ)
    # existing pulls by the front pullers whose power came from a helper
    pulls = []
    for l in open(BT).read().splitlines():
        m = re.match(r'\s+s(\d) B(\d+)\(([^|]*)\|([^)]*)\) (\w+)', l)
        if m and m[5] == 'ext0' and m[4].strip().lstrip('B').isdigit() and int(m[4].strip().lstrip('B')) in HELPERS:
            F = int(m[2]); e = int(m[1])
            pm = [mv for mv in table if mv['actor'] == F and mv['kind'] == 'pull']
            pulls.append((F, pm[0]['victim'], (e + 1) % 5, e))
    print('helper-powered pulls (puller, victim, pull slot, ext slot):', pulls)

    def free(b, x, kind, new):
        for k in range(5):
            a = at(b, x, k)
            if a in own[k]: return False
            if any(at(b2, x2, k) == a for (b2, x2) in new): return False
            bm = moves(b, k)
            for f in FACES:
                q = own[k].get(add(a, f))
                if q is None or q[0] == b: continue
                Q, qk = q; qm = Q is not None and moves(Q, k)
                if qm and not bm and qk in ('sl', 'ho') and (P.sticks(qk, kind) if kind in ('sl', 'ho') else True): return False
                if bm and not qm and kind in ('sl', 'ho') and (Q is None or P.sticks(kind, qk)): return False
                if f == (-1, 0, 0) and qm and not bm: return False
                if f == (1, 0, 0) and bm and not qm: return False
        return True

    options = {}
    for F, V, s, e in pulls:
        stick = [c for c, k in bodies[F]['cells'].items() if k == 'S-x'][0]
        vk = 'sl' if 'sl' in bodies[V]['cells'].values() else 'ho'
        pulses = [(k + 1) % 5 for k in range(5) if moves(V, k)]
        opts = []
        if e not in pulses: print('victim does not pulse at ext slot', F, V); continue
        s_abs = at(F, stick, e)
        targets = [s_abs] + [at(F, add(stick, f), e) for f in FACES if f != (-1, 0, 0) and bodies[F]['cells'].get(add(stick, f)) in ('sl', 'ho')]
        for t in targets:
            for d in range(6):
                dv = FACES[d]
                oa = add(t, (-dv[0], -dv[1], -dv[2]))
                if t == s_abs and oa == sx(s_abs, -1): continue
                o = sx(oa, -P.off(bodies[V]['word'], e))
                if o in bodies[V]['cells']: DBG[(F,'in victim')]+=1; continue
                if not free(V, o, 'O', {}): DBG[(F,'not free')]+=1; continue
                bad = False
                for k in pulses:
                    tt = add(at(V, o, k), dv); tk = own[k].get(tt, (None, None))[1]
                    if k == e:
                        if tt != s_abs and any(own[k].get(add(tt, f), (0, None))[1] in ('P', 'S-x') and add(tt, f) != s_abs for f in FACES): bad = True
                        continue
                    if tk in ('P', 'S-x'): bad = True
                    if tk in ('sl', 'ho', 'RB', 'GLASS', 'STONE', 'GLAZED_TERRACOTTA') and any(own[k].get(add(tt, f), (0, None))[1] in ('P', 'S-x') for f in FACES): bad = True
                if bad: DBG[(F,'pulse powers piston')]+=1; continue
                # attach to victim glue (observer is non-glue: any adjacent victim glue holds it)
                path = None
                vc = bodies[V]['cells']
                if any(vc.get(add(o, f)) in ('sl', 'ho') for f in FACES): path = []
                else:
                    frontier = [[]]
                    for n in range(conn):
                        nxt = []
                        for pth in frontier:
                            last = pth[-1] if pth else o
                            for f in FACES:
                                y = add(last, f)
                                if y in vc or y == o or y in pth: continue
                                nw = {(V, o): 'O'}; nw.update({(V, z): vk for z in pth})
                                if not free(V, y, vk, nw): continue
                                if any(P.sticks(vk, vc.get(add(y, g))) for g in FACES): path = pth + [y]; break
                                nxt.append(pth + [y])
                            if path is not None: break
                        if path is not None: break
                        frontier = nxt
                if path is None: DBG[(F,'no support')]+=1; continue
                opts.append(dict(F=F, V=V, o=o, d=d, path=path, via='direct' if t == s_abs else 'solid', cost=1 + len(path)))
        print('   reasons', {k[1]: v for k, v in DBG.items() if k[0] == F})
        opts.sort(key=lambda r: r['cost'])
        options[(F, V)] = opts[:kmax]
        print(f'B{F} pulls B{V} @s{s} (ext s{e}): {len(opts)} observer options; best cost',
              [o_['cost'] for o_ in opts[:kmax]])
    if any(not v for v in options.values()): print('some pull has no option');
    # build combinations from the tick-100 snapshot
    base = Flyer.load(SNAPS / 't100.flyer')
    start = {sx(tuple(p), dx): b for p, b in base.blocks()}
    for p in removed[0]: start.pop(p, None)
    keys = [k for k in options if options[k]]
    combos = list(itertools.product(*[range(len(options[k])) for k in keys]))
    random.seed(0); random.shuffle(combos); combos = combos[:300]
    files = []
    for ci, combo in enumerate(combos):
        g = Flyer(base.phase_x, base.phase_z, base.rng_state, 12)
        cells = dict(start); clash = False
        for k, i in zip(keys, combo):
            op = options[k][i]; V = op['V']
            vk = Kind.SLIME if 'sl' in bodies[V]['cells'].values() else Kind.HONEY
            if op['o'] in cells: clash = True
            cells[op['o']] = Block.observer(op['d'])
            for y in op['path']:
                if y in cells: clash = True
                cells[y] = Block(vk)
        if clash: continue
        for p, b in cells.items(): g.set(p, b)
        f = out / f'c{ci:04d}.flyer'; g.save(f); files.append(str(f))
    print(len(files), 'combinations built; screening')
    res = []
    for i in range(0, len(files), 40):
        p = subprocess.run([str(LH), '600', '100', '12'] + files[i:i+40], capture_output=True, text=True)
        res += [l.split(',') for l in p.stdout.splitlines()[1:]]
    res.sort(key=lambda r: (-int(r[1]), int(r[2])))
    with open(out / 'results.csv', 'w') as fh:
        fh.write('name,distance,failures,conserved,max_load,n_at_limit,n_at_limit_m1,hist\n')
        for r in res: fh.write(','.join(r) + '\n')
    for r in res[:10]: print(r)


if __name__ == '__main__':
    main()
