"""Single-process resume of sweep_pr.py (Windows multiprocessing crashed).  Skips (map, d) already listed in
--skip logs, appends to --log.  Assumes the original run was: sweep_pr.py L7_w2 7 --w mwwm,wmwm --nw 2 --r 1.
usage (use --wk 1 --threads 4 for 4 workers total): python sweep_resume.py L --w mwwm,wmwm --nw 2 --log runs/sweep/L7_w2_resume.log [--tl 60] [--wk 4]
       [--skip runs/sweep/L7_w2.log] [--retry-unknown 300]"""
import sys, re, time, argparse
from sweep_pr import *
ap = argparse.ArgumentParser()
ap.add_argument('L', type=int); ap.add_argument('--w', default='mwwm,wmwm'); ap.add_argument('--nw', type=int, default=2)
ap.add_argument('--r', type=int, default=1); ap.add_argument('--tl', type=float, default=60); ap.add_argument('--wk', type=int, default=1)
ap.add_argument('--log', required=True); ap.add_argument('--skip', nargs='*', default=[])
ap.add_argument('--threads', type=int, default=4); ap.add_argument('--retry-unknown', type=float, default=300); ap.add_argument('--fmax', type=int, default=4)
a = ap.parse_args()
ww = [WORDS[w] if w in WORDS else tuple(int(c) for c in w) for w in a.w.split(',')]
ms = {'K4': None, 'K5': None, 'V': 1}
pat = re.compile(r'^(\S+) \(([^)]*)\) (\S+) ([\d.]+)$')
done, unknown = set(), []
for f in a.skip + [a.log]:
    try: lines = open(f).read().splitlines()
    except FileNotFoundError: continue
    for ln in lines:
        m = pat.match(ln)
        if not m: continue
        key = (m[1], tuple(int(v) for v in m[2].split(',')))
        if m[3] == 'UNKNOWN': unknown.append(key)
        else: done.add(key)
        if m[3] == 'UNKNOWN' and f == a.log: pass
cands = sorted(candidates(list(YZ), 5, a.fmax, range(-3, 2)), key=lambda c: (c[2], abs(c[1][0] + 1)))
print('candidates', len(cands), 'already done', len(done), 'unknown to retry', len(set(unknown)), flush=True)
log = open(a.log, 'a')
cnt = {}
def run(mp, d, tl):
    args, st, dt, rep = one((mp, d, a.L, ww, a.r, tl, a.nw, a.wk, ms))
    log.write(f'{mp} {d} {st} {dt:.1f}\n'); log.flush()
    cnt[st] = cnt.get(st, 0) + 1
    if rep: print('FOUND', mp, d, st, '\n' + rep, flush=True)
    return st
from concurrent.futures import ThreadPoolExecutor, as_completed
# threads (CP-SAT releases the GIL): one process, threads x wk workers in total
todo = [(mp, tuple(d)) for mp, d, _ in cands if (mp, tuple(d)) not in done and (mp, tuple(d)) not in set(unknown)]
n = 0
with ThreadPoolExecutor(a.threads) as ex:
    futs = {ex.submit(run, mp, d, a.tl): (mp, d) for mp, d in todo}
    for f in as_completed(futs):
        n += 1
        if f.result() == 'UNKNOWN': unknown.append(futs[f])
        if n % 25 == 0: print(n, cnt, flush=True)
print('first pass done', cnt, flush=True)
with ThreadPoolExecutor(a.threads) as ex:
    rt = [(mp, d) for mp, d in sorted(set(unknown)) if (mp, d) not in done]
    for (mp, d), f in zip(rt, [ex.submit(run, mp, d, a.retry_unknown) for mp, d in rt]):
        print('retry', mp, d, f.result(), flush=True)
print('done', cnt, flush=True)
