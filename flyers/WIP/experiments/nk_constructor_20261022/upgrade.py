"""Greedy side-contact upgrade of a slab module (deterministic, no CP): an empty lane C next to >= 2 pushers gets a
next-body cell at x=-2; slab cells (x=-3) behind pushers that C now covers are removed while the next body's cells
stay connected (cells: (-2, C) and (-3, lane); adjacency: lateral at equal x, vertical within a lane)."""
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


def connected(cells):
    cells = set(cells)
    if not cells: return True
    st, seen = [next(iter(cells))], set()
    while st:
        u = st.pop()
        if u in seen: continue
        seen.add(u)
        x, y, z = u
        for v in [(x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1), (x + 1, y, z), (x - 1, y, z)]:
            if v in cells and v not in seen: st.append(v)
    return len(seen) == len(cells)


def upgrade(mod):
    P = set(map(tuple, mod['P'])); R = {r[1:] for r in mod['R']}
    W = set(map(tuple, mod['CONT']))
    a, b = mod['size']
    lanes = [(y, z) for y in range(-1, a + 1) for z in range(-1, b + 1)]
    improved = True
    while improved:
        improved = False
        best = None
        for c in lanes:
            if c in P or c in R or (-2,) + c in W: continue
            if any(v in R for v in nb(c)):   # keep C lanes away from RB lanes (drag at local 0/1)
                pass
            cov = [p for p in nb(c) if p in P]
            if len(cov) < 2: continue
            new = set(W) | {(-2,) + c}
            removed = 0
            for p in cov:
                cell = (-3,) + p
                if cell in new:
                    trial = new - {cell}
                    if connected(trial): new = trial; removed += 1
            gain = removed - 1
            if gain > 0 and (best is None or gain > best[0]): best = (gain, new)
        if best:
            W = best[1]; improved = True
    out = dict(mod); out['CONT'] = sorted(W)
    return out
