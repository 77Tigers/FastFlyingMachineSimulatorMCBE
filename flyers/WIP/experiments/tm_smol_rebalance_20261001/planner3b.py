"""Pull planner v3: victim-observer power, exact snapshot occupancy.
# planner3b = planner3 + (a) new cells of different bodies are checked for adhesion/contact with each other when
# exactly one of them moves (fixes observer dragged by a new puller connector); (b) env NOBAD=1 skips the
# "other observer pulses power no piston" check. Agent J2-front, 2026-10-02.

python planner3.py PULLER VICTIM SLOT [--conn=1] [--oconn=1] [--vconn=1] [--max=40]

Idea: for a pull on the victim's last move s, the victim moved at s-2, so its OWN observer pulses at slot s-1 start,
exactly when the puller's -X sticky must extend; at s and s+1 the victim has moved relative to the (resting) puller,
so a fixed observer no longer powers the sticky. No helper/RB needed; cost +1 observer (+support) on the victim.
The observer either faces the sticky from a side, or hard-powers a puller glue cell adjacent to the sticky.

Occupancy per slot start comes from the tick-100..108 snapshots (exact for that run, incl. hopping pushers/arms);
glue bodies are identified with the bodytrack model. Checks for every new cell (sticky, connectors, observer,
observer support, victim contact): free at all 5 slot starts, not dragged by foreign moving glue, no shoves, observer
pulses at other slots power no piston. Prints options with their added cell counts (puller, victim).
Use plan_options() from other scripts.
"""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
argv = sys.argv; sys.argv = ['x']
import planner as P
sys.argv = argv
from fastflyer import Flyer, Kind

FACES = P.FACES; add = P.add; sx = P.sx
SNAP_DX = -2
import os
NOBAD = bool(os.environ.get('NOBAD'))
_bodies = None; _occ = None


def load_state():
    global _bodies, _occ
    if _bodies is None:
        _bodies, _ = P.parse(str(HERE / 'base.bodytrack.txt'))
        _occ = []
        for k in range(5):
            snap = {sx(tuple(p), -SNAP_DX): b for p, b in Flyer.load(HERE / 'snaps' / f't{100+2*k}.flyer').blocks()}
            own = {}
            for b, d in _bodies.items():
                if not d['glue']: continue
                for c, kind in d['cells'].items(): own[sx(c, P.off(d['word'], k))] = (b, kind)
            occ = {}
            for p, blk in snap.items():
                if p in own: occ[p] = own[p]
                else: occ[p] = (None, 'P' if blk.kind in (Kind.PISTON, Kind.PISTON_ARM) else blk.kind.name)
            _occ.append(occ)
    return _bodies, _occ


def moves(b, k):
    return _bodies[b]['word'][k % 5] == 'm'


def ab(b, x, k): return sx(x, P.off(_bodies[b]['word'], k))


def is_glue(kind): return kind in ('sl', 'ho')


def cell_ok(b, x, kind, new, ignore=()):
    """new cell `kind` ('sl','ho','S','O') carried by body b at base-frame x. new: {(body,x): kind} already placed."""
    for k in range(5):
        a = ab(b, x, k)
        if a in _occ[k] and a not in ignore: return False
        for (b2, x2), k2 in new.items():
            if ab(b2, x2, k) == a: return False
            if b2 != b and moves(b2, k) != moves(b, k) and (is_glue(k2) or is_glue(kind)):
                if any(add(a, f) == ab(b2, x2, k) for f in FACES):
                    if not (is_glue(k2) and is_glue(kind) and not P.sticks(kind, k2)): return False
        bm = moves(b, k)
        for f in FACES:
            q = add(a, f)
            o = _occ[k].get(q)
            if o is None: continue
            Q, qk = o
            if Q == b: continue
            qm = (Q is not None and moves(Q, k))
            if qm and not bm and is_glue(qk) and (P.sticks(qk, kind) if is_glue(kind) else True): return False
            if bm and not qm and is_glue(kind) and Q is not None and P.sticks(kind, qk): return False
            if bm and not qm and is_glue(kind) and Q is None: return False   # would carry a piston/arm
            if f == (-1, 0, 0) and qm and not bm: return False
            if f == (1, 0, 0) and bm and not qm: return False
    return True


def path_to(b, x0, kind, new, maxn, glue_kind):
    """<=maxn glue cells (glue_kind) linking new cell x0 on body b to b's glue. Returns list or None."""
    cells = _bodies[b]['cells']
    def touches(x, kd): return any(is_glue(cells.get(add(x, f))) and (P.sticks(kd, cells[add(x, f)]) if is_glue(kd) else True) for f in FACES)
    if touches(x0, kind): return []
    frontier = [[]]
    for n in range(maxn):
        nxt = []
        for path in frontier:
            last = path[-1] if path else x0
            for f in FACES:
                y = add(last, f)
                if y in cells or y == x0 or y in path: continue
                nn = dict(new); nn.update({(b, p): glue_kind for p in path})
                if not cell_ok(b, y, glue_kind, nn): continue
                if touches(y, glue_kind): return path + [y]
                nxt.append(path + [y])
        frontier = nxt
    return None


def plan_options(Pb, V, s, conn=1, oconn=1, vconn=1, limit=40, hosts=None):
    bodies, occ = load_state()
    pk = 'sl' if 'sl' in bodies[Pb]['cells'].values() else 'ho'
    vk = 'sl' if 'sl' in bodies[V]['cells'].values() else 'ho'
    sm1 = (s - 1) % 5
    out = []
    vglue = [c for c, k in bodies[V]['cells'].items() if is_glue(k)]
    # contact cells: existing victim glue, or one new victim glue cell next to it
    contacts = [(c, []) for c in vglue]
    if vconn:
        for c in vglue:
            for f in FACES:
                y = add(c, f)
                if y not in bodies[V]['cells']: contacts.append((y, [y]))
    seen = set()
    for vc, vnew in contacts:
        # sticky abs at slot s = victim cell abs + 2x ; puller base frame:
        sabs = sx(ab(V, vc, s), 2)
        c = sx(sabs, -P.off(bodies[Pb]['word'], s))
        if (c, tuple(vnew)) in seen: continue
        seen.add((c, tuple(vnew)))
        new = {}
        ok = True
        for y in vnew:
            if not cell_ok(V, y, vk, new): ok = False; break
            new[(V, y)] = vk
        if not ok or c in bodies[Pb]['cells']: continue
        if not cell_ok(Pb, c, 'S', new): continue
        # arm cell free at s-1 start
        arm = ab(Pb, sx(c, -1), sm1)
        if arm in occ[sm1] or any(ab(b2, x2, sm1) == arm for (b2, x2) in new): continue
        new[(Pb, c)] = 'S'
        pp = path_to(Pb, c, 'S', new, conn, pk)
        if pp is None: continue
        for y in pp: new[(Pb, y)] = pk
        sticky_abs = ab(Pb, c, sm1)
        targets = [sticky_abs]   # direct (side) or via an adjacent puller glue cell (hard-powered solid)
        for f in FACES:
            if f == (-1, 0, 0): continue
            g = add(c, f)
            if bodies[Pb]['cells'].get(g) in ('sl', 'ho') or new.get((Pb, g)) == pk: targets.append(ab(Pb, g, sm1))
        for Q in (hosts or [b for b in bodies if bodies[b]['glue'] and b != Pb]):
            pulses = [(k + 1) % 5 for k in range(5) if moves(Q, k)]
            if sm1 not in pulses: continue
            qk = 'sl' if 'sl' in bodies[Q]['cells'].values() else 'ho'
            for t in targets:
                for d in FACES:
                    oabs = add(t, (-d[0], -d[1], -d[2]))
                    if t == sticky_abs and oabs == sx(sticky_abs, -1): continue    # sticky ignores its front
                    o = sx(oabs, -P.off(bodies[Q]['word'], sm1))
                    if (Q, o) in new or o in bodies[Q]['cells']: continue
                    if not cell_ok(Q, o, 'O', new): continue
                    # other pulses must not power any piston (directly or via a hard-powered solid)
                    bad = False
                    for k in pulses:
                        oa = ab(Q, o, k); tt = add(oa, d)
                        tk = occ[k].get(tt)
                        newk = {ab(b2, x2, k): kd for (b2, x2), kd in new.items()}
                        tkind = newk.get(tt, tk[1] if tk else None)
                        if k == sm1 and tt == t:
                            # still must not power other pistons via the solid
                            if tt != sticky_abs:
                                for f in FACES:
                                    n = add(tt, f)
                                    if n == sticky_abs: continue
                                    nk = newk.get(n, occ[k].get(n, (0, None))[1])
                                    if nk in ('P', 'S-x', 'S'): bad = True
                            continue
                        if tkind in ('P', 'S-x', 'S'): bad = True; break
                        if tkind in ('sl', 'ho', 'RB'):
                            for f in FACES:
                                n = add(tt, f)
                                nk = newk.get(n, occ[k].get(n, (0, None))[1])
                                if nk in ('P', 'S-x', 'S'): bad = True; break
                        if bad: break
                    if bad and not NOBAD: continue
                    nn = dict(new); nn[(Q, o)] = 'O'
                    op = path_to(Q, o, 'O', nn, oconn, qk)
                    if op is None: continue
                    for y in op: nn[(Q, y)] = qk
                    cost = {}
                    for (b2, _) in nn: cost[b2] = cost.get(b2, 0) + 1
                    out.append(dict(P=Pb, V=V, s=s, Q=Q, sticky=c, obs=o, obs_dir=d, cells=nn, cost=cost,
                                    costP=cost.get(Pb, 0), costV=cost.get(V, 0),
                                    via='direct' if t == sticky_abs else 'solid'))
                    if len(out) >= limit: return out
    return out


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    opt = {x.split('=')[0][2:]: int(x.split('=')[1]) for x in sys.argv[1:] if x.startswith('--')}
    res = plan_options(int(a[0]), int(a[1]), int(a[2]), conn=opt.get('conn', 1), oconn=opt.get('oconn', 1),
                       vconn=opt.get('vconn', 1), limit=opt.get('max', 40))
    res.sort(key=lambda r: sum(r['cost'].values()))
    print(len(res), 'options')
    for r in res[:15]:
        print(f"host B{r['Q']} cost {r['cost']} sticky {r['sticky']} obs {r['obs']} dir {r['obs_dir']} {r['via']} cells {sorted((f'B{b}', x, k) for (b, x), k in r['cells'].items())}")
