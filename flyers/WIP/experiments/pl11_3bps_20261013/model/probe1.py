import sys, time
sys.path.insert(0, '../../tm_smol_rebalance_20261001/j2_front_smol')
from layered import solve, report, TM, TM_REAR, TM_ALLOW, L
kinds = {}
TM_PULLS = {('B9', 0), ('B29', 1), ('B35', 0), ('B15', 2), ('B10', 3), ('B18', 4)}
kinds = {(n, s): ('pull' if (n, s) in TM_PULLS else 'push') for n in TM for s in range(L) if TM[n][0][s] == 'm'}
for label, kk, allow in [('real kinds, real graph', kinds, TM_ALLOW), ('real kinds, any graph', kinds, None), ('free kinds, any graph', None, None)]:
    t=time.time(); r = solve(TM, kk, TM_REAR, allow=allow, W_REAR=0, W_ALL=1000, time_limit=120)
    print(label, round(time.time()-t,1),'s'); report(r, TM, TM_REAR, lim=12)
