"""Exact half-turn symmetry: route three banks and copy each opposite bank.

The normal six-core hardware/swept keepouts are retained. Symmetry is a hard
constraint, rather than a cosmetic score. No simulator changes are involved.
"""
import collections, time
import final_router as base

def mirror(p): return p[0], -p[1], -p[2]
def mirrored(cells): return {mirror(p) for p in cells}

def route(mandatory, fixed, bounds, cap, rng, deadline, report, rail=None):
    must = [set(s) for s in mandatory]
    if any(mirrored(must[i]) != must[i+3] for i in range(3)):
        report['rejection'] = 'mandatory_symmetry'; return None
    blocked = [set(s) for s in fixed]
    for i in range(6):
        for j in range(6):
            if i != j: blocked[i].update(base.obstacles(must[j], j, i))
    # Both copies must clear every hardware and mandatory-body obstacle.
    for i in range(3): blocked[i].update(mirrored(blocked[i+3]))
    routes = [set(s) for s in must]
    history = [collections.Counter() for _ in range(3)]
    best = None
    for iteration in range(60):
        if time.monotonic() >= deadline: break
        for i in rng.sample(range(3), 3):
            weights = collections.Counter({p:v*.5 for p,v in history[i].items()})
            for member in (i, i+3):
                for j in range(6):
                    if j in (i,i+3): continue
                    for p in base.obstacles(routes[j]-must[j], j, member):
                        weights[p if member==i else mirror(p)] += 2+iteration*.6
            if rail is not None:
                # Prefer one straight X-layer backbone with short terminal stubs.
                for x in range(bounds[0], bounds[1]+1):
                    if x == rail: continue
                    for y in range(bounds[2], bounds[3]+1):
                        for z in range(bounds[4], bounds[5]+1):
                            weights[x,y,z] += .35*abs(x-rail)
            candidate = set(must[i])
            while len(base.components(candidate)) > 1:
                path = base.bridge(candidate, blocked[i], weights, bounds, rng, deadline)
                if path is None or len(candidate)+len(path)>cap: break
                candidate.update(path)
            if len(base.components(candidate)) == 1:
                # Temporary conflicts with the opposite copy are negotiated too.
                # Returning them is forbidden by the complete conflict check.
                copy = mirrored(candidate)
                routes[i], routes[i+3] = candidate, copy
        conflicts = []
        for i in range(6):
            for j in range(i):
                hit = routes[i] & base.obstacles(routes[j], j, i)
                if hit:
                    conflicts.append((i,j,len(hit)))
                    history[i%3].update(hit if i<3 else mirrored(hit))
                    reverse = routes[j] & base.obstacles(routes[i], i, j)
                    history[j%3].update(reverse if j<3 else mirrored(reverse))
        missing = sum(len(base.components(s))-1 for s in routes)
        score = (missing, sum(c for i,j,c in conflicts), max(map(len,routes)), sum(map(len,routes)))
        if best is None or score < best:
            best=score; report.update(best=score, iteration=iteration)
        if not missing and not conflicts:
            report['counts']=list(map(len,routes)); return routes
        if iteration%10==9:
            i=rng.randrange(3); routes[i],routes[i+3]=set(must[i]),set(must[i+3])
    return None
