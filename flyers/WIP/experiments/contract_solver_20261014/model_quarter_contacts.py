"""Bounded necessary contact geometry for closed20 X/T stacked-loop modules.

Four quadrants share five templates under90-degree rotation. Real connected
glue shapes, recorded piston contacts, base/arm clearance at slot boundaries.
Optional sources enforce normal firing/retraction on/off using one RB per
body. Sticky/stray power, G/H and movement-order clearance are omitted.
A feasible result is a contact scaffold, never a physical flyer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent


def rotate(p, q):
    x, y, z = p
    for _ in range(q % 4):
        y, z = -z, y
    return x, y, z


def shifted(p, dx):
    return p[0] + dx, p[1], p[2]


def prefix(word):
    return [sum(c == "m" for c in word[:t]) for t in range(5)]


def run(radius, seconds, open_seam, local_modules=None, sources=False, exact_carriers=False, hint=None, compatible=False):
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    data = json.loads((HERE / "results/quarter_ring20_role_plan.json").read_text(encoding="utf-8"))
    m = cp_model.CpModel()
    def point(label, lo, hi):
        return tuple(m.NewIntVar(a, b, f"{label}:{k}") for k, (a, b) in enumerate(zip(lo, hi)))
    def near(a, b, label):
        ds = [m.NewIntVar(0, 80, f"d{label}:{k}") for k in range(3)]
        for d, x, y in zip(ds, a, b):
            m.AddAbsEquality(d, x-y)
        v = m.NewBoolVar(f"adj{label}")
        # Positive witness only. Unchosen/inactive glue positions must not be
        # constrained to avoid adjacency, nor forced present by coincidence.
        m.Add(sum(ds) == 1).OnlyEnforceIf(v)
        return v
    def equal(a, b, label):
        v = m.NewBoolVar(label)
        for x, y in zip(a, b):
            m.Add(x == y).OnlyEnforceIf(v)
        return v
    def separated(a,b,conditions,label):
        ds=[m.NewIntVar(0,80,f"sep{label}:{k}") for k in range(3)]
        for d,x,y in zip(ds,a,b): m.AddAbsEquality(d,x-y)
        m.Add(sum(ds)!=1).OnlyEnforceIf(conditions)
    shapes = {}
    module_count = local_modules or 5
    quadrants = range(1 if local_modules else 4)
    active_names = {f"{r}{i+5*q}" for q in quadrants for i in range(module_count) for r in "XT"}
    for i in range(module_count):
        step = i * 2 * radius // 5
        y, z = (step, -radius) if step <= radius else (radius, step-2*radius)
        for role, cap in (("X", 7), ("T", 6)):
            pts, present = [], []
            for j in range(cap):
                lo, hi = ((-2, y-2, z-2), (2, y+2, z+2)) if role == "X" else ((1, y-3, z-3), (7, y+3, z+3))
                p = point(f"{role}{i}:{j}", lo, hi)
                v = m.NewBoolVar(f"on{role}{i}:{j}")
                if j == 0:
                    m.Add(v == 1)
                    if role == "X":
                        m.Add(p[1] == y); m.Add(p[2] == z)
                else:
                    # WLOG keep present points first; unused coordinates have
                    # no physical meaning and can coincide with the root.
                    m.Add(v <= present[-1])
                    for x, root in zip(p, pts[0]):
                        m.Add(x == root).OnlyEnforceIf(v.Not())
                    links = []
                    for k, prev in enumerate(pts):
                        link = near(p, prev, f"{role}{i}:{j}:{k}")
                        m.AddImplication(link, present[k])
                        links.append(link)
                    m.AddBoolOr(links).OnlyEnforceIf(v)
                pts.append(p); present.append(v)
            shapes[role, i] = list(zip(pts, present))
    def body(name):
        i = int(name[1:])
        return [(rotate(p, i // 5), v) for p, v in shapes[name[0], i % 5]]
    power = {}
    if sources:
        for (role,i), cells in shapes.items():
            step=i*2*radius//5
            y,z=(step,-radius) if step<=radius else (radius,step-2*radius)
            p=point(f"RB{role}{i}",(-3,y-4,z-4),(8,y+4,z+4))
            choices=[]
            for j,(g,on) in enumerate(cells):
                v=near(p,g,f"source{role}{i}:{j}")
                m.AddImplication(v,on); choices.append(v)
            m.AddBoolOr(choices)
            power[role,i]=p
    actions = [a for a in data["actions"] if int(a["target"][1:]) < module_count and
               (a["target"][0] == "X" or (a["target"][0] == "T" and a["kind"] == "push"))]
    actors = []
    contact_count = 0
    for ai, a in enumerate(actions):
        i = int(a["target"][1:]); step = i*2*radius//5
        y, z = (step, -radius) if step <= radius else (radius, step-2*radius)
        p = point(f"p{ai}", (-5, y-4, z-4), (10, y+4, z+4))
        pm = a["piston_moves"]
        sh = [sum(pm[:t]) for t in range(5)]
        actors.append((p, a, sh))
        ts = prefix(data["words"][a["target"]])
        t = a["slot"]
        target = shifted(p, sh[t] + (1 if a["kind"] == "push" else -2))
        choices = []
        for j, (gp, on) in enumerate(body(a["target"])):
            v = equal(target, shifted(gp, ts[t]), f"hit{ai}:{j}")
            m.AddImplication(v, on); choices.append(v)
        m.AddBoolOr(choices)
        if sources and a['kind']=='push':
            rb=power[a['target'][0],i]
            # Soft-power from the body's reserved RB, ignoring the front face.
            powered_offsets=[(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
            for tick,on in ((a['firing_slot'],True),((a['firing_slot']+1)%5,False)):
                relative=[m.NewIntVar(-80,80,f"rel{ai}:{tick}:{k}") for k in range(3)]
                for d,x,y in zip(relative,shifted(rb,ts[tick]),shifted(p,sh[tick])): m.Add(d==x-y)
                if on: m.AddAllowedAssignments(relative,powered_offsets)
                else: m.AddForbiddenAssignments(relative,powered_offsets)
        for c in a["carriers"]:
            if local_modules and c["body"] not in active_names:
                continue
            if open_seam and int(c["body"][1:]) // 5 != i // 5:
                continue
            cs = prefix(data["words"][c["body"]])
            for t, bit in enumerate(c["touch"]):
                if bit != "1": continue
                choices = []
                for j, (gp, on) in enumerate(body(c["body"])):
                    v = near(shifted(p, sh[t]), shifted(gp, cs[t]), f"carry{ai}:{c['body']}:{t}:{j}")
                    m.AddImplication(v, on); choices.append(v)
                m.AddBoolOr(choices); contact_count += 1
        if exact_carriers:
            for t in range(5):
                if not pm[t]: continue
                expected={c['body'] for c in a['carriers'] if c['touch'][t]=='1'}
                for name in active_names-expected:
                    if data['words'][name][t]!='m': continue
                    for j,(gp,on) in enumerate(body(name)):
                        ds=[m.NewIntVar(0,80,f"extra{ai}:{name}:{t}:{j}:{k}") for k in range(3)]
                        for d,x,y in zip(ds,shifted(p,sh[t]),shifted(gp,prefix(data['words'][name])[t])): m.AddAbsEquality(d,x-y)
                        m.Add(sum(ds)!=1).OnlyEnforceIf(on)
    # Encoding is injective within the bounded coordinate range. Inactive glue
    # gets private out-of-grid sentinels so it cannot obstruct actual cells.
    def encode(p): return (p[0]+30)*10000+(p[1]+30)*100+(p[2]+30)
    for t in range(5):
        occupied = []; serial = 0
        for name, word in data["words"].items():
            if name not in active_names: continue
            sh = prefix(word)[t]
            for gp, on in body(name):
                loc = m.NewIntVar(0, 2000000, f"occupied{t}:{serial}")
                m.Add(loc == encode(shifted(gp, sh))).OnlyEnforceIf(on)
                m.Add(loc == 1000000+serial).OnlyEnforceIf(on.Not())
                occupied.append(loc); serial += 1
            if sources:
                i=int(name[1:]); occupied.append(encode(shifted(rotate(power[name[0],i%5],i//5),sh)))
        for p, a, sh in actors:
            for q in quadrants:
                now = rotate(shifted(p, sh[t]), q)
                occupied.append(encode(now))
                if t == (a["firing_slot"]+1) % 5:
                    occupied.append(encode(shifted(now, 1 if a["kind"] == "push" else -1)))
        m.AddAllDifferent(occupied)
    materials={}
    if compatible:
        assert sources, 'compatibility requires reserved sources'
        materials={name:m.NewBoolVar(f'material{name}') for name in active_names}
        m.Add(materials['X0']==0)
        names=sorted(active_names)
        for ia,name in enumerate(names):
            for other in names[ia+1:]:
                same=m.NewBoolVar(f'same{name}:{other}')
                m.Add(materials[name]==materials[other]).OnlyEnforceIf(same)
                m.Add(materials[name]!=materials[other]).OnlyEnforceIf(same.Not())
                offsets={prefix(data['words'][name])[t]-prefix(data['words'][other])[t]
                         for t in range(5) if data['words'][name][t]=='m' or data['words'][other][t]=='m'}
                for d in offsets:
                    for j,(p,on) in enumerate(body(name)):
                        for k,(q,onq) in enumerate(body(other)):
                            separated(shifted(p,d),q,[on,onq,same],f'glue{name}:{other}:{d}:{j}:{k}')
        for owner in names:
            i=int(owner[1:]); rp=rotate(power[owner[0],i%5],i//5)
            for other in names:
                if owner==other: continue
                offsets={prefix(data['words'][owner])[t]-prefix(data['words'][other])[t]
                         for t in range(5) if data['words'][other][t]=='m'}
                for d in offsets:
                    for j,(q,on) in enumerate(body(other)):
                        separated(shifted(rp,d),q,[on],f'RB{owner}:{other}:{d}:{j}')
        for ai,(p,a,sh) in enumerate(actors):
            t=(a['firing_slot']+1)%5
            offsets=[(1 if a['kind']=='pull' else -1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
            for owner in names:
                i=int(owner[1:]); rp=shifted(rotate(power[owner[0],i%5],i//5),prefix(data['words'][owner])[t])
                ds=[m.NewIntVar(-80,80,f'off{ai}:{owner}:{k}') for k in range(3)]
                for d,x,y in zip(ds,rp,shifted(p,sh[t])): m.Add(d==x-y)
                m.AddForbiddenAssignments(ds,offsets)
    if hint:
        from check_quarter_contacts import check
        seed=json.loads(Path(hint).read_text(encoding='utf-8'))
        check(seed)
        assert seed['radius']==radius
        for (role,i),cells in shapes.items():
            saved=seed['glue'].get(f'{role}{i}')
            if saved is None: continue
            for j,(p,on) in enumerate(cells):
                m.AddHint(on,int(j<len(saved)))
                for v,x in zip(p,saved[j] if j<len(saved) else saved[0]): m.AddHint(v,x)
        for (role,i),p in power.items():
            saved=seed.get('redstone_sources',{}).get(f'{role}{i}')
            if saved is not None:
                for v,x in zip(p,saved): m.AddHint(v,x)
        for p,a,_ in actors:
            saved=next((x for x in seed['actors'] if (x['target'],x['slot'])==(a['target'],a['slot'])),None)
            if saved is not None:
                for v,x in zip(p,saved['at']): m.AddHint(v,x)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 4
    print(json.dumps({"stage":"solve", "local_modules":local_modules,
                      "variables":len(m.Proto().variables), "constraints":len(m.Proto().constraints)}),flush=True)
    started = time.monotonic()
    status = solver.Solve(m)
    result = {"radius": radius, "open_quadrant_seams": open_seam,
              "local_modules":local_modules,
              "checked_hint_sha256":hashlib.sha256(Path(hint).read_bytes()).hexdigest() if hint else None,
              "reserved_redstone_sources":sources, "forbid_extra_moving_carriers":exact_carriers,
              "conservative_compatibility":compatible,
              "active_body_names": sorted(active_names),
              "status": solver.StatusName(status), "solve_seconds": time.monotonic()-started,
              "solver_statistics": solver.ResponseStats(),
              "scope": __doc__, "recorded_contacts": contact_count,
              "source_sha256": source_hash,
              "role_plan_sha256": hashlib.sha256((HERE/'results/quarter_ring20_role_plan.json').read_bytes()).hexdigest()}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result["glue"] = {f"{r}{i}": [list(map(solver.Value, p)) for p, v in cells if solver.Value(v)]
                          for (r, i), cells in shapes.items()}
        result["actors"] = [{"target": a["target"], "slot": a["slot"], "at": list(map(solver.Value,p)),
                              "kind": a["kind"], "moves": a["piston_moves"]} for p,a,_ in actors]
        if sources:
            result['redstone_sources']={f'{r}{i}':list(map(solver.Value,p)) for (r,i),p in power.items()}
        if compatible: result['materials']={n:solver.Value(v) for n,v in materials.items()}
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out", type=Path)
    ap.add_argument("--radius", type=int, default=5)
    ap.add_argument("--seconds", type=float, default=90)
    ap.add_argument("--open-seam", action="store_true")
    ap.add_argument("--local-modules", type=int, choices=range(1,6))
    ap.add_argument("--sources", action="store_true")
    ap.add_argument("--exact-carriers", action="store_true")
    ap.add_argument("--hint",type=Path)
    ap.add_argument("--compatible",action='store_true')
    args = ap.parse_args()
    assert 3 <= args.radius <= 8 and args.seconds > 0
    result = run(args.radius, args.seconds, args.open_seam, args.local_modules,args.sources,args.exact_carriers,args.hint,args.compatible)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('glue','actors','scope')}),flush=True)
