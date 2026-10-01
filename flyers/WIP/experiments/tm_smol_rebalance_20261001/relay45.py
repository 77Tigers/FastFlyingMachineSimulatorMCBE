"""Front re-lay: B45 becomes a B37-shaped puller (pulls B37 at s3), a new helper H (B45-shaped) powers it.

python relay45.py OUTDIR

Isomorphism (rotate words by 3 slots, translate by T=(2,0,0) from old slot 2 to new slot 0):
  B37 -> B45new, B45 -> H, B32-34 -> B42-44 (already in place: B42-44 at slot 0 == B32-34 at slot 2 + T).
Free details searched here (everything else is copied):
  1. extra RB on B45new that powers B37's own sticky only at s4 (old B45 did this);
  2. B37 contact protrusion (<=2 honey cells) so B45new's sticky grabs B37 at s3;
  3. B34 (B37's s3 pusher) removed.
Writes OUTDIR/*.flyer and OUTDIR/results.txt (score.py metrics).
"""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
argv = sys.argv; sys.argv = ['x']
import planner as P
sys.argv = argv
from fastflyer import Flyer, Block, Kind
import score as S

T = (2, 0, 0); K = 2; SNAP_DX = -2


def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    bodies, _ = P.parse(str(HERE / 'base.bodytrack.txt'))
    # start from the tick-100 snapshot (same run as the copied tick-104 relation; pusher layout is not exactly periodic)
    base = Flyer.load(HERE / 'snaps' / 't100.flyer'); B = {P.sx(tuple(p), -SNAP_DX): b for p, b in base.blocks()}
    snaps = [{P.sx(tuple(p), -SNAP_DX): b for p, b in Flyer.load(HERE / 'snaps' / f't{100+2*k}.flyer').blocks()} for k in range(5)]
    def at(b, c, k): return P.sx(c, P.off(bodies[b]['word'], k))
    def real_piston(pb, k):
        p0 = at(pb, list(bodies[pb]['cells'])[0], k)
        for dx in (0, -1, -2, 1):
            b = snaps[k].get(P.sx(p0, dx))
            if b is not None and b.kind == Kind.PISTON and not b.sticky: return P.sx(p0, dx)
    swap = lambda k: Kind.HONEY if k == Kind.SLIME else Kind.SLIME

    # remove old B45 body and B34 (+ arms of removed extended pistons)
    g0 = {p: b for p, b in B.items()}
    for c in bodies[45]['cells']: g0.pop(c, None)
    b34 = [P.sx(list(bodies[34]['cells'])[0], dx) for dx in (0, -1, -2, 1)]
    b34 = [p for p in b34 if p in g0 and g0[p].kind == Kind.PISTON and not g0[p].sticky][0]
    if g0[b34].state in (1, 2, 3): g0.pop(P.sx(b34, 1), None)
    g0.pop(b34)
    # B45new = B37 at old slot 2 + T, materials swapped, sticky state from the tick-104 snapshot
    b45new = {}
    for c in bodies[37]['cells']:
        p = at(37, c, K); blk = snaps[K][p]
        q = P.add(p, T)
        b45new[q] = Block(swap(blk.kind)) if blk.kind in (Kind.SLIME, Kind.HONEY) else blk
        if blk.kind == Kind.PISTON and blk.state in (1, 2, 3): b45new[P.sx(q, -1)] = snaps[K][P.sx(p, -1)]
    # H = B45 at old slot 2 + T (swapped) + its pushers B42-44 at old slot 2 + T (states/arms copied)
    H = {}
    for c in bodies[45]['cells']:
        p = at(45, c, K); blk = snaps[K][p]
        H[P.add(p, T)] = Block(swap(blk.kind)) if blk.kind in (Kind.SLIME, Kind.HONEY) else blk
    for pb in (42, 43, 44):
        p = real_piston(pb, K); blk = snaps[K][p]; H[P.add(p, T)] = blk
        if blk.state in (1, 2, 3) and snaps[K].get(P.sx(p, 1)) is not None: H[P.add(P.sx(p, 1), T)] = snaps[K][P.sx(p, 1)]
    clash = [q for q in list(b45new) + list(H) if q in g0]
    print('B45new', len(b45new), 'H', len(H), 'static clashes with kept blocks:', clash)

    # 1. extra RB on B45new powering B37's sticky at s4 only (B37 sticky base (12,3,2))
    s37 = [c for c, k in bodies[37]['cells'].items() if k == 'S-x'][0]
    def s37_at(k): return at(37, s37, k)
    w45 = bodies[45]['word']   # B45new keeps B45's word (mmwwm)
    rb_opts = []
    for f in P.FACES:
        if f == (-1, 0, 0): continue
        r_abs4 = P.add(s37_at(4), f)
        r = P.sx(r_abs4, -P.off(w45, 4))        # B45new base frame
        if r in g0 or r in b45new or r in H: continue
        if any(P.add(P.sx(r, P.off(w45, k)), h) == s37_at(k) for k in (0, 1, 2, 3) for h in P.FACES): continue
        slime = lambda x: b45new.get(x) is not None and b45new[x].kind == Kind.SLIME
        if any(slime(P.add(r, h)) for h in P.FACES): rb_opts.append((r, None)); continue
        for h in P.FACES:
            cn = P.add(r, h)
            if cn in g0 or cn in b45new or cn in H: continue
            if any(slime(P.add(cn, h2)) for h2 in P.FACES): rb_opts.append((r, cn))
    print('power RB options', rb_opts)

    # 2. B37 contact: new sticky (B45new) grabs B37 at s3
    snew = [q for q, b in b45new.items() if b.kind == Kind.PISTON and b.sticky][0]
    need = P.sx(P.sx(snew, P.off(w45, 3) - 2), -P.off(bodies[37]['word'], 3))
    print('new sticky', snew, 'B37 contact cell needed (base)', need)
    v37 = {c for c, k in bodies[37]['cells'].items() if k == 'ho'}
    contacts = []
    if need in v37: contacts = [[]]
    else:
        occ = set(g0) | set(b45new) | set(H)
        if need not in occ:
            if any(P.add(need, f) in v37 for f in P.FACES): contacts.append([need])
            for f in P.FACES:
                y = P.add(need, f)
                if y in occ or y == P.sx(need, 1): continue
                if any(P.add(y, h) in v37 for h in P.FACES): contacts.append([need, y])
    print('contact options', contacts)

    rows = []
    for i, ((r, cn), con) in enumerate(itertools.product(rb_opts or [(None, None)], contacts)):
        g = Flyer(base.phase_x, base.phase_z, base.rng_state, 12)
        for p, b in g0.items(): g.set(p, b)
        for p, b in b45new.items(): g.set(p, b)
        for p, b in H.items(): g.set(p, b)
        if r is not None: g.set(r, Block(Kind.REDSTONE_BLOCK))
        if cn is not None: g.set(cn, Block(Kind.SLIME))
        for c in con: g.set(c, Block(Kind.HONEY))
        name = f'r{i}_rb{"x" if r is None else "_".join(map(str, r))}_c{len(con)}'
        g.save(out / f'{name}.flyer')
        res = S.score(str(out / f'{name}.flyer'))
        rows.append((res['dist600'], name, res))
    rows.sort(reverse=True)
    with open(out / 'results.txt', 'w') as fh:
        for d, name, res in rows: fh.write(f'{name} {res}\n')
    for d, name, res in rows[:10]: print(name, res)


if __name__ == '__main__':
    main()
