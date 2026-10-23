import sys
from concurrent.futures import ProcessPoolExecutor
def job(k):
    import exp_ring, calibrate as C, square
    return k, square.ring_size(k), C.one(k, [0, 1])
if __name__ == '__main__':
    with ProcessPoolExecutor(8) as ex:
        for r in ex.map(job, [int(x) for x in sys.argv[1].split(',')]): print(r, flush=True)
