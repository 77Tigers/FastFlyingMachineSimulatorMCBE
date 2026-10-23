"""Deterministic local search over a square-ring module in 3D (pushers at any level, targets/plate anywhere,
covers behind or beside), scored on the routed ring itself (max body glue + RB), checked by nk.Ring.check.
Starts from the family's module for a word. python modsearch.py K WORD [ITERS]"""
import sys, json, itertools
import families as F, square, sqbuild

D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def lanes_of(mod):
    return {tuple(p[:2]) for p in mod['P']}


def normalise(mod):
    """targets in PLATE for every pusher; drop plate cells nobody needs only if they are not connectors."""
    P = [tuple(p) if len(p) == 3 else (p[0], p[1], 0) for p in mod['P']]
    plate = set(tuple(c) for c in mod['PLATE'])
    for y, z, h in P: plate.add((h + 1, y, z))
    return dict(mod, P=P, PLATE=sorted(plate))


def score(k, mod, step, cv, L=None):
    try:
        r = sqbuild.assemble(k, mod, step, cv, L)
    except (RuntimeError, AssertionError, KeyError, IndexError):
        return None, None
    if r is None: return None, None
    Lr = r.T.L; m = Lr // 4
    sub = sorted({(X + d) % Lr for X in (0, 1, m) for d in range(-2, 3)})
    if r.check(sub): return None, r
    s = r.size()
    return (max(s), sum(s)), r


def neighbours(mod, a, b):
    """small edits: move one pusher (lane +-1 or level +-1) with its target, move one RB, toggle one plate cell,
    switch one cover between behind (-3) and beside (-2 in a free lane)."""
    P, R, PL, C = list(mod['P']), list(mod['R']), list(mod['PLATE']), list(mod['CONT'])
    occ = {(p[0], p[1]) for p in P} | {(r[1], r[2]) for r in R}
    out = []
    for i, (y, z, h) in enumerate(P):
        for dy, dz, dh in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (y + dy, z + dz, h + dh)
            if (q[0], q[1]) in occ and (dy or dz): continue
            if not (-1 <= q[0] <= a and -1 <= q[1] <= b) or not (-3 <= q[2] <= 1): continue
            P2 = P[:i] + [q] + P[i + 1:]
            C2 = [c for c in C if not (c[1:] == (y, z) and c[0] == h - 3)] + [(q[2] - 3, q[0], q[1])]
            PL2 = [c for c in PL if c != (h + 1, y, z)] + [(q[2] + 1, q[0], q[1])]
            out.append(dict(mod, P=P2, CONT=C2, PLATE=PL2))
    for i, (x, y, z) in enumerate(R):
        for dy, dz in D4:
            q = (x, y + dy, z + dz)
            if (q[1], q[2]) in occ: continue
            R2 = R[:i] + [q] + R[i + 1:]
            out.append(dict(mod, R=R2, PLATE=PL + [(x + 1, q[1], q[2])]))
        for dx in (1, -1):
            out.append(dict(mod, R=R[:i] + [(x + dx, y, z)] + R[i + 1:]))
    for i in range(len(PL)):
        out.append(dict(mod, PLATE=PL[:i] + PL[i + 1:]))
    for i in range(len(C)):
        out.append(dict(mod, CONT=C[:i] + C[i + 1:]))
        x, y, z = C[i]
        for dy, dz in D4:
            out.append(dict(mod, CONT=C[:i] + [(x + 1, y + dy, z + dz)] + C[i + 1:]))
        out.append(dict(mod, CONT=C[:i] + [(x - 1, y, z)] + C[i + 1:]))
    return out


def search(k, word, iters=30, verbose=True):
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    L = F.big_ring(k) if fam == 'latbig' else square.ring_size(k)
    m = L // 4
    mod = construct_mod(k, word)
    mod = normalise(mod)
    a, b = mod['size']
    step = (a + 2, 0) if m == 1 else (a + 1, sz)
    cur, _ = score(k, mod, step, (cy, cz), L)
    if verbose: print('start', cur, flush=True)
    for it in range(iters):
        best = None
        for nm in neighbours(mod, a, b):
            nm = normalise(nm)
            sc, _ = score(k, nm, step, (cy, cz), L)
            if sc is not None and sc < cur and (best is None or sc < best[0]): best = (sc, nm)
        if best is None: break
        cur, mod = best
        if verbose: print('iter', it, cur, flush=True)
    return cur, mod, step, (cy, cz), L


def construct_mod(k, word):
    import construct
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    L = F.big_ring(k) if fam == 'latbig' else square.ring_size(k)
    mod = construct.grid_module(k, 'slabP', box=(a, b)) if fam == 'slab' else F.lat_module(k, a, b)
    if L // 4 > 1 and (word >> 7) & 1: mod = F.mirror_y(mod)
    return mod


if __name__ == '__main__':
    k, word = int(sys.argv[1]), int(sys.argv[2])
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    cur, mod, step, cv, L = search(k, word, iters)
    print('final', cur); print(json.dumps({k_: [list(x) if isinstance(x, tuple) else x for x in v] if isinstance(v, list) else v for k_, v in mod.items()}))
    import simk
    r = sqbuild.assemble(k, mod, step, cv, L); pl = max(r.size()) + k
    r.flyer(pl).save(f'out/modsearch_{k}.flyer'); print('sim', simk.flies(f'out/modsearch_{k}.flyer', k, pl))
