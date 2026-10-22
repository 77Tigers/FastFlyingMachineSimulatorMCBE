"""Optimistic connected-glue bounds under witnessed mandatory phase exclusions."""
from search_T1_two_pushes import add,adj,dist
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum

def phase_witness(cells,groups,cap,word,material,obstacles):
 """Necessary bound after excluding contact with fixed or mandatory cells."""
 removed={}
 for name,shape,kind,otherword in obstacles:
  for k in sorted(offsets(word,otherword)):
   for q in sorted(shape):
    center=add(q,(-k,0,0));candidates=[center,*adj(center)] if material==kind else [center]
    for p in candidates:
     if p in cells and p not in removed:removed[p]={'body':name,'blocker_cell':q,'relative_x':k,'distance':dist(add(p,(k,0,0)),q)}
 allowed=cells-removed.keys();minimum=connected_glue_minimum(allowed,groups)
 return {'minimum':minimum,'cap':cap,'cap_feasible':minimum is not None and minimum<=cap,
         'allowed_cells':sorted(allowed),'contact_groups':[{'cells':sorted(g),'allowed':sorted(set(g)&allowed)} for g in groups],'excluded_cells':[{'cell':p,**v} for p,v in sorted(removed.items())]}
