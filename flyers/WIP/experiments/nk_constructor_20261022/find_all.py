import sys, json
from concurrent.futures import ProcessPoolExecutor
import find_ok
def one(args):
    k, fam = args
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): r = find_ok.find(k, fam)
    return k, fam, r
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]; fam = sys.argv[2]
    with ProcessPoolExecutor(4) as ex:
        for k, fam, r in ex.map(one, [(k, fam) for k in ks]): print(k, fam, r, flush=True)
