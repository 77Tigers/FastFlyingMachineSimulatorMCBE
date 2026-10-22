"""Necessary T0 routing counts for the budgeted G0 recovery trade; no native acceptance."""
import hashlib,itertools,json
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Kind
from search_T1_two_pushes import adj,dist,add,witnessed_sticky_pickup
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum
HERE=Path(__file__).resolve().parent

def main():
 base=HERE/'out/quarter_ring_contacts/G0_front_recovery_upper';f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={q['name']:q for q in c['ports']};root=(15,3,11);late=(19,4,11)
 fixed=set(f._cells)-body_of(f._cells,root)-body_of(f._cells,tuple(ports['X1_front']['at']));g0=body_of(f._cells,tuple(ports['G0']['at']));waiting=g0|{q for q,b in f._cells.items() if b.kind in [Kind.REDSTONE_BLOCK,Kind.OBSERVER] and any(dist(q,x)==1 for x in g0)}
 others=[(body_of(f._cells,tuple(q['at'])),f._cells[tuple(q['at'])].kind,q['word']) for q in c['ports'] if q['name'] not in ['T0','X1_front']];gm={(16,6,12),(16,5,13),(16,5,11)};answer=[]
 for k in [1,2]:
  moved=set([(16,6,12),(16,5,13)][:k]);cs={q for q in itertools.product(range(11,24),range(0,11),range(7,19)) if q not in fixed and dist(root,q)+dist(q,late)+dist(root,late)<=16 and not witnessed_sticky_pickup(q) and add(q,(1,0,0)) not in waiting and not any(dist(q,m)<=1 for m in gm-moved)}
  for material_exclusion in [False,True]:
   cells={q for q in cs if not material_exclusion or not any(mat==Kind.SLIME and any(dist(add(q,(x,0,0)),v)<=1 for x in offsets('mwwmm',word) for v in sh) for sh,mat,word in others)}
   minimum=connected_glue_minimum(cells,[{root},{late}]+[set(adj(m)) for m in moved]);answer.append({'transferred_G0_slots':list(range(1,k+1)),'fixed_material_exclusion':material_exclusion,'T0_minimum':minimum,'cap':9,'domain_cells':len(cells),'can_fit_optimistically':minimum is not None and minimum<=9})
 out=HERE/'out/quarter_ring_contacts/G0_T0_recovery_trade_budget/free_T0_geometry_bound.json';report={'scope':'Exact optimistic T0 connector count within necessary cap9 domains and fixed rear hardware. Omits new source/gate actors and other variable-body separation; false material exclusion is an additional relaxation. Not physical acceptance or global architecture impossibility.','base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'records':answer};out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
