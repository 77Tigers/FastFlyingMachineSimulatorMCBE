"""Mixed-module link tables: U module type a, X module type b (strict, link A->B, x = s-3).
usage: python mixed_link.py MODS.json IA IB PROCS R OUT   (MODS rows like clusters json)"""
import sys, json
from multiprocessing import Pool
import ring_designer as rd
from ring_designer import Ring, ORDER, hard_conflicts
from module_eval import mod_of
rd.STRICT = True
FAR = 60


def ev(a):
    ma, mb, rel = a
    place = {Y: (0, (FAR * (i + 1), FAR * (i + 1)), 0) for i, Y in enumerate(ORDER)}
    place['A'] = (0, (0, 0), 0); place['B'] = rel
    mods = {'A': ma, 'B': mb, 'C': ma, 'D': mb}
    try:
        ring = Ring(mods, place)
        if hard_conflicts(ring, first=True): return None
        ring.route('B', maxlen=10)
        bad = [b for b in ring.check() if (b[0] == 'B' and 'not carried' not in b[2]) or (b[0] == 'A' and 'carried by B' in b[2])]
        if bad: return None
        return (len(ring.glue['B']), rel)
    except Exception:
        return None


if __name__ == '__main__':
    rows = json.load(open(sys.argv[1])); ia, ib = int(sys.argv[2]), int(sys.argv[3])
    procs, R, out = int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    ma, mb = mod_of(*rows[ia][3:6]), mod_of(*rows[ib][3:6])
    jobs = [(ma, mb, (s - 3, (oy, oz), sym)) for s in range(0, 6) for sym in range(8)
            for oy in range(-R, R + 1) for oz in range(-R, R + 1)]
    with Pool(procs) as p: res = [x for x in p.imap_unordered(ev, jobs, chunksize=32) if x]
    json.dump(res, open(out, 'w'))
    for syms in [(1, 3), (0,), (2,), (4, 5, 6, 7)]:
        print(ia, '->', ib, syms, [min([g for g, rel in res if rel[0] == s - 3 and rel[2] in syms] or [99]) for s in range(6)], flush=True)
