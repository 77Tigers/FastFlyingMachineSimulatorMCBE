"""scan every uniform stack parameter list for k and M middle levels (stack.py); saves the best ring per params to
out/stack/ and simulates it (1 seed, 1000 blocks). python stack_scan.py K M [NLAY] [BACK_INDEX]"""
import sys, os, time, itertools
from concurrent.futures import ProcessPoolExecutor
import stack, tower2, square, bank_links
from nk import bodies_for


def back_entry(k, bi):
    """bi: int = extension-bank link index (n = k-1); 'path:i' = i-th link of a link0_screen output file"""
    if isinstance(bi, int) or bi.isdigit(): return bank_links.links(k - 1)[int(bi)]
    if bi.startswith('lat:'):   # side-contact CP module for k-1 hoppers in an A x B box, straight step (A+G, SZ)
        import families as F
        v = list(map(int, bi[4:].split(',')))
        A, B, SZ = v[:3]; G = v[3] if len(v) > 3 else 1; mir = len(v) > 4 and v[4]
        mod = F.lat_module(k - 1, A, B)
        if mir: mod = F.mirror_y(mod)
        return dict(mod=mod, step=(A + G, SZ), cv=(A - 1, B + 1))
    import ast
    path, i = bi.rsplit(':', 1)
    rows = [l for l in open(path) if l.startswith('((') or (l.startswith('(') and "'P'" in l)]
    line = rows[int(i)].strip(); a1 = line.index(') (') + 1; a2 = line.index(') {') + 1
    f, step, mod = ast.literal_eval(line[:a1]), ast.literal_eval(line[a1:a2]), ast.literal_eval(line[a2:])
    mod = {kk: [tuple(c) for c in v] if isinstance(v, list) else tuple(v) for kk, v in mod.items()}
    return dict(mod=mod, step=tuple(step), cv=f[2])


def job(args):
    k, params, nlay, bi, cv = args
    e = back_entry(k, bi)
    xo = tower2.balanced_xoff(k, square.ring_size(k), bodies_for(k) - 1)
    st = {}; t = time.time(); res = None
    for c in (cv if isinstance(cv, list) else [cv]):
        rr = stack.construct(k, (e["mod"], e["step"]), params, c, xo, nlay, stats=st,
                             max_leaves=int(os.environ.get("LEAVES", 40)))
        if rr and (res is None or rr[0] < res[0][0]): res = (rr, c)
    if not res: return params, None, st, time.time() - t
    (p, lc, r), cv = res
    name = 'out/stack/n%02d_' % k + '_'.join('%d%d' % ms for ms in params) + f'_b{str(bi).split("/")[-1].replace(":", "")}_c{cv[0]}{cv[1]}.flyer'.replace('-', 'm')
    r.flyer(p + 10).save(name)
    from tower import min_pl
    return params, (p, lc, cv, min_pl(name, k, p + 1), name), st, time.time() - t


if __name__ == '__main__':
    k, M = int(sys.argv[1]), int(sys.argv[2])
    nlay = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    bi = sys.argv[4] if len(sys.argv) > 4 else '0'
    if len(sys.argv) > 5 and sys.argv[5] == 'scan':   # corner offsets: the cheapest back rings
        e = back_entry(k, bi)
        cv = stack.back_corners(k, e['mod'], e['step'], span=8, keep=int(os.environ.get('NCV', 6)))
        print('corners', cv, flush=True)
    else:
        cv = tuple(map(int, sys.argv[5].split(','))) if len(sys.argv) > 5 else back_entry(k, bi).get('cv', (5, -2))
    os.makedirs('out/stack', exist_ok=True)
    pfix = [tuple(map(int, t.split(','))) for t in os.environ['PFIX'].split(';')] if os.environ.get('PFIX') else []
    jobs = [(k, p, nlay, bi, cv) for p in stack.all_params(k, M) if p[:len(pfix)] == pfix]
    print(len(jobs), 'param sets', flush=True)
    with ProcessPoolExecutor(int(os.environ.get('SW', 12))) as ex:
        for params, res, st, dt in ex.map(job, jobs):
            print(params, res, st, round(dt, 1), flush=True)
