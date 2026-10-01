"""Abstract rider-balance bound for the pull-twice lifecycle (agent F).

V has w=0 (moves 1,2,4,5). X (waits 5,2) moves 0,1,3,4. Z (waits 1,4) moves 0,2,3,5.
For each of V's pistons choose adjacency adj[Y][t] (Y in V,X,Z; slot start t) subject to:
  * every moving slot of k has >=1 moving adjacent body (carriers = moving adjacent bodies; each counts a rider)
  * continuity: if Y and k both move or both stay during slot t, adjacency at t+1 equals adjacency at t
  * fire slot: no moving adjacent body (except V for its own pusher P/Q)
  * P at slot 1 and Q at slot 4 (sitting behind V's contact cell, destination occupied): only V may touch;
    V must touch (contact). A at 2 / B at 5: V touches (obstruction).
Body load at its relative slot r = own(r) + Xrole(r-1) + Zrole(r+1)  (rotational symmetry of the schedule).
"""
import itertools
MV = dict(V=(0, 1, 1, 0, 1, 1), X=(1, 1, 0, 1, 1, 0), Z=(1, 0, 1, 1, 0, 1))
REL = dict(A=(2, 2, 1, 1, 2, 2), B=(1, 2, 2, 2, 2, 1), P=(-2, -1, -1, -2, -2, -2), Q=(-2, -2, -2, -2, -1, -1))
FIRE = dict(A=0, B=3, P=2, Q=5)
BODIES = 'VXZ'


def kmoves(k):
    f = FIRE[k]
    return tuple(int(t not in (f, (f + 1) % 6)) for t in range(6))


def patterns(k):
    km = kmoves(k)
    f = FIRE[k]
    res = set()
    for bits in itertools.product((0, 1), repeat=18):
        adj = {Y: bits[6 * i:6 * i + 6] for i, Y in enumerate(BODIES)}
        ok = True
        for Y in BODIES:
            for t in range(6):
                if MV[Y][t] == km[t] and adj[Y][(t + 1) % 6] != adj[Y][t]:
                    ok = False; break
            if not ok:
                break
        if not ok:
            continue
        for t in range(6):
            movers = [Y for Y in BODIES if MV[Y][t] and adj[Y][t]]
            if km[t] and not movers:
                ok = False; break
            if t == f and any(Y != 'V' or k in 'AB' for Y in movers):
                ok = False; break
        if not ok:
            continue
        if k == 'P' and (not adj['V'][1] or adj['X'][1] and MV['X'][1] or adj['Z'][1] and MV['Z'][1]):
            continue
        if k == 'Q' and (not adj['V'][4] or adj['X'][4] and MV['X'][4] or adj['Z'][4] and MV['Z'][4]):
            continue
        if k == 'A' and not adj['V'][2]:
            continue
        if k == 'B' and not adj['V'][5]:
            continue
        cnt = tuple(int(km[t] and MV[Y][t] and adj[Y][t]) for Y in BODIES for t in range(6))
        res.add(cnt)
    return res


def main():
    P = {k: patterns(k) for k in 'ABPQ'}
    print({k: len(v) for k, v in P.items()})
    best = None
    for combo in itertools.product(*[sorted(P[k]) for k in 'ABPQ']):
        tot = [sum(c[i] for c in combo) for i in range(18)]
        own = tot[0:6]; xr = tot[6:12]; zr = tot[12:18]
        loads = [own[r] + xr[(r - 1) % 6] + zr[(r + 1) % 6] for r in (1, 2, 4, 5)]
        key = (max(loads), sum(loads))
        if best is None or key < best[0]:
            best = (key, loads, combo)
    print(best[0], best[1])
    for k, c in zip('ABPQ', best[2]):
        print(k, 'V', c[0:6], 'X', c[6:12], 'Z', c[12:18])


if __name__ == '__main__':
    main()
