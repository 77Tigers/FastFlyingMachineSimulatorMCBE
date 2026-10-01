"""Shared-redstone variant: Y = X(V) = Z(U) carries ONE redstone touching A_V,P_U (slot w_V) and B_V,Q_U (w_V+3);
U drops its observer.  Placement constructor aligns chosen pairs; routing via gen.route2; exact via ilp optional."""
import random, json, sys, itertools
import gen, model
from model import Item, nb, sx
from sched import S, DISP, W, X_of, Z_of

def pairs():
    out = []
    for Y in range(3):
        V = [v for v in range(3) if X_of(v) == Y][0]; U = [u for u in range(3) if Z_of(u) == Y][0]
        out.append((Y, V, U))
    return out

class SB(gen.Builder):
    def __init__(self, rng, gt, places, oopt, drop):
        super().__init__(rng, gt, places, oopt)
        self.drop = drop  # set of U bodies without observer

    def setup(self):
        d = self.d
        errs = super().setup()
        # remove observers of dropped bodies
        if self.drop:
            keep = [it for it in d.items if not (it.cat == 'obs' and it.body in self.drop)]
            nd = model.Design(d.gtypes)
            for it in keep:
                pass
            # rebuild preserving piston indices (pistons are first)
            nd.carry = dict(d.carry)
            for it in keep:
                nd.add_item(it)
            self.d = nd
        errs = [e for e in self.d.all_errors() if e[0] not in ('uncovered', 'nocarrier', 'power')]
        return errs

    def rs_cands(self, v, extraU=None):
        d = self.d; X = X_of(v)
        sets = []
        specs = [('A', v, W[v]), ('B', v, (W[v] + 3) % 6)]
        if extraU is not None:
            specs += [('P', extraU, (W[extraU] + 2) % 6), ('Q', extraU, (W[extraU] + 5) % 6)]
        for k, b, t in specs:
            it = d.items[self.pidx[(b, k)]]
            front = sx(it.pos[t], it.face)
            sets.append({sx(q, -DISP[X][t]) for q in nb(it.pos[t]) if q != front})
        return sets

    def place_rs(self):
        d = self.d
        self.armc = [d.arm_ext(t) for t in range(6)]
        self.holders = {b: [] for b in range(3)}
        for Y, v, U in pairs():
            X = Y
            extra = U if U in self.drop else None
            sets = self.rs_cands(v, extra)
            if extra is not None:
                combos = [[c] for c in set.intersection(*sets)]
            else:
                combos = [[c] for c in sets[0] & sets[1]] + [[a, b] for a in sets[0] for b in sets[1] if a != b][:60]
            self.rng.shuffle(combos)
            placed = False
            for combo in combos:
                added = []; ok = True
                for c in combo:
                    pos = [sx(c, DISP[X][t]) for t in range(6)]
                    it = Item('rs', pos, [bool(S[X][t]) for t in range(6)], body=X, name=f'R{X}for{v}')
                    if d.item_errors(it, None, self.armc):
                        ok = False; break
                    added.append(d.add_item(it))
                if ok and not any(e[3] for e in d.power_errors()):
                    hs = []
                    for a in added:
                        h = [q for q in nb(d.items[a].pos[0]) if self.cell_ok(q, X)]
                        if not h: ok = False
                        hs.append(h)
                    if ok:
                        self.holders[X] += hs; placed = True; break
                for a in reversed(added):
                    self._pop(a)
            if not placed:
                return False
        return True

def aligned_places(rng, Y, V, U, base_place):
    """enumerate U placements (given V's) such that one redstone can touch A_V,B_V,P_U,Q_U."""
    gt, places, oopt = base_place
    out = []
    for su in range(8):
        for oy in range(-5, 6):
            for oz in range(-5, 6):
                for ox in range(-6, 7):
                    pl = list(places); pl[U] = (su, (ox, oy, oz))
                    B = SB(rng, gt, pl, oopt, set())
                    # quick geometric test without full setup: compute piston positions
                    pos = {}
                    for (b, k) in ((V, 'A'), (V, 'B'), (U, 'P'), (U, 'Q')):
                        u_, v_ = gen.LANES[k]
                        base = B.w(b, 0, u_, v_)
                        from sched import piston_x
                        pos[(b, k)] = [sx(base, piston_x(b, k, t)) for t in range(6)]
                    def cs(b, k, t, face):
                        p = pos[(b, k)][t]
                        return {sx(q, -DISP[Y][t]) for q in nb(p) if q != sx(p, face)}
                    inter = cs(V, 'A', W[V], -1) & cs(V, 'B', (W[V] + 3) % 6, -1) & cs(U, 'P', (W[U] + 2) % 6, 1) & cs(U, 'Q', (W[U] + 5) % 6, 1)
                    if inter:
                        out.append((su, (ox, oy, oz)))
    return out

def build(seed, place, drop, cap=10):
    rng = random.Random(seed)
    gt, places, oopt = place
    B = SB(rng, gt, places, oopt, drop)
    B.jitter = 1.0 if seed % 3 else 0
    errs = B.setup()
    if errs:
        return None, 'template'
    B.foreign('fixed')
    B.armc = [B.d.arm_ext(t) for t in range(6)]
    if not B.place_rs():
        return None, 'rs'
    r = B.route2(cap)
    if r:
        return None, r
    errs = B.d.all_errors()
    if errs:
        return None, 'final:' + str(errs[:2])
    return B, 'ok'

if __name__ == '__main__':
    rng = random.Random(0)
    print(pairs())
    Y, V, U = pairs()[0]
    base = (('S', 'H', 'S'), [(0, (0, 0, 0)), (0, (0, 0, 0)), (0, (0, 0, 0))], [0, 0, 0])
    al = aligned_places(rng, Y, V, U, base)
    print(len(al), al[:10])
