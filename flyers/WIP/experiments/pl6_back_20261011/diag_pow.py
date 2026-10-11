"""Which body's pistons cannot be powered?  powmiss = that body may take power from outside (still no extra power)."""
from twin6 import build
offs = [('flipz', (-1, -2, -3)), ('swap', (-1, -2, -4)), ('rot90', (-1, 1, -4)), ('rot180', (-2, -3, 0)), ('rot90', (-1, -3, -1))]
for mp, d in offs:
    res = []
    for pm, lab in (((0, 4), 'K0'), ((1, 5), 'N'), ((2, 6), 'K1'), ((0, 4, 1, 5), 'K0+N'), ((0, 4, 1, 5, 2, 6), 'all')):
        M = build(mp, d, 6, powmiss=pm); st, _ = M.solve(20, 4); res.append(f'{lab}:{st[:4]}')
    print(mp, d, ' '.join(res), flush=True)
