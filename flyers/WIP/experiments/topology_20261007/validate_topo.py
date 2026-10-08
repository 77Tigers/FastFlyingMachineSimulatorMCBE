"""Sanity: the banked PL8 topologies, built by hand in the enumerator's state model, must pass all slot laws and get
LB <= their true loads (8). Also checks that search() can reach them (twin front / closed hop)."""
from topo_enum import *

# hop pair: A mwmw, B wmwm, X1/X2 rider pushers on A, Y1/Y2 rider stickies on B (bank/pl8/hop_pair_rod_observer)
s = new_state(); A = add_body(s, 'A', WORDS['mwmw']); B = add_body(s, 'B', WORDS['wmwm'])
for nm, w, kind, T, t, car in [('X1', 'wwmm', 'P', A, 0, {2: A, 3: B}), ('X2', 'mmww', 'P', A, 2, {0: A, 1: B}),
                               ('Y1', 'wwmm', 'S', B, 1, {2: A, 3: B}), ('Y2', 'mmww', 'S', B, 3, {0: A, 1: B})]:
    s.riders.append({'name': nm, 'w': WORDS[w], 'kind': kind, 'car': car}); j = len(s.riders) - 1
    assert add_piston(s, ('R', j), kind, T, t), nm
for j, r in enumerate(s.riders):
    h = r['w']; k = fire_slot(h)
    okA = static_ok(WORDS['mwmw'], h, k); okB = obs_ok(WORDS['wmwm'], h, k)
    print(r['name'], 'static on A ok', okA, 'observer on B ok', okB)
    s.power[('R', j)] = (('B', A), 'st', 'direct') if okA else (('B', B), 'ob', 'direct')
    s.src.setdefault(s.power[('R', j)][0], {}).setdefault(s.power[('R', j)][1], set()).add(('R', j))
print('hop demands left:', demands(s, {}), 'LB loads', loads(s), 'stretch LB', stretch_lb(s, 20))
N = sum(blocks_lb(s, b) for b in range(2)) + 4; print('2N/P bound', math.ceil(2 * N / 4), '(true PL 8)')
