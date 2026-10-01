import sys, json, glob, time
import ilp
done = set()
end = time.time() + float(sys.argv[1]) * 3600
while time.time() < end:
    files = sorted(set(glob.glob('c6/*L22*.json') + glob.glob('c11/*L22*.json') + glob.glob('c11/*L21*.json') + ['best/pull_pl22.place.json']) - done)
    if not files:
        time.sleep(60); continue
    fn = files[0]; done.add(fn)
    g, p, o = json.load(open(fn)); place = (tuple(g), [(a, tuple(b)) for a, b in p], o)
    for rs in range(4):
        try:
            d, L = ilp.solve(place, rs, radius=3, Lmax=21, time_limit=300, verbose=False, free=(rs % 2 == 1))
        except Exception as e:
            print(fn, rs, 'err', e, flush=True); continue
        print(fn, rs, 'free' if rs % 2 else 'fixed', L if d is None else ('FOUND', d.max_load()), flush=True)
        if d is not None:
            f = d.to_flyer(limit=d.max_load()); f.translate(20, 20, 20); f.save(fn.replace('.json', f'_ilp{rs}_L{d.max_load()}.flyer'))
