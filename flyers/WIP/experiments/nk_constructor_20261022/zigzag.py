"""All-turn ring: every link is a 90-degree turn (no straight links, which cost ~3 more connector cells).
Square of 4 sides; side i = n_i zigzag pairs (left, right) then one left corner; opposite sides equal -> closes.
Left link: next body rotated +90 at offset cvL (in the current heading frame); right link: rotated -90 at cvR.
L = 4*(n1 + n2 + 1).  python zigzag.py K1,K2 [-v]"""
import sys, time
import construct, square, sqbuild
from nk import Timing, Ring, SYMS, bodies_for


def ring_size(k):
    L0 = bodies_for(k); L = L0
    while L % 4: L += L0
    return L


def turns(L):
    n = L // 4 - 1; n1 = (n + 1) // 2; n2 = n - n1
    seq = []
    for side in range(4):
        seq += ['L', 'R'] * (n1 if side % 2 == 0 else n2) + ['L']
    assert len(seq) == L
    return seq


def layout(L, cvL, cvR):
    place = []; p = (0, 0); h = 0
    for t in turns(L):
        place.append((0, p, h))
        v = cvL if t == 'L' else cvR
        d = SYMS[h](*v); p = (p[0] + d[0], p[1] + d[1])
        h = (h + (1 if t == 'L' else 3)) % 4
    return place, p, h


def make(k, mod, cvL, cvR):
    L = ring_size(k); T = Timing(k, L)
    place, p, h = layout(L, cvL, cvR)
    if p != (0, 0) or h != 0: return None
    return Ring(T, [mod] * L, place)


def hard_ok(r, bodies):
    for s in range(r.T.S):
        occ = r.world(s, bodies=bodies)
        for c, lst in occ.items():
            if len({e[0] for e in lst}) > 1: return False
    return True


def search(k, fam='latcp', verbose=False):
    mod = construct.grid_module(k, fam); a, b = mod['size']
    L = ring_size(k)
    seq = turns(L)
    iL = seq.index('L'); iR = seq.index('R') if 'R' in seq else None
    reps = [(iL + 1) % L] + ([(iR + 1) % L] if iR is not None else [])   # bodies whose incoming link is L / R
    rng = range(-2, max(a, b) + 4)
    scored = []
    for cvL in [(x, y) for x in rng for y in rng]:
        for cvR in ([(x, y) for x in rng for y in range(-(max(a, b) + 3), 3)] if iR is not None else [(0, 0)]):
            r = make(k, mod, cvL, cvR)
            if r is None: continue
            near = sorted({(X + d) % L for X in reps for d in range(-2, 3)})
            if not hard_ok(r, near): continue
            r.active = near
            try:
                for X in reps: r.route(X)
            except RuntimeError:
                continue
            scored.append((max(r.size()[X] for X in reps), cvL, cvR))
    scored.sort()
    for c, cvL, cvR in scored[:30]:
        r = make(k, mod, cvL, cvR)
        try:
            for X in range(L): r.route(X)
        except RuntimeError:
            continue
        bad = r.check()
        if verbose: print('  cand', c, cvL, cvR, max(r.size()), len(bad), bad[:1], flush=True)
        if not bad: return r, (cvL, cvR)
    return None, None


if __name__ == '__main__':
    for k in [int(x) for x in sys.argv[1].split(',')]:
        t = time.time(); r, par = search(k, fam=sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else 'latcp', verbose='-v' in sys.argv)
        if r: r.flyer(max(r.size()) + k + 20).save(f'out/n{k}_zz.flyer')
        print(k, 'L', ring_size(k), 'best', max(r.size()) if r else None, par, round(time.time() - t, 1), flush=True)
