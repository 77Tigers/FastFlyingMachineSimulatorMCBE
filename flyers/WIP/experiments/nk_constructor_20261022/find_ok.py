"""for one k and module family: try square layouts (checker-clean), simulate (1 seed, short), keep the first that flies."""
import sys, subprocess, pathlib, json
import construct, square, sqbuild
HERE = pathlib.Path(__file__).resolve().parent; NK = str(HERE / 'out/target/release/nkcheck.exe')
def find(k, fam):
    mod = construct.grid_module(k, fam); a, b = mod['size']; L = square.ring_size(k); m = L // 4
    cands = sqbuild.candidates(a, b, m) + [((a + gy, sz), (cy, cz)) for gy in (1, 2, 3) for sz in (-1, 0, 1)
                                         for cy in range(a - 1, a + 3) for cz in range(-1, b + 3)]
    res, seen = [], set()
    for step, cv in cands:
        if (step, cv) in seen: continue
        seen.add((step, cv))
        try: r = sqbuild.assemble(k, mod, step, cv)
        except Exception: continue
        if r is None or r.check(): continue
        res.append((max(r.size()), step, cv, r))
    res.sort(key=lambda x: x[0])
    for body, step, cv, r in res:
        p = HERE / f'out/t{k}.flyer'; r.flyer(body + k + 20).save(str(p))
        P = 2 * (k + 2)
        out = subprocess.run([NK, str(p), str(20 * P), str(10 * k), '1'], capture_output=True, text=True).stdout
        print(k, fam, body, step, cv, out.strip()[:80], flush=True)
        if 'FAIL' not in out: return body, step, cv
    return None
if __name__ == '__main__':
    print(find(int(sys.argv[1]), sys.argv[2]))
