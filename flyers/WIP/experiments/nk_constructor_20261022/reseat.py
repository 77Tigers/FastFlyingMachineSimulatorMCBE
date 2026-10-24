"""Reseat hoppers onto the connector (human N3 back bodies: hoppers stand beside the connector column and their
target is a cell the connector passes through anyway, so the plate costs nothing).
Loop: assemble + route the ring; for every hopper try moving it (with its RB link kept) behind any non-plate glue
cell of its body (target = that cell, hopper level = cell x - 1), optionally moving one RB next to it; keep the
best ring that passes nk's checker. python reseat.py K WORD [ITERS]"""
import sys, json
import families as F, sqbuild, square
from modsearch import score, normalise, construct_mod

D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def moves(r, mod, X=1):
    """candidate modules: hopper j -> behind a connector/contact cell of body X (module frame)."""
    plate = set(r.plates[X]); out = []
    cells = [sqbuild.to_local(r.place[X], g) for g in r.glue[X] - plate]
    P = list(mod['P']); R = list(mod['R'])
    used = {(p[0], p[1], p[2]) for p in P}
    for j, (y, z, h) in enumerate(P):
        for g in cells:
            q = (g[1], g[2], g[0] - 1)
            if q in used or (q[2], q[0], q[1]) in {tuple(c) for c in mod['PLATE']}: continue
            P2 = P[:j] + [q] + P[j + 1:]
            PL2 = [c for c in mod['PLATE'] if tuple(c) != (h + 1, y, z)]
            C2 = [c for c in mod['CONT'] if not (tuple(c[1:]) == (y, z) and c[0] == h - 3)]
            base = dict(mod, P=P2, PLATE=PL2, CONT=C2)
            out.append(base)
            # move one RB so it touches the new hopper (same level, a free neighbouring lane)
            for i, rb in enumerate(R):
                for dy, dz in D4:
                    nr = (q[2], q[0] + dy, q[1] + dz)
                    if (nr[1], nr[2], nr[0]) in used: continue
                    out.append(dict(base, R=R[:i] + [nr] + R[i + 1:]))
    return out


def search(k, word, iters=8, verbose=True):
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    L = F.big_ring(k) if fam == 'latbig' else square.ring_size(k)
    m = L // 4
    mod = normalise(construct_mod(k, word))
    a, b = mod['size']
    step = (a + 2, 0) if m == 1 else (a + 1, sz)
    cv = (cy, cz)
    cur, r = score(k, mod, step, cv, L)
    if verbose: print('start', cur, flush=True)
    for it in range(iters):
        best = None
        for X in sorted({1 % L, m % L}):
            for nm in moves(r, mod, X):
                nm = normalise(nm)
                # covers for moved hoppers: behind (-3) by default; the router connects them
                have = {(c[1], c[2]) for c in nm['CONT']}
                nm['CONT'] = list(nm['CONT']) + [(p[2] - 3, p[0], p[1]) for p in nm['P'] if (p[0], p[1]) not in have]
                sc, r2 = score(k, nm, step, cv, L)
                if sc is not None and sc < cur and (best is None or sc < best[0]): best = (sc, nm, r2)
        if best is None: break
        cur, mod, r = best
        if verbose: print('iter', it, cur, mod['P'], mod['R'], flush=True)
    return cur, mod, step, cv, L


if __name__ == '__main__':
    k = int(sys.argv[1])
    word = int(sys.argv[2]) if len(sys.argv) > 2 else json.load(open('bits.json'))[str(k)]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    cur, mod, step, cv, L = search(k, word, iters)
    print('final', cur)
    import simk
    r = sqbuild.assemble(k, mod, step, cv, L); pl = max(r.size()) + k
    p = f'out/reseat_{k}.flyer'; r.flyer(pl).save(p); print('sim', pl, simk.flies(p, k, pl)[0])
