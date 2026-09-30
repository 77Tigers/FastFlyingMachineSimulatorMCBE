"""Bound axial spans of the new fixed sparse role contracts, not global loads."""
from pathlib import Path
import json,itertools
h=Path(__file__).resolve().parent
back=json.loads((h/'compact_mixed_tile_contact_cover.json').read_text());front=json.loads((h/'pull_first_contact_cover.json').read_text())
S=[[(t+p)%5<3 for t in range(5)] for p in range(5)];D=[[sum(word[:t]) for t in range(5)] for word in S]
best=(100,1000);winners=[]
for tail in itertools.product(range(-3,4),repeat=4):
 gauge=(0,)+tail;sets=[set() for _ in range(10)]
 for node in range(10):
  phase=3*node%5;cover=front if node%2 else back;origin=cover['delta'];fi=gauge[phase]
  sets[node].update(p[0]-origin[0]+fi for p in cover['patches'][5])
  helpers=({4:(node+3)%10,3:(node+1)%10,1:(node-3)%10} if node%2 else {2:(node-1)%10,3:(node+1)%10,4:(node+3)%10})
  for old,new in helpers.items():sets[new].update(p[0]-origin[0]+D[old][phase]-D[0][phase]+fi for p in cover['patches'][old])
 spans=[max(values)-min(values) for values in sets];score=(max(spans),sum(spans))
 if score<best:best=score;winners=[]
 if score==best:winners.append(dict(gauge=gauge,spans=spans))
result=dict(search=2401,gauge_range=[-3,3],best=best,winners=winners,scope='fixed sparse contracts with one gauge per phase; X span only, not a global load lower bound')
(h/'hybrid_axial_bounds.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
