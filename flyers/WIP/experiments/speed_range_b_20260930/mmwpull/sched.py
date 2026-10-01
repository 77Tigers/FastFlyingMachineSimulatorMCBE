"""Pull-twice mmwmmw lifecycle (agent F, 2026-10-01).

Slot = 2 ticks, cycle = 6 slots, every body advances 4 per cycle.
Body i moves in slot t iff S[i][t].  Body waits: b0 {2,5}, b1 {0,3}, b2 {1,4}.
For a body V with first wait slot w (w, w+3 are its waits; moves w+1,w+2,w+4,w+5):
  A  sticky (faces -X) ahead of lane L1: extends (empty) at w, retracts at w+1 pulling cell1 (+X)
  P  normal (faces +X) behind lane L1:  pushes cell1 at w+2
  B  sticky ahead of lane L2: extends at w+3, pulls cell2 at w+4
  Q  normal behind lane L2: pushes cell2 at w+5
So every V move is: pull (w+1), push (w+2), pull (w+4), push (w+5).
REL[k][s] = piston x minus pulled/pushed glue x of V, at the START of slot s-w (s relative to w).
"""
S = ((1, 1, 0, 1, 1, 0), (0, 1, 1, 0, 1, 1), (1, 0, 1, 1, 0, 1))
DISP = [[sum(s[:t]) for t in range(7)] for s in S]
W = [S[i].index(0) for i in range(3)]          # first wait slot: b0->2, b1->0, b2->1

#            slot rel to w:  0   1   2   3   4   5
REL = dict(A=(2, 2, 1, 1, 2, 2),
           B=(1, 2, 2, 2, 2, 1),
           P=(-2, -1, -1, -2, -2, -2),
           Q=(-2, -2, -2, -2, -1, -1))
FIRE = dict(A=0, B=3, P=2, Q=5)
STICKY = dict(A=True, B=True, P=False, Q=False)
LANE = dict(A=1, B=2, P=1, Q=2)


def X_of(v):
    """body that moves at w_v and waits at w_v-1 (carries redstone for v's stickies)"""
    return next(j for j in range(3) if not S[j][(W[v] - 1) % 6])


def Z_of(v):
    return next(j for j in range(3) if not S[j][(W[v] + 1) % 6])


def piston_x(v, k, t):
    """x offset (relative to V's frame origin at t=0, i.e. V glue at x=0) at start of slot t (t may be 0..6)."""
    s = (t - W[v]) % 6
    return REL[k][s] + DISP[v][t]


def moves(v, k, t):
    return piston_x(v, k, t + 1) - piston_x(v, k, t) == 1 if t < 5 else (piston_x(v, k, 0) + 4 - piston_x(v, k, 5)) == 1


def fire(v, k):
    return (W[v] + FIRE[k]) % 6


def carrier_kind(v, k, t):
    """'frozen', 'V' (own body: adhesion/obstruction) or 'foreign' for the slot t move of piston k."""
    f = fire(v, k)
    if t in (f, (f + 1) % 6):
        return 'frozen'
    return 'V' if S[v][t] else 'foreign'


def check():
    for v in range(3):
        for k in 'ABPQ':
            mv = [moves(v, k, t) for t in range(6)]
            f = fire(v, k)
            assert sum(mv) == 4, (v, k, mv)
            assert not mv[f] and not mv[(f + 1) % 6], (v, k, mv, f)


def table():
    out = []
    out.append('slot   ' + ' '.join(f'{t:>9}' for t in range(6)))
    for v in range(3):
        out.append(f'b{v} move ' + ' '.join(f'{"M" if S[v][t] else "w":>9}' for t in range(6)) + f'   X=b{X_of(v)} Z=b{Z_of(v)}')
        for k in 'ABPQ':
            cells = []
            for t in range(6):
                c = carrier_kind(v, k, t)
                rel = REL[k][(t - W[v]) % 6]
                tag = {'frozen': 'FIRE' if t == fire(v, k) else 'frz', 'V': 'own', 'foreign': 'FOREIGN'}[c]
                cells.append(f'{tag}@{rel:+d}')
            out.append(f'  {k}{"s" if STICKY[k] else "n"}   ' + ' '.join(f'{c:>9}' for c in cells))
    return '\n'.join(out)


if __name__ == '__main__':
    check()
    print(table())
