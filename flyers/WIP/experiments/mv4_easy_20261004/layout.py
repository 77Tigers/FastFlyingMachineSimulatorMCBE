"""Geometry-only comparison and a readable template/phase diagram."""
from pathlib import Path
import json,collections
HERE=Path(__file__).resolve().parent

def measure(m):
    cells=[set(map(tuple,s)) for s in m['segments']]
    mirror=lambda p:(p[0],-p[1],-p[2])
    paired=[len({mirror(p) for p in cells[i]}^cells[i+3]) for i in range(3)]
    # For the irregular reference, center the half-turn on opposite bank centers.
    centered=[]
    for i in range(3):
        a,b=m['centers'][i],m['centers'][i+3]
        centered.append(len({(p[0],a[0]+b[0]-p[1],a[1]+b[1]-p[2]) for p in cells[i]}^cells[i+3]))
    counts=[]
    for s in cells:
        branches=elbows=0
        for p in s:
            neighbors=[]
            for k in range(3):
                for d in (-1,1):
                    q=list(p);q[k]+=d
                    if tuple(q) in s:neighbors.append(k)
            branches+=len(neighbors)>=3
            elbows+=len(neighbors)==2 and neighbors[0]!=neighbors[1]
        counts.append(dict(glue=len(s),branches=branches,elbows=elbows,
                           x_layers=len({p[0] for p in s})))
    return dict(glue_total=sum(map(len,cells)),opposite_half_turn_differences=paired,
                centered_opposite_differences=centered,body_metrics=counts)

baseline=json.loads((HERE.parent/'mv4_20261002/final_experiment_20261003/candidate_s3.json').read_text())
candidate=json.loads((HERE/'compact43/reroute_best.json').read_text())
comparison=dict(banked_pl49=measure(baseline),symmetric_pl43=measure(candidate))
(HERE/'geometry_comparison.json').write_text(json.dumps(comparison,indent=2))

colors=['#007a99','#ba6100','#7c4a9e']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600">',
     '<rect width="900" height="600" fill="#faf9f6"/>',
     '<g font-family="Arial,sans-serif" fill="#222">',
     '<text x="36" y="44" font-size="26">mv4: three templates, each repeated opposite</text>',
     '<text x="36" y="74" font-size="17">Transverse layout; every core moves +1 over 2rt, then waits 1rt.</text>']
centers=candidate['centers'];counts=candidate['counts']
points=[(450+42*y,295-42*z) for y,z in centers]
svg.append('<path d="M '+' L '.join(f'{x},{y}' for x,y in points)+' Z" fill="none" stroke="#bbb" stroke-width="2"/>')
for i in range(3):
    x,y=points[i];u,v=points[i+3]
    svg.append(f'<line x1="{x}" y1="{y}" x2="{u}" y2="{v}" stroke="{colors[i]}" stroke-width="1" stroke-dasharray="5 6" opacity=".35"/>')
for i,(x,y) in enumerate(points):
    phase=i%3;label='ABC'[phase]
    svg.extend([f'<circle cx="{x}" cy="{y}" r="44" fill="{colors[phase]}"/>',
                f'<text x="{x}" y="{y-5}" text-anchor="middle" fill="white" font-size="22">{label}{1+i//3}</text>',
                f'<text x="{x}" y="{y+18}" text-anchor="middle" fill="white" font-size="14">{counts[i]} glue</text>'])
for i in range(3):
    svg.append(f'<text x="{36+i*285}" y="510" fill="{colors[i]}" font-size="18">Template {"ABC"[i]}: phase {i}rt</text>')
svg.extend(['<text x="36" y="550" font-size="16">Opposite copies rotate 180°; slime and honey exchange. Pistons all point +X.</text>',
            '<text x="36" y="578" font-size="15">This diagram shows bank structure, not a block-by-block construction plan.</text></g></svg>'])
(HERE/'layout.svg').write_text('\n'.join(svg),encoding='utf-8')
print(json.dumps(comparison,indent=2))

