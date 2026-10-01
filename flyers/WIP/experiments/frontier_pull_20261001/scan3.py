"""generate all-pull placements whose base (power placed) has a legal cell for every carry need; save pkl."""
import construct, gen, specs, random, pickle, sys, ilp
from pmodel import nb, sx
sp = specs.pull3()
seed = int(sys.argv[1]); n = int(sys.argv[2])
rng = random.Random(seed)
found = 0
for k in range(n):
    r = construct.placement3(rng, sp)
    if r is None:
        continue
    pl, info = r
    for ps in range(4):
        B = ilp.base(sp, pl, ps)
        if B is None:
            continue
        d = B.d; armc = [d.arm_ext(t) for t in range(5)]
        ok = True
        for (i, t), cb in d.carry.items():
            it = d.items[i]
            if cb == it.victim:
                continue
            if not any(not d.item_errors(d.glue(cb, sx(q, -d.sch.DISP[cb][t])), None, armc) for q in nb(it.pos[t])):
                ok = False; break
        if ok:
            import itertools
            groups = []
            for (i, t), cb in d.carry.items():
                it = d.items[i]
                if cb == it.victim:
                    continue
                g = [(cb, sx(q, -d.sch.DISP[cb][t])) for q in nb(it.pos[t])]
                groups.append([x for x in g if not d.item_errors(d.glue(*x), None, armc)])
            for b in range(5):
                for h in B.holders[b]:
                    groups.append([(b, x) for x in h if not d.item_errors(d.glue(b, x), None, armc)])
            # reachability of group cells from each body's fixed cells over legal cells
            from collections import deque
            allp = [it.pos[0] for it in d.items]
            blo = [min(p[k] for p in allp) - 4 for k in range(3)]; bhi = [max(p[k] for p in allp) + 4 for k in range(3)]
            reach = {}
            for b in range(5):
                fixed = {it.pos[0] for it in d.items if it.cat == 'glue' and it.body == b}
                seen = set(fixed); dq = deque(fixed)
                while dq:
                    p = dq.popleft()
                    for q in nb(p):
                        if q in seen or not all(blo[k] <= q[k] <= bhi[k] for k in range(3)):
                            continue
                        if d.item_errors(d.glue(b, q), None, armc):
                            continue
                        seen.add(q); dq.append(q)
                reach[b] = seen
            groups = [[x for x in g if x[1] in reach[x[0]]] for g in groups]
            if not all(groups):
                ok = False
            memo = {}
            def conflict(x, y):
                if x[0] == y[0]:
                    return False
                if x[1] == y[1]:
                    return True
                key = (x, y)
                if key not in memo:
                    d.add_item(d.glue(*x)); memo[key] = bool(d.item_errors(d.glue(*y), None, armc)); d.pop_last()
                return memo[key]
            for g1, g2 in itertools.combinations(groups, 2):
                if not ok:
                    break
                if all(conflict(x, y) for x in g1 for y in g2):
                    ok = False
        if ok:
            name = f'p3b/s{seed}_{k}_p{ps}.pkl'
            pickle.dump((pl, ps), open(name, 'wb'))
            print('ok', name, flush=True)
            found += 1
            break
print('found', found)
