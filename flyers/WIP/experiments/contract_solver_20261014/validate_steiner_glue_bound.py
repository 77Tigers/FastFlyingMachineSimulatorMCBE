"""Reproduce independent brute-force and saved CP calibration of glue bounds."""
import itertools,json,random,hashlib
from pathlib import Path
from steiner_glue_bound import connected_glue_minimum
HERE=Path(__file__).resolve().parent

def connected(s):
 if not s:return False
 seen={next(iter(s))};todo=list(seen)
 while todo:
  x,y,z=todo.pop()
  for q in [(x-1,y,z),(x+1,y,z),(x,y-1,z),(x,y+1,z)]:
   if q in s and q not in seen:seen.add(q);todo.append(q)
 return seen==s

def main():
 count=0
 for group_limit in [3,5]:
  rng=random.Random(20261021)
  for trial in range(150):
   cells=set(rng.sample([(x,y,0) for x in range(3) for y in range(3)],rng.randrange(3,10)));groups=[set(rng.sample(sorted(cells),rng.randrange(1,min(3,len(cells))+1))) for _ in range(rng.randrange(1,group_limit+1))];brute=None
   for k in range(1,len(cells)+1):
    if any(connected(set(s)) and all(set(s)&g for g in groups) for s in itertools.combinations(cells,k)):brute=k;break
   assert connected_glue_minimum(cells,groups)==brute,(group_limit,trial,cells,groups,brute);count+=1
 run=HERE/'out/quarter_ring_contacts/joint_T1_both_X1_search';cp=json.loads((run/'per_body_glue_minima.json').read_text(encoding='utf-8'));dp=json.loads((run/'per_body_exact_steiner.json').read_text(encoding='utf-8'));checks=0
 for old,new in zip(cp['records'],dp['records']):
  assert old['index']==new['index']
  for n,v in old['bodies'].items():
   if v.get('optimal_minimum') is not None:assert v['optimal_minimum']==new['bodies'][n]['optimal_minimum'];checks+=1
 report={'bruteforce_graphs_passed':count,'seed':20261021,'group_limits':[3,5],'CP_optima_matched':checks,'solver_sha256':hashlib.sha256((HERE/'steiner_glue_bound.py').read_bytes()).hexdigest(),'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Exact optimistic connectivity count only; native acceptance unchanged.'};(run/'steiner_validation_reproduced.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(report)
if __name__=='__main__':main()
