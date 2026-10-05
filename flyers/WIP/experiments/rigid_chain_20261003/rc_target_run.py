import ringchain2 as R, random, itertools, re, pickle, sys, os
from collections import Counter
from rigid import to_flyer, loads
good = pickle.load(open('rc_targets.pkl', 'rb'))
sh, ns, reps = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(sh); cnt = Counter(); best = 99
for L, L2, o1, o2, off in good[sh::ns]:
    for mats in itertools.product(['slime', 'honey'], repeat=4):
        for rep in range(reps):
            segs, why = R.build_vacated(L, o1, o2, off, list(mats), rng, L2)
            cnt[re.sub(r'[-0-9(), ]+', '#', str(why))] += 1
            if segs is not None:
                Lo = loads(segs)
                print('FOUND load', Lo, L, L2, o1, o2, off, mats, [(s.name, len(s.cells)) for s in segs], flush=True)
                if Lo <= best:
                    best = Lo; tag = f'tgt_{sh}_{Lo}_{os.getpid()}'
                    pickle.dump(segs, open(f'rcvac/{tag}.pkl', 'wb')); to_flyer(segs, Lo).save(f'rcvac/{tag}.flyer')
    print('progress', dict(cnt.most_common(6)), flush=True)
print('done best', best, dict(cnt.most_common(8)), flush=True)
