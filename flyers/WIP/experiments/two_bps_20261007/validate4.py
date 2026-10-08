"""NS=4 validation of satflyer5: the banked mirrored PL8 (rigid_sat_20261004/runs/assembled/mirror_freeF_L8.pkl)
must be FEASIBLE at load 8 and INFEASIBLE at 7; also the hop PL8 record and capsL8_L9 (9 ok, 8 not)."""
import sys, pathlib, pickle
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from satflyer5 import check_fixed, convert4, to_flyer
RS = HERE.parent / 'rigid_sat_20261004' / 'runs' / 'assembled'
for name, Ls in (('mirror_freeF_L8', (8, 7)), ('capsL8_L9', (9, 8)), ('start7_front9', (9, 8))):
    d = pickle.load(open(RS / f'{name}.pkl', 'rb'))
    sol = convert4(d['sol'])
    for L in Ls:
        st, M = check_fixed(sol, 4, L, riders=d.get('riders', ()), merges=d.get('merges', ()))
        print(name, 'load', L, st, flush=True)
        if st in ('OPTIMAL', 'FEASIBLE') and L == Ls[0]:
            print('  max load', max(M.loads().values()))
            to_flyer(sol, L, 4).save(str(HERE / 'runs' / f'v4_{name}.flyer'))
