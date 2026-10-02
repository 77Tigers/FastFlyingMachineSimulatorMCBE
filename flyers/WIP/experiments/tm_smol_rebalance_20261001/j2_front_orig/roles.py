"""Per-cell roles of glue bodies from a research_runner trace starting at tick 0 of the start file.
python roles.py TRACE B1,B2,...   Tracks every block identity by following SOURCE moves (+dir of actor)."""
import sys, re, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); argv=sys.argv; sys.argv=['x']; import planner as P; sys.argv=argv
bodies, _ = P.parse(str(HERE.parent/'orig.bodytrack.txt'))
own = {c: b for b, d in bodies.items() for c in d['cells']}
C = lambda s: tuple(int(v) for v in re.findall(r'-?\d+', s)[:3])
pos2id = {c: c for c in own}       # current pos -> start cell id
roles = collections.defaultdict(set)
lines = open(sys.argv[1]).read().splitlines()
want = {int(x) for x in sys.argv[2].split(',')}
i = 0; tick = 0
while i < len(lines):
    l = lines[i]
    if l.startswith('TICK'): tick = int(l.split()[1])
    if l.startswith('ACTION') and 'sources=0' not in l and 'failure=None' in l:
        kind = 'ext' if ' extend ' in l else 'ret'
        pc = C(l.split('piston=Some(')[1])
        srcs = []; links = []; j = i + 1
        while j < len(lines) and lines[j].startswith(('SOURCE', 'LINK')):
            if lines[j].startswith('SOURCE'):
                srcs.append((C(lines[j][7:]), lines[j].split('}')[1].split()[0]))
            else:
                a, b = lines[j].split('->'); links.append((lines[j].split()[1], C(a), C(b)))
            j += 1
        # direction: all moves are +X in this flyer (check)
        ids = {p: pos2id.get(p) for p, _ in srcs}
        actor = pos2id.get(pc, pc)
        for p, k in srcs:
            cid = ids[p]
            if cid is None: continue
            b = own[cid]
            if b in want and bodies[b]['glue']:
                roles[cid].add(f't{tick}:{kind}by{own.get(actor, "?")}')
        for typ, a, b in links:
            ia, ib = ids.get(a), ids.get(b)
            if ia in own and own[ia] in want and ib is not None and (ib not in own or own[ib] != own[ia]):
                roles[ia].add(f'{typ}->{"B"+str(own[ib]) if ib in own else b}')
        # face cell directly in front of actor (push face / pull face)
        newpos = {}
        for p, k in srcs:
            if ids[p] is not None: newpos[(p[0]+1, p[1], p[2])] = ids[p]
        for p, _ in srcs:
            if pos2id.get(p) == ids[p]: pos2id.pop(p, None)
        pos2id.update(newpos)
        i = j; continue
    i += 1
for b in sorted(want):
    print(f'B{b} {bodies[b]["word"]}')
    for c, k in bodies[b]['cells'].items():
        r = sorted(x for x in roles[c] if not x.startswith('t'))
        print('  ', c, k, ' '.join(r))
