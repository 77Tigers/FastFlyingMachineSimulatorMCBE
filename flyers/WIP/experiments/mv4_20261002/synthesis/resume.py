"""Bounded continuation using the saved placement, hard candidate limit49."""
import six,search,json,subprocess
from pathlib import Path
out=search.OUT/'resume_candidates';out.mkdir(exist_ok=True)
best=json.loads((search.OUT.parent/'contacts/compact/six_bank.json').read_text())['best']
placement=(best['centers'],[r for r,m in best['orientations']],[-1 if m else 1 for r,m in best['orientations']])
records=[]
for kind,seeds in [('six',range(8)),('three',range(30))]:
 for seed in seeds:
  ans,why=six.build(seed,placement,cap=38) if kind=='six' else search.build(seed,compact=True,corecap=38)
  rec=dict(kind=kind,seed=seed,failure=why)
  if ans:
   f,m=ans;f.push_limit=49;p=out/f'{kind}_{seed}_pl49.flyer';f.save(p)
   rec['metadata']=m
   run=subprocess.run([str(search.ROOT/'target/release/fastflyer-research.exe'),'audit',str(p),'120','12'],capture_output=True,text=True)
   rec['audit']=run.stdout+run.stderr
   print(kind,seed,m['counts'],rec['audit'],flush=True)
   records.append(rec);(search.OUT/'resume.json').write_text(json.dumps(records,indent=2))
   if 'distance=40 ' in rec['audit'] and 'movement_failures=0' in rec['audit'] and 'conservation_mismatch_ticks=0' in rec['audit']:
    print('WORKING',p,flush=True);raise SystemExit(0)
  else:
   records.append(rec);print(kind,seed,why,flush=True)
   (search.OUT/'resume.json').write_text(json.dumps(records,indent=2))
