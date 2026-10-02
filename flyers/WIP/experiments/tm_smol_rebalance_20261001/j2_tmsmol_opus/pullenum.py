import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']; import planner as P; sys.argv = argv
bodies, ev = P.parse(str(HERE.parent / 'base.bodytrack.txt'))
REAR = {9, 10, 11, 15, 18}
glue = {b: d for b, d in bodies.items() if d['glue'] and len(d['cells']) >= 6}
mx = {b: sum(c[0] for c in d['cells']) / len(d['cells']) for b, d in glue.items()}
pulled = {(max((n, b) for b, n in e['moved'] if b in glue)[1], e['s']) for e in ev if e['act'] == 'pull'}
for V in sorted(glue):
    if V in REAR: continue
    w = glue[V]['word']
    for s in range(5):
        if w[s] == 'm' and w[(s + 1) % 5] == 'w' and (V, s) not in pulled:
            push = [e for e in ev if e['act'] == 'push' and e['s'] == s and any(b == V for b, _ in e['moved'])
                    and max((n, b) for b, n in e['moved'] if b in glue)[1] == V]
            for F in glue:
                fw = glue[F]['word']
                if F != V and fw[(s - 1) % 5] == 'w' and fw[s] == 'w' and mx[F] > mx[V]:
                    a = push[0]['actor'] if push else None
                    print(F, V, s, a, list(bodies[a]['cells'])[0] if a else None, 'dx=%.1f' % (mx[F] - mx[V]))
