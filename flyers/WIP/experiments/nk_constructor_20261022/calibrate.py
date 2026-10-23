"""offline: choose the 10-bit word per k (family, box, layout) by building + simulating every option;
modules are computed exactly as families.build does (deterministic CP), cached per (family, box). -> bits.json"""
import sys, json, subprocess, pathlib
from concurrent.futures import ProcessPoolExecutor
import families as F, square, construct, sqbuild
HERE = pathlib.Path(__file__).resolve().parent; NK = str(HERE / 'out/target/release/nkcheck.exe')


def flies(r, k, tag):
    pl = max(r.size()) + k; p = HERE / f'out/cal_{tag}.flyer'; r.flyer(pl).save(str(p))
    P = 2 * (k + 2); n = -(-1000 // k) + 1
    out = subprocess.run([NK, str(p), str(n * P), '1000', '1', 'at', str(pl)], capture_output=True, text=True).stdout
    return f'minpl={pl}' in out


def one(k):
    m = square.ring_size(k) // 4; L = square.ring_size(k)
    best = None   # (pl, word)
    fams = [0, 1] + ([2] if k <= 10 else [])
    for f in fams:
        boxes = [5] if f == 0 or m == 1 else range(16)
        for bv in boxes:
            lays = range(256) if m == 1 else range(16)
            for lv in lays:
                word = f | ((lv << 2) if m == 1 else ((bv << 2) | (lv << 6)))
                try: r = F.build(k, word)
                except Exception: continue
                if r is None: continue
                pl = max(r.size()) + k
                if best and pl >= best[0]: continue
                sub = sorted({(X + d) % L for X in (0, 1, m) for d in range(-2, 3)})
                if r.check(sub): continue
                if flies(r, k, f'{k}_{word}'): best = (pl, word)
    return k, best


if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else F.KS
    out = json.load(open(HERE / 'bits.json')) if (HERE / 'bits.json').exists() else {}
    with ProcessPoolExecutor(4) as ex:
        for k, best in ex.map(one, ks):
            print(k, best, flush=True)
            if best: out[str(k)] = best[1]; json.dump(out, open(HERE / 'bits.json', 'w'))
