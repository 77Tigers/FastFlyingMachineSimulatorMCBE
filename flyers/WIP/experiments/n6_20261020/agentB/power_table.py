"""Which bodies can time-power a piston, by relative-offset uniqueness (aligned rests, V = body 0).
Bodies 0..3 rest at global {0,1},{2,3},{4,5},{6,7}. A source block rigid on Z touches the piston (fixed
geometry) iff z(t) - p(t) equals one value r; the piston must be powered at tick 1 of exactly one slot.
RB/rod: power at every slot t whose value equals r.  Observer on Z: power at t only if Z moved in slot t-1."""
REST = [0, 2, 4, 6]
def moves(b, t): return (t % 8) not in (REST[b], REST[b] + 1)
def pos(b):            # position at start of slots 0..8
    p = [0]
    for t in range(8): p.append(p[-1] + moves(b, t))
    return p

def hopping(k):
    """V(=0)'s hopping pusher fired at V-local k: rides V 2..k-1, still k,k+1, carried by W(=1) k+2..1"""
    v, w = pos(0), pos(1)
    p = [None] * 9; p[2] = v[2] - 1
    seq = [(t % 8) for t in range(2, 10)]
    for t in seq:                       # slot t moves p to start of t+1
        nt = t + 1
        if t == k or t == (k + 1) % 8: step = 0
        elif 2 <= t <= k - 1: step = moves(0, t)
        else: step = moves(1, t)
        cur = p[t] if p[t] is not None else None
        p[nt % 8 if nt % 8 != 0 or t != 7 else 8] = cur + step if nt != 8 else cur + step
        if nt == 8: p[0] = cur + step - 6
    return p[:8]

def options(p, fire, label):
    out = []
    for Z in range(4):
        z = pos(Z)
        val = [z[t] - p[t] for t in range(8)]
        if sum(1 for t in range(8) if val[t] == val[fire]) == 1: out.append(f'RB on {Z}')
        pul = [t for t in range(8) if moves(Z, (t - 1) % 8)]
        if fire in pul and sum(1 for t in pul if val[t] == val[fire]) == 1: out.append(f'observer on {Z}')
    print(label, 'fires at slot', fire, '->', out or 'NONE')

for k in range(2, 8):
    options(hopping(k), k, f'hopping pusher of body 0, V-local {k}:')
for H in range(1, 4):
    options(pos(H)[:8], REST[H], f'rigid piston on body {H} (fires at its local 0 = global {REST[H]}):')
