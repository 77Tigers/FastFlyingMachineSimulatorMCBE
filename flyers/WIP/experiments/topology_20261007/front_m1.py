"""Single-chain front cap 'F pulls K5 + rider M' (topology T-F1 from the enumerator), exact satflyer test.
K2 boundary, K3/K4 templates, K5 free (wwmm), F = K6 free (mmww, may host pistons), rider pusher M (mwwm):
M rides F@0, pushes F@1, rides K5@3 (or anything the solver finds). No rider V.
usage: python front_m1.py LOAD TL WORKERS VARIANT   VARIANT in k5keep | k5free | k45free
"""
import sys, os, pickle, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'rigid_sat_20261004'))
from cfgsat import *
L = int(sys.argv[1]); tl = float(sys.argv[2]); wk = int(sys.argv[3]); variant = sys.argv[4]
kinds = KALL if os.environ.get('RODS') else KOBS
segs = [{'name': 'K2', 'tmpl': 2, 'open': BND_BACK}, {'name': 'K3', 'tmpl': 3}]
segs.append({'name': 'K4', 'tmpl': 4} if variant != 'k45free' else {'name': 'K4', 'free': 4, 'word': 'mmww', 'keep': True})
segs.append({'name': 'K5', 'free': 5, 'word': 'wwmm', 'keep': variant == 'k5keep'})
segs.append({'name': 'F', 'free': 6, 'word': 'mmww'})
segs.append(rider_seg('M', 'P', 'mwwm', 6))
cfg = {'segs': segs, 'load': L, 'automerge': False, 'kinds': kinds, 'box': (-3, 4, 2)}
st, sol, M = run(cfg, tl, wk, tag=None, objective=os.environ.get("OBJ") or None)
print('front_m1', variant, 'L', L, 'rods' if os.environ.get('RODS') else '', st, flush=True)
if sol:
    print(show(sol)); print(report(M))
    pickle.dump({'sol': sol, 'cfg': cfg}, open(HERE / 'runs' / f'front_m1_{variant}_L{L}.pkl', 'wb'))
