import sys, time
sys.path.insert(0, '../../tm_smol_rebalance_20261001/j2_front_smol')
from layered import solve, report, TM, TM_REAR, L
W = ['mmmww','wmmmw','wwmmm','mwwmm','mmwwm']
def feas(bodies, cap, rear=()):
    r = solve(bodies, None, rear, W_REAR=0, W_ALL=1000, cap=cap, time_limit=60)
    return r
# tm_smol with each body glue reduced
print('tm_smol cap11:', solve(TM, None, TM_REAR, cap=11, W_REAR=0,W_ALL=1000) is not None)
for g in (6,7,8,9):
    for copies in (1,2,3):
        B = {f'{w}_{c}': (w, g) for w in W for c in range(copies)}
        r = feas(B, 11)
        r10 = feas(B, 10)
        print(f'uniform glue {g}, {5*copies} bodies: cap11', r is not None, 'cap10', r10 is not None, 'max', r and r['max_all'])
