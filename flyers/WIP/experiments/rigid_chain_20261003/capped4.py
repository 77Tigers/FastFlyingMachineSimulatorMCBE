"""Cost-aware race-free capped chain (plan as capped3) with cheaper power sharing:
K0 = sticky, glue, pusher (+ extra pusher toward Y, + observer for Hz); no redstone/attach (Z powered by others).
Z = glue + two pushers. Every decision enumerates options and keeps the cheapest (fewest added cells).
"""
import random, sys, pathlib, re, copy, pickle, os
from rigid import Seg, check, to_flyer, add, D6, loads, glue_path, reserved_cells, kind_of, unique_offset, E as EX, W_
from alt import altchain
from capped2 import make_rider, rider_world, wpos, lpos, sub
X = (1, 0, 0)

def ncells(segs): return sum(len(s.cells) for s in segs)

def best_of(options, rng):
    """options: list of (cost, state). Pick min (max action load, max segment size, added cost), random ties."""
    if not options: return None
    def key(o):
        segs = o[1]
        return (loads(segs), max(len(x.cells) for x in segs if not x.rider), o[0])
    keyed = [(key(o), o) for o in options]
    m = min(k for k, _ in keyed)
    return rng.choice([o for k, o in keyed if k == m])[1]

def observer_options(segs, si, target_world, t, rng, maxlen=2):
    out = []
    for d in range(6):
        cs = copy.deepcopy(segs); seg = cs[si]
        ow = sub(target_world, D6[d]); ol = lpos(seg, ow, t)
        if ol in seg.cells or ol in reserved_cells(cs, seg, glue=False): continue
        seg.cells[ol] = ('O', d)
        p = glue_path(seg, [add(ol, dd) for dd in D6], cs, rng, maxlen=maxlen)
        if p is None: continue
        out.append((len(p) + 1, cs))
    return out

def ride_options(segs, ri, t, ci, rng, maxlen=3, tries=4):
    out = []; seen = set()
    for _ in range(tries):
        cs = copy.deepcopy(segs); r = cs[ri]; car = cs[ci]
        rw = rider_world(r, t)
        goals = [lpos(car, add(rw, d), t) for d in D6]
        p = glue_path(car, goals, cs, rng, maxlen=maxlen)
        if p is None: break
        key = tuple(sorted(p))
        if key in seen: continue
        seen.add(key); out.append((len(p), cs))
        if not p: break
    return out

def power_options(segs, si, piston_world, t, kind, rng, maxlen=2):
    s = segs[si]
    front = add(piston_world, EX if kind == 'P' else W_)
    out = []
    for d in D6:
        c = add(piston_world, d)
        if c == front: continue
        for oi, o in enumerate(segs):
            if o.rider or oi == si or not unique_offset(o, s, t): continue
            cs = copy.deepcopy(segs); oo = cs[oi]
            lc = lpos(oo, c, t)
            if lc in oo.cells or lc in reserved_cells(cs, oo, glue=False): continue
            oo.cells[lc] = 'R'
            if any(add(lc, dd) in oo.cells and oo.cells[add(lc, dd)] == 'g' for dd in D6):
                out.append((1, cs)); continue
            p = glue_path(oo, [add(lc, dd) for dd in D6], cs, rng, maxlen=maxlen)
            if p is not None: out.append((1 + len(p), cs))
    return out

def fix_power(segs, rng, rounds=8):
    for _ in range(rounds):
        r = check(segs)
        if r is None or 'power missing' not in r: return segs, r
        m = re.match(r't(\d+): (\S+) ([PS])@\((-?\d+), (-?\d+), (-?\d+)\)', r)
        t = int(m.group(1)); si = [i for i, x in enumerate(segs) if x.name == m.group(2)][0]
        pw = tuple(int(m.group(i)) for i in (4, 5, 6))
        st = best_of(power_options(segs, si, pw, t, m.group(3), rng), rng)
        if st is None: return segs, r
        segs = st
    return segs, check(segs)

def try_once(rng, n, a, c):
    chain = altchain(n, a, c)
    K0 = chain[0]; F = chain[-1]; E = chain[-2]; D = chain[-3]
    for cc, k in list(F.cells.items()):
        if k in ('P', 'S'): del F.cells[cc]
    # K0: drop its redstone and attach glue (only served the absent rear neighbour)
    for cc, k in list(K0.cells.items()):
        if k == 'R': del K0.cells[cc]
    att = (0, -c[0], -c[1])
    if att in K0.cells and K0.cells[att] == 'g': del K0.cells[att]
    Zo = (K0.origin[0] - 1, K0.origin[1] - a[0], K0.origin[2] - a[1])
    Z = Seg('Z', (2, 3), Zo, {(0, 0, 0): 'g', (0, a[0], a[1]): 'P'}, 'honey')
    k0x = K0.origin[0]
    # enumerate Y contact lanes: cY1 at x=k0x (Z pusher behind at k0x-1, s0), cY2 at Y-frame x=k0x+2 (K0 pusher @s2)
    opts = []
    base = (K0.origin[1], K0.origin[2])
    lanes = [(base[0] + dy, base[1] + dz) for dy in range(-2, 3) for dz in range(-2, 3)]
    rng.shuffle(lanes)
    for l1 in lanes[:12]:
        for l2 in lanes[:12]:
            segs = [copy.deepcopy(Z), Seg('Y', (0, 2), (0, 0, 0), {(k0x, l1[0], l1[1]): 'g'}, 'slime' if K0.mat == 'honey' else 'honey')] + copy.deepcopy(chain)
            Zs, Ys, K0s = segs[0], segs[1], segs[2]
            cY1 = (k0x, l1[0], l1[1]); cY2 = (k0x + 2, l2[0], l2[1])
            zp = lpos(Zs, sub(cY1, X), 0)
            kp = lpos(K0s, sub(wpos(Ys, cY2, 2), X), 2)
            if zp in Zs.cells or kp in K0s.cells or cY2 == cY1: continue
            if cY2 in reserved_cells(segs, Ys): continue
            Zs.cells[zp] = 'P'; K0s.cells[kp] = 'P'
            cost = 0
            if not any(add(cY1, d) == cY2 for d in D6):
                p = glue_path(Ys, [add(cY2, d) for d in D6], segs, rng, maxlen=4, extra_block=[cY2])
                if p is None: continue
                cost += len(p)
            Ys.cells[cY2] = 'g'
            p1 = glue_path(Zs, [add(zp, d) for d in D6], segs, rng, maxlen=3)
            p2 = glue_path(K0s, [add(kp, d) for d in D6], segs, rng, maxlen=3)
            if p1 is None or p2 is None: continue
            cost += len(p1) + len(p2)
            opts.append((cost, segs))
    segs = best_of(opts, rng)
    if segs is None: return None, 'Y lanes'
    names = [s.name for s in segs]
    idx = lambda nm: names.index(nm)
    # riders: choose contacts minimising ride+observer cost
    for name, kind, fire, tname, obs_seg, rides in (
            ('Hz', 'S', 1, 'Z', ('K0', 'Y'), [(0, 'Y'), (3, 'Z')]),
            ('H', 'P', 1, chain[-1].name, chain[-1].name, [(3, chain[-2].name), (0, chain[-1].name)]),
            ('H2', 'P', 3, chain[-2].name, chain[-2].name, [(1, chain[-3].name), (2, chain[-2].name)])):
        tgt = segs[idx(tname)]
        cands = [cc for cc, k in tgt.cells.items() if k == 'g']
        for cc in list(cands):
            for d in D6[2:]:
                if add(cc, d) not in tgt.cells: cands.append(add(cc, d))
        ropts = []; dbg = {}
        for cc in cands:
            cs = copy.deepcopy(segs); t2 = cs[idx(tname)]; cost = 0
            if cc not in t2.cells:
                if cc in reserved_cells(cs, t2): continue
                if not any(add(cc, d) in t2.cells and t2.cells[add(cc, d)] == 'g' for d in D6): continue
                t2.cells[cc] = 'g'; cost += 1
            r = make_rider(name, kind, fire, t2, cc)
            cs.append(r)
            if list(r.cells)[0] in reserved_cells(cs, r, glue=False): dbg['clash']=dbg.get('clash',0)+1; continue
            ri = len(cs) - 1
            # observer
            fire_t = fire
            oo = []
            for osg in (obs_seg if isinstance(obs_seg, tuple) else (obs_seg,)):
                oo += observer_options(cs, idx(osg), rider_world(r, fire_t), fire_t, rng, maxlen=3)
            st = best_of(oo, rng)
            if st is None: dbg['obs']=dbg.get('obs',0)+1; continue
            cost += min(o[0] for o in oo); cs = st
            states = [(cost, cs)]
            for t, cn in rides:
                nxt = []
                for c0, s0 in states:
                    for c1, s1 in ride_options(s0, ri, t, idx(cn), rng):
                        nxt.append((c0 + c1, s1))
                states = nxt
                if not states: dbg[f'ride{t}'] = dbg.get(f'ride{t}', 0) + 1; break
            ropts += states
        segs = best_of(ropts, rng)
        if segs is None: return None, f'rider {name} {sorted(dbg.items())}'
        names = [s.name for s in segs]
    segs, r = fix_power(segs, rng)
    return segs, r

if __name__ == '__main__':
    N = int(sys.argv[1]); out = pathlib.Path(sys.argv[2]); out.mkdir(exist_ok=True)
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    orients = [((1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, 1)), ((-1, 0), (0, -1)),
               ((0, 1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (1, 0)), ((0, -1), (-1, 0))]
    st = {}; found = 0; best = 99
    for it in range(N):
        a, c = rng.choice(orients)
        segs, why = try_once(rng, n, a, c)
        if segs is None or why is not None:
            k = re.sub(r'[-0-9(), ]+', '#', str(why)); st[k] = st.get(k, 0) + 1; continue
        found += 1; L = loads(segs)
        if L <= best:
            best = L
            tag = f's{os.getpid()}_{found:04d}_L{L}'
            to_flyer(segs, L).save(out / f'c4_{tag}.flyer'); pickle.dump(segs, open(out / f'c4_{tag}.pkl', 'wb'))
        print('FOUND', found, 'load', L, [(s.name, len(s.cells)) for s in segs if not s.rider], flush=True)
    print('found', found, 'best', best)
    for k, v in sorted(st.items(), key=lambda x: -x[1])[:14]: print(v, k)

def power_options2(segs, si, piston_world, t, kind, rng, maxlen=2):
    """Redstone (unique offset) + observers (pulse at t: carrier moved at t-1) facing the piston or a glue cell next
    to it + rods facing a glue cell next to it. Each with an attach path <= maxlen."""
    out = list(power_options(segs, si, piston_world, t, kind, rng, maxlen))
    s = segs[si]
    front = add(piston_world, EX if kind == 'P' else W_)
    occ = {}
    for i, o in enumerate(segs):
        for c, k in o.at(t).items(): occ[c] = (i, k)
    targets = [('piston', piston_world)]
    for d in D6:
        g = add(piston_world, d)
        if g == front: continue
        v = occ.get(g)
        if v and v[1] == 'g': targets.append(('glue', g))
    for typ, tw in targets:
        for d in range(6):
            srcw = sub(tw, D6[d])
            if srcw in occ: continue
            for oi, o in enumerate(segs):
                if o.rider: continue
                kinds = []
                if o.moves(t - 1): kinds.append(('O', d))
                if typ == 'glue': kinds.append(('D', d))
                for kk in kinds:
                    cs = copy.deepcopy(segs); oo = cs[oi]
                    lc = lpos(oo, srcw, t)
                    if lc in oo.cells or lc in reserved_cells(cs, oo, glue=False): continue
                    oo.cells[lc] = kk
                    if any(oo.cells.get(add(lc, dd)) == 'g' for dd in D6):
                        out.append((1, cs)); continue
                    p = glue_path(oo, [add(lc, dd) for dd in D6], cs, rng, maxlen=maxlen)
                    if p is not None: out.append((1 + len(p), cs))
    return out
