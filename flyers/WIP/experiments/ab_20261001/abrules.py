"""Shared hazard rule: carried piston with a different moving body directly in front."""
from abgen333 import nb


def _get(maps, c):
    for m in maps:
        v = m.get(c)
        if v is not None: return v
    return None


def carried_front_conflict(lay, b, w, k, occmaps, itemmaps):
    """b's glue at world w, slot k (b moves at k)."""
    L = lay.L
    def carriable(it):
        if it is None or it[0] != 'pist': return False
        p = it[1]
        f = p['f'] if isinstance(p, dict) else None
        return f is not None and k % L not in (f % L, (f + 1) % L)
    for n in nb(w):
        it = _get(itemmaps, n)
        if carriable(it):
            front = (n[0] + 1, n[1], n[2])
            o = _get(occmaps, front)
            if o is not None and o != b and lay.moves(o, k): return True
            it2 = _get(itemmaps, front)
            if it2 is not None and it2[0] in ('src', 'glazed') and it2[2] != b and lay.moves(it2[2], k): return True
    back = (w[0] - 1, w[1], w[2])
    it = _get(itemmaps, back)
    if carriable(it):
        for n in nb(back):
            if n == w: continue
            o = _get(occmaps, n)
            if o is not None and o != b and lay.moves(o, k): return True
    return False
