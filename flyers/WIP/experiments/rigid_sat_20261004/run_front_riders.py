"""Front cap with riders (2026-10-04): F = K6 passive body; rider pusher M (mwwm) gives F its 2nd push;
rider pusher V (wmmw) pushes K5 at slot 3 instead of F pulling it. Chain K2 (boundary), K3, K4 templates."""
import sys, os
import pickle
from cfgsat import *
L = int(sys.argv[1]) if len(sys.argv) > 1 else 7
tl = float(sys.argv[2]) if len(sys.argv) > 2 else 900
variant = sys.argv[3] if len(sys.argv) > 3 else 'k5keep'
segs = [{'name': 'K2', 'tmpl': 2, 'open': BND_BACK}, {'name': 'K3', 'tmpl': 3}, {'name': 'K4', 'tmpl': 4}]
if variant in ('k45free', 'k345free'):
    segs = [{'name': 'K2', 'tmpl': 2, 'open': BND_BACK}]
    segs.append({'name': 'K3', 'tmpl': 3} if variant == 'k45free' else {'name': 'K3', 'free': 3, 'word': 'wwmm'})
    segs.append({'name': 'K4', 'free': 4, 'word': 'mmww'})
if variant == 'k5tmpl': segs.append({'name': 'K5', 'tmpl': 5})
else: segs.append({'name': 'K5', 'free': 5, 'word': 'wwmm', 'keep': variant == 'k5keep'})
segs.append({'name': 'F', 'free': 6, 'word': 'mmww'})
segs.append(rider_seg('M', 'P', 'mwwm', 6))
segs.append(rider_seg('V', 'P', 'wmmw', 5))
cfg = {'segs': segs, 'load': L, 'automerge': False, 'kinds': KOBS, 'box': (-3, 4, 2)}
st, sol, M = run(cfg, tl, 16, objective=os.environ.get('OBJ') or None, hint=(pickle.load(open(os.environ['HINT'], 'rb'))['sol'] if os.environ.get('HINT') else None), tag=f'front_riders_{variant}_L{L}')
print('front riders', variant, 'L', L, st, flush=True)
if sol: print(show(sol)); print(report(M))
