"""Back cap with riders (2026-10-04). Variants:
  nq : K0,K1 free + rider sticky N (wmmw) + body Q (mwmw) + rider pusher X (wwmm)
  nb : K0,K1 free + body N (wmmw), solver may merge K0+N (automerge)   [found load 8 before with templates kept]
  n  : K0,K1 free + rider sticky N (wmmw) only"""
import sys, os
import pickle
from cfgsat import *
L = int(sys.argv[1]) if len(sys.argv) > 1 else 7
tl = float(sys.argv[2]) if len(sys.argv) > 2 else 900
variant = sys.argv[3] if len(sys.argv) > 3 else 'nq'
extra = []
am = False
if variant == 'nq':
    extra = [rider_seg('N', 'S', 'wmmw', 0), {'name': 'Q', 'free': 0, 'word': 'mwmw'}, rider_seg('X', 'P', 'wwmm', 0)]
elif variant == 'nb':
    extra = [{'name': 'N', 'free': 0, 'word': 'wmmw'}]; am = True
elif variant == 'nqm':   # Q carried with K0 at slot 0 (merge), N rides K0@1 and Q@2
    extra = [rider_seg('N', 'S', 'wmmw', 0), {'name': 'Q', 'free': 0, 'word': 'mwmw'}]; am = True
elif variant == 'n':
    extra = [rider_seg('N', 'S', 'wmmw', 0)]
nfree = int(os.environ.get('NFREE', '2'))
cfg = back_cfg(extra, L, nfree=nfree, automerge=am)
if am: cfg['mergeable'] = [('K0', x['name']) for x in extra if 'rider' not in x] + [('K1', x['name']) for x in extra if 'rider' not in x]
st, sol, M = run(cfg, tl, 16, objective=os.environ.get('OBJ') or None, hint=(pickle.load(open(os.environ['HINT'], 'rb'))['sol'] if os.environ.get('HINT') else None), tag=f'back_riders_{variant}_L{L}')
print('back riders', variant, 'L', L, st, flush=True)
if sol: print(show(sol)); print(report(M))
