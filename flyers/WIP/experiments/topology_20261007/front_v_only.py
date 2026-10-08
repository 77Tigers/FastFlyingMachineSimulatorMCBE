"""Enumerator survivor 'V-only single-chain front' (no F): K5 (free, wwmm) keeps only its sticky on K4; rider V
(wmmw) rides K4@1, K5@2 and pushes K5@3; K5's sticky powered from K4 (mmww static/relay is unique at slot 0).
usage: python front_v_only.py LOAD TL WORKERS [k45free]"""
import sys, os, pickle, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'rigid_sat_20261004'))
from cfgsat import *
L = int(sys.argv[1]); tl = float(sys.argv[2]); wk = int(sys.argv[3]); v = sys.argv[4] if len(sys.argv) > 4 else ''
segs = [{'name': 'K2', 'tmpl': 2, 'open': BND_BACK}, {'name': 'K3', 'tmpl': 3}]
segs.append({'name': 'K4', 'free': 4, 'word': 'mmww', 'keep': True} if v == 'k45free' else {'name': 'K4', 'tmpl': 4})
segs.append({'name': 'K5', 'free': 5, 'word': 'wwmm'})
segs.append(rider_seg('V', 'P', 'wmmw', 5))
cfg = {'segs': segs, 'load': L, 'automerge': False, 'kinds': KALL, 'box': (-3, 4, 2)}
st, sol, M = run(cfg, tl, wk, tag=None, objective=os.environ.get('OBJ') or None)
print('front_v_only', v, 'L', L, st, flush=True)
if sol:
    print(show(sol)); print(report(M))
    pickle.dump({'sol': sol, 'cfg': cfg}, open(HERE / 'runs' / f'front_v_only{v}_L{L}.pkl', 'wb'))
