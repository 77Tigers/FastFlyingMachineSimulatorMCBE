"""Build every N_k (k in range) with a family, find min PL over 3 seeds, print table + sum.
python run_all.py FAMILY [KMIN KMAX] [TICKS]"""
import sys, time, subprocess, pathlib, json
from concurrent.futures import ThreadPoolExecutor
import construct

HERE = pathlib.Path(__file__).resolve().parent
NK = HERE / 'out/target/release/nkcheck.exe'


def check(path, k, ticks, cases='1', fast=True):
    P = 2 * (k + 2); n = max(1, ticks // P) if ticks > 0 else 12
    r = subprocess.run([str(NK), str(path), str(n * P), str(n * k - k), cases] + (['fast'] if fast else []), capture_output=True, text=True)
    d = dict(kv.split('=', 1) for kv in r.stdout.split()[:4])
    return d


def check_at(path, k, pl, dist=1000):
    """one seed, untraced: pass at pl, fail at pl-1 => min PL = pl; else fall back to the traced search."""
    P = 2 * (k + 2); n = -(-dist // k) + 1
    while True:
        out = subprocess.run([str(NK), str(path), str(n * P), str(dist), '1', 'at', str(pl)], capture_output=True, text=True).stdout
        d = dict(kv.split('=', 1) for kv in out.split())
        if d['pass'] == 'true' and d['pass_below'] == 'false': return {'minpl': str(pl), 'first_fail': 'at'}
        if d['pass'] == 'true': pl -= 1; continue
        pl += 1
        if pl > 400: return {'minpl': 'FAIL', 'first_fail': 'at'}


def one(fam, k, ticks):
    t = time.time()
    try:
        if fam == 'sq':
            import sqbuild
            ring = sqbuild.build_fast(k, json.load(open(HERE / 'square_table.json')))
            if ring is None: raise RuntimeError('no square layout')
        else:
            ring = construct.build(k, fam)
    except Exception as e:
        return k, None, f'build error {e}', 0
    bt = time.time() - t
    p = construct.OUT / f'n{k}_{fam}.flyer'
    ring.flyer(max(ring.size()) + 3 * k + 10).save(str(p))
    d = check_at(p, k, max(ring.size()) + k)
    return k, d, f'L={ring.T.L} maxbody={max(ring.size())}', bt


if __name__ == '__main__':
    fam = sys.argv[1]
    k0, k1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (3, 24)
    ticks = int(sys.argv[4]) if len(sys.argv) > 4 else 0   # 0 = 12 cycles
    res = {}
    with ThreadPoolExecutor(4) as ex:
        for k, d, info, bt in ex.map(lambda k: one(fam, k, ticks), range(k0, k1 + 1)):
            pl = d['minpl'] if d else 'ERR'
            print(f'k={k:2d} minpl={pl:>5} build={bt:.2f}s {info} {d.get("first_fail", "") if d else ""}', flush=True)
            res[k] = int(pl) if d and pl.isdigit() else None
    ok = [v for v in res.values() if v]
    print(f'{fam}: solved {len(ok)}/{len(res)} sum={sum(ok)}')
    (HERE / 'out' / f'results_{fam}.json').write_text(json.dumps(res))
