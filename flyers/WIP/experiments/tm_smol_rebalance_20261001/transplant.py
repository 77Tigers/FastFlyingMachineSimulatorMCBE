"""Extend a tm_smol sticky chain by one link (front re-lay, role-level construction).

python transplant.py OUTDIR [--chain=2]

Chain 2 of tm_smol: helper B45 (r4) powers B37's sticky (B37 r1) which pulls B35 (r3); B45's pushers B42-44 hop
between B45 and B37. Rotating every word by +3 slots maps (B35, B37, B45) -> (B37, B45, H): so "B45 pulls B37 at s3"
is the same relation one link further forward, with a new helper H (word wwmmm). Chain 1 is analogous:
(B29, B36, B41) -> (B36, B41, H) with B41 pulling B36 at s4.

Construction: the original relation as it stands at slot 2 (tick 104; new slot 0 = old slot 2 after the 3-slot
shift) is copied forward by a translation D:
  H      := helper glue/RB + its pushers (with piston states/arms from the tick-104 snapshot)
  puller := gains the old puller's sticky (+arm) and every old-puller cell touching/shoving the helper group
glue materials are swapped (slime<->honey) so neighbours keep contrasting materials, then the victim's old third pusher is removed, and the victim gets one contact cell if the new sticky would not
find its glue. D is scanned in a box (geometry detail only); static collisions are rejected; survivors are
simulated with score.py. Writes OUTDIR/D_dx_dy_dz.flyer and OUTDIR/results.txt.
"""
import sys, pathlib, itertools, subprocess
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
sys_argv = sys.argv; sys.argv = ['x']
import planner as P
sys.argv = sys_argv
from fastflyer import Flyer, Block, Kind
import score as S

CHAINS = {2: dict(victim=37, puller=45, helper_pushers=(42, 43, 44), old_puller=37, old_helper=45, drop=34, pull_slot=3),
          1: dict(victim=36, puller=41, helper_pushers=(38, 39, 40), old_puller=36, old_helper=41, drop=31, pull_slot=4)}
SNAP_DX = -2          # snapshot frame = base frame - 2 (measured at tick 100)


def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    ch = CHAINS[int(next((a.split('=')[1] for a in sys.argv if a.startswith('--chain=')), 2))]
    bodies, ev = P.parse(str(HERE / 'base.bodytrack.txt'))
    base = Flyer.load(HERE / 'base.flyer')
    bcells = {tuple(p): b for p, b in base.blocks()}
    snap = {tuple(p): b for p, b in Flyer.load(HERE / 'snaps' / 't104.flyer').blocks()}
    K = 2  # old slot copied to new slot 0

    def at(b, c, k): return P.sx(c, P.off(bodies[b]['word'], k))
    def snapcell(p):  # block at base-frame position p at tick 104
        return snap.get(P.sx(p, SNAP_DX))

    # ---- features at old slot 2, base frame ----
    helper_cells = {at(ch['old_helper'], c, K): snapcell(at(ch['old_helper'], c, K)) for c in bodies[ch['old_helper']]['cells']}
    pist = {}
    for pb in ch['helper_pushers']:
        c = list(bodies[pb]['cells'])[0]; p0 = at(pb, c, K)
        # hop timing makes the word-based position approximate: find the +X normal piston near it in the snapshot
        cand = [P.sx(p0, dx) for dx in (0, -1, -2, 1) if snapcell(P.sx(p0, dx)) is not None
                and snapcell(P.sx(p0, dx)).kind == Kind.PISTON and not snapcell(P.sx(p0, dx)).sticky]
        if not cand: print('pusher not found', pb); return
        p = cand[0]; blk = snapcell(p)
        pist[p] = blk
        if blk is not None and blk.kind == Kind.PISTON and blk.state in (1, 2, 3):
            arm = P.sx(p, 1)
            if snapcell(arm) is not None and snapcell(arm).kind == Kind.PISTON_ARM: pist[arm] = snapcell(arm)
    op = ch['old_puller']
    sticky = [c for c, k in bodies[op]['cells'].items() if k == 'S-x'][0]
    sp = at(op, sticky, K); feat_p = {sp: snapcell(sp)}
    if snapcell(P.sx(sp, -1)) is not None and snapcell(P.sx(sp, -1)).kind == Kind.PISTON_ARM:
        feat_p[P.sx(sp, -1)] = snapcell(P.sx(sp, -1))
    group = [(ch['old_helper'], c) for c in bodies[ch['old_helper']]['cells']] + \
            [(pb, list(bodies[pb]['cells'])[0]) for pb in ch['helper_pushers']]
    for c, kind in bodies[op]['cells'].items():
        if kind not in ('sl', 'ho'): continue
        touch = any(P.add(at(op, c, k), f) == at(b, g, k) for k in range(5) for f in P.FACES for b, g in group) or \
                any(P.add(c, f) == sticky for f in P.FACES)
        if touch: feat_p[at(op, c, K)] = snapcell(at(op, c, K))
    feat_h = dict(helper_cells); feat_h.update(pist)
    print('helper group cells', len(feat_h), 'puller features', len(feat_p))

    pul = ch['puller']; vic = ch['victim']
    pcells = set(bodies[pul]['cells'])
    results = []
    for D in itertools.product(range(-1, 6), range(-4, 5), range(-4, 5)):
        g = Flyer(base.phase_x, base.phase_z, base.rng_state, base.push_limit)
        for p, b in base.blocks(): g.set(p, b)
        drop = list(bodies[ch['drop']]['cells'])[0]
        g.remove(drop)
        cur = {tuple(p) for p, _ in g.blocks()}
        new = {}
        okk = True
        for src in (feat_h, feat_p):
            for p, blk in src.items():
                q = P.add(p, D)
                if blk is None: okk = False; break
                if q in cur:
                    if q in pcells and src is feat_p and blk.kind in (Kind.SLIME, Kind.HONEY): continue  # already glue
                    okk = False; break
                if blk.kind in (Kind.SLIME, Kind.HONEY):   # carry the material contrast one link forward
                    blk = Block(Kind.HONEY if blk.kind == Kind.SLIME else Kind.SLIME)
                new[q] = blk
            if not okk: break
        if not okk: continue
        # every added puller glue cell must be glue-connected to the puller (allow one connector per island)
        hset = {P.add(p, D) for p in feat_h}
        pmat = Kind.SLIME if 'sl' in bodies[pul]['cells'].values() else Kind.HONEY
        pglue = {c for c, k in bodies[pul]['cells'].items() if k in ('sl', 'ho')}
        addg = {q for q, b in new.items() if q not in hset and b.kind in (Kind.SLIME, Kind.HONEY)}
        def comp_ok(cells):
            seen = set(pglue); todo = list(pglue)
            while todo:
                x = todo.pop()
                for f in P.FACES:
                    y = P.add(x, f)
                    if y in cells and y not in seen: seen.add(y); todo.append(y)
            return cells <= seen
        if not comp_ok(addg | pglue):
            fixed = False
            occ0 = cur | set(new)
            for q in sorted(addg):
                for f in P.FACES:
                    y = P.add(q, f)
                    if y in occ0: continue
                    if comp_ok(addg | pglue | {y}):
                        new[y] = Block(pmat); addg.add(y); fixed = True; break
                if fixed: break
            if not fixed: continue
        # the sticky itself must touch puller glue (old or added)
        snew0 = P.add(sp, D)
        if not any(P.add(snew0, f) in (pglue | addg) for f in P.FACES if f != (-1, 0, 0)): continue
        for q, blk in new.items(): g.set(q, blk)
        snew = P.add(sp, D)                                   # new sticky, base frame of the puller
        wpul, wvic = bodies[pul]['word'], bodies[vic]['word']
        k = ch['pull_slot']
        need = P.sx(P.sx(snew, P.off(wpul, k) - 2), -P.off(wvic, k))   # victim base cell the sticky must grab
        vcells = bodies[vic]['cells']; vmat = Kind.HONEY if 'ho' in vcells.values() else Kind.SLIME
        vk = 'ho' if vmat == Kind.HONEY else 'sl'
        extra = []
        if vcells.get(need) not in ('sl', 'ho'):
            if need in cur or need in new: continue
            if not any(vcells.get(P.add(need, f)) == vk for f in P.FACES):
                link = [P.add(need, f) for f in P.FACES if P.add(need, f) not in cur and P.add(need, f) not in new
                        and P.add(need, f) != P.sx(need, 1)
                        and any(vcells.get(P.add(P.add(need, f), h)) == vk for h in P.FACES)]
                if not link: continue
                extra.append(link[0])
            extra.append(need)
        for q in extra: g.set(q, Block(vmat))
        name = f'D_{D[0]}_{D[1]}_{D[2]}_v{len(extra)}'
        g.save(out / f'{name}.flyer')
        results.append(name)
    print(len(results), 'static-valid translations; simulating')
    lines = []
    for name in results:
        r = S.score(str(out / f'{name}.flyer'))
        lines.append((r['dist600'], -r['rear12'], name, r))
    lines.sort(reverse=True)
    with open(out / 'results.txt', 'w') as fh:
        for d, _, name, r in lines:
            fh.write(f"{name} dist600={r['dist600']} fail={r['failures']} cons={r['conserved']} all12={r['all12']} rear12={r['rear12']} max={r['max']}\n")
    for d, _, name, r in lines[:12]:
        print(name, r)


if __name__ == '__main__':
    main()
