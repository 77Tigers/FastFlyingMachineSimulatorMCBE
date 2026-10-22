import sys, json, time, square
from concurrent.futures import ProcessPoolExecutor
def one(k):
    t = time.time(); r, par = square.search(k)
    if r is None: return k, None, None, time.time() - t
    r.flyer(max(r.size()) + 3 * k + 10).save(f'out/n{k}_square.flyer')
    return k, max(r.size()), par, time.time() - t
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else list(range(3, 25))
    res = {}
    with ProcessPoolExecutor(6) as ex:
        for k, body, par, dt in ex.map(one, ks):
            print(k, body, par, round(dt, 1), flush=True); res[k] = (body, par)
    json.dump({str(k): v for k, v in res.items()}, open('out/square_params.json', 'w'))
