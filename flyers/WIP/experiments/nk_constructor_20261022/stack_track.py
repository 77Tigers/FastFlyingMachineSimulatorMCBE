# moved from the session scratchpad: model-vs-simulation divergence finder for stack rings (run from this folder)
"""first divergence between a ring model and the simulation: track every block's body from the model's canonical
world, apply each successful action of fastflyer-research trace (all moves +x here), compare per slot with the model.
first_div(r, flyer_path, ticks) -> list of (slot, body, expected moves?, simulated moves?, action info)"""
import re, subprocess, collections
EXE = '../../../../target/release/fastflyer-research.exe'
def first_div(r, path, ticks, maxn=8):
    out = subprocess.run([EXE, 'trace', path, '0', str(ticks)], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
    w0 = r.world(0, canon=True); mins = [min(c[i] for c in w0) for i in range(3)]
    sh = (-(mins[0] // 16) * 16, -mins[1], -(mins[2] // 16) * 16)
    pos = {}
    for c, lst in w0.items():
        for X, kind, info in lst: pos[(c[0] + sh[0], c[1] + sh[1], c[2] + sh[2])] = (X, kind)
    acts = []; cur = None
    for l in out.splitlines():
        m = re.match(r'ACTION Tick (\d+) \S+ (.*?) @ \((-?\d+), (-?\d+), (-?\d+)\).*failure=(.*)$', l)
        if m: cur = dict(t=int(m[1]), what=m[2], p=tuple(map(int, m.group(3, 4, 5))), fail=m[6], src=[]); acts.append(cur); continue
        m = re.match(r'SOURCE Coord \{ x: (-?\d+), y: (-?\d+), z: (-?\d+) \}', l)
        if m and cur is not None: cur['src'].append(tuple(map(int, m.group(1, 2, 3))))
    T = r.T; moved = collections.defaultdict(set); who = collections.defaultdict(list)
    bytick = collections.defaultdict(list)
    for a in acts: bytick[a['t']].append(a)
    divs = []
    for t in range(ticks):
        for a in bytick.get(t, []):
            if a['fail'] != 'None': continue
            ids = [(c, pos.pop(c)) for c in a['src'] if c in pos]
            bodies = {X for c, (X, kind) in ids if kind == 'g'}
            for c, v in ids: pos[(c[0] + 1, c[1], c[2])] = v
            s = t // 2
            for X in bodies: moved[s].add(X); who[(s, X)].append((a['what'], pos.get((a['p'][0] + 1, a['p'][1], a['p'][2])) or pos.get(a['p']), sorted(bodies)))
        if t % 2 == 1:
            s = t // 2
            for X in range(T.L):
                exp = T.moves(X, s % T.S); got = X in moved[s]
                if exp != got: divs.append((s, X, exp, got, who.get((s, X))))
            if divs: return divs[:maxn]
    return divs
