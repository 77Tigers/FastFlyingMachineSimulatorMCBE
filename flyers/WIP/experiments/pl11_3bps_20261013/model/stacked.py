"""Role-model check of the 'stacked loops' plan (back loop L0, front loop L1, tentacle base G, tip helper H).
Body cells exclude stickies (layered.py counts a glued sticky as a rider of its own body)."""
import sys, itertools
sys.path.insert(0, '../../tm_smol_rebalance_20261001/j2_front_smol')
from layered import solve, report, L

def word(ph): return ''.join('m' if (t - ph) % 5 < 3 else 'w' for t in range(5))

def build(gL0=8, gL1=7, gG=8, gH=6, split=True):
    B, kinds, allow = {}, {}, {}
    q = [(-2 * k) % 5 for k in range(5)]          # L0 ring: X_{k+1} two phases earlier
    for k in range(5):
        X, T, G, H = f'X{k}', f'T{k}', f'G{k}', f'H{k}'
        ph = {X: q[k], T: q[k] + 3, G: q[k] + 6, H: q[k] + 9}
        for n, g in ((X, gL0), (T, gL1), (G, gG), (H, gH)): B[n] = (word(ph[n] % 5), g)
        for n in (X, T, G):           # two pushes then one pull
            p = ph[n] % 5
            kinds[(n, p)] = kinds[(n, (p + 1) % 5)] = 'push'; kinds[(n, (p + 2) % 5)] = 'pull'
        for j in range(3): kinds[(H, (ph[H] + j) % 5)] = 'push'
    for k in range(5):
        X, T, G, H = f'X{k}', f'T{k}', f'G{k}', f'H{k}'
        Xn = f'X{(k + 1) % 5}'; Tp = f'T{(k - 1) % 5}'
        allow[(Xn, 'push')] = {X}                    # back ring: X_k carries X_{k+1}'s pushers
        allow[(X, 'pull')] = {T}                     # T_k's sticky pulls X_k
        allow[(T, 'push')] = {X, Tp} if split else {X}   # T's pushers: back victim + front-loop neighbour
        allow[(T, 'pull')] = {G}
        allow[(G, 'push')] = {T}                     # tentacle base pushers carried by its victim
        allow[(G, 'pull')] = {H}
        allow[(H, 'push')] = {G}
    return B, kinds, allow

if __name__ == '__main__':
    for split in (True, False):
        for cap in (11, 12):
            B, kinds, allow = build(split=split)
            r = solve(B, kinds, (), allow=allow, cap=cap, W_REAR=0, W_ALL=1000, time_limit=120)
            print(f'split={split} cap={cap}:', 'INFEASIBLE' if r is None else f"max {r['max_all']}")
            if r is not None and cap == 11:
                report(r, B, (), lim=11)
