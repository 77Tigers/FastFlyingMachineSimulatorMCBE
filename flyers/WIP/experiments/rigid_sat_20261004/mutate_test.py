"""Mutation test: satflyer verdict vs rigid.check on random single-block edits of known-good designs."""
import sys, pathlib, random, copy, pickle, os, io, contextlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
import rigid
import validate
from alt import altchain
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
KS = ['g', 'P', 'S', 'R', None]
cases = [(pickle.load(open(HERE.parent / 'rigid_chain_20261003' / 'back_leaf_A8B8_load9.pkl', 'rb')), ['a2', 'b2'], True),
         (altchain(6), ['K0', 'K5'], False)]
stats = {}
for it in range(int(sys.argv[2]) if len(sys.argv) > 2 else 30):
    base, opn, leaf = cases[it % 2]
    segs = copy.deepcopy(base)
    s = rng.choice([x for x in segs if x.name not in opn])
    c = rng.choice(list(s.cells))
    d = rng.choice(rigid.D6)
    nc = (c[0] + d[0], c[1] + d[1], c[2] + d[2])
    k = s.cells.pop(c)
    mode = rng.random()
    if mode < 0.5 and nc not in s.cells: s.cells[nc] = k          # move block
    elif mode < 0.8: s.cells[c] = rng.choice([q for q in KS[:4] if q != k])  # change kind
    # else: delete
    rigid.LEAF = leaf
    rc = rigid.check(segs, ignore=set(opn))
    with contextlib.redirect_stdout(io.StringIO()):
        try: st = validate.run(segs, opn, leaf)
        except Exception as e: st = 'EXC ' + str(e)
    key = ('rigid_ok' if rc is None else 'rigid_bad', st)
    stats[key] = stats.get(key, 0) + 1
    if (rc is None) != (st in ('OPTIMAL', 'FEASIBLE')):
        print('MISMATCH', it, s.name, c, '->', nc, k, mode < 0.5, '| rigid:', rc, '| sat:', st, flush=True)
print(stats)
