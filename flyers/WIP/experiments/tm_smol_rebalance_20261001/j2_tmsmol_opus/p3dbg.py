import sys, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']; import planner3 as P3, planner as P; sys.argv = argv
Pb, V, s = map(int, sys.argv[1:4]); conn = int(sys.argv[4]) if len(sys.argv) > 4 else 3
bodies, occ = P3.load_state()
pk = 'sl' if 'sl' in bodies[Pb]['cells'].values() else 'ho'
sm1 = (s - 1) % 5; C = collections.Counter()
vglue = [c for c, k in bodies[V]['cells'].items() if P3.is_glue(k)]
for vc in vglue:
    sabs = P3.sx(P3.ab(V, vc, s), 2); c = P3.sx(sabs, -P.off(bodies[Pb]['word'], s))
    if c in bodies[Pb]['cells']: C['sticky cell is puller cell'] += 1; print(vc, c, 'own'); continue
    if not P3.cell_ok(Pb, c, 'S', {}):
        why = []
        for k in range(5):
            a = P3.ab(Pb, c, k)
            if a in occ[k]: why.append(f'k{k}occ{occ[k][a]}')
        print(vc, 'sticky', c, 'not ok', why[:3]); C['S not ok'] += 1; continue
    arm = P3.ab(Pb, P3.sx(c, -1), sm1)
    if arm in occ[sm1]: print(vc, c, 'arm occupied', occ[sm1][arm]); C['arm'] += 1; continue
    pp = P3.path_to(Pb, c, 'S', {(Pb, c): 'S'}, conn, pk)
    print(vc, c, 'path', pp); C['path ok' if pp is not None else 'no path'] += 1
print(C)
print('puller cells', bodies[Pb]['cells']); print('victim cells', bodies[V]['cells'])
# observer stage diagnostics for path-ok contacts
for vc in vglue:
    sabs = P3.sx(P3.ab(V, vc, s), 2); c = P3.sx(sabs, -P.off(bodies[Pb]['word'], s))
    if c in bodies[Pb]['cells'] or not P3.cell_ok(Pb, c, 'S', {}): continue
    new = {(Pb, c): 'S'}; pp = P3.path_to(Pb, c, 'S', new, conn, pk)
    if pp is None: continue
    for y in pp: new[(Pb, y)] = pk
    sticky_abs = P3.ab(Pb, c, sm1)
    targets = [sticky_abs] + [P3.ab(Pb, P3.add(c, f), sm1) for f in P3.FACES if f != (-1,0,0) and (bodies[Pb]['cells'].get(P3.add(c, f)) in ('sl','ho') or new.get((Pb, P3.add(c, f))) == pk)]
    R = collections.Counter()
    for Q in [b for b in bodies if bodies[b]['glue'] and b != Pb]:
        pulses = [(k + 1) % 5 for k in range(5) if P3.moves(Q, k)]
        if sm1 not in pulses: continue
        for t in targets:
            for d in P3.FACES:
                oabs = P3.add(t, (-d[0], -d[1], -d[2]))
                if t == sticky_abs and oabs == P3.sx(sticky_abs, -1): continue
                o = P3.sx(oabs, -P.off(bodies[Q]['word'], sm1))
                if (Q, o) in new or o in bodies[Q]['cells']: R['ownQ'] += 1; continue
                if not P3.cell_ok(Q, o, 'O', new):
                    bad = [k for k in range(5) if P3.ab(Q, o, k) in occ[k]]
                    R[f'Q{Q} obs not ok occ@{bad}'] += 1; continue
                R[f'Q{Q} obs ok -> pulses/path stage'] += 1
    print('contact', vc, 'sticky', c, dict(R))
