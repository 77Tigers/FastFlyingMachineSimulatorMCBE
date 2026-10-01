import sys, pathlib, pickle, glob
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
import climb, simtools
n = 0
for pf in sorted(glob.glob('pool1?.pkl')):
    pool = pickle.load(open(pf, 'rb'))
    vs = {f'c{i}': climb.build(c, m) for i, (c, m) in enumerate(pool)}
    res = simtools.screen(vs, 360)
    for k, r in res.items():
        if r['clean'] == 'true' and int(r['distance']) >= 118:
            n += 1; i = int(k[1:]); name = f'w_{pf[4:-4]}_{i}.flyer'
            vs[k].save(name); print(name, len(pool[i][0]), r['max_successful_action'], flush=True)
    print(pf, len(pool), flush=True)
