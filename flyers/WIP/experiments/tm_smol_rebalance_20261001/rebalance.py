"""Greedy local search that lowers the number of actions at the push limit while keeping a flyer running.

python rebalance.py IN.flyer OUTDIR [LIMIT=12] [ROUNDS=1] [TICKS=600]

Each round generates single edits of the current best flyer:
  del  : remove one glue/redstone cell
  move : remove one glue/redstone cell and place the same kind (or the other glue) in an empty cell
         within Chebyshev distance 2 that touches an existing glue/redstone cell
and screens them with loadhist.exe (TICKS ticks, histogram from tick 100, encoded LIMIT).
A variant is kept only if it travels the full 3 bps distance (TICKS*0.3) with zero failures, conserves kinds, and
has max load <= LIMIT. Score = (actions at LIMIT, actions at LIMIT-1, block count). Results go to OUTDIR/roundN.csv;
the round winner is saved as OUTDIR/bestN.flyer.
"""
import sys, pathlib, subprocess, csv, shutil, uuid, itertools
from concurrent.futures import ThreadPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from fastflyer.research import binary
    return binary(n)

EXE = _tb('loadhist')
WORKERS = 10
GLUE = (Kind.SLIME, Kind.HONEY)
EDITABLE = (Kind.SLIME, Kind.HONEY, Kind.REDSTONE_BLOCK)
FACES = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def clone(f):
    g = Flyer(f.phase_x, f.phase_z, f.rng_state, f.push_limit)
    for p, b in f.blocks(): g.set(p, b)
    return g


def add(p, d): return (p[0]+d[0], p[1]+d[1], p[2]+d[2])


def variants(f):
    cells = {tuple(p): b for p, b in f.blocks()}
    edit = [p for p, b in cells.items() if b.kind in EDITABLE]
    out = {}
    for p in edit:
        k = cells[p].kind
        g = clone(f); g.remove(p); out[f'del_{p[0]}_{p[1]}_{p[2]}'] = g
        kinds = [k] if k == Kind.REDSTONE_BLOCK else list(GLUE)
        for d in itertools.product(range(-2, 3), repeat=3):
            e = add(p, d)
            if e == p or e in cells: continue
            if not any(add(e, fd) in cells and cells[add(e, fd)].kind in EDITABLE and add(e, fd) != p for fd in FACES):
                continue
            for k2 in kinds:
                g = clone(f); g.remove(p); g.set(e, Block(k2))
                out[f'mv_{p[0]}_{p[1]}_{p[2]}_to_{e[0]}_{e[1]}_{e[2]}_{k2.name[0]}'] = g
    return out


def screen(flyers, outdir, ticks, limit):
    wd = outdir / f'tmp_{uuid.uuid4().hex[:8]}'
    wd.mkdir(parents=True)
    names = sorted(flyers)
    for n in names: flyers[n].save(wd / f'{n}.flyer')
    chunks = [names[i::WORKERS] for i in range(WORKERS)]
    def run(chunk):
        if not chunk: return []
        p = subprocess.run([str(EXE), str(ticks), '100', str(limit)] + [str(wd / f'{n}.flyer') for n in chunk],
                           capture_output=True, text=True)
        return list(csv.DictReader(p.stdout.splitlines()))
    rows = []
    with ThreadPoolExecutor(WORKERS) as ex:
        for r in ex.map(run, chunks): rows += r
    shutil.rmtree(wd, ignore_errors=True)
    return rows


def ok(r, ticks, limit):
    return (int(r['distance']) >= ticks * 3 // 10 and r['failures'] == '0' and r['conserved'] == 'true'
            and int(r['max_load']) <= limit)


def key(r, nblocks):
    return (int(r['n_at_limit']), int(r['n_at_limit_m1']), nblocks[r['name']])


def main():
    src = pathlib.Path(sys.argv[1]); outdir = pathlib.Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    rounds = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    ticks = int(sys.argv[5]) if len(sys.argv) > 5 else 600
    cur = Flyer.load(src); cur.push_limit = limit
    base = screen({'base': cur}, outdir, ticks, limit)[0]
    print('start', base['n_at_limit'], base['n_at_limit_m1'], base['hist'], flush=True)
    best_key = (int(base['n_at_limit']), int(base['n_at_limit_m1']), len(list(cur.blocks())))
    for rnd in range(1, rounds + 1):
        vs = variants(cur)
        nblocks = {n: len(list(g.blocks())) for n, g in vs.items()}
        rows = screen(vs, outdir, ticks, limit)
        with open(outdir / f'round{rnd}.csv', 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        good = sorted((r for r in rows if ok(r, ticks, limit)), key=lambda r: key(r, nblocks))
        print(f'round {rnd}: {len(vs)} variants, {len(good)} run clean', flush=True)
        for r in good[:8]: print('  ', r['name'], r['n_at_limit'], r['n_at_limit_m1'], r['hist'], flush=True)
        if not good or key(good[0], nblocks) >= best_key:
            print('no improvement; stop', flush=True); break
        best_key = key(good[0], nblocks)
        cur = vs[good[0]['name']]
        cur.save(outdir / f'best{rnd}.flyer')
        (outdir / f'best{rnd}.txt').write_text(good[0]['name'] + '\n')


if __name__ == '__main__':
    main()
