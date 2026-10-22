"""Build a square ring (L=20 for k=8) from a joint_cp result: straight links use the CP's E cells (cover +
connector) verbatim; corner links get the CP cover cells only and are connected by nk.Ring.route.
python build_sq.py RESULT.json OUT.flyer [cvy cvz | search]"""
import sys, json, itertools
sys.path.insert(0, '../nk_constructor_20261022')
from nk import Timing, Ring
import square


def module(res, cont):
    return dict(R=[(0,) + tuple(r) for r in res['R']], P=[tuple(p) for p in res['P']],
                PLATE=[(1,) + tuple(p) for p in res['PL']], CONT=cont, size=(res['a'], res['b']))


def build(res, cv, k=8):
    L = square.ring_size(k); m = L // 4; T = Timing(k, L)
    E = [(e[0],) + tuple(e[1]) for e in res['E']]
    P = {tuple(p) for p in res['P']}
    nb = lambda l: [(l[0] + 1, l[1]), (l[0] - 1, l[1]), (l[0], l[1] + 1), (l[0], l[1] - 1)]
    cover = [e for e in E if (e[0] == -3 and e[1:] in P) or (e[0] == -2 and any(v in P for v in nb(e[1:])))]
    straight, corner = module(res, E), module(res, cover)
    mods = [corner if j % m == m - 1 else straight for j in range(L)]
    place = square.square_layout(L, res['a'], res['b'], tuple(res['step']), cv)
    r = Ring(T, mods, place)
    for X in range(L):
        if X % m == 0: r.route(X)          # bodies covering a corner predecessor
    return r


if __name__ == '__main__':
    res = json.load(open(sys.argv[1]))
    if len(sys.argv) > 3 and sys.argv[3] == 'search':
        a, b = res['a'], res['b']; best = None
        for cv in itertools.product(range(-3, a + b + 4), range(-3, a + b + 4)):
            try:
                r = build(res, cv)
            except (RuntimeError, AssertionError):
                continue
            s = max(r.size()); bad = r.check(list(range(0, 3)) + [4, 5, 6])
            if not bad and (best is None or s < best[0]): best = (s, cv); print('cv', cv, 'max', s, r.size()[:6], flush=True)
        cv = best[1]
    else:
        cv = (int(sys.argv[3]), int(sys.argv[4]))
    r = build(res, cv)
    bad = r.check()
    print('cv', cv, 'sizes', r.size(), 'max', max(r.size()), 'bad', len(bad), bad[:4])
    r.flyer(max(r.size()) + 8).save(sys.argv[2])
