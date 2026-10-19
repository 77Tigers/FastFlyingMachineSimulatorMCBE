"""Change H0's early firing/recovery rows jointly with G0 source/columns.

This bounded geometry generator preserves all phase states. Its necessary
power/contact checks are hypotheses; only strict native verification accepts.
"""
import argparse,hashlib,itertools,json
from pathlib import Path
from ortools.sat.python import cp_model
from model_recovery_layout import connectivity


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('parent',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();parent=json.loads(a.parent.read_text(encoding='utf-8'))['results'][37]
    old={tuple(c[:3]):c[3] for c in parent['macro_cells']}
    results=[];statuses={};allocations=0
    for hrows in itertools.combinations([(-1,13),(1,13),(0,12)],2):
      fixed={p:b for p,b in old.items() if b!=2 and b!=1 and p not in [(18,1,14),(17,0,14),(17,1,13),(17,1,15),(21,-1,13),(21,1,13)]}
      for y,z in hrows:fixed[21,y,z]=9
      hglue={(22,0,13),(22,0,14),*((22,y,z) for y,z in hrows)}
      for p in hglue:
        assert p not in fixed;fixed[p]=1
      for cy in range(-1,3):
       for cz in range(12,16):
        for rows in itertools.combinations([(cy-1,cz),(cy+1,cz),(cy,cz-1),(cy,cz+1)],3):
          rb=(18,cy,cz);norms={(17,y,z) for y,z in rows};actors=norms|{rb}
          if len(actors)!=4 or actors&fixed.keys() or (17,0,13) in actors:continue
          mandatory={(19,cy,cz),(19,0,14),*((19,y,z) for y,z in hrows),*((19,y,z) for y,z in rows)}
          if len(mandatory)>7 or mandatory&(fixed.keys()|actors):continue
          model=cp_model.CpModel()
          gs={(19,y,z):model.NewBoolVar(f'g{y}_{z}') for y in range(-2,4) for z in range(11,17) if (19,y,z) not in fixed and (19,y,z) not in actors}
          if not mandatory<=gs.keys():continue
          for p in mandatory:model.Add(gs[p]==1)
          model.Add(sum(gs.values())<=7)
          connectivity(model,gs,(19,cy,cz),7);model.Minimize(sum(gs.values()))
          solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=.25;solver.parameters.num_search_workers=1
          solved=solver.Solve(model);key=solver.StatusName(solved);statuses[key]=statuses.get(key,0)+1;allocations+=1
          if solved not in (cp_model.OPTIMAL,cp_model.FEASIBLE):continue
          shape={p for p,v in gs.items() if solver.Value(v)}
          cells={**fixed,rb:6,**{p:9 for p in norms},**{p:2 for p in shape}}
          assert len(cells)==len(fixed)+4+len(shape)
          # Shared RB powers all G0 rows after their T0 carry0. H0's
          # two early normals remain lateral neighbors of RB21,0,13.
          assert all(abs(y-cy)+abs(z-cz)==1 for y,z in rows)
          assert all(abs(y)+abs(z-13)==1 for y,z in hrows)
          m={**parent,'macro_cells':[[*p,b] for p,b in sorted(cells.items())],'G0_normals_at_initial':[list(p) for p in sorted(norms)],
             'family':{'parent_macro':37,'H0_early_rows':hrows,'H0_glue':sorted(hglue),'G0_source':rb,'G0_rows':rows,'G0_glue':sorted(shape),'CP_status':key}}
          results.append(m)
    results.sort(key=lambda m:(len(m['family']['G0_glue']),m['family']['G0_source'],m['family']['H0_early_rows']))
    a.out.write_text(json.dumps({'scope':__doc__,'parent_sha256':hashlib.sha256(a.parent.read_bytes()).hexdigest(),'allocations':allocations,'statuses':statuses,'results':results},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'allocations':allocations,'statuses':statuses,'macros':len(results)}))


if __name__=='__main__':main()
