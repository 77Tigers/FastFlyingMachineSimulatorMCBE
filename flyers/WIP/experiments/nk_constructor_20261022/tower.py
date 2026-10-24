"""Tower (front segment) prototype for small k, after tm_smol's front segments.
Back ring = the square side-contact ring, but each back body V has k-1 hoppers; its last move is a pull by its front
segment F_V. F_V sits on top of V and rests 2 slots before V (V's PREV phase), so V is F_V's hopper carrier:
F_V's k hoppers stand on V's plate cells (V's plate is their cover, as in the terrace). F_V's sticky stands on a V
plate cell and pulls it at V's last move. F_V's sticky is powered by a redstone block that F_U (the segment before)
lowers onto it at the start of F_V's rest; F_V carries the same kind of block for F_W.
python tower.py K"""
import sys, itertools
import families as F, square, sqbuild
from nk import Timing, SYMS, add
from nk2 import Timing2, Ring2

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


def front_layouts(k, vplate, a, b):
    """front segment lanes over the back module: sticky s on a V plate lane, k hopper lanes H on V plate lanes,
    F RB lanes R (no V plate below; each hopper next to one; none next to s), attach lane s2 next to s."""
    lanes = [(y, z) for y in range(-1, a + 1) for z in range(-1, b + 1)]
    vp = set(vplate)
    for s in sorted(vp):
        rest = sorted(vp - {s})
        for H in itertools.combinations(rest, k):
            Hs = set(H)
            cand_r = [l for l in lanes if l not in vp and l not in Hs and l != s and s not in nb(l)
                      and any(h in nb(l) for h in H)]
            for nr in range(1, k + 1):
                for R in itertools.combinations(cand_r, nr):
                    if all(any(r in nb(h) for r in R) for h in H):
                        for s2 in nb(s):
                            if s2 in vp or s2 in Hs or s2 in R: continue
                            yield s, list(H), list(R), s2
                        break
                else: continue
                break


def build(k, word, layout_index=0, extra_vplate=()):
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    vmod = F.lat_module(k - 1, a, b)
    if vmod is None: return None
    if (word >> 7) & 1: vmod = F.mirror_y(vmod)
    vmod = dict(vmod); vmod['PLATE'] = list(vmod['PLATE']) + [(1,) + tuple(c) for c in extra_vplate]
    a, b = vmod['size']
    L = square.ring_size(k); m = L // 4
    T0 = Timing(k, L)
    step = (a + 1, sz)
    place = square.square_layout(L, a, b, step, (cy, cz))
    vplate = [tuple(c[1:]) for c in vmod['PLATE']]
    lays = list(itertools.islice(front_layouts(k, vplate, a, b), layout_index + 1))
    if len(lays) <= layout_index: return None
    s, H, R, s2 = lays[layout_index]
    # bodies 0..L-1 back, L..2L-1 front; front i rests 2 slots before back i and is carried by it
    rests = list(T0.rest) + [(T0.rest[i] - 2) % T0.S for i in range(L)]
    nxt = [T0.nxt(i) for i in range(L)] + list(range(L))
    T = Timing2(k, rests, nxt)
    # front x0 so that front-frame -3 at its local 0 is the back plate level (+1): x0_F = x0_V + 4 - D
    mods, places, mats = [], [], []
    for i in range(L):
        mods.append(vmod); places.append(place[i]); mats.append('slime' if i % 2 == 0 else 'honey')
    for i in range(L):
        Fi = L + i
        D = T.shift(Fi, T.rest[Fi]) - T.shift(i, T.rest[Fi])
        x0 = place[i][0] + 4 - D
        fmod = dict(P=[tuple(h) for h in H], R=[(0,) + tuple(r) for r in R],
                    PLATE=[(1,) + tuple(c) for c in H + R] + [(0,) + tuple(s2), (1,) + tuple(s2)],
                    CONT=[(-3,) + tuple(h) for h in H], size=(a, b),
                    RIG=[dict(pos=(0,) + tuple(s), dir=-1, victim=i)])
        mods.append(fmod); places.append((x0,) + place[i][1:]); mats.append('honey' if i % 2 == 0 else 'slime')
    r = Ring2(T, mods, places, mat=mats)
    r.layout = (s, H, R, s2)
    return r


def add_power_arms(r, k, choice=0):
    """each front segment F_V carries a redstone block that F_V's motion lowers beside F_W's sticky exactly at the
    start of F_W's rest (F_V is then at its lowest relative to F_W). choice picks the side / attach cell."""
    T = r.T; L = T.L // 2
    for i in range(L):
        FV, FW = L + i, L + T.nxt(i)
        st = T.rest[FW]
        sp = r.mw(FW, r.mods[FW]['RIG'][0]['pos'], st)
        occ = r.world(st)
        opts = []
        for d in N4:
            w = (sp[0], sp[1] + d[0], sp[2] + d[1])
            if occ.get(w): continue
            x0, (oy, oz), si = r.place[FV]
            loc = sqbuild.to_local(r.place[FV], (w[0] - x0 - T.shift(FV, st), w[1], w[2]))
            for att in ((-1, 0, 0), (1, 0, 0)) + tuple((0,) + d2 for d2 in N4):
                opts.append((loc, att))
        if not opts: return None
        loc, att = opts[choice % len(opts)]
        mod = dict(r.mods[FV]); mod['R'] = list(mod['R']) + [loc]; r.mods[FV] = mod
        a = r.mw(FV, add(loc, att), 0, FV)
        r.extra[FV] = set(r.extra[FV]) | {a}; r.glue[FV] = r.glue[FV] | {a}
    r.__dict__.pop('_hw', None); r.invalidate()
    return r


def min_pl(path, k, hi):
    import simk
    best = None
    for pl in range(hi, 0, -1):
        ok, out = simk.flies(path, k, pl)
        if 'pass=true' in out: best = pl
        else: break
    return best


if __name__ == '__main__':
    import json
    k = int(sys.argv[1])
    w = json.load(open('bits.json'))[str(k)]
    r = build(k, w)
    print('layout', r.layout if r else None)


def route_all(r):
    D = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for X in range(r.T.L):
        full = set(r.plates[X]); comps = []; seen = set()
        for c in full:
            if c in seen: continue
            st = [c]; comp = set()
            while st:
                u = st.pop()
                if u in comp: continue
                comp.add(u); st += [add(u, d) for d in D if add(u, d) in full]
            seen |= comp; comps.append(comp)
        tree = max(comps, key=len)
        r.plates[X] = tree; r.extra[X] = set(r.extra[X]) | (full - tree)
        r.route(X); r.plates[X] = full
    return r


def scan(k, word, extras, nlay=40):
    from terrace import collisions
    out = []
    for extra in extras:
        for li in range(nlay):
            r = build(k, word, li, extra)
            if r is None: break
            if collisions(r): continue
            try: route_all(r)
            except RuntimeError: continue
            bad = r.check()
            L = r.T.L // 2
            out.append((len(bad), max(r.size()[:L]), max(r.size()[L:]), extra, li, r.layout))
    return sorted(out)


def full_scan(k, word, extras, nlay=60, nch=24, keep=6):
    import nk2, simk
    from terrace import collisions
    res = []
    for extra in extras:
        for li in range(nlay):
            base = build(k, word, li, extra)
            if base is None: break
            if collisions(base): continue
            for ch in range(nch):
                r = build(k, word, li, extra)
                if add_power_arms(r, k, ch) is None or collisions(r): continue
                if nk2.power_problems(r): continue
                try: route_all(r)
                except RuntimeError: continue
                if r.check(): continue
                res.append((max(r.size()), extra, li, ch))
    res.sort(key=lambda t: t[0])
    out = []
    for sz, extra, li, ch in res[:keep]:
        r = build(k, word, li, extra); add_power_arms(r, k, ch); route_all(r)
        p = f'out/tower{k}.flyer'; r.flyer(80).save(p)
        out.append((sz, extra, li, ch, min_pl(p, k, 3 * k + 20)))
    return out
