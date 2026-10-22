import sys, json, joint_cp
h = json.load(open('out/best27.json'))
for a,b,st in [(4,5,(5,0)),(5,4,(6,0))]:
    hint = h if all(p[0]<a and p[1]<b for p in h['P']+h['R']+h['PL']) else None
    r = joint_cp.solve(8, a, b, st, float(sys.argv[1]), workers=4, hint=hint, xlo=-3, margin=1)
    print(a,b,st,'cost',r['cost'],'bound',r['bound'],flush=True)
    json.dump(r, open(f'out/long_{a}{b}_{st[0]}{st[1]}.json','w'))
