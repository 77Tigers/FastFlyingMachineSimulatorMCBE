"""Generalized generator for two-body A/B 2.5 bps flyers (see gen25.py for the lifecycle).

Power modes:
  obs : A observer (pulses after A moves = odd slots) hard-powers A glue H adjacent to P1,Q2.
  rs  : redstone block carried by B, adjacent to P1,Q2 at B-rel 0 (start of slot 1); B moves in
        that slot so power ends; symmetric copy for G3.
Carry: A glue adjacent to P1 and Q2 at A-rel 0; B glue adjacent to P1,Q2 at B-rel -1.
Usage: gen25b.py OUTDIR MAXLOAD
"""
import sys, itertools, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen25 import (DIRS, E, W, OFF, add, sx, nb, make_R, steiner, world_items, forbidden_for, box)
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind


def opts_cover(a, b, forb):
    """carry-cell options: common neighbour or one neighbour each."""
    na = [c for c in nb(a) if c not in forb]
    nbb = [c for c in nb(b) if c not in forb]
    common = [[c] for c in set(na) & set(nbb)]
    return common + [[x, y] for x in na for y in nbb if x != y]


def piston_world(spec, s):
    out = {}
    for c, t in spec['G1']: out[sx(c, OFF['G1'][s])] = 'G1'
    for c, t in spec['G3']: out[sx(c, OFF['G3'][s])] = 'G3'
    return out


def power_ok(spec, sources_by_slot):
    """sources_by_slot[s] = set of world cells that soft-power adjacent pistons at slot start s."""
    want = {0: 'G1', 2: 'G3'}
    for s in range(4):
        pw = piston_world(spec, s)
        hit = set()
        for src in sources_by_slot[s]:
            for n in nb(src):
                if n in pw: hit.add((n, pw[n]))
        groups = {g for _, g in hit}
        if s in want:
            # all members of wanted group powered, nothing else
            need = {c for c, g in pw.items() if g == want[s]}
            if {c for c, _ in hit} != need: return False
        elif hit:
            return False
    return True


def gen(outdir, maxload, only=None):
    outdir = Path(outdir); outdir.mkdir(exist_ok=True)
    P1 = (0, 0, 0)
    syms = []
    for c in range(-3, 4): syms += [('mz', c, 0), ('my', c, 0)]
    for c1 in range(-3, 4):
        for c2 in range(-3, 4): syms.append(('rot', c1, c2))
    for c1 in range(-2, 3): syms.append(('diag', c1, 0))
    rows = []; seen = set(); n = 0
    for Q2 in itertools.product((-1, 0, 1), (-2, -1, 0, 1, 2), (-2, -1, 0, 1, 2)):
        if Q2 == (0, 0, 0): continue
        if only is not None and Q2 != only: continue
        for (kind, c1, c2) in syms:
            R = make_R(kind, c1, c2)
            G1, G3, occ = world_items(P1, Q2, R)
            okp = True
            for s in range(4):
                cells = [sx(c, OFF['G1'][s]) for c, _ in G1] + [sx(c, OFF['G3'][s]) for c, _ in G3]
                if len(set(cells)) < 4: okp = False
            if not okp: continue
            fA = forbidden_for('A', occ); fB = forbidden_for('B', occ)
            D1 = sx(P1, 1); C2 = sx(Q2, -2); D3 = R(D1); C0 = R(C2)
            if D1 in fB or D3 in fB or C2 in fA or C0 in fA or D1 == C2: continue
            spec = dict(G1=G1, G3=G3)
            # ---- power choices
            pchoices = []
            for H in set(nb(P1)) & set(nb(Q2)):
                if H in fA: continue
                for od in range(6):
                    O = add(H, DIRS[od])
                    if O in fA or R(O) in fA: continue
                    pchoices.append(('obs', H, O, od ^ 1))
            for Rs in set(nb(P1)) & set(nb(Q2)):
                if Rs in fB: continue
                pchoices.append(('rs', Rs, None, None))
            for pc in pchoices:
                mode = pc[0]
                if mode == 'obs':
                    H, O, od = pc[1], pc[2], pc[3]
                    obs = {O, R(O)}
                    srcs = [set() for _ in range(4)]
                    # observer pulse at S1 and S3 (after A moves); hard-powered H acts as source
                    srcs[0] = {sx(h, OFF['A'][0]) for h in {H, R(H)}}
                    srcs[2] = {sx(h, OFF['A'][2]) for h in {H, R(H)}}
                    if not power_ok(spec, srcs): continue
                    Aextra = [H, R(H)]; Anon = obs; Bnon = set()
                else:
                    Rs = pc[1]; Bnon = {Rs, R(Rs)}
                    if len(Bnon) < 2 and False: continue
                    srcs = [{sx(r, OFF['B'][s]) for r in Bnon} for s in range(4)]
                    if not power_ok(spec, srcs): continue
                    Aextra = []; Anon = set()
                # ---- A body
                fA2 = set(fA) | Anon | Bnon_A(Bnon)
                bestA = None
                for cov in opts_cover(P1, Q2, fA2):
                    terms = list(dict.fromkeys([C2, C0] + Aextra + cov + [R(c) for c in cov]))
                    if any(t in fA2 for t in terms): continue
                    if len(terms) > 6 or len(terms) + len(Anon) + 2 > maxload: continue
                    if mode == 'obs' and not any(o in set(nb(H)) for o in [O]): continue
                    allowed = set(box(terms + [P1, Q2], 2)) - fA2
                    t = steiner(terms, allowed)
                    if t is None: continue
                    Aset = t | {R(c) for c in t}
                    if Aset & fA2: continue
                    if bestA is None or len(Aset) < len(bestA): bestA = Aset
                if bestA is None: continue
                loadA = len(bestA) + len(Anon) + 2
                if loadA > maxload: continue
                # ---- B body: forbidden = A collision lines, adhesion hazards
                fB2 = set(fB) | Bnon
                for a in list(bestA) + list(Anon):
                    fB2.add(a); fB2.add(sx(a, -1))
                for si in (0, 2):
                    bad = [sx(o, OFF['A'][si]) for o in Anon]
                    grp = spec['G1'] if si == 0 else spec['G3']
                    bad += [sx(c, OFF['G1' if si == 0 else 'G3'][si]) for c, t in grp if t == 'Q']
                    for w in bad:
                        for nn in nb(w): fB2.add(sx(nn, -OFF['B'][si]))
                # A glue must not touch B redstone while A moves (S2, S0)
                if mode == 'rs':
                    bad_hz = False
                    for si in (1, 3):
                        aw = {sx(c, OFF['A'][si]) for c in bestA}
                        for r in Bnon:
                            rw = sx(r, OFF['B'][si])
                            if any(x in aw for x in nb(rw)): bad_hz = True
                    if bad_hz: continue
                bestB = None
                holders = [[None]] if mode == 'obs' else [[h, R(h)] for h in nb(Rs) if h not in fB2]
                for cov in opts_cover(sx(P1, -1), sx(Q2, -1), fB2):
                    for hold in holders:
                        terms = [D1, D3] + cov + [R(c) for c in cov] + [h for h in hold if h is not None]
                        terms = list(dict.fromkeys(terms))
                        if any(t in fB2 for t in terms): continue
                        if len(terms) > 6 or len(terms) + len(Bnon) + 2 > maxload: continue
                        allowed = set(box(terms + [P1, Q2], 2)) - fB2
                        t = steiner(terms, allowed)
                        if t is None: continue
                        Bset = t | {R(c) for c in t}
                        if Bset & fB2: continue
                        if bestB is None or len(Bset) < len(bestB): bestB = Bset
                if bestB is None: continue
                loadB = len(bestB) + len(Bnon) + 2
                if max(loadA, loadB) > maxload: continue
                key = (frozenset(bestA), frozenset(bestB), frozenset(Anon), frozenset(Bnon))
                if key in seen: continue
                seen.add(key)
                f = Flyer(rng_state=5, push_limit=40)
                for c in bestA: f.set(c, Block(Kind.HONEY))
                for c in bestB: f.set(c, Block(Kind.SLIME))
                for c, t in G1 + G3:
                    f.set(c, Block.piston(E) if t == 'P' else Block.piston(W, sticky=True))
                if mode == 'obs':
                    tgt = add(O, DIRS[od]); f.set(O, Block.observer(od, powered=True))
                    Ro, Rt = R(O), R(tgt)
                    f.set(Ro, Block.observer(DIRS.index((Rt[0] - Ro[0], Rt[1] - Ro[1], Rt[2] - Ro[2])), powered=True))
                else:
                    for r in Bnon: f.set(r, Block(Kind.REDSTONE_BLOCK))
                f.translate(20, 20, 20)
                name = 'q%d_%d_%d_c%04d' % (Q2[0], Q2[1], Q2[2], n)
                f.save(outdir / f'{name}.flyer')
                rows.append(dict(name=name, Q2=Q2, sym=[kind, c1, c2], mode=mode, loadA=loadA, loadB=loadB))
                n += 1
        print('Q2', Q2, 'n', n, flush=True)
    tag = '' if only is None else '_%d_%d_%d' % only
    (outdir / ('manifest%s.json' % tag)).write_text(json.dumps(rows, indent=1))


def Bnon_A(Bnon):
    return set(Bnon) | {sx(r, 1) for r in Bnon}


def _one(args):
    gen(*args)


if __name__ == '__main__':
    from multiprocessing import Pool
    qs = [q for q in itertools.product((-1, 0, 1), (-2, -1, 0, 1, 2), (-2, -1, 0, 1, 2)) if q != (0, 0, 0)]
    with Pool(5) as pool:
        pool.map(_one, [(sys.argv[1], int(sys.argv[2]), q) for q in qs], chunksize=1)
