import sys, json
sys.path.insert(0, '../nk_constructor_20261022')
import joint_cp, sqbuild
r = sqbuild.build_fast(8, json.load(open('../nk_constructor_20261022/square_table.json')))
m = r.mods[0]
P = [list(p) for p in m['P']]; R = [list(x[1:]) for x in m['R']]; PL = [list(x[1:]) for x in m['PLATE']]
E = sorted((r.glue[1] - r.plates[1]))
print('ref E', len(E), E)
secs = float(sys.argv[1]) if len(sys.argv) > 1 else 300
res = joint_cp.solve(8, 4, 5, (5, 0), secs, workers=4, xlo=-4, margin=2, hint=dict(P=P, R=R, PL=PL))
print('cost', res['cost'], 'bound', res['bound'], 'plate', len(res['PL']), 'R', len(res['R']), 'E', len(res['E']))
print(joint_cp.show(res)); print(json.dumps(res))
json.dump(res, open('out/jcp_8_45_50.json', 'w'))
