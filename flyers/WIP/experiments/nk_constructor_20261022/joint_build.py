"""Square ring from a joint_cp result (module + next body's straight-link glue E = cover + connector, solved together;
idea from the nk_newmech subagent, its build_sq.py generalised to any k). Straight links use E verbatim; the body
before each corner gives only cover cells, and the 4 corner bodies are connected by the router.
python joint_build.py K1,K2   (search corner offsets, simulate, store in joint_table.json)"""
import sys, json, itertools, subprocess, pathlib
import square
from nk import Timing, Ring

HERE = pathlib.Path(__file__).resolve().parent
NK = str(HERE / 'out/target/release/nkcheck.exe')


def module(res, cont):
    return dict(R=[(0,) + tuple(r) for r in res['R']], P=[tuple(p) for p in res['P']],
                PLATE=[(1,) + tuple(p) for p in res['PL']], CONT=cont, size=(res['a'], res['b']))


def build(k, res, cv):
    L = square.ring_size(k); m = L // 4; T = Timing(k, L)
    E = [(e[0],) + tuple(e[1]) for e in res['E']]
    P = {tuple(p) for p in res['P']}
    nb = lambda l: [(l[0] + 1, l[1]), (l[0] - 1, l[1]), (l[0], l[1] + 1), (l[0], l[1] - 1)]
    cover = [e for e in E if (e[0] == -3 and e[1:] in P) or (e[0] == -2 and any(v in P for v in nb(e[1:])))]
    straight, corner = module(res, E), module(res, cover)
    mods = [corner if j % m == m - 1 else straight for j in range(L)]
    r = Ring(T, mods, square.square_layout(L, res['a'], res['b'], tuple(res['step']), tuple(cv)))
    for X in range(0, L, m): r.route(X)
    return r


def sim_ok(r, k):
    pl = max(r.size()) + k; p = HERE / f'out/jb{k}.flyer'; r.flyer(pl).save(str(p))
    P = 2 * (k + 2); n = -(-1000 // k) + 1
    out = subprocess.run([NK, str(p), str(n * P), '1000', '1', 'at', str(pl)], capture_output=True, text=True).stdout
    return f'minpl={pl}' in out


def search(k, res):
    a, b = res['a'], res['b']; L = square.ring_size(k); m = L // 4
    cands = []
    for cv in itertools.product(range(-2, a + b + 3), range(-2, a + b + 3)):
        try: r = build(k, res, cv)
        except (RuntimeError, AssertionError): continue
        cands.append((max(r.size()), cv, r))
    cands.sort(key=lambda c: c[0])
    for s, cv, r in cands[:15]:
        sub = sorted({(X + d) % L for X in (0, m) for d in range(-2, 3)})
        if r.check(sub): continue
        if sim_ok(r, k): return s, cv
    return None


if __name__ == '__main__':
    mods = json.load(open(HERE / 'modules_joint.json'))
    tab = json.load(open(HERE / 'joint_table.json')) if (HERE / 'joint_table.json').exists() else {}
    for k in [int(x) for x in sys.argv[1].split(',')]:
        if str(k) not in mods: continue
        res = search(k, mods[str(k)])
        print(k, 'joint cost', mods[str(k)]['cost'], '->', res, flush=True)
        if res: tab[str(k)] = [res[0], list(res[1])]; json.dump(tab, open(HERE / 'joint_table.json', 'w'))
