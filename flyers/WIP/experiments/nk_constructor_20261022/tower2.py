"""Towers of height h on the square side-contact ring (tm_smol style), any small k.
Level 0 = back ring body V_i; level j >= 1 = segment T(j, i) stacked on T(j-1, i):
- rests 2 slots before the level below (rest = rest(V_i) - 2j), so the level below carries its hoppers: the hoppers
  stand on the lower level's plate cells (that plate is their cover);
- its sticky stands on a lower-level plate cell and pulls the lower level on that level's last move, so levels
  0..h-1 need only k-1 hoppers; the top level has k;
- the sticky of level j < h is powered by a redstone block of level j+1 hanging beside it (level j+1 is at its lowest
  relative to level j exactly at the start of level j's rest); the top sticky by a block of the previous tower's top.
python tower2.py K H"""
import sys, itertools
import families as F, square, sqbuild
from nk import Timing, add
from nk2 import Timing2, Ring2, power_problems
from tower import route_all, min_pl

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


def level_layouts(n, below, a, b):
    """lanes for a level with n hoppers over the lower level's plate lanes `below`."""
    lanes = [(y, z) for y in range(-1, a + 1) for z in range(-1, b + 1)]
    bl = set(below)
    for s in sorted(bl):
        for H in itertools.combinations(sorted(bl - {s}), n):
            Hs = set(H)
            cand = [l for l in lanes if l not in bl and l not in Hs and l != s and s not in nb(l)
                    and any(h in nb(l) for h in H) and 0 <= l[0] < a and 0 <= l[1] < b]
            done = False
            for nr in range(1, n + 1):
                for R in itertools.combinations(cand, nr):
                    if all(any(r in nb(h) for r in R) for h in H):
                        for s2 in nb(s):
                            if s2 in Hs or s2 in R or s2 in bl or not (0 <= s2[0] < a and 0 <= s2[1] < b): continue
                            yield s, list(H), list(R), s2
                        done = True; break
                if done: break


def build(k, word, h, choice, power_top=True):
    """choice: tuple of layout indices, one per level 1..h."""
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    vmod = F.lat_module(k - 1, a, b)
    if vmod is None: return None
    if (word >> 7) & 1: vmod = F.mirror_y(vmod)
    a, b = vmod['size']
    L = square.ring_size(k)
    T0 = Timing(k, L)
    place = square.square_layout(L, a, b, (a + 1, sz), (cy, cz))
    below = [tuple(c[1:]) for c in vmod['PLATE']]
    lays = []
    for j in range(1, h + 1):
        n = k if (j >= h - 1 if power_top else j == h) else k - 1
        g = list(itertools.islice(level_layouts(n, below, a, b), choice[j - 1] + 1))
        if len(g) <= choice[j - 1]: return None
        s, H, R, s2 = g[choice[j - 1]]
        lays.append((s, H, R, s2))
        below = H + R + [s2]
    S = T0.S
    rests, nxt = list(T0.rest), [T0.nxt(i) for i in range(L)]
    for j in range(1, h + 1):
        rests += [(T0.rest[i] - 2 * j) % S for i in range(L)]
        nxt += [(j - 1) * L + i for i in range(L)]
    T = Timing2(k, rests, nxt)
    mods = [vmod] * L; places = list(place); mats = ['slime' if i % 2 == 0 else 'honey' for i in range(L)]
    for j in range(1, h + 1):
        s, H, R, s2 = lays[j - 1]
        for i in range(L):
            X, Y = j * L + i, (j - 1) * L + i
            D = T.shift(X, T.rest[X]) - T.shift(Y, T.rest[X])
            x0 = places[Y][0] + 4 - D
            top_only = power_top and j == h
            mods.append(dict(P=[tuple(c) for c in H], R=[(0,) + tuple(c) for c in R],
                             PLATE=[(1,) + tuple(c) for c in H + R] + ([] if top_only else [(0,) + tuple(s2), (1,) + tuple(s2)]),
                             CONT=[(-3,) + tuple(c) for c in H], size=(a, b),
                             RIG=[] if top_only else [dict(pos=(0,) + tuple(s), dir=-1, victim=Y)]))
            places.append((x0,) + place[i][1:])
            mats.append('honey' if (i + j) % 2 else 'slime')
    r = Ring2(T, mods, places, mat=mats)
    r.lays, r.h, r.L0, r.power_top = lays, h, L, power_top
    return r


def add_power(r, choices):
    """choices[j-1] picks the block cell / attach cell for the stickies of level j."""
    T = r.T; L = r.L0; h = r.h
    for j in range(1, h + 1):
        if r.power_top and j == h: continue
        for i in range(L):
            tgt = j * L + i
            src = (j + 1) * L + i if j < h else j * L + (i - 1) % L
            st = T.rest[tgt]
            sp = r.mw(tgt, r.mods[tgt]['RIG'][0]['pos'], st)
            occ = r.world(st)
            opts = []
            for d in N4:
                w = (sp[0], sp[1] + d[0], sp[2] + d[1])
                if occ.get(w): continue
                cx = w[0] - r.place[src][0] - T.shift(src, st)
                loc = sqbuild.to_local(r.place[src], (cx, w[1], w[2]))
                for att in ((1, 0, 0), (-1, 0, 0)) + tuple((0,) + d2 for d2 in N4):
                    opts.append((loc, att))
            if not opts: return None
            loc, att = opts[choices[j - 1] % len(opts)]
            mod = dict(r.mods[src]); mod['R'] = list(mod['R']) + [loc]; r.mods[src] = mod
            a_ = r.mw(src, add(loc, att), 0, src)
            r.extra[src] = set(r.extra[src]) | {a_}; r.glue[src] = r.glue[src] | {a_}
    r.__dict__.pop('_hw', None); r.invalidate()
    return r


def scan(k, word, h, nlay=6, npow=12, keep=4, verbose=False):
    from terrace import collisions
    res = []
    for lc in itertools.product(range(nlay), repeat=h):
        base = build(k, word, h, lc)
        if base is None or collisions(base): continue
        for pc in itertools.product(range(npow), repeat=h - 1):
            pc = pc + (0,)
            r = build(k, word, h, lc)
            if add_power(r, pc) is None or collisions(r): continue
            if power_problems(r): continue
            try: route_all(r)
            except RuntimeError: continue
            if r.check(): continue
            L = r.L0
            res.append((max(r.size()[:L]), max(r.size()), lc, pc))
            if verbose: print(res[-1], flush=True)
    res.sort(key=lambda t: (t[1], t[0]))
    out = []
    for back, sz, lc, pc in res[:keep]:
        r = build(k, word, h, lc); add_power(r, pc); route_all(r)
        p = f'out/tower2_{k}_{h}_{word}_{len(out)}.flyer'; r.flyer(4 * k + 30).save(p)
        out.append((back, sz, lc, pc, min_pl(p, k, 4 * k + 10)))
    return out


def _job(args):
    k, h, word, nlay, npow = args
    try: return word, scan(k, word, h, nlay, npow, keep=2)
    except Exception as e: return word, repr(e)[:80]


if __name__ == '__main__':
    from concurrent.futures import ProcessPoolExecutor
    k, h = int(sys.argv[1]), int(sys.argv[2])
    nlay, npow = int(sys.argv[3]), int(sys.argv[4])
    words = [1 | (v << 2) | (l << 6) for v in range(16) for l in range(16)]
    with ProcessPoolExecutor(10) as ex:
        for word, res in ex.map(_job, [(k, h, w, nlay, npow) for w in words]):
            if res: print(word, F.unpack(word, k), res, flush=True)
