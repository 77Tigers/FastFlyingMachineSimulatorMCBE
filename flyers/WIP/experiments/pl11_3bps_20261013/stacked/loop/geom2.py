"""Static geometry search for the two-module stage: placements (yz symmetry x sticky-aligned shift) of T_a (B24 shape, X_a=B16) and T_b (B33 shape, X_b=B9)."""
import json, collections, itertools
nm = {tuple(json.loads(k.replace('(', '[').replace(')', ']'))): v for k, v in json.load(open('core0_names.json')).items()}
cells = collections.defaultdict(dict)
for p, (n, k) in nm.items(): cells[n][p] = k
W = {'B7': (0,1,4), 'B8': (1,2,3), 'B9': (0,1,2), 'B15': (0,3,4), 'B16': (2,3,4), 'B33': (3,4,0), 'B24': (0,1,2)}
def wp(w, s): return sum(1 for m in w if m < s)
D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
GL = ('sl', 'ho')
SYMS = [(sy, sz, sw) for sy in (1,-1) for sz in (1,-1) for sw in (False, True)]
def tsym(p, sym):
    y, z = p[1]*sym[0], p[2]*sym[1]
    if sym[2]: y, z = z, y
    return (p[0], y, z)
def shape(body, sym, sticky_target, dist):
    """cells of T body transformed by sym, then translated so its sticky lands at (x_cell+dist, y_cell, z_cell); returns dict pos->kind."""
    base = {tsym(p, sym): k for p, k in cells[body].items()}
    s = [p for p, k in base.items() if k == 'S'][0]
    tx, ty, tz = sticky_target[0] + dist, sticky_target[1], sticky_target[2]
    d = (tx - s[0], ty - s[1], tz - s[2])
    return {(p[0]+d[0], p[1]+d[1], p[2]+d[2]): k for p, k in base.items()}
def leading(body):
    best = {}
    for p, k in cells[body].items():
        if k in GL:
            key = (p[1], p[2])
            if key not in best or p[0] > best[key][0]: best[key] = p
    return list(best.values())
def at_slot(cs, word, s): return {(p[0]+wp(word, s), p[1], p[2]): k for p, k in cs.items()}
def check(Tb_cells, Ta_cells, kb, ka, stage='both'):
    """returns list of violation strings."""
    bodies = {b: cells[b] for b in ('B7', 'B8', 'B9', 'B15', 'B16')}
    bodies['Ta'] = Ta_cells; bodies['Tb'] = Tb_cells
    words = dict(W); words['Ta'] = W['B24']; words['Tb'] = W['B33']
    kind_override = {'Ta': ka, 'Tb': kb}
    v = []
    for s in range(5):
        pos = {b: at_slot(c, words[b], s) for b, c in bodies.items()}
        occ = {}
        for b, c in pos.items():
            for p, k in c.items():
                if p in occ: v.append(f'overlap s{s} {b}/{occ[p]} {p}')
                occ[p] = b
        for b in ('Ta', 'Tb'):
            for p, k in pos[b].items():
                if k not in GL: continue
                kk = kind_override[b]
                for d in D6:
                    q = (p[0]+d[0], p[1]+d[1], p[2]+d[2])
                    o = occ.get(q)
                    if o and o != b and pos[o][q] in GL:
                        ok = pos[o][q] if o not in kind_override else kind_override[o]
                        if ok == kk: v.append(f'adhesion s{s} {b}-{o} {p}')
    return v
if __name__ == '__main__':
    XA, XB = 'B16', 'B9'
    distb = 2 + wp(W[XB], 2) - wp(W['B33'], 2)      # pull at X's last move (slot 2)
    dista = 2 + wp(W[XA], 4) - wp(W['B24'], 4)      # slot 4
    print('dist', dista, distb)
    res = []
    for sa in SYMS:
        for ta in leading(XA):
            Ta = shape('B24', sa, ta, dista)
            for sb in SYMS:
                for tb in leading(XB):
                    Tb = shape('B33', sb, tb, distb)
                    for ka in GL:
                        for kb in GL:
                            vio = check(Tb, Ta, kb, ka)
                            if not vio: res.append((sa, ta, sb, tb, ka, kb))
    print(len(res), 'static-feasible combos')
    json.dump(res, open('geom2_static.json', 'w'))
