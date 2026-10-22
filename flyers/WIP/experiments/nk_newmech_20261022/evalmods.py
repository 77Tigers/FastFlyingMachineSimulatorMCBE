import sys, json, joint_cp
sys.path.insert(0, '../nk_constructor_20261022')
mods = {}
b27 = json.load(open('out/best27.json')); mods['b27'] = dict(P=b27['P'], R=b27['R'], PL=b27['PL'])
for name, fn in (('cp', 'modules_cp.json'), ('lat', 'modules_lat.json'), ('lat2', 'modules_lat2.json')):
    try: d = json.load(open('../nk_constructor_20261022/' + fn))['8']
    except Exception: continue
    pl = d.get('pl') or sorted(set(map(tuple, d['P'])) | set(map(tuple, d['R'])))
    mods[name] = dict(P=d['P'], R=d['R'], PL=[list(x) for x in pl])
steps = [(5,0),(5,1),(4,1),(4,2),(6,0),(5,2),(6,1)]
secs = float(sys.argv[1])
best = None
for name, md in mods.items():
    a = max(p[0] for p in md['PL']) + 1; b = max(p[1] for p in md['PL']) + 1
    for st in steps:
        if st[0] < a and st[1] < b: continue
        r = joint_cp.solve(8, a, b, st, secs, workers=4, fix=md, xlo=-3, margin=1)
        if r is None: print(name, st, 'infeasible', flush=True); continue
        print(name, (a, b), st, 'cost', r['cost'], 'bound', r['bound'], flush=True)
        json.dump(r, open(f'out/ev_{name}_{st[0]}{st[1]}.json', 'w'))
