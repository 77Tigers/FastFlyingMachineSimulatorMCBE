import sys, json, joint_cp
h = json.load(open('out/jcp_8_45_50.json'))
cfgs = [(4,4,(5,0)),(4,4,(4,1)),(4,5,(5,1)),(4,4,(5,1)),(4,5,(5,0)),(5,4,(6,0)),(4,4,(6,0))]
for a,b,st in cfgs:
    hint = h if all(p[0]<a and p[1]<b for p in h['P']+h['R']+h['PL']) else None
    r = joint_cp.solve(8, a, b, st, float(sys.argv[1]), workers=4, hint=hint)
    if r is None: print(a,b,st,'none',flush=True); continue
    print(a,b,st,'cost',r['cost'],'bound',r['bound'],flush=True)
    json.dump(r, open(f'out/jcp_8_{a}{b}_{st[0]}{st[1]}.json','w'))
