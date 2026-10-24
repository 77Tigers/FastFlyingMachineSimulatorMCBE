"""offline: best slab/lat word per k under the current decoding -> out/bits_sl.json (merged later)"""
import sys, json, pathlib
from concurrent.futures import ProcessPoolExecutor
import calibrate as C
HERE = pathlib.Path(__file__).resolve().parent
def job(k): return C.one(k, [0, 1])
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    p = HERE / 'out/bits_sl.json'
    out = json.load(open(p)) if p.exists() else {}
    with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 6) as ex:
        for k, best in ex.map(job, ks):
            print(k, best, flush=True)
            if best: out[str(k)] = list(best); json.dump(out, open(p, 'w'))
