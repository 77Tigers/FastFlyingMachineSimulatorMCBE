"""Generic hopper-cap builder on the 5-block alternating chain (see capped.py for the cap plan).
Helpers: make_rider(kind, fire, target, contact_cell) computes the rider's slot-0 cell and ride word;
attach_observer / ensure_ride use rigid.glue_path (BFS through cells free at every slot).
"""
import random, sys, pathlib, re
from rigid import Seg, check, to_flyer, add, D6, loads, glue_path, reserved_cells
from alt import altchain
X = (1, 0, 0)
def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def wpos(seg, c, t): return (seg.origin[0] + c[0] + seg.pos(t), seg.origin[1] + c[1], seg.origin[2] + c[2])
def lpos(seg, w, t): return (w[0] - seg.origin[0] - seg.pos(t), w[1] - seg.origin[1], w[2] - seg.origin[2])

def make_rider(name, kind, fire, target, contact):
    """kind 'P': fires at `fire` pushing target's contact; 'S': extends at `fire`, pulls at fire+1."""
    if kind == 'P':
        k = fire; at = sub(wpos(target, contact, k), X)
    else:
        k = fire; at = add(wpos(target, contact, (fire + 1) % 4 if fire < 3 else 4), (2, 0, 0))
        if fire == 3:   # pull at slot 0 of next cycle: target there = pos 2 more
            at = add(wpos(target, contact, 0), (4, 0, 0))
    rides = sorted({(fire + 2) % 4, (fire + 3) % 4})
    n_before = sum(1 for s in rides if s < fire)
    p0 = (at[0] - n_before, at[1], at[2])
    return Seg(name, tuple(rides), (0, 0, 0), {p0: kind}, rider=True, fire=fire)

def rider_world(r, t):
    return list(r.at(t))[0]

def attach_observer(seg, target_world, t, segs, rng):
    dirs = list(range(6)); rng.shuffle(dirs)
    for d in dirs:
        ow = sub(target_world, D6[d]); ol = lpos(seg, ow, t)
        if ol in seg.cells: continue
        res = reserved_cells(segs, seg, glue=False)
        if ol in res: continue
        seg.cells[ol] = ('O', d)
        goals = [add(ol, dd) for dd in D6]
        if glue_path(seg, goals, segs, rng, maxlen=2) is not None: return True
        del seg.cells[ol]
    return False

def ensure_ride(r, t, car, segs, rng, maxlen=3):
    rw = rider_world(r, t)
    goals = [lpos(car, add(rw, d), t) for d in D6]
    return glue_path(car, goals, segs, rng, maxlen=maxlen) is not None

def try_once(rng, n, a, c):
    chain = altchain(n, a, c)
    K0 = chain[0]; F = chain[-1]; E = chain[-2]; D = chain[-3]
    for cc, k in list(F.cells.items()):
        if k in ('P', 'S'): del F.cells[cc]
    Zo = (K0.origin[0] - 1, K0.origin[1] - a[0], K0.origin[2] - a[1])
    Z = Seg('Z', (2, 3), Zo, {(0, 0, 0): 'g', (0, a[0], a[1]): 'P', (0, -a[0], -a[1]): 'g'}, 'honey')
    segs = [Z] + chain
    # contacts (choose existing glue or extend by one glue cell)
    def pick_contact(seg, t, kind):
        cands = [cc for cc, k in seg.cells.items() if k == 'g']
        cc = rng.choice(cands)
        if rng.random() < 0.5:
            d = rng.choice(D6[2:]); nc = add(cc, d)
            if nc not in seg.cells and nc not in reserved_cells(segs, seg): seg.cells[nc] = 'g'; cc = nc
        return cc
    Hz = make_rider('Hz', 'S', 1, Z, pick_contact(Z, 2, 'S'))
    H = make_rider('H', 'P', 1, F, pick_contact(F, 1, 'P'))
    H2 = make_rider('H2', 'P', 3, E, pick_contact(E, 3, 'P'))
    allsegs = segs + [Hz, H, H2]
    for r in (Hz, H, H2):
        if list(r.cells)[0] in reserved_cells(allsegs, r, glue=False): return None, f'rider clash {r.name}'
    if not attach_observer(K0, rider_world(Hz, 1), 1, allsegs, rng): return None, 'obsK0'
    if not attach_observer(F, rider_world(H, 1), 1, allsegs, rng): return None, 'obsF'
    if not attach_observer(E, rider_world(H2, 3), 3, allsegs, rng): return None, 'obsE'
    for r, t, car in [(Hz, 3, Z), (Hz, 0, K0), (H, 3, E), (H, 0, F), (H2, 1, D), (H2, 2, E)]:
        if not ensure_ride(r, t, car, allsegs, rng): return None, f'ride {r.name}{t}'
    return allsegs, 'ok'

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
        if segs is None: st[why] = st.get(why, 0) + 1; continue
        r = check(segs)
        if r: k = re.sub(r'[-0-9(), ]+', '#', r); st[k] = st.get(k, 0) + 1; continue
        found += 1; L = loads(segs)
        if L < best: best = L
        to_flyer(segs, L).save(out / f'cap{found:04d}_L{L}.flyer')
        print('FOUND', found, 'load', L, [len(s.cells) for s in segs], flush=True)
    print('found', found, 'best', best)
    for k, v in sorted(st.items(), key=lambda x: -x[1])[:14]: print(v, k)
