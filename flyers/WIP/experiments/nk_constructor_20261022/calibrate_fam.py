"""offline: search one family's words for each k and keep it in bits.json only if it beats the current word.
python calibrate_fam.py FAMILY_INDEX K1,K2,... [WORKERS]"""
import sys, json, pathlib
from concurrent.futures import ProcessPoolExecutor
import families as F, square
from calibrate import flies
HERE = pathlib.Path(__file__).resolve().parent


def one(args):
    fam, k, cur = args
    best = None
    cand = []
    for bv in range(16):
        for lv in range(16):
            word = fam | (bv << 2) | (lv << 6)
            try: r = F.build(k, word)
            except Exception: continue
            if r is None: continue
            cand.append((max(r.size()) + k, word))
    cand.sort()
    for pl, word in cand:
        if cur is not None and pl >= cur: break
        r = F.build(k, word); L = r.T.L; m = L // 4
        sub = sorted({(X + d) % L for X in (0, 1, m, 2 * m, 3 * m) for d in range(-3, 4)})
        if r.check(sub): continue
        if flies(r, k, f'{k}_{word}'): best = (pl, word); break
    return k, cur, best


if __name__ == '__main__':
    fam = int(sys.argv[1]); ks = [int(x) for x in sys.argv[2].split(',')]
    nw = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    bits = json.load(open(HERE / 'bits.json'))
    def cur_pl(k):
        r = F.build(k, bits[str(k)]); return max(r.size()) + k if r else None
    jobs = [(fam, k, cur_pl(k)) for k in ks]
    with ProcessPoolExecutor(nw) as ex:
        for k, cur, best in ex.map(one, jobs):
            print(k, 'current', cur, 'new', best, flush=True)
            if best:
                b = json.load(open(HERE / 'bits.json')); b[str(k)] = best[1]; json.dump(b, open(HERE / 'bits.json', 'w'))
