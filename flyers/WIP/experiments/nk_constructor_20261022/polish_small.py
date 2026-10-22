"""offline: for small k try module families x wide square candidates, full routing + checker + 1-seed sim; report
improvements over square_table.json."""
import sys, json, subprocess, pathlib
import construct, square, sqbuild
from concurrent.futures import ProcessPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent; NK = str(HERE / 'out/target/release/nkcheck.exe')
def one(k):
    t = json.load(open(HERE / 'square_table.json')); cur = max(sqbuild.build_fast(k, t).size())
    best = None
    for fam in ('slabP', 'cp', 'latcp'):
        mod = construct.grid_module(k, fam); a, b = mod['size']; L = square.ring_size(k); m = L // 4
        cands = sqbuild.candidates(a, b, m) if m == 1 else [((a + gy, sz), (cy, cz)) for gy in (1, 2) for sz in (-2, -1, 0, 1)
                                                            for cy in range(a - 2, a + 2) for cz in range(b - 1, b + 4)]
        for step, cv in cands:
            try: r = sqbuild.assemble(k, mod, step, cv)
            except Exception: continue
            if r is None: continue
            body = max(r.size())
            if body >= cur or (best and body >= best[0]): continue
            if r.check(): continue
            p = HERE / f'out/ps{k}.flyer'; r.flyer(body + k).save(str(p))
            P = 2 * (k + 2); n = -(-1000 // k) + 1
            out = subprocess.run([NK, str(p), str(n * P), '1000', '1', 'at', str(body + k)], capture_output=True, text=True).stdout
            if 'minpl=' + str(body + k) in out: best = (body, [list(step), list(cv), fam])
    return k, cur, best
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    with ProcessPoolExecutor(3) as ex:
        for k, cur, best in ex.map(one, ks): print(k, cur, best, flush=True)
